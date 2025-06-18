from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable, Protocol
from dataclasses import dataclass
import json
import aiohttp
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import time
import hashlib

class HelloMoonEndpoint(str, Enum):
    """Available HelloMoon API endpoints."""
    ACCOUNTS = "accounts"
    TRANSACTIONS = "transactions"
    NFTS = "nfts"
    MARKET_DATA = "market-data"
    TOKENS = "tokens"
    COLLECTIONS = "collections"
    SALES = "sales"
    LISTINGS = "listings"
    OFFERS = "offers"
    BIDS = "bids"

class HelloMoonError(Exception):
    """Base exception for HelloMoon API errors."""
    pass

class ConnectionError(HelloMoonError):
    """Raised when there are connection issues with the HelloMoon API."""
    pass

class AuthenticationError(HelloMoonError):
    """Raised when there are authentication issues with the HelloMoon API."""
    pass

class RateLimitError(HelloMoonError):
    """Raised when rate limits are exceeded."""
    pass

class ValidationError(HelloMoonError):
    """Raised when input validation fails."""
    pass

@dataclass
class HelloMoonConfig:
    """Configuration for the HelloMoon MCP connector."""
    api_key: str
    base_url: str = "https://api.hellomoon.io/v1"
    ws_url: str = "wss://api.hellomoon.io/v1/ws"
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100  # requests per minute
    cache_ttl: int = 300  # 5 minutes
    cache_size: int = 1000

class HelloMoonModel(Protocol):
    """Protocol defining the model interface for HelloMoon data."""
    
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information."""
        ...
    
    async def get_transaction_info(self, signature: str) -> Dict[str, Any]:
        """Get transaction information."""
        ...
    
    async def get_nft_metadata(self, mint_address: str) -> Dict[str, Any]:
        """Get NFT metadata."""
        ...
    
    async def get_market_data(self, mint_address: str) -> Dict[str, Any]:
        """Get market data for an NFT."""
        ...
    
    async def get_token_info(self, mint_address: str) -> Dict[str, Any]:
        """Get token information."""
        ...
    
    async def get_collection_info(self, collection_id: str) -> Dict[str, Any]:
        """Get collection information."""
        ...
    
    async def get_recent_sales(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get recent NFT sales."""
        ...
    
    async def get_active_listings(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get active NFT listings."""
        ...
    
    async def get_active_offers(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get active NFT offers."""
        ...
    
    async def get_active_bids(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get active NFT bids."""
        ...

class HelloMoonContext:
    """Context manager for HelloMoon API operations."""
    
    def __init__(self, config: HelloMoonConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = RateLimiter(RateLimitConfig(requests_per_minute=config.rate_limit))
        self._cache = Cache(CacheConfig(ttl=config.cache_ttl, max_size=config.cache_size))
    
    async def __aenter__(self):
        """Set up the client session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        if self._session is not None:
            await self._session.close()
            self._session = None
    
    @with_retry(RetryConfig())
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request to the HelloMoon API."""
        if self._session is None:
            raise ConnectionError("Client session not initialized")
            
        await self._rate_limiter.acquire()
        
        url = f"{self.config.base_url}/{endpoint}"
        async with self._session.request(method, url, **kwargs) as response:
            if response.status == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status >= 500:
                raise ConnectionError(f"Server error: {response.status}")
                
            response.raise_for_status()
            return await response.json()

class HelloMoonController:
    """Controller for HelloMoon API operations."""
    
    def __init__(self, context: HelloMoonContext):
        self.context = context
    
    @with_cache(Cache())
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information."""
        return await self.context._make_request(
            "GET",
            f"{HelloMoonEndpoint.ACCOUNTS}/{address}"
        )
    
    @with_cache(Cache())
    async def get_transaction_info(self, signature: str) -> Dict[str, Any]:
        """Get transaction information."""
        return await self.context._make_request(
            "GET",
            f"{HelloMoonEndpoint.TRANSACTIONS}/{signature}"
        )
    
    @with_cache(Cache())
    async def get_nft_metadata(self, mint_address: str) -> Dict[str, Any]:
        """Get NFT metadata."""
        return await self.context._make_request(
            "GET",
            f"{HelloMoonEndpoint.NFTS}/{mint_address}"
        )
    
    @with_cache(Cache())
    async def get_market_data(self, mint_address: str) -> Dict[str, Any]:
        """Get market data for an NFT."""
        return await self.context._make_request(
            "GET",
            f"{HelloMoonEndpoint.MARKET_DATA}/{mint_address}"
        )
    
    @with_cache(Cache())
    async def get_token_info(self, mint_address: str) -> Dict[str, Any]:
        """Get token information."""
        return await self.context._make_request(
            "GET",
            f"{HelloMoonEndpoint.TOKENS}/{mint_address}"
        )
    
    @with_cache(Cache())
    async def get_collection_info(self, collection_id: str) -> Dict[str, Any]:
        """Get collection information."""
        return await self.context._make_request(
            "GET",
            f"{HelloMoonEndpoint.COLLECTIONS}/{collection_id}"
        )
    
    async def get_recent_sales(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get recent NFT sales."""
        params = {"limit": limit, "offset": offset}
        if collection_id:
            params["collection_id"] = collection_id
        return await self.context._make_request(
            "GET",
            HelloMoonEndpoint.SALES,
            params=params
        )
    
    async def get_active_listings(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get active NFT listings."""
        params = {"limit": limit, "offset": offset}
        if collection_id:
            params["collection_id"] = collection_id
        return await self.context._make_request(
            "GET",
            HelloMoonEndpoint.LISTINGS,
            params=params
        )
    
    async def get_active_offers(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get active NFT offers."""
        params = {"limit": limit, "offset": offset}
        if collection_id:
            params["collection_id"] = collection_id
        return await self.context._make_request(
            "GET",
            HelloMoonEndpoint.OFFERS,
            params=params
        )
    
    async def get_active_bids(
        self,
        collection_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get active NFT bids."""
        params = {"limit": limit, "offset": offset}
        if collection_id:
            params["collection_id"] = collection_id
        return await self.context._make_request(
            "GET",
            HelloMoonEndpoint.BIDS,
            params=params
        )

class HelloMoonProvider:
    """Provider for HelloMoon API operations."""
    
    def __init__(self, config: HelloMoonConfig):
        self.config = config
        self.context = HelloMoonContext(config)
        self.controller = HelloMoonController(self.context)
    
    async def __aenter__(self):
        """Set up the provider."""
        await self.context.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        await self.context.__aexit__(exc_type, exc_val, exc_tb)
    
    def get_model(self) -> HelloMoonModel:
        """Get the HelloMoon model interface."""
        return self.controller

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int
    burst_size: int = 1
    window_size: int = 60  # in seconds

@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""
    max_retries: int = 3
    initial_delay: float = 1.0  # in seconds
    max_delay: float = 30.0  # in seconds
    retry_on_status_codes: List[int] = [429, 500, 502, 503, 504]

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
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if not self.config.enabled:
            return None
            
        if key not in self.cache:
            return None
            
        if time.time() - self.timestamps[key] > self.config.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
            
        return self.cache[key]
    
    async def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        if not self.config.enabled:
            return
            
        if len(self.cache) >= self.config.max_size:
            # Remove oldest entry
            oldest_key = min(self.timestamps.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            
        self.cache[key] = value
        self.timestamps[key] = time.time()

def with_retry(config: RetryConfig):
    """Decorator for retrying failed requests."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if not isinstance(e, HelloMoonError) or getattr(e, 'status_code', None) not in config.retry_on_status_codes:
                        raise
                    
                    if attempt < config.max_retries - 1:
                        await asyncio.sleep(min(delay, config.max_delay))
                        delay *= 2
            
            raise last_exception
        return wrapper
    return decorator

def with_cache(cache: Cache):
    """Decorator for caching function results."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache.config.enabled:
                return await func(*args, **kwargs)
                
            key = cache._generate_key(*args, **kwargs)
            result = await cache.get(key)
            
            if result is not None:
                return result
                
            result = await func(*args, **kwargs)
            await cache.set(key, result)
            return result
        return wrapper
    return decorator 