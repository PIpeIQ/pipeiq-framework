from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
import json
import aiohttp
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import time
import hashlib

class InquiryStatus(str, Enum):
    """Status of a Persona inquiry."""
    CREATED = "created"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REVIEW = "review"

class VerificationType(str, Enum):
    """Types of verifications supported by Persona."""
    GOVERNMENT_ID = "government_id"
    SELFIE = "selfie"
    DATABASE = "database"
    DOCUMENT = "document"
    PHONE = "phone"
    EMAIL = "email"
    NFC = "nfc"

class ReportType(str, Enum):
    """Types of reports available in Persona."""
    WATCHLIST = "watchlist"
    SANCTIONS = "sanctions"
    ADVERSE_MEDIA = "adverse_media"
    POLITICALLY_EXPOSED = "politically_exposed"

class DocumentType(str, Enum):
    """Types of documents supported by Persona."""
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    ID_CARD = "id_card"
    RESIDENCE_PERMIT = "residence_permit"
    VISA = "visa"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"

class CaseStatus(str, Enum):
    """Status of a Persona case."""
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    REVIEW = "review"
    APPROVED = "approved"
    DECLINED = "declined"

class VerificationMethod(str, Enum):
    """Methods for verification."""
    DOCUMENT = "document"
    SELFIE = "selfie"
    DATABASE = "database"
    PHONE = "phone"
    EMAIL = "email"
    NFC = "nfc"
    FACE_MATCH = "face_match"
    LIVENESS = "liveness"

class WebhookEventType(str, Enum):
    """Types of webhook events supported by Persona."""
    INQUIRY_CREATED = "inquiry.created"
    INQUIRY_COMPLETED = "inquiry.completed"
    INQUIRY_REVIEWED = "inquiry.reviewed"
    DOCUMENT_VERIFIED = "document.verified"
    CASE_CREATED = "case.created"
    CASE_UPDATED = "case.updated"
    REPORT_GENERATED = "report.generated"

class BatchOperationType(str, Enum):
    """Types of batch operations supported."""
    CREATE_INQUIRIES = "create_inquiries"
    UPDATE_CASES = "update_cases"
    GENERATE_REPORTS = "generate_reports"
    VERIFY_DOCUMENTS = "verify_documents"

class RetryStrategy(str, Enum):
    """Strategies for retrying failed requests."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CONSTANT = "constant"

@dataclass
class InquiryConfig:
    """Configuration for creating a Persona inquiry."""
    template_id: str
    reference_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    redirect_url: Optional[str] = None
    webhook_url: Optional[str] = None

@dataclass
class VerificationConfig:
    """Configuration for creating a verification."""
    type: VerificationType
    country: Optional[str] = None
    document_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ReportConfig:
    """Configuration for creating a report."""
    type: ReportType
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DocumentConfig:
    """Configuration for document verification."""
    type: DocumentType
    country: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    front_image: Optional[str] = None  # Base64 encoded image
    back_image: Optional[str] = None   # Base64 encoded image
    selfie_image: Optional[str] = None # Base64 encoded image

@dataclass
class CaseConfig:
    """Configuration for creating a case."""
    reference_id: str
    status: CaseStatus = CaseStatus.OPEN
    metadata: Optional[Dict[str, Any]] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None

@dataclass
class VerificationMethodConfig:
    """Configuration for verification methods."""
    method: VerificationMethod
    enabled: bool = True
    options: Optional[Dict[str, Any]] = None

@dataclass
class WebhookConfig:
    """Configuration for webhook endpoints."""
    url: str
    events: List[WebhookEventType]
    secret: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BatchOperationConfig:
    """Configuration for batch operations."""
    type: BatchOperationType
    items: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: int
    burst_size: int = 1
    window_size: int = 1  # in seconds

@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""
    max_retries: int = 3
    initial_delay: float = 1.0  # in seconds
    max_delay: float = 30.0  # in seconds
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])

@dataclass
class CacheConfig:
    """Configuration for caching."""
    ttl: int = 300  # time to live in seconds
    max_size: int = 1000  # maximum number of cached items
    enabled: bool = True

class RateLimiter:
    """Rate limiter implementation using token bucket algorithm."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire a token from the rate limiter."""
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(
                self.config.burst_size,
                self.tokens + time_passed * self.config.requests_per_second
            )
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.config.requests_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 1
            
            self.tokens -= 1
            self.last_update = now

class Cache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if not self.config.enabled:
            return None
            
        async with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if time.time() < item["expires_at"]:
                    return item["value"]
                del self.cache[key]
        return None
    
    async def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        if not self.config.enabled:
            return
            
        async with self.lock:
            if len(self.cache) >= self.config.max_size:
                # Remove oldest item
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]["expires_at"]
                )
                del self.cache[oldest_key]
            
            self.cache[key] = {
                "value": value,
                "expires_at": time.time() + self.config.ttl
            }

def with_retry(config: RetryConfig):
    """Decorator for adding retry mechanism to async functions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        break
                    
                    if isinstance(e, aiohttp.ClientResponseError):
                        if e.status not in config.retry_on_status_codes:
                            raise
                    
                    if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                        delay = min(delay * 2, config.max_delay)
                    elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
                        delay = min(delay + config.initial_delay, config.max_delay)
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

def with_cache(cache: Cache):
    """Decorator for adding caching to async functions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache.config.enabled:
                return await func(*args, **kwargs)
            
            # Skip caching for non-GET requests
            if "method" in kwargs and kwargs["method"] != "GET":
                return await func(*args, **kwargs)
            
            key = cache._generate_key(*args, **kwargs)
            cached_value = await cache.get(key)
            
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            await cache.set(key, result)
            return result
        return wrapper
    return decorator

class PersonaError(Exception):
    """Base exception for Persona-related errors."""
    pass

class ConnectionError(PersonaError):
    """Raised when there's an error connecting to Persona."""
    pass

class VerificationError(PersonaError):
    """Raised when there's an error during verification."""
    pass

class ReportError(PersonaError):
    """Raised when there's an error generating a report."""
    pass

class PersonaService:
    """Service for interacting with Persona's identity verification API."""
    
    def __init__(
        self,
        api_key: str,
        environment: str = "sandbox",
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        cache_config: Optional[CacheConfig] = None
    ):
        """Initialize the Persona service.
        
        Args:
            api_key: Your Persona API key
            environment: API environment ('sandbox' or 'production')
            rate_limit_config: Rate limit configuration
            retry_config: Retry configuration
            cache_config: Cache configuration
        """
        self.api_key = api_key
        self.environment = environment
        self.base_url = f"https://{environment}.withpersona.com/api/v1"
        self.session = None
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            rate_limit_config or RateLimitConfig(requests_per_second=10)
        )
        
        # Initialize cache
        self.cache = Cache(cache_config or CacheConfig())
        
        # Store retry config
        self.retry_config = retry_config or RetryConfig()

    async def __aenter__(self):
        """Set up the aiohttp session."""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the aiohttp session."""
        if self.session:
            await self.session.close()

    @with_retry(RetryConfig())
    @with_cache(Cache(CacheConfig()))
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to the Persona API with rate limiting."""
        if not self.session:
            raise ConnectionError("Not connected to Persona API")
        
        await self.rate_limiter.acquire()
        
        async with self.session.request(
            method,
            f"{self.base_url}/{endpoint}",
            **kwargs
        ) as response:
            if response.status >= 400:
                error_text = await response.text()
                if response.status == 429:
                    raise PersonaError("Rate limit exceeded")
                raise PersonaError(f"API error: {error_text}")
            return await response.json()

    async def create_inquiry(self, config: InquiryConfig) -> Dict[str, Any]:
        """Create a new identity verification inquiry.
        
        Args:
            config: Inquiry configuration
            
        Returns:
            Dict containing inquiry details
        """
        data = {
            "data": {
                "type": "inquiry",
                "attributes": {
                    "template_id": config.template_id,
                    "reference_id": config.reference_id,
                    "metadata": config.metadata,
                    "expires_at": config.expires_at.isoformat() if config.expires_at else None,
                    "redirect_url": config.redirect_url,
                    "webhook_url": config.webhook_url
                }
            }
        }
        
        return await self._make_request("POST", "inquiries", json=data)

    async def get_inquiry(self, inquiry_id: str) -> Dict[str, Any]:
        """Get details of a specific inquiry.
        
        Args:
            inquiry_id: ID of the inquiry to retrieve
            
        Returns:
            Dict containing inquiry details
        """
        return await self._make_request("GET", f"inquiries/{inquiry_id}")

    async def create_verification(self, inquiry_id: str, config: VerificationConfig) -> Dict[str, Any]:
        """Create a new verification for an inquiry.
        
        Args:
            inquiry_id: ID of the inquiry
            config: Verification configuration
            
        Returns:
            Dict containing verification details
        """
        data = {
            "data": {
                "type": "verification",
                "attributes": {
                    "type": config.type.value,
                    "country": config.country,
                    "document_type": config.document_type,
                    "metadata": config.metadata
                }
            }
        }
        
        return await self._make_request("POST", f"inquiries/{inquiry_id}/verifications", json=data)

    async def get_verification(self, inquiry_id: str, verification_id: str) -> Dict[str, Any]:
        """Get details of a specific verification.
        
        Args:
            inquiry_id: ID of the inquiry
            verification_id: ID of the verification
            
        Returns:
            Dict containing verification details
        """
        return await self._make_request("GET", f"inquiries/{inquiry_id}/verifications/{verification_id}")

    async def create_report(self, inquiry_id: str, config: ReportConfig) -> Dict[str, Any]:
        """Create a new report for an inquiry.
        
        Args:
            inquiry_id: ID of the inquiry
            config: Report configuration
            
        Returns:
            Dict containing report details
        """
        data = {
            "data": {
                "type": "report",
                "attributes": {
                    "type": config.type.value,
                    "metadata": config.metadata
                }
            }
        }
        
        return await self._make_request("POST", f"inquiries/{inquiry_id}/reports", json=data)

    async def get_report(self, inquiry_id: str, report_id: str) -> Dict[str, Any]:
        """Get details of a specific report.
        
        Args:
            inquiry_id: ID of the inquiry
            report_id: ID of the report
            
        Returns:
            Dict containing report details
        """
        return await self._make_request("GET", f"inquiries/{inquiry_id}/reports/{report_id}")

    async def list_inquiries(
        self,
        page_size: int = 10,
        page_number: int = 1,
        status: Optional[InquiryStatus] = None
    ) -> Dict[str, Any]:
        """List all inquiries with optional filtering.
        
        Args:
            page_size: Number of results per page
            page_number: Page number to retrieve
            status: Filter by inquiry status
            
        Returns:
            Dict containing list of inquiries and pagination info
        """
        params = {
            "page[size]": page_size,
            "page[number]": page_number
        }
        if status:
            params["filter[status]"] = status.value
            
        return await self._make_request("GET", "inquiries", params=params)

    async def approve_inquiry(self, inquiry_id: str) -> Dict[str, Any]:
        """Approve an inquiry.
        
        Args:
            inquiry_id: ID of the inquiry to approve
            
        Returns:
            Dict containing updated inquiry details
        """
        return await self._make_request("POST", f"inquiries/{inquiry_id}/approve")

    async def decline_inquiry(self, inquiry_id: str) -> Dict[str, Any]:
        """Decline an inquiry.
        
        Args:
            inquiry_id: ID of the inquiry to decline
            
        Returns:
            Dict containing updated inquiry details
        """
        return await self._make_request("POST", f"inquiries/{inquiry_id}/decline")

    async def mark_for_review(self, inquiry_id: str) -> Dict[str, Any]:
        """Mark an inquiry for manual review.
        
        Args:
            inquiry_id: ID of the inquiry to mark for review
            
        Returns:
            Dict containing updated inquiry details
        """
        return await self._make_request("POST", f"inquiries/{inquiry_id}/review")

    async def create_document_verification(
        self,
        inquiry_id: str,
        config: DocumentConfig
    ) -> Dict[str, Any]:
        """Create a document verification.
        
        Args:
            inquiry_id: ID of the inquiry
            config: Document configuration
            
        Returns:
            Dict containing verification details
        """
        data = {
            "data": {
                "type": "document_verification",
                "attributes": {
                    "document_type": config.type.value,
                    "country": config.country,
                    "metadata": config.metadata,
                    "front_image": config.front_image,
                    "back_image": config.back_image,
                    "selfie_image": config.selfie_image
                }
            }
        }
        
        return await self._make_request("POST", f"inquiries/{inquiry_id}/document_verifications", json=data)

    async def create_case(self, config: CaseConfig) -> Dict[str, Any]:
        """Create a new case.
        
        Args:
            config: Case configuration
            
        Returns:
            Dict containing case details
        """
        data = {
            "data": {
                "type": "case",
                "attributes": {
                    "reference_id": config.reference_id,
                    "status": config.status.value,
                    "metadata": config.metadata,
                    "assignee": config.assignee,
                    "tags": config.tags
                }
            }
        }
        
        return await self._make_request("POST", "cases", json=data)

    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """Get details of a specific case.
        
        Args:
            case_id: ID of the case
            
        Returns:
            Dict containing case details
        """
        return await self._make_request("GET", f"cases/{case_id}")

    async def update_case(
        self,
        case_id: str,
        status: Optional[CaseStatus] = None,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update a case.
        
        Args:
            case_id: ID of the case
            status: New case status
            assignee: New assignee
            tags: New tags
            metadata: New metadata
            
        Returns:
            Dict containing updated case details
        """
        data = {
            "data": {
                "type": "case",
                "attributes": {}
            }
        }
        
        if status:
            data["data"]["attributes"]["status"] = status.value
        if assignee:
            data["data"]["attributes"]["assignee"] = assignee
        if tags:
            data["data"]["attributes"]["tags"] = tags
        if metadata:
            data["data"]["attributes"]["metadata"] = metadata
            
        return await self._make_request("PATCH", f"cases/{case_id}", json=data)

    async def configure_verification_methods(
        self,
        inquiry_id: str,
        methods: List[VerificationMethodConfig]
    ) -> Dict[str, Any]:
        """Configure verification methods for an inquiry.
        
        Args:
            inquiry_id: ID of the inquiry
            methods: List of verification method configurations
            
        Returns:
            Dict containing updated inquiry details
        """
        data = {
            "data": {
                "type": "verification_methods",
                "attributes": {
                    "methods": [
                        {
                            "method": method.method.value,
                            "enabled": method.enabled,
                            "options": method.options
                        }
                        for method in methods
                    ]
                }
            }
        }
        
        return await self._make_request("POST", f"inquiries/{inquiry_id}/verification_methods", json=data)

    async def get_verification_methods(self, inquiry_id: str) -> Dict[str, Any]:
        """Get configured verification methods for an inquiry.
        
        Args:
            inquiry_id: ID of the inquiry
            
        Returns:
            Dict containing verification method configurations
        """
        return await self._make_request("GET", f"inquiries/{inquiry_id}/verification_methods")

    async def list_cases(
        self,
        page_size: int = 10,
        page_number: int = 1,
        status: Optional[CaseStatus] = None,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List all cases with optional filtering.
        
        Args:
            page_size: Number of results per page
            page_number: Page number to retrieve
            status: Filter by case status
            assignee: Filter by assignee
            tags: Filter by tags
            
        Returns:
            Dict containing list of cases and pagination info
        """
        params = {
            "page[size]": page_size,
            "page[number]": page_number
        }
        if status:
            params["filter[status]"] = status.value
        if assignee:
            params["filter[assignee]"] = assignee
        if tags:
            params["filter[tags]"] = ",".join(tags)
            
        return await self._make_request("GET", "cases", params=params)

    async def add_case_tag(self, case_id: str, tag: str) -> Dict[str, Any]:
        """Add a tag to a case.
        
        Args:
            case_id: ID of the case
            tag: Tag to add
            
        Returns:
            Dict containing updated case details
        """
        data = {
            "data": {
                "type": "case_tag",
                "attributes": {
                    "tag": tag
                }
            }
        }
        
        return await self._make_request("POST", f"cases/{case_id}/tags", json=data)

    async def remove_case_tag(self, case_id: str, tag: str) -> Dict[str, Any]:
        """Remove a tag from a case.
        
        Args:
            case_id: ID of the case
            tag: Tag to remove
            
        Returns:
            Dict containing updated case details
        """
        return await self._make_request("DELETE", f"cases/{case_id}/tags/{tag}")

    async def register_webhook(self, config: WebhookConfig) -> Dict[str, Any]:
        """Register a webhook endpoint.
        
        Args:
            config: Webhook configuration
            
        Returns:
            Dict containing webhook registration details
        """
        data = {
            "data": {
                "type": "webhook",
                "attributes": {
                    "url": config.url,
                    "events": [event.value for event in config.events],
                    "secret": config.secret,
                    "metadata": config.metadata
                }
            }
        }
        
        return await self._make_request("POST", "webhooks", json=data)

    async def list_webhooks(self) -> Dict[str, Any]:
        """List all registered webhooks.
        
        Returns:
            Dict containing list of webhooks
        """
        return await self._make_request("GET", "webhooks")

    async def delete_webhook(self, webhook_id: str) -> None:
        """Delete a webhook endpoint.
        
        Args:
            webhook_id: ID of the webhook to delete
        """
        return await self._make_request("DELETE", f"webhooks/{webhook_id}")

    async def execute_batch_operation(self, config: BatchOperationConfig) -> Dict[str, Any]:
        """Execute a batch operation.
        
        Args:
            config: Batch operation configuration
            
        Returns:
            Dict containing batch operation results
        """
        data = {
            "data": {
                "type": "batch_operation",
                "attributes": {
                    "operation_type": config.type.value,
                    "items": config.items,
                    "options": config.options
                }
            }
        }
        
        return await self._make_request("POST", "batch_operations", json=data)

    async def get_batch_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """Get the status of a batch operation.
        
        Args:
            operation_id: ID of the batch operation
            
        Returns:
            Dict containing batch operation status and results
        """
        return await self._make_request("GET", f"batch_operations/{operation_id}")

    async def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
        secret: str
    ) -> bool:
        """Verify the signature of a webhook payload.
        
        Args:
            payload: Raw webhook payload
            signature: Webhook signature
            secret: Webhook secret
            
        Returns:
            bool indicating if signature is valid
        """
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    async def process_webhook_event(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a webhook event.
        
        Args:
            payload: Webhook event payload
            signature: Webhook signature
            secret: Webhook secret
            
        Returns:
            Dict containing processed event details
        """
        if signature and secret:
            if not await self.verify_webhook_signature(
                json.dumps(payload),
                signature,
                secret
            ):
                raise PersonaError("Invalid webhook signature")
        
        event_type = payload.get("data", {}).get("type")
        if not event_type:
            raise PersonaError("Invalid webhook payload")
            
        return {
            "event_type": event_type,
            "processed_at": datetime.utcnow().isoformat(),
            "payload": payload
        }

    async def create_batch_inquiries(
        self,
        inquiries: List[InquiryConfig]
    ) -> Dict[str, Any]:
        """Create multiple inquiries in a batch.
        
        Args:
            inquiries: List of inquiry configurations
            
        Returns:
            Dict containing batch operation results
        """
        config = BatchOperationConfig(
            type=BatchOperationType.CREATE_INQUIRIES,
            items=[{
                "type": "inquiry",
                "attributes": {
                    "reference_id": inquiry.reference_id,
                    "template_id": inquiry.template_id,
                    "metadata": inquiry.metadata
                }
            } for inquiry in inquiries]
        )
        
        return await self.execute_batch_operation(config)

    async def update_batch_cases(
        self,
        case_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update multiple cases in a batch.
        
        Args:
            case_updates: List of case updates
            
        Returns:
            Dict containing batch operation results
        """
        config = BatchOperationConfig(
            type=BatchOperationType.UPDATE_CASES,
            items=case_updates
        )
        
        return await self.execute_batch_operation(config)

    async def generate_batch_reports(
        self,
        reports: List[ReportConfig]
    ) -> Dict[str, Any]:
        """Generate multiple reports in a batch.
        
        Args:
            reports: List of report configurations
            
        Returns:
            Dict containing batch operation results
        """
        config = BatchOperationConfig(
            type=BatchOperationType.GENERATE_REPORTS,
            items=[{
                "type": "report",
                "attributes": {
                    "type": report.type.value,
                    "inquiry_id": report.inquiry_id,
                    "metadata": report.metadata
                }
            } for report in reports]
        )
        
        return await self.execute_batch_operation(config)

    async def verify_batch_documents(
        self,
        documents: List[DocumentConfig]
    ) -> Dict[str, Any]:
        """Verify multiple documents in a batch.
        
        Args:
            documents: List of document configurations
            
        Returns:
            Dict containing batch operation results
        """
        config = BatchOperationConfig(
            type=BatchOperationType.VERIFY_DOCUMENTS,
            items=[{
                "type": "document_verification",
                "attributes": {
                    "document_type": doc.type.value,
                    "country": doc.country,
                    "metadata": doc.metadata,
                    "front_image": doc.front_image,
                    "back_image": doc.back_image,
                    "selfie_image": doc.selfie_image
                }
            } for doc in documents]
        )
        
        return await self.execute_batch_operation(config)

    async def clear_cache(self) -> None:
        """Clear the cache."""
        async with self.cache.lock:
            self.cache.cache.clear()
    
    async def update_rate_limit(self, config: RateLimitConfig) -> None:
        """Update rate limit configuration."""
        self.rate_limiter = RateLimiter(config)
    
    async def update_retry_config(self, config: RetryConfig) -> None:
        """Update retry configuration."""
        self.retry_config = config
    
    async def update_cache_config(self, config: CacheConfig) -> None:
        """Update cache configuration."""
        self.cache.config = config
        if not config.enabled:
            await self.clear_cache() 