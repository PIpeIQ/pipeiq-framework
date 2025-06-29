import pytest
import os
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from pipeiq.hellomoon_mcp import (
    HelloMoonProvider,
    HelloMoonConfig,
    HelloMoonEndpoint,
    HelloMoonError,
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    RateLimitConfig,
    RetryConfig,
    CacheConfig,
    HelloMoonModel
)

@pytest.fixture
def mock_config():
    return HelloMoonConfig(
        api_key="test_api_key",
        base_url="https://api.hellomoon.io/v1",
        ws_url="wss://api.hellomoon.io/v1/ws",
        timeout=30,
        max_retries=3,
        rate_limit=100,
        cache_ttl=300,
        cache_size=1000
    )

@pytest.fixture
def mock_response():
    return {
        "data": {
            "id": "test_id",
            "name": "Test NFT",
            "description": "Test Description",
            "image": "https://example.com/image.png",
            "attributes": [
                {"trait_type": "Rarity", "value": "Legendary"},
                {"trait_type": "Level", "value": 99}
            ]
        }
    }

@pytest.fixture
def mock_session():
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"data": {"id": "test_id"}})
    session.request.return_value.__aenter__.return_value = response
    return session

class TestHelloMoonProvider:
    """Test cases for HelloMoonProvider class."""
    
    @pytest.mark.asyncio
    async def test_init(self, mock_config):
        """Test initialization of HelloMoonProvider."""
        provider = HelloMoonProvider(mock_config)
        assert provider.config == mock_config
        assert provider.context.config == mock_config
        assert provider.controller.context == provider.context
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config, mock_session):
        """Test context manager behavior."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                assert provider.context._session is not None
                assert provider.context._session.headers["Authorization"] == f"Bearer {mock_config.api_key}"
            
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_model(self, mock_config):
        """Test get_model method."""
        provider = HelloMoonProvider(mock_config)
        model = provider.get_model()
        assert isinstance(model, HelloMoonModel)

class TestHelloMoonController:
    """Test cases for HelloMoonController class."""
    
    @pytest.mark.asyncio
    async def test_get_account_info(self, mock_config, mock_session):
        """Test get_account_info method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_account_info("test_address")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.ACCOUNTS}/test_address",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout
                )
    
    @pytest.mark.asyncio
    async def test_get_transaction_info(self, mock_config, mock_session):
        """Test get_transaction_info method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_transaction_info("test_signature")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.TRANSACTIONS}/test_signature",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout
                )
    
    @pytest.mark.asyncio
    async def test_get_nft_metadata(self, mock_config, mock_session):
        """Test get_nft_metadata method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_nft_metadata("test_mint_address")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.NFTS}/test_mint_address",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout
                )
    
    @pytest.mark.asyncio
    async def test_get_market_data(self, mock_config, mock_session):
        """Test get_market_data method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_market_data("test_mint_address")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.MARKET_DATA}/test_mint_address",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout
                )
    
    @pytest.mark.asyncio
    async def test_get_token_info(self, mock_config, mock_session):
        """Test get_token_info method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_token_info("test_mint_address")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.TOKENS}/test_mint_address",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout
                )
    
    @pytest.mark.asyncio
    async def test_get_collection_info(self, mock_config, mock_session):
        """Test get_collection_info method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_collection_info("test_collection_id")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.COLLECTIONS}/test_collection_id",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout
                )
    
    @pytest.mark.asyncio
    async def test_get_recent_sales(self, mock_config, mock_session):
        """Test get_recent_sales method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_recent_sales(
                    collection_id="test_collection_id",
                    limit=50,
                    offset=0
                )
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.SALES}",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout,
                    params={"collection_id": "test_collection_id", "limit": 50, "offset": 0}
                )
    
    @pytest.mark.asyncio
    async def test_get_active_listings(self, mock_config, mock_session):
        """Test get_active_listings method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_active_listings(
                    collection_id="test_collection_id",
                    limit=50,
                    offset=0
                )
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.LISTINGS}",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout,
                    params={"collection_id": "test_collection_id", "limit": 50, "offset": 0}
                )
    
    @pytest.mark.asyncio
    async def test_get_active_offers(self, mock_config, mock_session):
        """Test get_active_offers method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_active_offers(
                    collection_id="test_collection_id",
                    limit=50,
                    offset=0
                )
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.OFFERS}",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout,
                    params={"collection_id": "test_collection_id", "limit": 50, "offset": 0}
                )
    
    @pytest.mark.asyncio
    async def test_get_active_bids(self, mock_config, mock_session):
        """Test get_active_bids method."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.controller.get_active_bids(
                    collection_id="test_collection_id",
                    limit=50,
                    offset=0
                )
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once_with(
                    "GET",
                    f"{mock_config.base_url}/{HelloMoonEndpoint.BIDS}",
                    headers={"Authorization": f"Bearer {mock_config.api_key}"},
                    timeout=mock_config.timeout,
                    params={"collection_id": "test_collection_id", "limit": 50, "offset": 0}
                )

class TestHelloMoonContext:
    """Test cases for HelloMoonContext class."""
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_config, mock_session):
        """Test successful request."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                response = await provider.context._make_request("GET", "test_endpoint")
                assert response == {"data": {"id": "test_id"}}
                mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_authentication_error(self, mock_config, mock_session):
        """Test authentication error."""
        mock_session.request.return_value.__aenter__.return_value.status = 401
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                with pytest.raises(AuthenticationError):
                    await provider.context._make_request("GET", "test_endpoint")
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, mock_config, mock_session):
        """Test rate limit error."""
        mock_session.request.return_value.__aenter__.return_value.status = 429
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                with pytest.raises(RateLimitError):
                    await provider.context._make_request("GET", "test_endpoint")
    
    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, mock_config, mock_session):
        """Test connection error."""
        mock_session.request.return_value.__aenter__.return_value.status = 500
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with HelloMoonProvider(mock_config) as provider:
                with pytest.raises(ConnectionError):
                    await provider.context._make_request("GET", "test_endpoint") 