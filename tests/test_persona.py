import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from pipeiq.persona import (
    PersonaService,
    InquiryStatus,
    VerificationType,
    ReportType,
    InquiryConfig,
    VerificationConfig,
    ReportConfig,
    PersonaError,
    ConnectionError,
    VerificationError,
    ReportError,
    DocumentConfig,
    DocumentType,
    CaseConfig,
    CaseStatus,
    VerificationMethodConfig,
    VerificationMethod,
    WebhookConfig,
    WebhookEventType,
    BatchOperationConfig,
    BatchOperationType,
    RateLimitConfig,
    RetryConfig,
    RetryStrategy,
    CacheConfig
)
import hmac
import hashlib
import time
import asyncio

@pytest.fixture
async def persona_service():
    """Create a Persona service instance for testing."""
    service = PersonaService(api_key="test_key", environment="sandbox")
    async with service as s:
        yield s

@pytest.mark.asyncio
async def test_create_inquiry(persona_service):
    """Test creating a new inquiry."""
    config = InquiryConfig(
        template_id="test_template",
        reference_id="test_ref",
        metadata={"user_id": "123"},
        expires_at=datetime.now() + timedelta(hours=1),
        redirect_url="https://example.com/redirect",
        webhook_url="https://example.com/webhook"
    )
    
    result = await persona_service.create_inquiry(config)
    
    assert "data" in result
    assert result["data"]["type"] == "inquiry"
    assert result["data"]["attributes"]["template_id"] == config.template_id
    assert result["data"]["attributes"]["reference_id"] == config.reference_id

@pytest.mark.asyncio
async def test_get_inquiry(persona_service):
    """Test retrieving an inquiry."""
    inquiry_id = "test_inquiry_id"
    
    result = await persona_service.get_inquiry(inquiry_id)
    
    assert "data" in result
    assert result["data"]["type"] == "inquiry"
    assert result["data"]["id"] == inquiry_id

@pytest.mark.asyncio
async def test_create_verification(persona_service):
    """Test creating a verification."""
    inquiry_id = "test_inquiry_id"
    config = VerificationConfig(
        type=VerificationType.GOVERNMENT_ID,
        country="US",
        document_type="drivers_license",
        metadata={"document_number": "123456"}
    )
    
    result = await persona_service.create_verification(inquiry_id, config)
    
    assert "data" in result
    assert result["data"]["type"] == "verification"
    assert result["data"]["attributes"]["type"] == config.type.value
    assert result["data"]["attributes"]["country"] == config.country

@pytest.mark.asyncio
async def test_get_verification(persona_service):
    """Test retrieving a verification."""
    inquiry_id = "test_inquiry_id"
    verification_id = "test_verification_id"
    
    result = await persona_service.get_verification(inquiry_id, verification_id)
    
    assert "data" in result
    assert result["data"]["type"] == "verification"
    assert result["data"]["id"] == verification_id

@pytest.mark.asyncio
async def test_create_report(persona_service):
    """Test creating a report."""
    inquiry_id = "test_inquiry_id"
    config = ReportConfig(
        type=ReportType.WATCHLIST,
        metadata={"search_type": "global"}
    )
    
    result = await persona_service.create_report(inquiry_id, config)
    
    assert "data" in result
    assert result["data"]["type"] == "report"
    assert result["data"]["attributes"]["type"] == config.type.value

@pytest.mark.asyncio
async def test_get_report(persona_service):
    """Test retrieving a report."""
    inquiry_id = "test_inquiry_id"
    report_id = "test_report_id"
    
    result = await persona_service.get_report(inquiry_id, report_id)
    
    assert "data" in result
    assert result["data"]["type"] == "report"
    assert result["data"]["id"] == report_id

@pytest.mark.asyncio
async def test_list_inquiries(persona_service):
    """Test listing inquiries with filters."""
    result = await persona_service.list_inquiries(
        page_size=5,
        page_number=1,
        status=InquiryStatus.COMPLETED
    )
    
    assert "data" in result
    assert isinstance(result["data"], list)
    assert len(result["data"]) <= 5
    assert "meta" in result
    assert "pagination" in result["meta"]

@pytest.mark.asyncio
async def test_approve_inquiry(persona_service):
    """Test approving an inquiry."""
    inquiry_id = "test_inquiry_id"
    
    result = await persona_service.approve_inquiry(inquiry_id)
    
    assert "data" in result
    assert result["data"]["type"] == "inquiry"
    assert result["data"]["attributes"]["status"] == InquiryStatus.APPROVED.value

@pytest.mark.asyncio
async def test_decline_inquiry(persona_service):
    """Test declining an inquiry."""
    inquiry_id = "test_inquiry_id"
    
    result = await persona_service.decline_inquiry(inquiry_id)
    
    assert "data" in result
    assert result["data"]["type"] == "inquiry"
    assert result["data"]["attributes"]["status"] == InquiryStatus.DECLINED.value

@pytest.mark.asyncio
async def test_mark_for_review(persona_service):
    """Test marking an inquiry for review."""
    inquiry_id = "test_inquiry_id"
    
    result = await persona_service.mark_for_review(inquiry_id)
    
    assert "data" in result
    assert result["data"]["type"] == "inquiry"
    assert result["data"]["attributes"]["status"] == InquiryStatus.REVIEW.value

@pytest.mark.asyncio
async def test_connection_error():
    """Test connection error handling."""
    service = PersonaService(api_key="test_key")
    
    with pytest.raises(ConnectionError):
        await service.create_inquiry(InquiryConfig(template_id="test"))

@pytest.mark.asyncio
async def test_verification_error(persona_service):
    """Test verification error handling."""
    inquiry_id = "test_inquiry_id"
    config = VerificationConfig(type=VerificationType.GOVERNMENT_ID)
    
    with patch.object(persona_service.session, 'post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 400
        mock_post.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="Invalid verification"
        )
        
        with pytest.raises(VerificationError):
            await persona_service.create_verification(inquiry_id, config)

@pytest.mark.asyncio
async def test_report_error(persona_service):
    """Test report error handling."""
    inquiry_id = "test_inquiry_id"
    config = ReportConfig(type=ReportType.WATCHLIST)
    
    with patch.object(persona_service.session, 'post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 400
        mock_post.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="Invalid report"
        )
        
        with pytest.raises(ReportError):
            await persona_service.create_report(inquiry_id, config)

@pytest.mark.asyncio
async def test_inquiry_config_validation():
    """Test inquiry configuration validation."""
    with pytest.raises(TypeError):
        InquiryConfig()  # Missing required template_id
    
    with pytest.raises(TypeError):
        InquiryConfig(template_id=123)  # Invalid template_id type

@pytest.mark.asyncio
async def test_verification_config_validation():
    """Test verification configuration validation."""
    with pytest.raises(TypeError):
        VerificationConfig()  # Missing required type
    
    with pytest.raises(ValueError):
        VerificationConfig(type="invalid_type")  # Invalid verification type

@pytest.mark.asyncio
async def test_report_config_validation():
    """Test report configuration validation."""
    with pytest.raises(TypeError):
        ReportConfig()  # Missing required type
    
    with pytest.raises(ValueError):
        ReportConfig(type="invalid_type")  # Invalid report type

@pytest.mark.asyncio
async def test_document_verification(persona_service):
    """Test document verification functionality."""
    # Mock response for document verification
    mock_response = {
        "data": {
            "id": "doc_123",
            "type": "document_verification",
            "attributes": {
                "status": "completed",
                "document_type": "passport",
                "country": "US",
                "metadata": {"key": "value"}
            }
        }
    }
    persona_service.session.get.return_value.__aenter__.return_value.status = 200
    persona_service.session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
    
    # Test document verification creation
    config = DocumentConfig(
        type=DocumentType.PASSPORT,
        country="US",
        metadata={"key": "value"},
        front_image="base64_front_image",
        back_image="base64_back_image"
    )
    
    result = await persona_service.create_document_verification("inq_123", config)
    assert result["data"]["id"] == "doc_123"
    assert result["data"]["attributes"]["document_type"] == "passport"
    assert result["data"]["attributes"]["country"] == "US"

@pytest.mark.asyncio
async def test_case_management(persona_service):
    """Test case management functionality."""
    # Mock response for case creation
    mock_create_response = {
        "data": {
            "id": "case_123",
            "type": "case",
            "attributes": {
                "reference_id": "ref_123",
                "status": "open",
                "metadata": {"key": "value"},
                "assignee": "user_123",
                "tags": ["tag1", "tag2"]
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 201
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_create_response)
    
    # Test case creation
    config = CaseConfig(
        reference_id="ref_123",
        status=CaseStatus.OPEN,
        metadata={"key": "value"},
        assignee="user_123",
        tags=["tag1", "tag2"]
    )
    
    result = await persona_service.create_case(config)
    assert result["data"]["id"] == "case_123"
    assert result["data"]["attributes"]["reference_id"] == "ref_123"
    assert result["data"]["attributes"]["status"] == "open"
    
    # Mock response for case update
    mock_update_response = {
        "data": {
            "id": "case_123",
            "type": "case",
            "attributes": {
                "status": "review",
                "assignee": "user_456",
                "tags": ["tag1", "tag2", "tag3"]
            }
        }
    }
    persona_service.session.patch.return_value.__aenter__.return_value.status = 200
    persona_service.session.patch.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_update_response)
    
    # Test case update
    result = await persona_service.update_case(
        "case_123",
        status=CaseStatus.REVIEW,
        assignee="user_456",
        tags=["tag1", "tag2", "tag3"]
    )
    assert result["data"]["attributes"]["status"] == "review"
    assert result["data"]["attributes"]["assignee"] == "user_456"
    assert "tag3" in result["data"]["attributes"]["tags"]

@pytest.mark.asyncio
async def test_verification_methods(persona_service):
    """Test verification methods configuration."""
    # Mock response for verification methods configuration
    mock_response = {
        "data": {
            "type": "verification_methods",
            "attributes": {
                "methods": [
                    {
                        "method": "document",
                        "enabled": True,
                        "options": {"require_back": True}
                    },
                    {
                        "method": "selfie",
                        "enabled": True,
                        "options": {"require_liveness": True}
                    }
                ]
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 200
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
    
    # Test verification methods configuration
    methods = [
        VerificationMethodConfig(
            method=VerificationMethod.DOCUMENT,
            enabled=True,
            options={"require_back": True}
        ),
        VerificationMethodConfig(
            method=VerificationMethod.SELFIE,
            enabled=True,
            options={"require_liveness": True}
        )
    ]
    
    result = await persona_service.configure_verification_methods("inq_123", methods)
    assert len(result["data"]["attributes"]["methods"]) == 2
    assert result["data"]["attributes"]["methods"][0]["method"] == "document"
    assert result["data"]["attributes"]["methods"][1]["method"] == "selfie"

@pytest.mark.asyncio
async def test_case_listing_and_filtering(persona_service):
    """Test case listing and filtering functionality."""
    # Mock response for case listing
    mock_response = {
        "data": [
            {
                "id": "case_123",
                "type": "case",
                "attributes": {
                    "reference_id": "ref_123",
                    "status": "open",
                    "assignee": "user_123",
                    "tags": ["tag1"]
                }
            },
            {
                "id": "case_456",
                "type": "case",
                "attributes": {
                    "reference_id": "ref_456",
                    "status": "review",
                    "assignee": "user_456",
                    "tags": ["tag2"]
                }
            }
        ],
        "meta": {
            "page": {
                "number": 1,
                "size": 10,
                "total": 2
            }
        }
    }
    persona_service.session.get.return_value.__aenter__.return_value.status = 200
    persona_service.session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
    
    # Test case listing with filters
    result = await persona_service.list_cases(
        page_size=10,
        page_number=1,
        status=CaseStatus.OPEN,
        assignee="user_123",
        tags=["tag1"]
    )
    assert len(result["data"]) == 2
    assert result["meta"]["page"]["total"] == 2

@pytest.mark.asyncio
async def test_case_tag_management(persona_service):
    """Test case tag management functionality."""
    # Mock response for adding tag
    mock_add_response = {
        "data": {
            "id": "case_123",
            "type": "case",
            "attributes": {
                "tags": ["tag1", "tag2", "new_tag"]
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 200
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_add_response)
    
    # Test adding tag
    result = await persona_service.add_case_tag("case_123", "new_tag")
    assert "new_tag" in result["data"]["attributes"]["tags"]
    
    # Mock response for removing tag
    mock_remove_response = {
        "data": {
            "id": "case_123",
            "type": "case",
            "attributes": {
                "tags": ["tag1", "tag2"]
            }
        }
    }
    persona_service.session.delete.return_value.__aenter__.return_value.status = 200
    persona_service.session.delete.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_remove_response)
    
    # Test removing tag
    result = await persona_service.remove_case_tag("case_123", "new_tag")
    assert "new_tag" not in result["data"]["attributes"]["tags"]

@pytest.mark.asyncio
async def test_document_verification_error_handling(persona_service):
    """Test error handling for document verification."""
    # Test connection error
    persona_service.session = None
    with pytest.raises(ConnectionError):
        await persona_service.create_document_verification(
            "inq_123",
            DocumentConfig(type=DocumentType.PASSPORT, country="US")
        )
    
    # Test API error
    persona_service.session = AsyncMock()
    persona_service.session.post.return_value.__aenter__.return_value.status = 400
    persona_service.session.post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Invalid document type")
    
    with pytest.raises(VerificationError):
        await persona_service.create_document_verification(
            "inq_123",
            DocumentConfig(type=DocumentType.PASSPORT, country="US")
        )

@pytest.mark.asyncio
async def test_case_management_error_handling(persona_service):
    """Test error handling for case management."""
    # Test connection error
    persona_service.session = None
    with pytest.raises(ConnectionError):
        await persona_service.create_case(
            CaseConfig(reference_id="ref_123")
        )
    
    # Test API error
    persona_service.session = AsyncMock()
    persona_service.session.post.return_value.__aenter__.return_value.status = 400
    persona_service.session.post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Invalid reference ID")
    
    with pytest.raises(PersonaError):
        await persona_service.create_case(
            CaseConfig(reference_id="ref_123")
        )

@pytest.mark.asyncio
async def test_verification_methods_error_handling(persona_service):
    """Test error handling for verification methods."""
    # Test connection error
    persona_service.session = None
    with pytest.raises(ConnectionError):
        await persona_service.configure_verification_methods(
            "inq_123",
            [VerificationMethodConfig(method=VerificationMethod.DOCUMENT)]
        )
    
    # Test API error
    persona_service.session = AsyncMock()
    persona_service.session.post.return_value.__aenter__.return_value.status = 400
    persona_service.session.post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Invalid method configuration")
    
    with pytest.raises(VerificationError):
        await persona_service.configure_verification_methods(
            "inq_123",
            [VerificationMethodConfig(method=VerificationMethod.DOCUMENT)]
        )

@pytest.mark.asyncio
async def test_webhook_management(persona_service):
    """Test webhook management functionality."""
    # Mock response for webhook registration
    mock_register_response = {
        "data": {
            "id": "webhook_123",
            "type": "webhook",
            "attributes": {
                "url": "https://example.com/webhook",
                "events": ["inquiry.created", "inquiry.completed"],
                "secret": "test_secret",
                "metadata": {"key": "value"}
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 201
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_register_response)
    
    # Test webhook registration
    config = WebhookConfig(
        url="https://example.com/webhook",
        events=[WebhookEventType.INQUIRY_CREATED, WebhookEventType.INQUIRY_COMPLETED],
        secret="test_secret",
        metadata={"key": "value"}
    )
    
    result = await persona_service.register_webhook(config)
    assert result["data"]["id"] == "webhook_123"
    assert result["data"]["attributes"]["url"] == "https://example.com/webhook"
    
    # Mock response for webhook listing
    mock_list_response = {
        "data": [
            {
                "id": "webhook_123",
                "type": "webhook",
                "attributes": {
                    "url": "https://example.com/webhook",
                    "events": ["inquiry.created", "inquiry.completed"]
                }
            }
        ]
    }
    persona_service.session.get.return_value.__aenter__.return_value.status = 200
    persona_service.session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_list_response)
    
    # Test webhook listing
    webhooks = await persona_service.list_webhooks()
    assert len(webhooks["data"]) == 1
    assert webhooks["data"][0]["id"] == "webhook_123"
    
    # Test webhook deletion
    persona_service.session.delete.return_value.__aenter__.return_value.status = 204
    await persona_service.delete_webhook("webhook_123")

@pytest.mark.asyncio
async def test_webhook_verification(persona_service):
    """Test webhook signature verification."""
    # Test valid signature
    payload = '{"data":{"type":"inquiry.created"}}'
    secret = "test_secret"
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    assert await persona_service.verify_webhook_signature(payload, signature, secret)
    
    # Test invalid signature
    assert not await persona_service.verify_webhook_signature(payload, "invalid_signature", secret)
    
    # Test webhook event processing
    event_payload = {
        "data": {
            "type": "inquiry.created",
            "attributes": {
                "inquiry_id": "inq_123"
            }
        }
    }
    
    result = await persona_service.process_webhook_event(
        event_payload,
        signature,
        secret
    )
    assert result["event_type"] == "inquiry.created"
    assert "processed_at" in result

@pytest.mark.asyncio
async def test_batch_operations(persona_service):
    """Test batch operations functionality."""
    # Mock response for batch operation
    mock_batch_response = {
        "data": {
            "id": "batch_123",
            "type": "batch_operation",
            "attributes": {
                "operation_type": "create_inquiries",
                "status": "processing",
                "total_items": 2,
                "processed_items": 0
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 202
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_batch_response)
    
    # Test batch inquiry creation
    inquiries = [
        InquiryConfig(reference_id="ref_1", template_id="template_1"),
        InquiryConfig(reference_id="ref_2", template_id="template_2")
    ]
    
    result = await persona_service.create_batch_inquiries(inquiries)
    assert result["data"]["id"] == "batch_123"
    assert result["data"]["attributes"]["operation_type"] == "create_inquiries"
    
    # Mock response for batch operation status
    mock_status_response = {
        "data": {
            "id": "batch_123",
            "type": "batch_operation",
            "attributes": {
                "status": "completed",
                "total_items": 2,
                "processed_items": 2,
                "results": [
                    {"id": "inq_1", "status": "success"},
                    {"id": "inq_2", "status": "success"}
                ]
            }
        }
    }
    persona_service.session.get.return_value.__aenter__.return_value.status = 200
    persona_service.session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_status_response)
    
    # Test batch operation status check
    status = await persona_service.get_batch_operation_status("batch_123")
    assert status["data"]["attributes"]["status"] == "completed"
    assert status["data"]["attributes"]["processed_items"] == 2

@pytest.mark.asyncio
async def test_batch_document_verification(persona_service):
    """Test batch document verification."""
    # Mock response for batch document verification
    mock_response = {
        "data": {
            "id": "batch_123",
            "type": "batch_operation",
            "attributes": {
                "operation_type": "verify_documents",
                "status": "processing",
                "total_items": 2
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 202
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
    
    # Test batch document verification
    documents = [
        DocumentConfig(
            type=DocumentType.PASSPORT,
            country="US",
            front_image="base64_front_1"
        ),
        DocumentConfig(
            type=DocumentType.DRIVERS_LICENSE,
            country="US",
            front_image="base64_front_2",
            back_image="base64_back_2"
        )
    ]
    
    result = await persona_service.verify_batch_documents(documents)
    assert result["data"]["id"] == "batch_123"
    assert result["data"]["attributes"]["operation_type"] == "verify_documents"

@pytest.mark.asyncio
async def test_batch_case_updates(persona_service):
    """Test batch case updates."""
    # Mock response for batch case updates
    mock_response = {
        "data": {
            "id": "batch_123",
            "type": "batch_operation",
            "attributes": {
                "operation_type": "update_cases",
                "status": "processing",
                "total_items": 2
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 202
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
    
    # Test batch case updates
    case_updates = [
        {
            "id": "case_1",
            "attributes": {
                "status": "review",
                "assignee": "user_1"
            }
        },
        {
            "id": "case_2",
            "attributes": {
                "status": "approved",
                "assignee": "user_2"
            }
        }
    ]
    
    result = await persona_service.update_batch_cases(case_updates)
    assert result["data"]["id"] == "batch_123"
    assert result["data"]["attributes"]["operation_type"] == "update_cases"

@pytest.mark.asyncio
async def test_batch_report_generation(persona_service):
    """Test batch report generation."""
    # Mock response for batch report generation
    mock_response = {
        "data": {
            "id": "batch_123",
            "type": "batch_operation",
            "attributes": {
                "operation_type": "generate_reports",
                "status": "processing",
                "total_items": 2
            }
        }
    }
    persona_service.session.post.return_value.__aenter__.return_value.status = 202
    persona_service.session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
    
    # Test batch report generation
    reports = [
        ReportConfig(
            type=ReportType.WATCHLIST,
            inquiry_id="inq_1"
        ),
        ReportConfig(
            type=ReportType.POLITICALLY_EXPOSED,
            inquiry_id="inq_2"
        )
    ]
    
    result = await persona_service.generate_batch_reports(reports)
    assert result["data"]["id"] == "batch_123"
    assert result["data"]["attributes"]["operation_type"] == "generate_reports"

@pytest.mark.asyncio
async def test_webhook_error_handling(persona_service):
    """Test webhook error handling."""
    # Test connection error
    persona_service.session = None
    with pytest.raises(ConnectionError):
        await persona_service.register_webhook(
            WebhookConfig(
                url="https://example.com/webhook",
                events=[WebhookEventType.INQUIRY_CREATED]
            )
        )
    
    # Test API error
    persona_service.session = AsyncMock()
    persona_service.session.post.return_value.__aenter__.return_value.status = 400
    persona_service.session.post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Invalid webhook URL")
    
    with pytest.raises(PersonaError):
        await persona_service.register_webhook(
            WebhookConfig(
                url="https://example.com/webhook",
                events=[WebhookEventType.INQUIRY_CREATED]
            )
        )
    
    # Test invalid webhook payload
    with pytest.raises(PersonaError):
        await persona_service.process_webhook_event({})

@pytest.mark.asyncio
async def test_batch_operation_error_handling(persona_service):
    """Test batch operation error handling."""
    # Test connection error
    persona_service.session = None
    with pytest.raises(ConnectionError):
        await persona_service.execute_batch_operation(
            BatchOperationConfig(
                type=BatchOperationType.CREATE_INQUIRIES,
                items=[]
            )
        )
    
    # Test API error
    persona_service.session = AsyncMock()
    persona_service.session.post.return_value.__aenter__.return_value.status = 400
    persona_service.session.post.return_value.__aenter__.return_value.text = AsyncMock(return_value="Invalid batch operation")
    
    with pytest.raises(PersonaError):
        await persona_service.execute_batch_operation(
            BatchOperationConfig(
                type=BatchOperationType.CREATE_INQUIRIES,
                items=[]
            )
        )

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality."""
    # Create service with custom rate limit
    rate_limit_config = RateLimitConfig(requests_per_second=2, burst_size=2)
    async with PersonaService("test_key", rate_limit_config=rate_limit_config) as persona_service:
        # Mock session responses
        persona_service.session = AsyncMock()
        persona_service.session.request.return_value.__aenter__.return_value.status = 200
        persona_service.session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"data": {"id": "test"}}
        )
        
        # Make multiple requests quickly
        start_time = time.time()
        tasks = [
            persona_service.get_inquiry("test_id")
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify rate limiting
        assert len(results) == 5
        assert end_time - start_time >= 2.0  # Should take at least 2 seconds
        
        # Verify request count
        assert persona_service.session.request.call_count == 5

@pytest.mark.asyncio
async def test_retry_mechanism():
    """Test retry mechanism functionality."""
    # Create service with custom retry config
    retry_config = RetryConfig(
        max_retries=2,
        initial_delay=0.1,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    )
    async with PersonaService("test_key", retry_config=retry_config) as persona_service:
        # Mock session to fail twice then succeed
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 500
        response.text = AsyncMock(return_value="Internal Server Error")
        
        success_response = AsyncMock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={"data": {"id": "test"}})
        
        persona_service.session.request.return_value.__aenter__.side_effect = [
            response,
            response,
            success_response
        ]
        
        # Make request
        result = await persona_service.get_inquiry("test_id")
        
        # Verify retry behavior
        assert result == {"data": {"id": "test"}}
        assert persona_service.session.request.call_count == 3

@pytest.mark.asyncio
async def test_caching():
    """Test caching functionality."""
    # Create service with custom cache config
    cache_config = CacheConfig(ttl=1, max_size=10, enabled=True)
    async with PersonaService("test_key", cache_config=cache_config) as persona_service:
        # Mock session response
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"data": {"id": "test"}})
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Make first request
        result1 = await persona_service.get_inquiry("test_id")
        
        # Make second request (should be cached)
        result2 = await persona_service.get_inquiry("test_id")
        
        # Verify caching
        assert result1 == result2
        assert persona_service.session.request.call_count == 1
        
        # Wait for cache to expire
        await asyncio.sleep(1.1)
        
        # Make third request (should not be cached)
        result3 = await persona_service.get_inquiry("test_id")
        
        # Verify cache expiration
        assert result3 == result1
        assert persona_service.session.request.call_count == 2

@pytest.mark.asyncio
async def test_cache_management():
    """Test cache management functionality."""
    async with PersonaService("test_key") as persona_service:
        # Mock session response
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"data": {"id": "test"}})
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Make some requests to populate cache
        await persona_service.get_inquiry("test_id1")
        await persona_service.get_inquiry("test_id2")
        
        # Clear cache
        await persona_service.clear_cache()
        
        # Make another request
        await persona_service.get_inquiry("test_id1")
        
        # Verify cache was cleared
        assert persona_service.session.request.call_count == 3

@pytest.mark.asyncio
async def test_rate_limit_update():
    """Test rate limit configuration update."""
    async with PersonaService("test_key") as persona_service:
        # Update rate limit
        new_config = RateLimitConfig(requests_per_second=5, burst_size=5)
        await persona_service.update_rate_limit(new_config)
        
        # Verify new configuration
        assert persona_service.rate_limiter.config.requests_per_second == 5
        assert persona_service.rate_limiter.config.burst_size == 5

@pytest.mark.asyncio
async def test_retry_config_update():
    """Test retry configuration update."""
    async with PersonaService("test_key") as persona_service:
        # Update retry config
        new_config = RetryConfig(
            max_retries=5,
            initial_delay=0.5,
            strategy=RetryStrategy.LINEAR_BACKOFF
        )
        await persona_service.update_retry_config(new_config)
        
        # Verify new configuration
        assert persona_service.retry_config.max_retries == 5
        assert persona_service.retry_config.initial_delay == 0.5
        assert persona_service.retry_config.strategy == RetryStrategy.LINEAR_BACKOFF

@pytest.mark.asyncio
async def test_cache_config_update():
    """Test cache configuration update."""
    async with PersonaService("test_key") as persona_service:
        # Update cache config
        new_config = CacheConfig(ttl=600, max_size=100, enabled=False)
        await persona_service.update_cache_config(new_config)
        
        # Verify new configuration
        assert persona_service.cache.config.ttl == 600
        assert persona_service.cache.config.max_size == 100
        assert not persona_service.cache.config.enabled
        
        # Verify cache was cleared
        assert len(persona_service.cache.cache) == 0

@pytest.mark.asyncio
async def test_rate_limit_error_handling():
    """Test rate limit error handling."""
    async with PersonaService("test_key") as persona_service:
        # Mock session to return rate limit error
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 429
        response.text = AsyncMock(return_value="Rate limit exceeded")
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Make request
        with pytest.raises(PersonaError) as exc_info:
            await persona_service.get_inquiry("test_id")
        
        assert "Rate limit exceeded" in str(exc_info.value)

@pytest.mark.asyncio
async def test_cache_overflow():
    """Test cache overflow handling."""
    # Create service with small cache
    cache_config = CacheConfig(max_size=2, ttl=10)
    async with PersonaService("test_key", cache_config=cache_config) as persona_service:
        # Mock session response
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"data": {"id": "test"}})
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Fill cache
        await persona_service.get_inquiry("test_id1")
        await persona_service.get_inquiry("test_id2")
        await persona_service.get_inquiry("test_id3")
        
        # Verify cache size
        assert len(persona_service.cache.cache) == 2
        assert persona_service.session.request.call_count == 3

@pytest.mark.asyncio
async def test_concurrent_rate_limiting():
    """Test rate limiting with concurrent requests."""
    rate_limit_config = RateLimitConfig(requests_per_second=5, burst_size=10)
    async with PersonaService("test_key", rate_limit_config=rate_limit_config) as persona_service:
        # Mock session responses
        persona_service.session = AsyncMock()
        persona_service.session.request.return_value.__aenter__.return_value.status = 200
        persona_service.session.request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"data": {"id": "test"}}
        )
        
        # Create many concurrent requests
        start_time = time.time()
        tasks = [
            persona_service.get_inquiry(f"test_id_{i}")
            for i in range(20)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify rate limiting with concurrent requests
        assert len(results) == 20
        assert end_time - start_time >= 3.0  # Should take at least 3 seconds
        assert persona_service.session.request.call_count == 20

@pytest.mark.asyncio
async def test_retry_with_different_strategies():
    """Test retry mechanism with different strategies."""
    strategies = [
        RetryStrategy.EXPONENTIAL_BACKOFF,
        RetryStrategy.LINEAR_BACKOFF,
        RetryStrategy.CONSTANT
    ]
    
    for strategy in strategies:
        retry_config = RetryConfig(
            max_retries=2,
            initial_delay=0.1,
            strategy=strategy
        )
        
        async with PersonaService("test_key", retry_config=retry_config) as persona_service:
            # Mock session to fail twice then succeed
            persona_service.session = AsyncMock()
            response = AsyncMock()
            response.status = 500
            response.text = AsyncMock(return_value="Internal Server Error")
            
            success_response = AsyncMock()
            success_response.status = 200
            success_response.json = AsyncMock(return_value={"data": {"id": "test"}})
            
            persona_service.session.request.return_value.__aenter__.side_effect = [
                response,
                response,
                success_response
            ]
            
            # Make request and measure time
            start_time = time.time()
            result = await persona_service.get_inquiry("test_id")
            end_time = time.time()
            
            # Verify retry behavior
            assert result == {"data": {"id": "test"}}
            assert persona_service.session.request.call_count == 3
            
            # Verify delay patterns
            if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                assert end_time - start_time >= 0.3  # 0.1 + 0.2
            elif strategy == RetryStrategy.LINEAR_BACKOFF:
                assert end_time - start_time >= 0.3  # 0.1 + 0.2
            else:  # CONSTANT
                assert end_time - start_time >= 0.2  # 0.1 + 0.1

@pytest.mark.asyncio
async def test_cache_with_different_ttls():
    """Test caching with different TTL values."""
    ttl_values = [1, 5, 10]
    
    for ttl in ttl_values:
        cache_config = CacheConfig(ttl=ttl, max_size=10, enabled=True)
        async with PersonaService("test_key", cache_config=cache_config) as persona_service:
            # Mock session response
            persona_service.session = AsyncMock()
            response = AsyncMock()
            response.status = 200
            response.json = AsyncMock(return_value={"data": {"id": "test"}})
            persona_service.session.request.return_value.__aenter__.return_value = response
            
            # Make first request
            result1 = await persona_service.get_inquiry("test_id")
            
            # Make second request (should be cached)
            result2 = await persona_service.get_inquiry("test_id")
            
            # Verify caching
            assert result1 == result2
            assert persona_service.session.request.call_count == 1
            
            # Wait for cache to expire
            await asyncio.sleep(ttl + 0.1)
            
            # Make third request (should not be cached)
            result3 = await persona_service.get_inquiry("test_id")
            
            # Verify cache expiration
            assert result3 == result1
            assert persona_service.session.request.call_count == 2

@pytest.mark.asyncio
async def test_cache_with_different_request_types():
    """Test caching behavior with different HTTP methods."""
    async with PersonaService("test_key") as persona_service:
        # Mock session responses
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"data": {"id": "test"}})
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Test GET request (should be cached)
        result1 = await persona_service.get_inquiry("test_id")
        result2 = await persona_service.get_inquiry("test_id")
        assert persona_service.session.request.call_count == 1
        
        # Test POST request (should not be cached)
        result3 = await persona_service.create_inquiry(InquiryConfig(
            reference_id="test_ref",
            template_id="test_template"
        ))
        result4 = await persona_service.create_inquiry(InquiryConfig(
            reference_id="test_ref",
            template_id="test_template"
        ))
        assert persona_service.session.request.call_count == 3

@pytest.mark.asyncio
async def test_rate_limit_with_different_burst_sizes():
    """Test rate limiting with different burst sizes."""
    burst_sizes = [1, 5, 10]
    
    for burst_size in burst_sizes:
        rate_limit_config = RateLimitConfig(
            requests_per_second=10,
            burst_size=burst_size
        )
        async with PersonaService("test_key", rate_limit_config=rate_limit_config) as persona_service:
            # Mock session responses
            persona_service.session = AsyncMock()
            persona_service.session.request.return_value.__aenter__.return_value.status = 200
            persona_service.session.request.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={"data": {"id": "test"}}
            )
            
            # Make burst_size + 1 requests quickly
            start_time = time.time()
            tasks = [
                persona_service.get_inquiry(f"test_id_{i}")
                for i in range(burst_size + 1)
            ]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify rate limiting
            assert len(results) == burst_size + 1
            assert end_time - start_time >= 0.1  # Should take at least 0.1 seconds
            assert persona_service.session.request.call_count == burst_size + 1

@pytest.mark.asyncio
async def test_retry_with_custom_status_codes():
    """Test retry mechanism with custom status codes."""
    retry_config = RetryConfig(
        max_retries=2,
        initial_delay=0.1,
        retry_on_status_codes=[400, 401, 403]  # Custom status codes
    )
    
    async with PersonaService("test_key", retry_config=retry_config) as persona_service:
        # Mock session to fail with custom status codes
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 400
        response.text = AsyncMock(return_value="Bad Request")
        
        success_response = AsyncMock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={"data": {"id": "test"}})
        
        persona_service.session.request.return_value.__aenter__.side_effect = [
            response,
            response,
            success_response
        ]
        
        # Make request
        result = await persona_service.get_inquiry("test_id")
        
        # Verify retry behavior
        assert result == {"data": {"id": "test"}}
        assert persona_service.session.request.call_count == 3

@pytest.mark.asyncio
async def test_cache_with_large_dataset():
    """Test caching behavior with a large dataset."""
    cache_config = CacheConfig(max_size=5, ttl=10)
    async with PersonaService("test_key", cache_config=cache_config) as persona_service:
        # Mock session responses
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"data": {"id": "test"}})
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Make more requests than cache size
        for i in range(10):
            await persona_service.get_inquiry(f"test_id_{i}")
        
        # Verify cache size limit
        assert len(persona_service.cache.cache) == 5
        assert persona_service.session.request.call_count == 10

@pytest.mark.asyncio
async def test_concurrent_cache_access():
    """Test concurrent access to cache."""
    async with PersonaService("test_key") as persona_service:
        # Mock session responses
        persona_service.session = AsyncMock()
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"data": {"id": "test"}})
        persona_service.session.request.return_value.__aenter__.return_value = response
        
        # Make concurrent requests for the same resource
        tasks = [
            persona_service.get_inquiry("test_id")
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)
        
        # Verify cache behavior
        assert all(r == results[0] for r in results)
        assert persona_service.session.request.call_count == 1

@pytest.mark.asyncio
async def test_rate_limit_with_window_size():
    """Test rate limiting with different window sizes."""
    window_sizes = [1, 2, 5]
    
    for window_size in window_sizes:
        rate_limit_config = RateLimitConfig(
            requests_per_second=10,
            burst_size=5,
            window_size=window_size
        )
        async with PersonaService("test_key", rate_limit_config=rate_limit_config) as persona_service:
            # Mock session responses
            persona_service.session = AsyncMock()
            persona_service.session.request.return_value.__aenter__.return_value.status = 200
            persona_service.session.request.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={"data": {"id": "test"}}
            )
            
            # Make requests over multiple windows
            start_time = time.time()
            for _ in range(3):
                tasks = [
                    persona_service.get_inquiry(f"test_id_{i}")
                    for i in range(5)
                ]
                await asyncio.gather(*tasks)
                await asyncio.sleep(window_size)
            end_time = time.time()
            
            # Verify rate limiting
            assert persona_service.session.request.call_count == 15
            assert end_time - start_time >= window_size * 2 