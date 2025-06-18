"""
HelloMoon API Connector

This module provides a comprehensive client for interacting with the HelloMoon API.
It supports both REST API and WebSocket connections, with features like rate limiting,
caching, and automatic retries.

Example:
    ```python
    from pipeiq.hellomoon import HelloMoonClient, HelloMoonConfig

    async def main():
        config = HelloMoonConfig(api_key="your_api_key")
        async with HelloMoonClient(config) as client:
            # Get account info
            account = await client.get_account_info("address")
            
            # Subscribe to updates
            async def handle_update(data):
                print(f"Received update: {data}")
            
            await client.subscribe_to_account("address", handle_update)

    asyncio.run(main())
    ```

Note:
    - All API calls are asynchronous and should be awaited
    - Use the context manager (`async with`) to ensure proper resource cleanup
    - Set your API key in environment variables or pass it directly in the config
"""

import os
import json
import asyncio
import time
from typing import Dict, List, Optional, Union, Any, Callable, AsyncGenerator
import aiohttp
import websockets
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from functools import wraps
import backoff
from cachetools import TTLCache

load_dotenv()

class HelloMoonConfig(BaseModel):
    """Configuration for HelloMoon API client.
    
    Attributes:
        api_key (str): Your HelloMoon API key. Can be set via environment variable HELLOMOON_API_KEY.
        base_url (str): Base URL for REST API endpoints.
        ws_url (str): WebSocket URL for real-time updates.
        timeout (int): Request timeout in seconds.
        max_retries (int): Maximum number of retry attempts for failed requests.
        rate_limit (int): Maximum requests per minute.
        cache_ttl (int): Time-to-live for cached responses in seconds.
        cache_size (int): Maximum number of items to store in cache.
    """
    api_key: str = Field(default_factory=lambda: os.getenv("HELLOMOON_API_KEY", ""))
    base_url: str = "https://api.hellomoon.io/v1"
    ws_url: str = "wss://api.hellomoon.io/v1/ws"
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100  # requests per minute
    cache_ttl: int = 300  # 5 minutes cache TTL
    cache_size: int = 1000  # Maximum number of items in cache

class HelloMoonError(Exception):
    """Base exception for HelloMoon API errors."""
    pass

class RateLimitError(HelloMoonError):
    """Raised when rate limit is exceeded."""
    pass

class AuthenticationError(HelloMoonError):
    """Raised when authentication fails."""
    pass

class HelloMoonClient:
    """Client for interacting with HelloMoon API.
    
    This client provides methods for interacting with both REST API endpoints
    and WebSocket connections. It includes features like rate limiting,
    response caching, and automatic retries.
    
    Example:
        ```python
        async with HelloMoonClient() as client:
            # Get account info
            account = await client.get_account_info("address")
            
            # Get NFT metadata
            nft = await client.get_nft_metadata("mint")
            
            # Subscribe to updates
            await client.subscribe_to_account("address", handle_update)
        ```
    
    Note:
        - Use the context manager (`async with`) to ensure proper resource cleanup
        - All methods are asynchronous and should be awaited
        - Rate limiting and caching are handled automatically
    """
    
    def __init__(self, config: Optional[HelloMoonConfig] = None):
        """Initialize the HelloMoon client.
        
        Args:
            config (Optional[HelloMoonConfig]): Configuration for the client.
                If not provided, default configuration will be used.
        """
        self.config = config or HelloMoonConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._cache = TTLCache(
            maxsize=self.config.cache_size,
            ttl=self.config.cache_ttl
        )
        self._rate_limit_tokens = self.config.rate_limit
        self._last_token_refill = time.time()
        self._rate_limit_lock = asyncio.Lock()

    async def __aenter__(self) -> 'HelloMoonClient':
        """Initialize resources when entering the context manager."""
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.config.api_key}"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting the context manager."""
        if self._session:
            await self._session.close()
        if self._ws:
            await self._ws.close()

    async def _refill_rate_limit_tokens(self):
        """Refill rate limit tokens based on time elapsed."""
        async with self._rate_limit_lock:
            now = time.time()
            time_passed = now - self._last_token_refill
            new_tokens = int(time_passed * (self.config.rate_limit / 60))
            if new_tokens > 0:
                self._rate_limit_tokens = min(
                    self.config.rate_limit,
                    self._rate_limit_tokens + new_tokens
                )
                self._last_token_refill = now

    async def _consume_rate_limit_token(self):
        """Consume a rate limit token, waiting if necessary."""
        while True:
            await self._refill_rate_limit_tokens()
            async with self._rate_limit_lock:
                if self._rate_limit_tokens > 0:
                    self._rate_limit_tokens -= 1
                    return
            await asyncio.sleep(0.1)

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, RateLimitError),
        max_tries=3
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict:
        """Make an HTTP request to the HelloMoon API with rate limiting and caching.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint path
            params (Optional[Dict]): Query parameters
            data (Optional[Dict]): Request body data
            use_cache (bool): Whether to use caching for GET requests
            
        Returns:
            Dict: API response data
            
        Raises:
            HelloMoonError: If the request fails
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        if not self._session:
            raise RuntimeError("Client session not initialized. Use async with context manager.")

        # Check cache for GET requests
        cache_key = f"{method}:{endpoint}:{str(params)}:{str(data)}"
        if use_cache and method == "GET" and cache_key in self._cache:
            return self._cache[cache_key]

        await self._consume_rate_limit_token()

        url = f"{self.config.base_url}/{endpoint}"
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=data,
                timeout=self.config.timeout
            ) as response:
                if response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status == 401:
                    raise AuthenticationError("Invalid API key")
                response.raise_for_status()
                result = await response.json()
                
                # Cache successful GET responses
                if use_cache and method == "GET":
                    self._cache[cache_key] = result
                
                return result
        except aiohttp.ClientError as e:
            raise HelloMoonError(f"API request failed: {str(e)}")

    async def batch_get_accounts(self, addresses: List[str]) -> List[Dict]:
        """Get information for multiple accounts in a single request.
        
        Args:
            addresses (List[str]): List of account addresses to fetch
            
        Returns:
            List[Dict]: List of account information dictionaries
        """
        data = {"addresses": addresses}
        return await self._make_request("POST", "batch/accounts", data=data)

    async def batch_get_transactions(self, signatures: List[str]) -> List[Dict]:
        """Get details for multiple transactions in a single request.
        
        Args:
            signatures (List[str]): List of transaction signatures to fetch
            
        Returns:
            List[Dict]: List of transaction information dictionaries
        """
        data = {"signatures": signatures}
        return await self._make_request("POST", "batch/transactions", data=data)

    async def get_nft_metadata(self, mint: str) -> Dict:
        """Get NFT metadata including collection information.
        
        Args:
            mint (str): NFT mint address
            
        Returns:
            Dict: NFT metadata including name, symbol, and collection info
        """
        return await self._make_request("GET", f"nft/{mint}/metadata")

    async def get_nft_collection(self, collection_address: str) -> Dict:
        """Get NFT collection information.
        
        Args:
            collection_address (str): Collection address
            
        Returns:
            Dict: Collection information including name, description, and stats
        """
        return await self._make_request("GET", f"nft/collection/{collection_address}")

    async def get_market_data(self, mint: str) -> Dict:
        """Get market data for a token.
        
        Args:
            mint (str): Token mint address
            
        Returns:
            Dict: Market data including price, volume, and market cap
        """
        return await self._make_request("GET", f"market/{mint}")

    async def get_token_price_history(
        self,
        mint: str,
        timeframe: str = "1d",
        limit: int = 100
    ) -> List[Dict]:
        """Get historical price data for a token.
        
        Args:
            mint (str): Token mint address
            timeframe (str): Time interval for data points (e.g., "1d", "1h")
            limit (int): Maximum number of data points to return
            
        Returns:
            List[Dict]: List of price data points with timestamps
        """
        params = {
            "timeframe": timeframe,
            "limit": limit
        }
        return await self._make_request("GET", f"market/{mint}/history", params=params)

    async def get_token_holders(
        self,
        mint: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get token holders with pagination.
        
        Args:
            mint (str): Token mint address
            limit (int): Maximum number of holders to return
            offset (int): Number of holders to skip
            
        Returns:
            List[Dict]: List of holder information including address and balance
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        return await self._make_request("GET", f"token/{mint}/holders", params=params)

    async def get_token_transfers(
        self,
        mint: str,
        limit: int = 100,
        before: Optional[str] = None
    ) -> List[Dict]:
        """Get token transfer history.
        
        Args:
            mint (str): Token mint address
            limit (int): Maximum number of transfers to return
            before (Optional[str]): Signature to start from (for pagination)
            
        Returns:
            List[Dict]: List of transfer information including sender, receiver, and amount
        """
        params = {
            "limit": limit,
            "before": before
        }
        return await self._make_request("GET", f"token/{mint}/transfers", params=params)

    async def subscribe_to_token_transfers(
        self,
        mint: str,
        callback: Callable[[Dict], None]
    ):
        """Subscribe to token transfer events via WebSocket.
        
        Args:
            mint (str): Token mint address to monitor
            callback (Callable[[Dict], None]): Async callback function to handle updates
            
        Note:
            The callback function will receive transfer data as it occurs.
            The subscription will continue until the WebSocket connection is closed.
        """
        if not self._ws:
            self._ws = await websockets.connect(
                self.config.ws_url,
                extra_headers={"Authorization": f"Bearer {self.config.api_key}"}
            )

        subscription = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tokenTransferSubscribe",
            "params": [mint]
        }
        
        await self._ws.send(json.dumps(subscription))
        
        while True:
            try:
                response = await self._ws.recv()
                data = json.loads(response)
                await callback(data)
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"Error in WebSocket subscription: {e}")
                break

    async def get_program_instructions(
        self,
        program_id: str,
        limit: int = 100,
        before: Optional[str] = None
    ) -> List[Dict]:
        """Get recent program instructions.
        
        Args:
            program_id (str): Program address
            limit (int): Maximum number of instructions to return
            before (Optional[str]): Signature to start from (for pagination)
            
        Returns:
            List[Dict]: List of instruction data including accounts and data
        """
        params = {
            "limit": limit,
            "before": before
        }
        return await self._make_request("GET", f"program/{program_id}/instructions", params=params)

    async def get_account_changes(
        self,
        address: str,
        limit: int = 100,
        before: Optional[str] = None
    ) -> List[Dict]:
        """Get account data changes history.
        
        Args:
            address (str): Account address
            limit (int): Maximum number of changes to return
            before (Optional[str]): Signature to start from (for pagination)
            
        Returns:
            List[Dict]: List of account data changes with timestamps
        """
        params = {
            "limit": limit,
            "before": before
        }
        return await self._make_request("GET", f"account/{address}/changes", params=params)

    async def get_account_info(self, address: str) -> Dict:
        """Get account information."""
        return await self._make_request("GET", f"account/{address}")

    async def get_transaction(self, signature: str) -> Dict:
        """Get transaction details."""
        return await self._make_request("GET", f"transaction/{signature}")

    async def get_token_metadata(self, mint: str) -> Dict:
        """Get token metadata."""
        return await self._make_request("GET", f"token/{mint}/metadata")

    async def subscribe_to_account(self, address: str, callback: callable):
        """Subscribe to account updates via WebSocket."""
        if not self._ws:
            self._ws = await websockets.connect(
                self.config.ws_url,
                extra_headers={"Authorization": f"Bearer {self.config.api_key}"}
            )

        subscription = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "accountSubscribe",
            "params": [address]
        }
        
        await self._ws.send(json.dumps(subscription))
        
        while True:
            try:
                response = await self._ws.recv()
                data = json.loads(response)
                await callback(data)
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"Error in WebSocket subscription: {e}")
                break

    async def get_program_accounts(
        self,
        program_id: str,
        filters: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Get program accounts with optional filters."""
        data = {
            "programId": program_id,
            "filters": filters or []
        }
        return await self._make_request("POST", "program/accounts", data=data)

    async def get_token_accounts(
        self,
        owner: str,
        program_id: str = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    ) -> List[Dict]:
        """Get token accounts for an owner."""
        return await self._make_request(
            "GET",
            f"token/accounts/{owner}",
            params={"programId": program_id}
        )

    async def get_signatures_for_address(
        self,
        address: str,
        limit: int = 100,
        before: Optional[str] = None
    ) -> List[Dict]:
        """Get signatures for an address."""
        params = {
            "limit": limit,
            "before": before
        }
        return await self._make_request(
            "GET",
            f"signatures/{address}",
            params=params
        ) 