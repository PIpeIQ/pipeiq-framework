import pytest
import os
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pipeiq.hellomoon import (
    HelloMoonClient,
    HelloMoonConfig,
    RateLimitError,
    AuthenticationError,
    HelloMoonError
)

@pytest.fixture
def mock_config():
    return HelloMoonConfig(api_key="test_api_key")

@pytest.fixture
async def client(mock_config):
    async with HelloMoonClient(mock_config) as client:
        yield client

@pytest.fixture
def mock_response():
    return {"data": {"test": "data"}}

@pytest.fixture
def mock_error_response():
    return {"error": {"message": "Test error"}}

class TestHelloMoonConfig:
    def test_default_config(self):
        config = HelloMoonConfig()
        assert config.api_key == ""
        assert config.base_url == "https://api.hellomoon.io/v1"
        assert config.ws_url == "wss://api.hellomoon.io/v1/ws"
        assert config.timeout == 30
        assert config.rate_limit == 100
        assert config.cache_ttl == 300
        assert config.cache_size == 1000

    def test_custom_config(self):
        config = HelloMoonConfig(
            api_key="custom_key",
            timeout=60,
            rate_limit=200,
            cache_ttl=600,
            cache_size=2000
        )
        assert config.api_key == "custom_key"
        assert config.timeout == 60
        assert config.rate_limit == 200
        assert config.cache_ttl == 600
        assert config.cache_size == 2000

    def test_env_var_config(self):
        os.environ["HELLOMOON_API_KEY"] = "env_key"
        config = HelloMoonConfig()
        assert config.api_key == "env_key"
        del os.environ["HELLOMOON_API_KEY"]

class TestHelloMoonClient:
    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with HelloMoonClient() as client:
            assert client._session is not None
            assert isinstance(client._session, aiohttp.ClientSession)
        assert client._session.closed

    @pytest.mark.asyncio
    async def test_make_request_success(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client._make_request("GET", "test/endpoint")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_make_request_rate_limit(self, client):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.status = 429
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            with pytest.raises(RateLimitError):
                await client._make_request("GET", "test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_auth_error(self, client):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.status = 401
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            with pytest.raises(AuthenticationError):
                await client._make_request("GET", "test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.side_effect = aiohttp.ClientError()
            
            with pytest.raises(HelloMoonError):
                await client._make_request("GET", "test/endpoint")

    @pytest.mark.asyncio
    async def test_caching(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            # First call should hit the API
            result1 = await client._make_request("GET", "test/endpoint")
            assert result1 == mock_response
            
            # Second call should use cache
            result2 = await client._make_request("GET", "test/endpoint")
            assert result2 == mock_response
            
            # Verify only one API call was made
            assert mock_request.call_count == 1

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        client.config.rate_limit = 2  # Set low rate limit for testing
        
        async def make_requests():
            tasks = []
            for _ in range(3):  # Try to make 3 requests
                tasks.append(client._make_request("GET", "test/endpoint"))
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = {"data": "test"}
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            results = await make_requests()
            assert any(isinstance(r, RateLimitError) for r in results)

    @pytest.mark.asyncio
    async def test_batch_get_accounts(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client.batch_get_accounts(["addr1", "addr2"])
            assert result == mock_response
            assert mock_request.call_args[1]["json"] == {"addresses": ["addr1", "addr2"]}

    @pytest.mark.asyncio
    async def test_get_nft_metadata(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client.get_nft_metadata("test_mint")
            assert result == mock_response
            assert mock_request.call_args[0][1] == "nft/test_mint/metadata"

    @pytest.mark.asyncio
    async def test_get_market_data(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client.get_market_data("test_mint")
            assert result == mock_response
            assert mock_request.call_args[0][1] == "market/test_mint"

    @pytest.mark.asyncio
    async def test_get_token_price_history(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client.get_token_price_history("test_mint", timeframe="1d", limit=50)
            assert result == mock_response
            assert mock_request.call_args[1]["params"] == {"timeframe": "1d", "limit": 50}

    @pytest.mark.asyncio
    async def test_get_token_holders_pagination(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client.get_token_holders("test_mint", limit=10, offset=20)
            assert result == mock_response
            assert mock_request.call_args[1]["params"] == {"limit": 10, "offset": 20}

    @pytest.mark.asyncio
    async def test_websocket_subscription(self, client):
        mock_websocket = AsyncMock()
        mock_websocket.recv.return_value = '{"jsonrpc": "2.0", "result": "test_data"}'
        
        with patch("websockets.connect", return_value=mock_websocket):
            callback_called = False
            
            async def test_callback(data):
                nonlocal callback_called
                callback_called = True
                assert data == {"jsonrpc": "2.0", "result": "test_data"}
            
            # Start subscription
            subscription_task = asyncio.create_task(
                client.subscribe_to_token_transfers("test_mint", test_callback)
            )
            
            # Let it run for a short time
            await asyncio.sleep(0.1)
            
            # Cancel the subscription
            subscription_task.cancel()
            try:
                await subscription_task
            except asyncio.CancelledError:
                pass
            
            assert callback_called
            assert mock_websocket.send.call_count == 1
            assert json.loads(mock_websocket.send.call_args[0][0]) == {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tokenTransferSubscribe",
                "params": ["test_mint"]
            }

    @pytest.mark.asyncio
    async def test_websocket_connection_error(self, client):
        with patch("websockets.connect", side_effect=websockets.exceptions.ConnectionError):
            with pytest.raises(websockets.exceptions.ConnectionError):
                await client.subscribe_to_token_transfers("test_mint", lambda x: None)

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, client, mock_response):
        with patch("aiohttp.ClientSession.request") as mock_request:
            # Simulate two failures followed by success
            mock_request.side_effect = [
                aiohttp.ClientError(),
                aiohttp.ClientError(),
                AsyncMock().__aenter__.return_value
            ]
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client._make_request("GET", "test/endpoint")
            assert result == mock_response
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, client):
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = {"invalid": "format"}
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            result = await client._make_request("GET", "test/endpoint")
            assert result == {"invalid": "format"}

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, mock_response):
        async def make_request():
            return await client._make_request("GET", "test/endpoint")
        
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.json.return_value = mock_response
            mock_request.return_value.__aenter__.return_value.raise_for_status = Mock()
            
            # Make multiple concurrent requests
            tasks = [make_request() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            assert all(r == mock_response for r in results)
            assert mock_request.call_count == 5  # Each request should hit the API due to rate limiting 