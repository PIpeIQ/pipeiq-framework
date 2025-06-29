from typing import Dict, Optional, Any, List, Union, Callable
import requests
from .logger import logger
from .solana import SolanaWallet
from datetime import datetime, timedelta
import json
import asyncio
from ratelimit import limits, sleep_and_retry
import uuid
from enum import Enum
import hashlib

class AttestationStatus(Enum):
    """Enum for attestation status."""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING = "pending"
    FAILED = "failed"

class AttestationError(Exception):
    """Base exception for attestation service errors."""
    pass

class AttestationValidationError(AttestationError):
    """Raised when attestation validation fails."""
    pass

class AttestationVersionError(AttestationError):
    """Raised when attestation versioning operations fail."""
    pass

class AuditLogEntry:
    """Represents an audit log entry for attestation operations."""
    
    def __init__(
        self,
        operation: str,
        attestation_id: str,
        wallet_address: str,
        timestamp: datetime,
        details: Dict[str, Any],
        version: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.operation = operation
        self.attestation_id = attestation_id
        self.wallet_address = wallet_address
        self.timestamp = timestamp
        self.details = details
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log entry to dictionary."""
        return {
            "id": self.id,
            "operation": self.operation,
            "attestation_id": self.attestation_id,
            "wallet_address": self.wallet_address,
            "timestamp": int(self.timestamp.timestamp()),
            "details": self.details,
            "version": self.version
        }

class AttestationVersion:
    """Represents a version of an attestation."""
    
    def __init__(
        self,
        attestation_id: str,
        version: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        created_at: datetime,
        created_by: str,
        changes: Optional[Dict[str, Any]] = None
    ):
        self.attestation_id = attestation_id
        self.version = version
        self.data = data
        self.metadata = metadata
        self.created_at = created_at
        self.created_by = created_by
        self.changes = changes or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary."""
        return {
            "attestation_id": self.attestation_id,
            "version": self.version,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": int(self.created_at.timestamp()),
            "created_by": self.created_by,
            "changes": self.changes
        }

class AttestationTemplate:
    """Template for creating attestations with predefined structure."""
    
    def __init__(
        self,
        name: str,
        schema: Dict[str, Any],
        required_fields: List[str],
        default_metadata: Optional[Dict[str, Any]] = None,
        default_tags: Optional[List[str]] = None,
        default_expiry_days: Optional[int] = None,
        version: str = "1.0.0"
    ):
        self.name = name
        self.schema = schema
        self.required_fields = required_fields
        self.default_metadata = default_metadata or {}
        self.default_tags = default_tags or []
        self.default_expiry_days = default_expiry_days
        self.version = version

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data against the template schema."""
        try:
            # Check required fields
            for field in self.required_fields:
                if field not in data:
                    raise AttestationValidationError(f"Missing required field: {field}")
            
            # Validate against schema
            # Add schema validation logic here
            return True
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return False

class WebhookHandler:
    """Handler for attestation service webhooks."""
    
    def __init__(self, secret: str):
        self.secret = secret
        self.handlers: Dict[str, List[Callable]] = {}
        
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
    async def handle_webhook(self, payload: Dict[str, Any], signature: str):
        """Handle incoming webhook payload."""
        try:
            # Verify webhook signature
            if not self._verify_signature(payload, signature):
                raise AttestationError("Invalid webhook signature")
                
            event_type = payload.get("event_type")
            if event_type not in self.handlers:
                logger.warning(f"No handlers registered for event type: {event_type}")
                return
                
            # Call registered handlers
            for handler in self.handlers[event_type]:
                try:
                    await handler(payload)
                except Exception as e:
                    logger.error(f"Handler error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Webhook handling error: {str(e)}")
            raise AttestationError(f"Webhook handling error: {str(e)}")
            
    def _verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify webhook signature."""
        # Add signature verification logic here
        return True

class AttestationService:
    def __init__(
        self,
        solana_wallet: SolanaWallet,
        base_url: str = "https://attestation.solana.com",
        network: str = "mainnet-beta",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit: int = 100,  # requests per minute
        webhook_secret: Optional[str] = None,
        enable_audit_logging: bool = True
    ):
        """
        Initialize the Solana Attestation Service client.
        
        Args:
            solana_wallet: Solana wallet instance for signing
            base_url: Base URL for the attestation service
            network: Solana network to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit: Maximum requests per minute
            webhook_secret: Secret for webhook signature verification
            enable_audit_logging: Whether to enable audit logging
        """
        self.wallet = solana_wallet
        self.base_url = base_url
        self.network = network
        self.timeout = timeout
        self.webhook_handler = WebhookHandler(webhook_secret) if webhook_secret else None
        self.enable_audit_logging = enable_audit_logging
        self._audit_logs: List[AuditLogEntry] = []
        
        # Configure session with retry strategy
        self._session = requests.Session()
        retry_strategy = requests.adapters.Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        
        # Configure rate limiting
        self._rate_limited_request = sleep_and_retry(
            limits(calls=rate_limit, period=60)(self._make_request)
        )
        
        logger.info(f"Initialized Attestation Service for network: {network}")

    def _log_audit(self, operation: str, attestation_id: str, details: Dict[str, Any], version: Optional[str] = None):
        """Log an audit entry."""
        if not self.enable_audit_logging:
            return
            
        entry = AuditLogEntry(
            operation=operation,
            attestation_id=attestation_id,
            wallet_address=str(self.wallet.public_key),
            timestamp=datetime.now(),
            details=details,
            version=version
        )
        self._audit_logs.append(entry)
        logger.debug(f"Audit log entry created: {entry.to_dict()}")

    async def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a rate-limited request."""
        return self._session.request(method, url, **kwargs)

    def _generate_version(self, data: Dict[str, Any]) -> str:
        """Generate a version hash for attestation data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:10]

    async def create_attestation(
        self,
        data: Dict[str, Any],
        attestation_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new attestation.
        
        Args:
            data: The data to be attested
            attestation_type: Type of attestation
            metadata: Optional metadata for the attestation
            expires_at: Optional expiration timestamp
            tags: Optional list of tags for categorization
            
        Returns:
            Dict containing attestation details
            
        Raises:
            AttestationError: If attestation creation fails
        """
        try:
            # Generate version
            version = self._generate_version(data)
            
            # Prepare the attestation request
            payload = {
                "data": data,
                "type": attestation_type,
                "wallet_address": str(self.wallet.public_key),
                "network": self.network,
                "timestamp": int(datetime.now().timestamp()),
                "version": version
            }
            
            if metadata:
                payload["metadata"] = metadata
            if expires_at:
                payload["expires_at"] = int(expires_at.timestamp())
            if tags:
                payload["tags"] = tags
                
            # Sign the request
            signature = await self.wallet.sign_message(json.dumps(payload, sort_keys=True))
            payload["signature"] = signature
            
            # Make the API request
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Creating attestation of type: {attestation_type}")
            response = await self._rate_limited_request(
                "POST",
                f"{self.base_url}/v1/attestations",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Attestation creation failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully created attestation: {result['id']}")
            
            # Log audit entry
            self._log_audit(
                "create",
                result["id"],
                {
                    "type": attestation_type,
                    "version": version,
                    "status": AttestationStatus.ACTIVE.value
                },
                version
            )
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def update_attestation(
        self,
        attestation_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing attestation with a new version.
        
        Args:
            attestation_id: ID of the attestation to update
            data: New data for the attestation
            metadata: Optional new metadata
            reason: Optional reason for the update
            
        Returns:
            Dict containing updated attestation details
            
        Raises:
            AttestationError: If update fails
        """
        try:
            # Get current attestation
            current = await self.get_attestation(attestation_id)
            
            # Generate new version
            new_version = self._generate_version(data)
            
            # Prepare update payload
            payload = {
                "data": data,
                "wallet_address": str(self.wallet.public_key),
                "timestamp": int(datetime.now().timestamp()),
                "version": new_version,
                "previous_version": current["version"]
            }
            
            if metadata:
                payload["metadata"] = metadata
            if reason:
                payload["reason"] = reason
                
            # Sign the request
            signature = await self.wallet.sign_message(json.dumps(payload, sort_keys=True))
            payload["signature"] = signature
            
            logger.debug(f"Updating attestation: {attestation_id}")
            response = await self._rate_limited_request(
                "PUT",
                f"{self.base_url}/v1/attestations/{attestation_id}",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Attestation update failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully updated attestation: {attestation_id}")
            
            # Log audit entry
            self._log_audit(
                "update",
                attestation_id,
                {
                    "previous_version": current["version"],
                    "new_version": new_version,
                    "reason": reason
                },
                new_version
            )
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def get_attestation_versions(
        self,
        attestation_id: str,
        page: int = 1,
        per_page: int = 20
    ) -> List[AttestationVersion]:
        """
        Get version history of an attestation.
        
        Args:
            attestation_id: ID of the attestation
            page: Page number for pagination
            per_page: Number of versions per page
            
        Returns:
            List of attestation versions
            
        Raises:
            AttestationError: If retrieval fails
        """
        try:
            logger.debug(f"Getting versions for attestation: {attestation_id}")
            response = await self._rate_limited_request(
                "GET",
                f"{self.base_url}/v1/attestations/{attestation_id}/versions",
                params={"page": page, "per_page": per_page},
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Version retrieval failed: {response.text}")
                
            versions = response.json()
            return [
                AttestationVersion(
                    attestation_id=v["attestation_id"],
                    version=v["version"],
                    data=v["data"],
                    metadata=v["metadata"],
                    created_at=datetime.fromtimestamp(v["created_at"]),
                    created_by=v["created_by"],
                    changes=v.get("changes")
                )
                for v in versions
            ]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def get_audit_logs(
        self,
        attestation_id: Optional[str] = None,
        operation: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[AuditLogEntry]:
        """
        Get audit logs with optional filters.
        
        Args:
            attestation_id: Optional attestation ID filter
            operation: Optional operation type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            page: Page number for pagination
            per_page: Number of entries per page
            
        Returns:
            List of audit log entries
            
        Raises:
            AttestationError: If retrieval fails
        """
        try:
            params = {
                "page": page,
                "per_page": per_page
            }
            
            if attestation_id:
                params["attestation_id"] = attestation_id
            if operation:
                params["operation"] = operation
            if start_time:
                params["start_time"] = int(start_time.timestamp())
            if end_time:
                params["end_time"] = int(end_time.timestamp())
                
            logger.debug("Getting audit logs")
            response = await self._rate_limited_request(
                "GET",
                f"{self.base_url}/v1/audit-logs",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Audit log retrieval failed: {response.text}")
                
            logs = response.json()
            return [
                AuditLogEntry(
                    operation=l["operation"],
                    attestation_id=l["attestation_id"],
                    wallet_address=l["wallet_address"],
                    timestamp=datetime.fromtimestamp(l["timestamp"]),
                    details=l["details"],
                    version=l.get("version")
                )
                for l in logs
            ]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def create_attestation_from_template(
        self,
        template: AttestationTemplate,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create an attestation using a template.
        
        Args:
            template: Attestation template to use
            data: Data to be attested
            metadata: Optional metadata
            tags: Optional tags
            expires_at: Optional expiration timestamp
            
        Returns:
            Dict containing attestation details
            
        Raises:
            AttestationError: If attestation creation fails
        """
        if not template.validate_data(data):
            raise AttestationError("Data validation failed")
            
        # Merge with template defaults
        final_metadata = {**template.default_metadata, **(metadata or {})}
        final_tags = template.default_tags + (tags or [])
        
        if expires_at is None and template.default_expiry_days:
            expires_at = datetime.now() + timedelta(days=template.default_expiry_days)
            
        return await self.create_attestation(
            data=data,
            attestation_type=template.name,
            metadata=final_metadata,
            tags=final_tags,
            expires_at=expires_at
        )

    async def register_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a webhook endpoint.
        
        Args:
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            secret: Optional webhook secret
            
        Returns:
            Dict containing webhook registration details
            
        Raises:
            AttestationError: If registration fails
        """
        try:
            payload = {
                "url": url,
                "events": events,
                "wallet_address": str(self.wallet.public_key),
                "network": self.network
            }
            
            if secret:
                payload["secret"] = secret
                
            signature = await self.wallet.sign_message(json.dumps(payload, sort_keys=True))
            payload["signature"] = signature
            
            logger.debug(f"Registering webhook for events: {events}")
            response = await self._rate_limited_request(
                "POST",
                f"{self.base_url}/v1/webhooks",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Webhook registration failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully registered webhook: {result['id']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def list_webhooks(self) -> List[Dict[str, Any]]:
        """
        List registered webhooks.
        
        Returns:
            List of webhook details
            
        Raises:
            AttestationError: If retrieval fails
        """
        try:
            logger.debug("Listing webhooks")
            response = await self._rate_limited_request(
                "GET",
                f"{self.base_url}/v1/webhooks",
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Webhook listing failed: {response.text}")
                
            result = response.json()
            logger.info(f"Found {len(result)} webhooks")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def delete_webhook(self, webhook_id: str) -> None:
        """
        Delete a registered webhook.
        
        Args:
            webhook_id: ID of the webhook to delete
            
        Raises:
            AttestationError: If deletion fails
        """
        try:
            logger.debug(f"Deleting webhook: {webhook_id}")
            response = await self._rate_limited_request(
                "DELETE",
                f"{self.base_url}/v1/webhooks/{webhook_id}",
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Webhook deletion failed: {response.text}")
                
            logger.info(f"Successfully deleted webhook: {webhook_id}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def create_batch_attestations(
        self,
        attestations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple attestations in a single batch.
        
        Args:
            attestations: List of attestation data dictionaries
            
        Returns:
            List of created attestation details
            
        Raises:
            AttestationError: If batch creation fails
        """
        try:
            payload = {
                "attestations": attestations,
                "wallet_address": str(self.wallet.public_key),
                "network": self.network,
                "timestamp": int(datetime.now().timestamp())
            }
            
            signature = await self.wallet.sign_message(json.dumps(payload, sort_keys=True))
            payload["signature"] = signature
            
            logger.debug(f"Creating batch of {len(attestations)} attestations")
            response = self._session.post(
                f"{self.base_url}/v1/attestations/batch",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Batch creation failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully created {len(result)} attestations")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def revoke_attestation(
        self,
        attestation_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Revoke an existing attestation.
        
        Args:
            attestation_id: ID of the attestation to revoke
            reason: Optional reason for revocation
            
        Returns:
            Dict containing revocation details
            
        Raises:
            AttestationError: If revocation fails
        """
        try:
            payload = {
                "wallet_address": str(self.wallet.public_key),
                "timestamp": int(datetime.now().timestamp())
            }
            
            if reason:
                payload["reason"] = reason
                
            signature = await self.wallet.sign_message(json.dumps(payload, sort_keys=True))
            payload["signature"] = signature
            
            logger.debug(f"Revoking attestation: {attestation_id}")
            response = self._session.post(
                f"{self.base_url}/v1/attestations/{attestation_id}/revoke",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Revocation failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully revoked attestation: {attestation_id}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def search_attestations(
        self,
        query: Optional[str] = None,
        attestation_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        wallet_address: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search for attestations with various filters.
        
        Args:
            query: Optional search query
            attestation_type: Optional type filter
            tags: Optional list of tags to filter by
            wallet_address: Optional wallet address filter
            status: Optional status filter (active, revoked, expired)
            page: Page number for pagination
            per_page: Number of results per page
            
        Returns:
            Dict containing search results and pagination info
            
        Raises:
            AttestationError: If search fails
        """
        try:
            params = {
                "page": page,
                "per_page": per_page
            }
            
            if query:
                params["q"] = query
            if attestation_type:
                params["type"] = attestation_type
            if tags:
                params["tags"] = ",".join(tags)
            if wallet_address:
                params["wallet_address"] = wallet_address
            if status:
                params["status"] = status
                
            logger.debug("Searching attestations with filters")
            response = self._session.get(
                f"{self.base_url}/v1/attestations/search",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Search failed: {response.text}")
                
            result = response.json()
            logger.info(f"Found {len(result['items'])} attestations")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def verify_attestation(self, attestation_id: str) -> Dict[str, Any]:
        """
        Verify an existing attestation.
        
        Args:
            attestation_id: ID of the attestation to verify
            
        Returns:
            Dict containing verification details
            
        Raises:
            AttestationError: If verification fails
        """
        try:
            logger.debug(f"Verifying attestation: {attestation_id}")
            response = self._session.get(
                f"{self.base_url}/v1/attestations/{attestation_id}/verify",
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Verification failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully verified attestation: {attestation_id}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    async def get_attestation(self, attestation_id: str) -> Dict[str, Any]:
        """
        Get details of an existing attestation.
        
        Args:
            attestation_id: ID of the attestation to retrieve
            
        Returns:
            Dict containing attestation details
            
        Raises:
            AttestationError: If retrieval fails
        """
        try:
            logger.debug(f"Retrieving attestation: {attestation_id}")
            response = self._session.get(
                f"{self.base_url}/v1/attestations/{attestation_id}",
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                raise AttestationError(f"Retrieval failed: {response.text}")
                
            result = response.json()
            logger.info(f"Successfully retrieved attestation: {attestation_id}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise AttestationError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise AttestationError(f"Unexpected error: {str(e)}")

    def close(self):
        """Close the session."""
        logger.info("Closing Attestation Service session")
        self._session.close() 