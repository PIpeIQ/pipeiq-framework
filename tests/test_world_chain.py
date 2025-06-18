import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import asyncio
import time
from pipeiq.world_chain import (
    WorldChainService,
    WorldChainError,
    WorldChainValidationError,
    WorldChainNetworkError,
    WorldChainStatus,
    TokenType,
    NodeStatus,
    TransactionType,
    RateLimitExceededError,
    BatchOperationError
)
from pipeiq.solana import SolanaWallet
import aiohttp

@pytest.fixture
def mock_wallet():
    wallet = Mock(spec=SolanaWallet)
    wallet.public_key = "test_public_key"
    wallet.sign_message = AsyncMock(return_value="test_signature")
    return wallet

@pytest.fixture
def world_chain_service(mock_wallet):
    return WorldChainService(
        mock_wallet,
        base_url="https://api.test.world.org/v1",
        rate_limit=5,  # Lower rate limit for testing
        enable_audit_logging=True,
        max_retries=2,
        retry_delay=0.1
    )

@pytest.mark.asyncio
async def test_verify_human(world_chain_service):
    """Test human verification."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "proof_123",
        "status": WorldChainStatus.COMPLETED.value,
        "verified": True
    }
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        result = await world_chain_service.verify_human(
            proof={"type": "world_id", "data": "test_proof"}
        )
        
        assert result["id"] == "proof_123"
        assert result["verified"] is True
        assert result["status"] == WorldChainStatus.COMPLETED.value

@pytest.mark.asyncio
async def test_verify_human_network_error(world_chain_service):
    """Test human verification network error."""
    with patch(
        "aiohttp.ClientSession.post",
        side_effect=aiohttp.ClientError("Network error")
    ):
        with pytest.raises(WorldChainNetworkError):
            await world_chain_service.verify_human(
                proof={"type": "world_id", "data": "test_proof"}
            )

@pytest.mark.asyncio
async def test_get_gas_status(world_chain_service):
    """Test getting gas status."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "wallet_address": "test_public_key",
        "free_gas_available": True,
        "gas_balance": "1000000"
    }
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await world_chain_service.get_gas_status()
        
        assert result["wallet_address"] == "test_public_key"
        assert result["free_gas_available"] is True
        assert result["gas_balance"] == "1000000"

@pytest.mark.asyncio
async def test_deploy_mini_app(world_chain_service):
    """Test mini app deployment."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "app_123",
        "status": WorldChainStatus.PENDING.value,
        "deployment_url": "https://test.world.org/apps/app_123"
    }
    
    app_data = {
        "name": "Test App",
        "version": "1.0.0",
        "config": {"key": "value"}
    }
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        result = await world_chain_service.deploy_mini_app(
            app_data=app_data,
            metadata={"description": "Test app"}
        )
        
        assert result["id"] == "app_123"
        assert result["status"] == WorldChainStatus.PENDING.value
        assert "deployment_url" in result

@pytest.mark.asyncio
async def test_update_mini_app(world_chain_service):
    """Test mini app update."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "app_123",
        "status": WorldChainStatus.COMPLETED.value,
        "version": "1.0.1"
    }
    
    updates = {
        "version": "1.0.1",
        "config": {"key": "updated_value"}
    }
    
    with patch("aiohttp.ClientSession.put", return_value=mock_response):
        result = await world_chain_service.update_mini_app(
            app_id="app_123",
            updates=updates,
            metadata={"reason": "Bug fix"}
        )
        
        assert result["id"] == "app_123"
        assert result["status"] == WorldChainStatus.COMPLETED.value
        assert result["version"] == "1.0.1"

@pytest.mark.asyncio
async def test_bridge_token(world_chain_service):
    """Test token bridging."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "bridge_123",
        "status": WorldChainStatus.PENDING.value,
        "token_type": TokenType.USDC.value,
        "amount": "1000",
        "destination_chain": "ethereum"
    }
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        result = await world_chain_service.bridge_token(
            token_type=TokenType.USDC,
            amount="1000",
            destination_chain="ethereum",
            metadata={"reason": "Transfer"}
        )
        
        assert result["id"] == "bridge_123"
        assert result["status"] == WorldChainStatus.PENDING.value
        assert result["token_type"] == TokenType.USDC.value
        assert result["amount"] == "1000"
        assert result["destination_chain"] == "ethereum"

@pytest.mark.asyncio
async def test_get_bridge_status(world_chain_service):
    """Test getting bridge status."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "bridge_123",
        "status": WorldChainStatus.COMPLETED.value,
        "completion_time": "2024-03-14T12:00:00Z"
    }
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await world_chain_service.get_bridge_status("bridge_123")
        
        assert result["id"] == "bridge_123"
        assert result["status"] == WorldChainStatus.COMPLETED.value
        assert "completion_time" in result

@pytest.mark.asyncio
async def test_get_node_status(world_chain_service):
    """Test getting node status."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "node_123",
        "status": NodeStatus.ACTIVE.value,
        "region": "us-west",
        "version": "1.0.0"
    }
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await world_chain_service.get_node_status("node_123")
        
        assert result["id"] == "node_123"
        assert result["status"] == NodeStatus.ACTIVE.value
        assert result["region"] == "us-west"
        assert result["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_list_nodes(world_chain_service):
    """Test listing nodes with filtering."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "node_123",
            "status": NodeStatus.ACTIVE.value,
            "region": "us-west"
        },
        {
            "id": "node_456",
            "status": NodeStatus.SYNCING.value,
            "region": "us-east"
        }
    ]
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Test listing all nodes
        all_nodes = await world_chain_service.list_nodes()
        assert len(all_nodes) == 2
        
        # Test filtering by status
        active_nodes = await world_chain_service.list_nodes(
            status=NodeStatus.ACTIVE
        )
        assert len(active_nodes) == 1
        assert active_nodes[0]["status"] == NodeStatus.ACTIVE.value
        
        # Test filtering by region
        west_nodes = await world_chain_service.list_nodes(region="us-west")
        assert len(west_nodes) == 1
        assert west_nodes[0]["region"] == "us-west"

@pytest.mark.asyncio
async def test_audit_logging(world_chain_service):
    """Test audit logging functionality."""
    # Perform some operations to generate logs
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test_id"}
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        await world_chain_service.verify_human(
            proof={"type": "world_id", "data": "test_proof"}
        )
        
        # Get audit logs
        logs = await world_chain_service.get_audit_logs()
        
        assert len(logs) > 0
        assert logs[0]["operation"] == "verify_human"
        assert logs[0]["wallet_address"] == "test_public_key"

@pytest.mark.asyncio
async def test_audit_log_filtering(world_chain_service):
    """Test audit log filtering with various criteria."""
    # Add test logs with different timestamps and operations
    now = datetime.now()
    world_chain_service._audit_logs = [
        {
            "timestamp": (now - timedelta(hours=2)).isoformat(),
            "operation": "verify_human",
            "wallet_address": "test_public_key",
            "details": {"proof_id": "test_1"}
        },
        {
            "timestamp": (now - timedelta(hours=1)).isoformat(),
            "operation": "deploy_mini_app",
            "wallet_address": "test_public_key",
            "details": {"app_id": "test_2"}
        },
        {
            "timestamp": now.isoformat(),
            "operation": "bridge_token",
            "wallet_address": "test_public_key",
            "details": {"bridge_id": "test_3"}
        }
    ]
    
    # Test filtering by time range
    logs = await world_chain_service.get_audit_logs(
        start_time=now - timedelta(hours=1)
    )
    assert len(logs) == 2
    
    # Test filtering by operation
    logs = await world_chain_service.get_audit_logs(
        operation="verify_human"
    )
    assert len(logs) == 1
    assert logs[0]["operation"] == "verify_human"
    
    # Test filtering by both time and operation
    logs = await world_chain_service.get_audit_logs(
        start_time=now - timedelta(hours=1),
        operation="bridge_token"
    )
    assert len(logs) == 1
    assert logs[0]["operation"] == "bridge_token"

@pytest.mark.asyncio
async def test_get_network_info(world_chain_service):
    """Test getting network information."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "active",
        "block_height": 12345,
        "gas_price": "1000000",
        "network_load": "low",
        "active_nodes": 100,
        "total_transactions": 1000000
    }
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        result = await world_chain_service.get_network_info()
        
        assert result["status"] == "active"
        assert result["block_height"] == 12345
        assert result["gas_price"] == "1000000"
        assert result["network_load"] == "low"
        assert result["active_nodes"] == 100
        assert result["total_transactions"] == 1000000

@pytest.mark.asyncio
async def test_context_manager(world_chain_service):
    """Test async context manager functionality."""
    async with world_chain_service as service:
        assert service._session is not None
        assert isinstance(service._session, aiohttp.ClientSession)
    
    assert service._session is None

@pytest.mark.asyncio
async def test_get_token_balance(world_chain_service):
    """Test getting token balance with caching."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "token_type": TokenType.USDC.value,
        "balance": "1000.00",
        "last_updated": datetime.now().isoformat()
    }
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # First call should hit the API
        result = await world_chain_service.get_token_balance(TokenType.USDC)
        assert result["token_type"] == TokenType.USDC.value
        assert result["balance"] == "1000.00"
        
        # Second call should use cache
        cached_result = await world_chain_service.get_cached_token_balance(TokenType.USDC)
        assert cached_result == result

@pytest.mark.asyncio
async def test_get_token_balance_network_error(world_chain_service):
    """Test token balance retrieval with network error."""
    with patch(
        "aiohttp.ClientSession.get",
        side_effect=aiohttp.ClientError("Network error")
    ):
        with pytest.raises(WorldChainNetworkError):
            await world_chain_service.get_token_balance(TokenType.USDC)

@pytest.mark.asyncio
async def test_monitor_node_health(world_chain_service):
    """Test node health monitoring."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "node_123",
        "status": NodeStatus.ACTIVE.value,
        "health_score": 0.95
    }
    
    callbacks = []
    async def mock_callback(status):
        callbacks.append(status)
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Start monitoring
        monitor_task = asyncio.create_task(
            world_chain_service.monitor_node_health(
                "node_123",
                interval=0.1,
                callback=mock_callback
            )
        )
        
        # Wait for a few callbacks
        await asyncio.sleep(0.3)
        monitor_task.cancel()
        
        # Verify callbacks were received
        assert len(callbacks) > 0
        assert all(cb["status"] == NodeStatus.ACTIVE.value for cb in callbacks)

@pytest.mark.asyncio
async def test_monitor_node_health_error(world_chain_service):
    """Test node health monitoring with errors."""
    callbacks = []
    async def mock_callback(status):
        callbacks.append(status)
    
    with patch(
        "aiohttp.ClientSession.get",
        side_effect=aiohttp.ClientError("Network error")
    ):
        # Start monitoring
        monitor_task = asyncio.create_task(
            world_chain_service.monitor_node_health(
                "node_123",
                interval=0.1,
                callback=mock_callback
            )
        )
        
        # Wait for a few callbacks
        await asyncio.sleep(0.3)
        monitor_task.cancel()
        
        # Verify error callbacks were received
        assert len(callbacks) > 0
        assert all("error" in cb for cb in callbacks)

@pytest.mark.asyncio
async def test_session_initialization_check(world_chain_service):
    """Test session initialization checks."""
    # Ensure session is None
    world_chain_service._session = None
    
    # Test that operations raise WorldChainError when session is not initialized
    with pytest.raises(WorldChainError):
        await world_chain_service.verify_human({"type": "test"})
    
    with pytest.raises(WorldChainError):
        await world_chain_service.get_gas_status()
    
    with pytest.raises(WorldChainError):
        await world_chain_service.deploy_mini_app({"name": "test"})
    
    with pytest.raises(WorldChainError):
        await world_chain_service.bridge_token(
            TokenType.USDC,
            "1000",
            "ethereum"
        )

@pytest.mark.asyncio
async def test_cached_data_access(world_chain_service):
    """Test accessing cached data."""
    # Set up test cache data
    world_chain_service._node_health_cache = {
        "node_123": {
            "id": "node_123",
            "status": NodeStatus.ACTIVE.value,
            "health_score": 0.95
        }
    }
    
    world_chain_service._token_balances_cache = {
        TokenType.USDC.value: {
            "token_type": TokenType.USDC.value,
            "balance": "1000.00"
        }
    }
    
    # Test accessing cached node health
    node_health = await world_chain_service.get_cached_node_health("node_123")
    assert node_health["status"] == NodeStatus.ACTIVE.value
    assert node_health["health_score"] == 0.95
    
    # Test accessing cached token balance
    token_balance = await world_chain_service.get_cached_token_balance(TokenType.USDC)
    assert token_balance["token_type"] == TokenType.USDC.value
    assert token_balance["balance"] == "1000.00"
    
    # Test accessing non-existent cached data
    assert await world_chain_service.get_cached_node_health("nonexistent") is None
    assert await world_chain_service.get_cached_token_balance(TokenType.ETH) is None

@pytest.mark.asyncio
async def test_rate_limiting(world_chain_service):
    """Test rate limiting functionality."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Should succeed for rate limit number of requests
        for _ in range(5):
            await world_chain_service.get_gas_status()

        # Next request should fail
        with pytest.raises(RateLimitExceededError):
            await world_chain_service.get_gas_status()

        # Wait for rate limit reset
        await asyncio.sleep(1.1)
        
        # Should succeed again after reset
        await world_chain_service.get_gas_status()

@pytest.mark.asyncio
async def test_rate_limit_status(world_chain_service):
    """Test rate limit status monitoring."""
    status = await world_chain_service.get_rate_limit_status()
    assert status["rate_limit"] == 5
    assert status["remaining_tokens"] == 5
    assert "reset_time" in status

    # Make some requests
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await world_chain_service.get_gas_status()
        await world_chain_service.get_gas_status()

        # Check updated status
        status = await world_chain_service.get_rate_limit_status()
        assert status["remaining_tokens"] == 3

@pytest.mark.asyncio
async def test_batch_bridge_tokens(world_chain_service):
    """Test batch token bridging."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "bridge_123",
        "status": WorldChainStatus.PENDING.value
    }

    operations = [
        {
            "token_type": TokenType.USDC,
            "amount": "1000",
            "destination_chain": "ethereum"
        },
        {
            "token_type": TokenType.WLD,
            "amount": "500",
            "destination_chain": "polygon"
        }
    ]

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        results = await world_chain_service.batch_bridge_tokens(operations)
        assert len(results) == 2
        assert all(r["status"] == WorldChainStatus.PENDING.value for r in results)

@pytest.mark.asyncio
async def test_batch_bridge_tokens_partial_failure(world_chain_service):
    """Test batch token bridging with partial failures."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "bridge_123",
        "status": WorldChainStatus.PENDING.value
    }

    operations = [
        {
            "token_type": TokenType.USDC,
            "amount": "1000",
            "destination_chain": "ethereum"
        },
        {
            "token_type": TokenType.WLD,
            "amount": "invalid",  # This should fail
            "destination_chain": "polygon"
        }
    ]

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        with pytest.raises(BatchOperationError) as exc_info:
            await world_chain_service.batch_bridge_tokens(operations)
        assert "completed with errors" in str(exc_info.value)

@pytest.mark.asyncio
async def test_batch_deploy_mini_apps(world_chain_service):
    """Test batch mini app deployment."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "app_123",
        "status": WorldChainStatus.PENDING.value
    }

    apps = [
        {
            "app_data": {"name": "App 1", "version": "1.0.0"},
            "metadata": {"description": "Test app 1"}
        },
        {
            "app_data": {"name": "App 2", "version": "1.0.0"},
            "metadata": {"description": "Test app 2"}
        }
    ]

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        results = await world_chain_service.batch_deploy_mini_apps(apps)
        assert len(results) == 2
        assert all(r["status"] == WorldChainStatus.PENDING.value for r in results)

@pytest.mark.asyncio
async def test_transaction_history(world_chain_service):
    """Test transaction history tracking and filtering."""
    # Perform some operations to generate transactions
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_123",
        "status": WorldChainStatus.COMPLETED.value
    }

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        # Create some transactions
        await world_chain_service.verify_human({"type": "test"})
        await world_chain_service.bridge_token(
            TokenType.USDC,
            "1000",
            "ethereum"
        )

        # Test filtering by type
        verify_txs = await world_chain_service.get_transaction_history(
            transaction_type=TransactionType.VERIFY
        )
        assert len(verify_txs) == 1
        assert verify_txs[0]["type"] == TransactionType.VERIFY.value

        bridge_txs = await world_chain_service.get_transaction_history(
            transaction_type=TransactionType.BRIDGE
        )
        assert len(bridge_txs) == 1
        assert bridge_txs[0]["type"] == TransactionType.BRIDGE.value

        # Test filtering by time
        now = datetime.now()
        recent_txs = await world_chain_service.get_transaction_history(
            start_time=now - timedelta(minutes=5)
        )
        assert len(recent_txs) == 2

        # Test limit
        limited_txs = await world_chain_service.get_transaction_history(limit=1)
        assert len(limited_txs) == 1

@pytest.mark.asyncio
async def test_retry_logic(world_chain_service):
    """Test retry logic for failed requests."""
    mock_response = Mock()
    mock_response.status_code = 429  # Too Many Requests
    mock_response.headers = {"Retry-After": "1"}

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(WorldChainError):
            await world_chain_service.get_gas_status()

@pytest.mark.asyncio
async def test_service_status(world_chain_service):
    """Test service status monitoring."""
    status = await world_chain_service.get_service_status()
    assert "rate_limit" in status
    assert "cache_sizes" in status
    assert "transaction_count" in status
    assert "audit_log_count" in status
    assert "session_active" in status

    # Perform some operations
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await world_chain_service.get_gas_status()
        
        # Check updated status
        status = await world_chain_service.get_service_status()
        assert status["rate_limit"]["remaining_tokens"] == 4

@pytest.mark.asyncio
async def test_cache_management(world_chain_service):
    """Test cache management functionality."""
    # Add some test data to caches
    world_chain_service._node_health_cache = {
        "node_123": {"status": NodeStatus.ACTIVE.value}
    }
    world_chain_service._token_balances_cache = {
        TokenType.USDC.value: {"balance": "1000"}
    }

    # Clear caches
    await world_chain_service.clear_caches()
    assert len(world_chain_service._node_health_cache) == 0
    assert len(world_chain_service._token_balances_cache) == 0

@pytest.mark.asyncio
async def test_transaction_history_management(world_chain_service):
    """Test transaction history management."""
    # Add some test transactions
    world_chain_service._transaction_history = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": TransactionType.VERIFY.value,
            "details": {"proof_id": "test_1"}
        }
    ]

    # Clear history
    await world_chain_service.clear_transaction_history()
    assert len(world_chain_service._transaction_history) == 0

@pytest.mark.asyncio
async def test_error_recovery(world_chain_service):
    """Test error recovery with retries."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(WorldChainError) as exc_info:
            await world_chain_service.get_gas_status()
        assert "API request failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_network_error_recovery(world_chain_service):
    """Test network error recovery with retries."""
    with patch(
        "aiohttp.ClientSession.get",
        side_effect=aiohttp.ClientError("Network error")
    ):
        with pytest.raises(WorldChainNetworkError) as exc_info:
            await world_chain_service.get_gas_status()
        assert "Network error after 2 retries" in str(exc_info.value)

@pytest.mark.asyncio
async def test_edge_cases_rate_limiting(world_chain_service):
    """Test edge cases in rate limiting."""
    # Test with zero rate limit
    service = WorldChainService(
        mock_wallet(),
        rate_limit=0,
        enable_audit_logging=True
    )
    with pytest.raises(RateLimitExceededError):
        await service.get_gas_status()

    # Test with negative rate limit
    service = WorldChainService(
        mock_wallet(),
        rate_limit=-1,
        enable_audit_logging=True
    )
    with pytest.raises(RateLimitExceededError):
        await service.get_gas_status()

    # Test with very high rate limit
    service = WorldChainService(
        mock_wallet(),
        rate_limit=1000000,
        enable_audit_logging=True
    )
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Should not raise RateLimitExceededError
        await service.get_gas_status()

@pytest.mark.asyncio
async def test_edge_cases_batch_operations(world_chain_service):
    """Test edge cases in batch operations."""
    # Test empty batch
    with pytest.raises(WorldChainValidationError):
        await world_chain_service.batch_bridge_tokens([])

    # Test batch with invalid token type
    operations = [{
        "token_type": "INVALID",
        "amount": "1000",
        "destination_chain": "ethereum"
    }]
    with pytest.raises(WorldChainValidationError):
        await world_chain_service.batch_bridge_tokens(operations)

    # Test batch with negative amount
    operations = [{
        "token_type": TokenType.USDC,
        "amount": "-1000",
        "destination_chain": "ethereum"
    }]
    with pytest.raises(WorldChainValidationError):
        await world_chain_service.batch_bridge_tokens(operations)

@pytest.mark.asyncio
async def test_integration_workflow(world_chain_service):
    """Test integration of multiple features in a workflow."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_123",
        "status": WorldChainStatus.COMPLETED.value
    }

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        # 1. Verify human
        verify_result = await world_chain_service.verify_human({"type": "test"})
        assert verify_result["status"] == WorldChainStatus.COMPLETED.value

        # 2. Deploy mini app
        app_result = await world_chain_service.deploy_mini_app(
            app_data={"name": "Test App"},
            metadata={"description": "Test"}
        )
        assert app_result["status"] == WorldChainStatus.COMPLETED.value

        # 3. Bridge tokens
        bridge_result = await world_chain_service.bridge_token(
            TokenType.USDC,
            "1000",
            "ethereum"
        )
        assert bridge_result["status"] == WorldChainStatus.COMPLETED.value

        # 4. Check transaction history
        history = await world_chain_service.get_transaction_history()
        assert len(history) == 3
        assert all(tx["status"] == WorldChainStatus.COMPLETED.value for tx in history)

        # 5. Check rate limit status
        rate_status = await world_chain_service.get_rate_limit_status()
        assert rate_status["remaining_tokens"] < world_chain_service.rate_limit

@pytest.mark.asyncio
async def test_performance_batch_operations(world_chain_service):
    """Test performance of batch operations."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_123",
        "status": WorldChainStatus.COMPLETED.value
    }

    # Test with large batch
    operations = [
        {
            "token_type": TokenType.USDC,
            "amount": str(i),
            "destination_chain": "ethereum"
        }
        for i in range(100)
    ]

    start_time = time.time()
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        results = await world_chain_service.batch_bridge_tokens(operations)
    end_time = time.time()

    assert len(results) == 100
    assert end_time - start_time < 5.0  # Should complete within 5 seconds

@pytest.mark.asyncio
async def test_performance_rate_limiting(world_chain_service):
    """Test performance under rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    start_time = time.time()
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Make multiple requests
        tasks = [
            world_chain_service.get_gas_status()
            for _ in range(10)
        ]
        await asyncio.gather(*tasks)
    end_time = time.time()

    assert end_time - start_time < 2.0  # Should handle rate limiting efficiently

@pytest.mark.asyncio
async def test_batch_update_mini_apps(world_chain_service):
    """Test batch updating of mini apps."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "app_123",
        "status": WorldChainStatus.COMPLETED.value,
        "version": "1.0.1"
    }

    updates = [
        {
            "app_id": f"app_{i}",
            "updates": {
                "version": "1.0.1",
                "config": {"key": f"value_{i}"}
            }
        }
        for i in range(5)
    ]

    with patch("aiohttp.ClientSession.put", return_value=mock_response):
        results = await world_chain_service.batch_update_mini_apps(updates)
        assert len(results) == 5
        assert all(r["status"] == WorldChainStatus.COMPLETED.value for r in results)

@pytest.mark.asyncio
async def test_concurrent_operations(world_chain_service):
    """Test concurrent operations with rate limiting."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    async def make_request():
        return await world_chain_service.get_gas_status()

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        # Run multiple operations concurrently
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Some requests should succeed, others should hit rate limit
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = sum(1 for r in results if isinstance(r, RateLimitExceededError))
        
        assert success_count > 0
        assert error_count > 0
        assert success_count + error_count == 10

@pytest.mark.asyncio
async def test_error_recovery_edge_cases(world_chain_service):
    """Test error recovery in edge cases."""
    # Test with invalid response format
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(WorldChainError):
            await world_chain_service.get_gas_status()

    # Test with connection timeout
    with patch(
        "aiohttp.ClientSession.get",
        side_effect=asyncio.TimeoutError("Connection timeout")
    ):
        with pytest.raises(WorldChainNetworkError):
            await world_chain_service.get_gas_status()

    # Test with server error
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(WorldChainError):
            await world_chain_service.get_gas_status()

@pytest.mark.asyncio
async def test_transaction_history_edge_cases(world_chain_service):
    """Test transaction history edge cases."""
    # Test with invalid timestamp
    world_chain_service._transaction_history = [
        {
            "timestamp": "invalid_timestamp",
            "type": TransactionType.VERIFY.value,
            "details": {"proof_id": "test_1"}
        }
    ]

    with pytest.raises(ValueError):
        await world_chain_service.get_transaction_history(
            start_time=datetime.now()
        )

    # Test with missing required fields
    world_chain_service._transaction_history = [
        {
            "timestamp": datetime.now().isoformat(),
            "details": {"proof_id": "test_1"}
        }
    ]

    with pytest.raises(KeyError):
        await world_chain_service.get_transaction_history(
            transaction_type=TransactionType.VERIFY
        )

@pytest.mark.asyncio
async def test_cache_edge_cases(world_chain_service):
    """Test cache edge cases."""
    # Test with invalid cache data
    world_chain_service._node_health_cache = {
        "node_123": None
    }
    
    with pytest.raises(TypeError):
        await world_chain_service.get_cached_node_health("node_123")

    # Test with invalid token type in cache
    world_chain_service._token_balances_cache = {
        "INVALID": {"balance": "1000"}
    }
    
    with pytest.raises(ValueError):
        await world_chain_service.get_cached_token_balance(TokenType.USDC) 