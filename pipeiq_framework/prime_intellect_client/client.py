"""
Prime Intellect API Client
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import logging

from .models import GPUAvailability
from .exceptions import (
    PrimeIntellectError,
    APIError,
    ValidationError,
    NetworkError,
    AuthenticationError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class PrimeIntellectClient:
    """
    Async client for the Prime Intellect API.
    
    Example:
        async with PrimeIntellectClient("your-api-key") as client:
            offers = await client.get_availability(gpu_type="H100_80GB")
            for offer in offers:
                print(f"Provider: {offer.provider}, Price: ${offer.prices.on_demand}/hr")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.primeintellect.ai",
        timeout: float = 30.0,
    ):
        """
        Initialize the Prime Intellect client.
        
        Args:
            api_key: Prime Intellect API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "User-Agent": "prime-intellect-client/0.1.0",
            }
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers=headers,
            )

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        await self._ensure_session()
        
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        
        # Build query string if params provided
        if params:
            clean_params = {}
            for key, value in params.items():
                if value is not None:
                    if isinstance(value, list):
                        for item in value:
                            if item is not None:
                                clean_params.setdefault(key, []).append(str(item))
                    else:
                        clean_params[key] = str(value)
            
            if clean_params:
                url += "?" + urlencode(clean_params, doseq=True)

        try:
            logger.debug(f"Making {method} request to {url}")
            
            async with self._session.request(method, url) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        return await response.json()
                    except aiohttp.ContentTypeError as e:
                        raise APIError(f"Invalid JSON response: {e}")
                        
                elif response.status == 401:
                    raise AuthenticationError("Invalid API key", status_code=401)
                    
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded", status_code=429)
                    
                elif response.status == 422:
                    raise ValidationError(f"Validation error: {response_text}")
                    
                else:
                    raise APIError(
                        f"API request failed: {response.status} - {response_text}",
                        status_code=response.status,
                    )

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")
        except asyncio.TimeoutError:
            raise NetworkError("Request timeout")

    async def get_availability(
        self,
        *,
        regions: Optional[List[str]] = None,
        gpu_count: Optional[int] = None,
        gpu_type: Optional[str] = None,
        socket: Optional[str] = None,
        security: Optional[str] = None,
    ) -> List[GPUAvailability]:
        """
        Get GPU availability information.
        
        Args:
            regions: List of regions to filter by
            gpu_count: Desired number of GPUs
            gpu_type: GPU model
            socket: Socket type
            security: Security type
            
        Returns:
            List of GPUAvailability objects
            
        Raises:
            ValidationError: Invalid parameters
            AuthenticationError: Invalid API key
            APIError: API error response
            NetworkError: Network/connection error
        """
        params = {}
        if regions is not None:
            params["regions"] = regions
        if gpu_count is not None:
            params["gpu_count"] = gpu_count
        if gpu_type is not None:
            params["gpu_type"] = gpu_type
        if socket is not None:
            params["socket"] = socket
        if security is not None:
            params["security"] = security
            
        response_data = await self._make_request(
            "GET", "/api/v1/availability/", params=params
        )
        
        # Parse the response - it's a dict with GPU types as keys
        all_offers = []
        for gpu_type_key, offers in response_data.items():
            for offer_data in offers:
                all_offers.append(GPUAvailability.from_dict(offer_data))
        
        return all_offers

    async def get_cluster_availability(
        self,
        *,
        regions: Optional[List[str]] = None,
        gpu_count: Optional[int] = None,
        gpu_type: Optional[str] = None,
        socket: Optional[str] = None,
        security: Optional[str] = None,
    ) -> List[GPUAvailability]:
        """
        Get cluster availability information for multi-node deployments.
        
        Args:
            regions: List of regions to filter by
            gpu_count: Desired number of GPUs
            gpu_type: GPU model
            socket: Socket type
            security: Security type
            
        Returns:
            List of GPUAvailability objects for cluster configurations
            
        Raises:
            ValidationError: Invalid parameters
            AuthenticationError: Invalid API key
            APIError: API error response
            NetworkError: Network/connection error
        """
        params = {}
        if regions is not None:
            params["regions"] = regions
        if gpu_count is not None:
            params["gpu_count"] = gpu_count
        if gpu_type is not None:
            params["gpu_type"] = gpu_type
        if socket is not None:
            params["socket"] = socket
        if security is not None:
            params["security"] = security
            
        response_data = await self._make_request(
            "GET", "/api/v1/availability/clusters", params=params
        )
        
        # Parse the response - same format as regular availability
        all_offers = []
        for gpu_type_key, offers in response_data.items():
            for offer_data in offers:
                all_offers.append(GPUAvailability.from_dict(offer_data))
        
        return all_offers 