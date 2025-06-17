"""
Phantom wallet error classes.
"""

class PhantomError(Exception):
    """Base exception for Phantom wallet errors."""
    pass

class PhantomConnectionError(PhantomError):
    """Exception raised for connection errors."""
    pass

class TransactionError(PhantomError):
    """Exception raised for transaction errors."""
    pass

class SwapError(PhantomError):
    """Exception raised for swap errors."""
    pass

class NFTError(PhantomError):
    """Exception raised for NFT operation errors."""
    pass

class StakeError(PhantomError):
    """Exception raised for staking errors."""
    pass

class ProgramError(PhantomError):
    """Exception raised for program interaction errors."""
    pass

class FeatureError(PhantomError):
    """Exception raised for wallet feature errors."""
    pass 