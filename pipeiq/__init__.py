"""
PipeIQ - A Solana-compatible SDK for connecting to different models and MCP servers
"""

from .client import PipeIQClient
from .models import ModelConfig, MCPConfig
from .solana import SolanaWallet
from .attestation import AttestationService, AttestationError

__version__ = "0.1.0"
__all__ = [
    "PipeIQClient",
    "ModelConfig",
    "MCPConfig",
    "SolanaWallet",
    "AttestationService",
    "AttestationError"
] 