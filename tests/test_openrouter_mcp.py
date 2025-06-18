"""
Test cases for the OpenRouter MCP connector.
"""

import pytest
import os
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from pipeiq.openrouter_mcp import (
    OpenRouterProvider,
    OpenRouterConfig,
    OpenRouterError,
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    ValidationError
)

# Test Fixtures
@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return OpenRouterConfig(
        api_key="test_api_key",
        site_url="https://test.com",
        site_name="Test Site"
    )

@pytest.fixture
def mock_response():
    """Create a mock API response."""
    return {
        "id": "test_id",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Test response"
                }
            }
        ]
    }

@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value=mock_response())
    session.request.return_value.__aenter__.return_value = response
    return session

# Test Provider
class TestOpenRouterProvider:
    """Test cases for OpenRouterProvider."""
    
    @pytest.mark.asyncio
    async def test_init(self, mock_config):
        """Test provider initialization."""
        provider = OpenRouterProvider(mock_config)
        assert provider.config == mock_config
        assert provider._context is None
        assert provider._controller is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config, mock_session):
        """Test context manager behavior."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                assert provider._context is not None
                assert provider._controller is not None
                model = provider.get_model()
                assert model is not None
    
    @pytest.mark.asyncio
    async def test_get_model_without_context(self, mock_config):
        """Test getting model without context."""
        provider = OpenRouterProvider(mock_config)
        with pytest.raises(RuntimeError):
            provider.get_model()

# Test Controller
class TestOpenRouterController:
    """Test cases for OpenRouterController."""
    
    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_config, mock_session):
        """Test chat completion."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                model = provider.get_model()
                result = await model.chat_completion(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="gpt-4",
                    temperature=0.7
                )
                assert result == mock_response()
    
    @pytest.mark.asyncio
    async def test_text_completion(self, mock_config, mock_session):
        """Test text completion."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                model = provider.get_model()
                result = await model.text_completion(
                    prompt="Hello",
                    model="gpt-4",
                    temperature=0.7
                )
                assert result == mock_response()
    
    @pytest.mark.asyncio
    async def test_list_models(self, mock_config, mock_session):
        """Test listing models."""
        mock_session.request.return_value.__aenter__.return_value.json.return_value = {
            "data": [
                {"id": "gpt-4", "name": "GPT-4"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
            ]
        }
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                model = provider.get_model()
                result = await model.list_models()
                assert len(result) == 2
                assert result[0]["id"] == "gpt-4"
    
    @pytest.mark.asyncio
    async def test_get_credits(self, mock_config, mock_session):
        """Test getting credits."""
        mock_session.request.return_value.__aenter__.return_value.json.return_value = {
            "credits": 100,
            "used": 50
        }
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                model = provider.get_model()
                result = await model.get_credits()
                assert result["credits"] == 100
                assert result["used"] == 50

# Test Context
class TestOpenRouterContext:
    """Test cases for OpenRouterContext."""
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_config, mock_session):
        """Test successful request."""
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                result = await provider._context.make_request(
                    "POST",
                    "chat/completions",
                    data={"messages": [{"role": "user", "content": "Hello"}]}
                )
                assert result == mock_response()
    
    @pytest.mark.asyncio
    async def test_make_request_authentication_error(self, mock_config, mock_session):
        """Test authentication error."""
        mock_session.request.return_value.__aenter__.return_value.status = 401
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                with pytest.raises(AuthenticationError):
                    await provider._context.make_request("GET", "models")
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, mock_config, mock_session):
        """Test rate limit error."""
        mock_session.request.return_value.__aenter__.return_value.status = 429
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                with pytest.raises(RateLimitError):
                    await provider._context.make_request("GET", "models")
    
    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, mock_config, mock_session):
        """Test connection error."""
        mock_session.request.side_effect = Exception("Connection error")
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with OpenRouterProvider(mock_config) as provider:
                with pytest.raises(ConnectionError):
                    await provider._context.make_request("GET", "models")

# Test Rate Limiter
class TestRateLimiter:
    """Test cases for RateLimiter."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter(self, mock_config):
        """Test rate limiter behavior."""
        from pipeiq.openrouter_mcp import RateLimiter, RateLimitConfig
        
        config = RateLimitConfig(requests_per_minute=2)
        limiter = RateLimiter(config)
        
        # Should allow first request
        await limiter.acquire()
        
        # Should allow second request
        await limiter.acquire()
        
        # Should raise rate limit error
        with pytest.raises(RateLimitError):
            await limiter.acquire()

# Test Cache
class TestCache:
    """Test cases for Cache."""
    
    def test_cache_get_set(self, mock_config):
        """Test cache get and set operations."""
        from pipeiq.openrouter_mcp import Cache, CacheConfig
        
        config = CacheConfig(ttl=300, max_size=1000)
        cache = Cache(config)
        
        # Test setting and getting value
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        # Test getting non-existent value
        assert cache.get("non_existent") is None
    
    def test_cache_ttl(self, mock_config):
        """Test cache TTL behavior."""
        from pipeiq.openrouter_mcp import Cache, CacheConfig
        
        config = CacheConfig(ttl=1, max_size=1000)
        cache = Cache(config)
        
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        # Wait for TTL to expire
        asyncio.get_event_loop().time = lambda: 2.0
        assert cache.get("test_key") is None
    
    def test_cache_size_limit(self, mock_config):
        """Test cache size limit behavior."""
        from pipeiq.openrouter_mcp import Cache, CacheConfig
        
        config = CacheConfig(ttl=300, max_size=2)
        cache = Cache(config)
        
        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Add one more item, should remove oldest
        cache.set("key3", "value3")
        
        assert cache.get("key1") is None  # Oldest item should be removed
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3" 