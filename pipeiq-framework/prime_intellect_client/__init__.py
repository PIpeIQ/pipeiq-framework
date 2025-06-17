"""
Prime Intellect API Client

An async Python client for the Prime Intellect REST API.
"""

from .client import PrimeIntellectClient
from .models import (
    GPUAvailability,
    ResourceSpec,
    Pricing,
    GPUType,
    SocketType,
    SecurityType,
    StockStatus,
    Provider,
)
from .exceptions import (
    PrimeIntellectError,
    APIError,
    ValidationError,
    NetworkError,
    AuthenticationError,
    RateLimitError,
)

__version__ = "0.1.0"
__all__ = [
    "PrimeIntellectClient",
    "GPUAvailability",
    "ResourceSpec",
    "Pricing",
    "GPUType",
    "SocketType", 
    "SecurityType",
    "StockStatus",
    "Provider",
    "PrimeIntellectError",
    "APIError",
    "ValidationError", 
    "NetworkError",
    "AuthenticationError",
    "RateLimitError",
] 