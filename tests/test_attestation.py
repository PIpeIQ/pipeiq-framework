import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from pipeiq.attestation import (
    AttestationService,
    AttestationError,
    AttestationValidationError,
    AttestationVersionError,
    AttestationTemplate,
    WebhookHandler,
    AttestationStatus,
    AuditLogEntry,
    AttestationVersion
)
from pipeiq.solana import SolanaWallet

@pytest.fixture
def mock_wallet():
    wallet = Mock(spec=SolanaWallet)
    wallet.public_key = "test_public_key"
    wallet.sign_message = AsyncMock(return_value="test_signature")
    return wallet

@pytest.fixture
def attestation_service(mock_wallet):
    return AttestationService(
        mock_wallet,
        rate_limit=100,
        webhook_secret="test_secret",
        enable_audit_logging=True
    )

@pytest.fixture
def attestation_template():
    return AttestationTemplate(
        name="test_template",
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        },
        required_fields=["name", "age"],
        default_metadata={"version": "1.0"},
        default_tags=["template"],
        default_expiry_days=30,
        version="1.0.0"
    )

@pytest.mark.asyncio
async def test_create_attestation_success(attestation_service):
    """Test successful attestation creation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "status": "active"
    }
    
    with patch("requests.Session.post", return_value=mock_response):
        result = await attestation_service.create_attestation(
            data={"test": "data"},
            attestation_type="test_type",
            metadata={"key": "value"},
            expires_at=datetime.now() + timedelta(days=1),
            tags=["test", "example"]
        )
        
        assert result["id"] == "test_id"
        assert result["status"] == "active"

@pytest.mark.asyncio
async def test_create_attestation_error(attestation_service):
    """Test attestation creation with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.post", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.create_attestation(
                data={"test": "data"},
                attestation_type="test_type"
            )

@pytest.mark.asyncio
async def test_create_batch_attestations_success(attestation_service):
    """Test successful batch attestation creation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "test_id_1", "status": "active"},
        {"id": "test_id_2", "status": "active"}
    ]
    
    attestations = [
        {
            "data": {"test": "data1"},
            "type": "test_type1"
        },
        {
            "data": {"test": "data2"},
            "type": "test_type2"
        }
    ]
    
    with patch("requests.Session.post", return_value=mock_response):
        result = await attestation_service.create_batch_attestations(attestations)
        
        assert len(result) == 2
        assert result[0]["id"] == "test_id_1"
        assert result[1]["id"] == "test_id_2"

@pytest.mark.asyncio
async def test_create_batch_attestations_error(attestation_service):
    """Test batch attestation creation with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.post", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.create_batch_attestations([
                {"data": {"test": "data"}, "type": "test_type"}
            ])

@pytest.mark.asyncio
async def test_revoke_attestation_success(attestation_service):
    """Test successful attestation revocation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "status": "revoked",
        "revocation_reason": "test reason"
    }
    
    with patch("requests.Session.post", return_value=mock_response):
        result = await attestation_service.revoke_attestation(
            attestation_id="test_id",
            reason="test reason"
        )
        
        assert result["id"] == "test_id"
        assert result["status"] == "revoked"
        assert result["revocation_reason"] == "test reason"

@pytest.mark.asyncio
async def test_revoke_attestation_error(attestation_service):
    """Test attestation revocation with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.post", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.revoke_attestation("test_id")

@pytest.mark.asyncio
async def test_search_attestations_success(attestation_service):
    """Test successful attestation search."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"id": "test_id_1", "type": "test_type"},
            {"id": "test_id_2", "type": "test_type"}
        ],
        "total": 2,
        "page": 1,
        "per_page": 20
    }
    
    with patch("requests.Session.get", return_value=mock_response):
        result = await attestation_service.search_attestations(
            query="test",
            attestation_type="test_type",
            tags=["test"],
            wallet_address="test_wallet",
            status="active",
            page=1,
            per_page=20
        )
        
        assert len(result["items"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1

@pytest.mark.asyncio
async def test_search_attestations_error(attestation_service):
    """Test attestation search with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.get", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.search_attestations()

@pytest.mark.asyncio
async def test_verify_attestation_success(attestation_service):
    """Test successful attestation verification."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "status": "active",
        "verified": True
    }
    
    with patch("requests.Session.get", return_value=mock_response):
        result = await attestation_service.verify_attestation("test_id")
        
        assert result["id"] == "test_id"
        assert result["status"] == "active"
        assert result["verified"] is True

@pytest.mark.asyncio
async def test_verify_attestation_error(attestation_service):
    """Test attestation verification with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.get", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.verify_attestation("test_id")

@pytest.mark.asyncio
async def test_get_attestation_success(attestation_service):
    """Test successful attestation retrieval."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "type": "test_type",
        "data": {"test": "data"},
        "status": "active"
    }
    
    with patch("requests.Session.get", return_value=mock_response):
        result = await attestation_service.get_attestation("test_id")
        
        assert result["id"] == "test_id"
        assert result["type"] == "test_type"
        assert result["data"] == {"test": "data"}
        assert result["status"] == "active"

@pytest.mark.asyncio
async def test_get_attestation_error(attestation_service):
    """Test attestation retrieval with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.get", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.get_attestation("test_id")

def test_close_session(attestation_service):
    """Test session closure."""
    with patch("requests.Session.close") as mock_close:
        attestation_service.close()
        mock_close.assert_called_once()

@pytest.mark.asyncio
async def test_create_attestation_from_template_success(
    attestation_service,
    attestation_template
):
    """Test successful attestation creation from template."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "status": "active"
    }
    
    with patch("requests.Session.post", return_value=mock_response):
        result = await attestation_service.create_attestation_from_template(
            template=attestation_template,
            data={"name": "Test User", "age": 25},
            metadata={"custom": "value"},
            tags=["custom"],
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        assert result["id"] == "test_id"
        assert result["status"] == "active"

@pytest.mark.asyncio
async def test_create_attestation_from_template_validation_failure(
    attestation_service,
    attestation_template
):
    """Test attestation creation from template with validation failure."""
    with pytest.raises(AttestationError):
        await attestation_service.create_attestation_from_template(
            template=attestation_template,
            data={"name": "Test User"}  # Missing required field 'age'
        )

@pytest.mark.asyncio
async def test_register_webhook_success(attestation_service):
    """Test successful webhook registration."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "webhook_id",
        "url": "https://example.com/webhook",
        "events": ["attestation.created"]
    }
    
    with patch("requests.Session.post", return_value=mock_response):
        result = await attestation_service.register_webhook(
            url="https://example.com/webhook",
            events=["attestation.created"],
            secret="webhook_secret"
        )
        
        assert result["id"] == "webhook_id"
        assert result["url"] == "https://example.com/webhook"
        assert result["events"] == ["attestation.created"]

@pytest.mark.asyncio
async def test_register_webhook_error(attestation_service):
    """Test webhook registration with error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    with patch("requests.Session.post", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.register_webhook(
                url="https://example.com/webhook",
                events=["attestation.created"]
            )

@pytest.mark.asyncio
async def test_list_webhooks_success(attestation_service):
    """Test successful webhook listing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "webhook_id_1",
            "url": "https://example.com/webhook1"
        },
        {
            "id": "webhook_id_2",
            "url": "https://example.com/webhook2"
        }
    ]
    
    with patch("requests.Session.get", return_value=mock_response):
        result = await attestation_service.list_webhooks()
        
        assert len(result) == 2
        assert result[0]["id"] == "webhook_id_1"
        assert result[1]["id"] == "webhook_id_2"

@pytest.mark.asyncio
async def test_delete_webhook_success(attestation_service):
    """Test successful webhook deletion."""
    mock_response = Mock()
    mock_response.status_code = 200
    
    with patch("requests.Session.delete", return_value=mock_response):
        await attestation_service.delete_webhook("webhook_id")

@pytest.mark.asyncio
async def test_delete_webhook_error(attestation_service):
    """Test webhook deletion with error."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    
    with patch("requests.Session.delete", return_value=mock_response):
        with pytest.raises(AttestationError):
            await attestation_service.delete_webhook("webhook_id")

@pytest.mark.asyncio
async def test_webhook_handler():
    """Test webhook handler functionality."""
    handler = WebhookHandler("test_secret")
    
    # Register event handlers
    event1_handler = AsyncMock()
    event2_handler = AsyncMock()
    
    handler.register_handler("event1", event1_handler)
    handler.register_handler("event2", event2_handler)
    
    # Test handling valid webhook
    payload = {
        "event_type": "event1",
        "data": {"key": "value"}
    }
    
    await handler.handle_webhook(payload, "valid_signature")
    event1_handler.assert_called_once_with(payload)
    event2_handler.assert_not_called()
    
    # Test handling unknown event
    payload["event_type"] = "unknown_event"
    await handler.handle_webhook(payload, "valid_signature")
    # Should not raise error for unknown events

@pytest.mark.asyncio
async def test_rate_limiting(attestation_service):
    """Test rate limiting functionality."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test_id"}
    
    with patch("requests.Session.get", return_value=mock_response) as mock_get:
        # Make multiple requests
        for _ in range(5):
            await attestation_service.get_attestation("test_id")
        
        # Verify rate limiting was applied
        assert mock_get.call_count == 5
        # Add assertions for rate limiting behavior if needed 

@pytest.mark.asyncio
async def test_create_attestation_with_versioning(attestation_service):
    """Test attestation creation with versioning."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "status": AttestationStatus.ACTIVE.value,
        "version": "abc123"
    }
    
    with patch("requests.Session.post", return_value=mock_response):
        result = await attestation_service.create_attestation(
            data={"test": "data"},
            attestation_type="test_type"
        )
        
        assert result["id"] == "test_id"
        assert result["version"] == "abc123"
        assert result["status"] == AttestationStatus.ACTIVE.value

@pytest.mark.asyncio
async def test_update_attestation_version(attestation_service):
    """Test attestation version update."""
    # Mock current attestation
    current_response = Mock()
    current_response.status_code = 200
    current_response.json.return_value = {
        "id": "test_id",
        "version": "abc123",
        "data": {"old": "data"}
    }
    
    # Mock update response
    update_response = Mock()
    update_response.status_code = 200
    update_response.json.return_value = {
        "id": "test_id",
        "version": "def456",
        "data": {"new": "data"}
    }
    
    with patch("requests.Session.get", return_value=current_response), \
         patch("requests.Session.put", return_value=update_response):
        result = await attestation_service.update_attestation(
            attestation_id="test_id",
            data={"new": "data"},
            reason="Update test"
        )
        
        assert result["id"] == "test_id"
        assert result["version"] == "def456"

@pytest.mark.asyncio
async def test_get_attestation_versions(attestation_service):
    """Test retrieving attestation versions."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "attestation_id": "test_id",
            "version": "abc123",
            "data": {"test": "data1"},
            "metadata": {"key": "value1"},
            "created_at": int(datetime.now().timestamp()),
            "created_by": "test_wallet",
            "changes": {"field": "value1"}
        },
        {
            "attestation_id": "test_id",
            "version": "def456",
            "data": {"test": "data2"},
            "metadata": {"key": "value2"},
            "created_at": int(datetime.now().timestamp()),
            "created_by": "test_wallet",
            "changes": {"field": "value2"}
        }
    ]
    
    with patch("requests.Session.get", return_value=mock_response):
        versions = await attestation_service.get_attestation_versions("test_id")
        
        assert len(versions) == 2
        assert versions[0].version == "abc123"
        assert versions[1].version == "def456"
        assert isinstance(versions[0], AttestationVersion)

@pytest.mark.asyncio
async def test_audit_logging(attestation_service):
    """Test audit logging functionality."""
    # Create an attestation to generate audit log
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "status": AttestationStatus.ACTIVE.value,
        "version": "abc123"
    }
    
    with patch("requests.Session.post", return_value=mock_response):
        await attestation_service.create_attestation(
            data={"test": "data"},
            attestation_type="test_type"
        )
        
        # Get audit logs
        logs = await attestation_service.get_audit_logs(
            attestation_id="test_id",
            operation="create"
        )
        
        assert len(logs) > 0
        assert isinstance(logs[0], AuditLogEntry)
        assert logs[0].operation == "create"
        assert logs[0].attestation_id == "test_id"
        assert logs[0].version == "abc123"

@pytest.mark.asyncio
async def test_audit_log_filtering(attestation_service):
    """Test audit log filtering."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "log1",
            "operation": "create",
            "attestation_id": "test_id",
            "wallet_address": "test_wallet",
            "timestamp": int(datetime.now().timestamp()),
            "details": {"type": "test"},
            "version": "abc123"
        }
    ]
    
    with patch("requests.Session.get", return_value=mock_response):
        logs = await attestation_service.get_audit_logs(
            attestation_id="test_id",
            operation="create",
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now()
        )
        
        assert len(logs) == 1
        assert logs[0].operation == "create"
        assert logs[0].attestation_id == "test_id"

@pytest.mark.asyncio
async def test_validation_error(attestation_service, attestation_template):
    """Test attestation validation error."""
    with pytest.raises(AttestationValidationError):
        await attestation_service.create_attestation_from_template(
            template=attestation_template,
            data={"name": "Test User"}  # Missing required field 'age'
        )

@pytest.mark.asyncio
async def test_version_error(attestation_service):
    """Test attestation version error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Version conflict"
    
    with patch("requests.Session.put", return_value=mock_response):
        with pytest.raises(AttestationVersionError):
            await attestation_service.update_attestation(
                attestation_id="test_id",
                data={"test": "data"}
            ) 