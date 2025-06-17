"""
Custom exceptions for the Prime Intellect client library.
"""

from typing import Optional


class PrimeIntellectError(Exception):
    """Base exception for all Prime Intellect client errors."""
    pass


class APIError(PrimeIntellectError):
    """Exception raised for API errors (non-2xx responses)."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(PrimeIntellectError):
    """Exception raised for invalid input parameters."""
    pass


class NetworkError(PrimeIntellectError):
    """Exception raised for network-related errors."""
    pass


class AuthenticationError(APIError):
    """Exception raised for authentication errors (401)."""
    pass


class RateLimitError(APIError):
    """Exception raised for rate limit errors (429)."""
    pass 