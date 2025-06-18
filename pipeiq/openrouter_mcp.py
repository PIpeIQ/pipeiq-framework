"""
OpenRouter MCP Connector

This module provides a Model Context Protocol (MCP) implementation for OpenRouter,
enabling access to various AI models through a unified interface.
"""

from typing import Any, Dict, List, Optional, Protocol, Union
from dataclasses import dataclass
import json
import asyncio
import aiohttp
from typing_extensions import TypedDict

# Model Protocol Definition
class OpenRouterModel(Protocol):
    """Protocol defining the interface for OpenRouter operations."""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]: ...
    
    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]: ...
    
    async def list_models(self) -> List[Dict[str, Any]]: ...
    
    async def get_credits(self) -> Dict[str, Any]: ...

# Configuration Classes
@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter client."""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100
    cache_ttl: int = 300
    cache_size: int = 1000

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int
    burst_size: int = 1
    window_size: int = 60

@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    retry_on_status_codes: List[int] = [429, 500, 502, 503, 504]

@dataclass
class CacheConfig:
    """Configuration for caching."""
    ttl: int = 300
    max_size: int = 1000
    enabled: bool = True

# Error Classes
class OpenRouterError(Exception):
    """Base exception for OpenRouter errors."""
    pass

class ConnectionError(OpenRouterError):
    """Raised when there's a connection error."""
    pass

class AuthenticationError(OpenRouterError):
    """Raised when there's an authentication error."""
    pass

class RateLimitError(OpenRouterError):
    """Raised when rate limit is exceeded."""
    pass

class ValidationError(OpenRouterError):
    """Raised when input validation fails."""
    pass

# Context Layer
class OpenRouterContext:
    """Manages the lifecycle of OpenRouter resources and handles low-level operations."""
    
    def __init__(self, config: OpenRouterConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = RateLimiter(
            RateLimitConfig(requests_per_minute=config.rate_limit)
        )
        self._cache = Cache(CacheConfig(
            ttl=config.cache_ttl,
            max_size=config.cache_size
        ))
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        if self.config.site_url:
            headers["HTTP-Referer"] = self.config.site_url
        if self.config.site_name:
            headers["X-Title"] = self.config.site_name
        return headers
    
    @with_retry(RetryConfig())
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an API request with rate limiting and retry logic."""
        if not self.session:
            raise ConnectionError("Session not initialized")
        
        await self._rate_limiter.acquire()
        
        try:
            async with self.session.request(
                method,
                f"{self.config.base_url}/{endpoint}",
                headers=self._get_headers(),
                json=data
            ) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status >= 500:
                    raise ConnectionError(f"Server error: {response.status}")
                
                result = await response.json()
                
                if "error" in result:
                    raise OpenRouterError(result["error"])
                
                return result
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Connection error: {str(e)}")

# Controller Layer
class OpenRouterController:
    """Implements the OpenRouter model protocol and contains business logic."""
    
    def __init__(self, context: OpenRouterContext):
        self.context = context
    
    @with_cache()
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Get a chat completion from the model."""
        data = {
            "messages": messages,
            "stream": stream
        }
        if model:
            data["model"] = model
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        
        return await self.context.make_request(
            "POST",
            "chat/completions",
            data=data
        )
    
    @with_cache()
    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Get a text completion from the model."""
        data = {
            "prompt": prompt,
            "stream": stream
        }
        if model:
            data["model"] = model
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        
        return await self.context.make_request(
            "POST",
            "completions",
            data=data
        )
    
    @with_cache(ttl=3600)  # Cache model list for 1 hour
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        result = await self.context.make_request("GET", "models")
        return result.get("data", [])
    
    async def get_credits(self) -> Dict[str, Any]:
        """Get credit information."""
        return await self.context.make_request("GET", "credits")

# Provider Layer
class OpenRouterProvider:
    """Main entry point for the OpenRouter connector."""
    
    def __init__(self, config: OpenRouterConfig):
        self.config = config
        self._context: Optional[OpenRouterContext] = None
        self._controller: Optional[OpenRouterController] = None
    
    async def __aenter__(self):
        self._context = OpenRouterContext(self.config)
        await self._context.__aenter__()
        self._controller = OpenRouterController(self._context)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._context:
            await self._context.__aexit__(exc_type, exc_val, exc_tb)
    
    def get_model(self) -> OpenRouterModel:
        """Get the model interface."""
        if not self._controller:
            raise RuntimeError("Provider not initialized. Use async with context.")
        return self._controller

# Utility Classes
class RateLimiter:
    """Implements token bucket rate limiting."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.requests_per_minute
        self.last_update = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token for making a request."""
        async with self.lock:
            now = asyncio.get_event_loop().time()
            time_passed = now - self.last_update
            self.tokens = min(
                self.config.requests_per_minute,
                self.tokens + time_passed * (self.config.requests_per_minute / 60)
            )
            
            if self.tokens < 1:
                raise RateLimitError("Rate limit exceeded")
            
            self.tokens -= 1
            self.last_update = now

class Cache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache if it exists and is not expired."""
        if not self.config.enabled:
            return None
        
        if key not in self._cache:
            return None
        
        if asyncio.get_event_loop().time() - self._timestamps[key] > self.config.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Set a value in cache."""
        if not self.config.enabled:
            return
        
        if len(self._cache) >= self.config.max_size:
            # Remove oldest entry
            oldest_key = min(self._timestamps.items(), key=lambda x: x[1])[0]
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        self._cache[key] = value
        self._timestamps[key] = asyncio.get_event_loop().time()

def with_retry(config: RetryConfig):
    """Decorator for adding retry logic to methods."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(config.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < config.max_retries - 1:
                        delay = min(
                            config.initial_delay * (2 ** attempt),
                            config.max_delay
                        )
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator

def with_cache(ttl: Optional[int] = None):
    """Decorator for adding caching to methods."""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'context') or not self.context._cache.config.enabled:
                return await func(self, *args, **kwargs)
            
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = self.context._cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = await func(self, *args, **kwargs)
            self.context._cache.set(key, result)
            return result
        return wrapper
    return decorator 