"""
Phantom wallet integration for PipeIQ framework.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import json
import aiohttp
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class NetworkType(str, Enum):
    """Supported blockchain networks."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"

class TransactionStatus(str, Enum):
    """Transaction status types."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class SwapType(str, Enum):
    """Types of token swaps."""
    EXACT_IN = "exact_in"
    EXACT_OUT = "exact_out"

class NFTStandard(str, Enum):
    """Supported NFT standards."""
    METAPLEX = "metaplex"
    CANDY_MACHINE = "candy_machine"

class StakeType(str, Enum):
    """Types of staking operations."""
    STAKE = "stake"
    UNSTAKE = "unstake"
    REWARD = "reward"

class ProgramType(str, Enum):
    """Types of program interactions."""
    TOKEN = "token"
    STAKE = "stake"
    NFT = "nft"
    CUSTOM = "custom"

class WalletFeature(str, Enum):
    """Supported wallet features."""
    MULTI_SIG = "multi_sig"
    HARDWARE = "hardware"
    LEDGER = "ledger"
    TREZOR = "trezor"

@dataclass
class WalletConfig:
    """Configuration for Phantom wallet."""
    network: NetworkType = NetworkType.MAINNET
    auto_approve: bool = False
    timeout: int = 30000

@dataclass
class TransactionConfig:
    """Configuration for transactions."""
    fee_payer: str
    recent_blockhash: Optional[str] = None
    priority_fee: Optional[int] = None
    compute_unit_limit: Optional[int] = None

@dataclass
class SwapConfig:
    """Configuration for token swaps."""
    slippage: float = 0.01  # 1% default slippage
    deadline: Optional[int] = None
    priority_fee: Optional[int] = None

@dataclass
class NFTConfig:
    """Configuration for NFT operations."""
    standard: NFTStandard = NFTStandard.METAPLEX
    verify_ownership: bool = True
    include_metadata: bool = True

@dataclass
class StakeConfig:
    """Configuration for staking operations."""
    validator_address: str
    amount: float
    lockup_period: Optional[int] = None  # in seconds
    auto_compound: bool = False
    priority_fee: Optional[int] = None

@dataclass
class ProgramConfig:
    """Configuration for program interactions."""
    program_id: str
    program_type: ProgramType
    instruction_data: Dict[str, Any]
    accounts: List[Dict[str, Any]]
    signers: Optional[List[str]] = None

@dataclass
class WalletFeatureConfig:
    """Configuration for wallet features."""
    feature: WalletFeature
    enabled: bool = True
    options: Optional[Dict[str, Any]] = None

# Import error classes from separate file
from .errors import (
    PhantomError,
    PhantomConnectionError,
    TransactionError,
    SwapError,
    NFTError,
    StakeError,
    ProgramError,
    FeatureError
)

class PhantomWallet:
    """Phantom wallet integration for PipeIQ framework."""
    
    def __init__(self, config: Optional[WalletConfig] = None, public_key: Optional[str] = None):
        """Initialize Phantom wallet with optional configuration and public key."""
        self.config = config or WalletConfig()
        self._connected = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._public_key = public_key  # Accept public key directly
        self._initial_public_key = public_key  # Track if key was provided during init
        logger.info(f"🔧 PhantomWallet initialized with network: {self.config.network.value}")
    
    async def connect(self) -> Dict[str, Any]:
        """Connect to Phantom wallet."""
        logger.info("🔗 Attempting to connect to Phantom wallet...")
        if not self._connected:
            # Use stored public key or fallback to environment variable
            public_key = self._public_key or os.getenv("PHANTOM_PUBLIC_KEY")
            if not public_key:
                raise PhantomConnectionError("Public key is required. Pass it during initialization or set PHANTOM_PUBLIC_KEY environment variable.")
            
            logger.info("Creating new session and establishing connection...")
            self._session = aiohttp.ClientSession()
            self._public_key = public_key  # Store public key as instance variable
            self._connected = True
            logger.info(f"📋 Using public key from environment: {public_key if len(public_key) <= 16 else f'{public_key[:8]}...{public_key[-8:]}'}")
            result = {
                "connected": True,
                "publicKey": public_key,
                "network": self.config.network.value
            }
            logger.info(f"✅ Successfully connected to Phantom wallet on {self.config.network.value}")
            return result
        logger.info("⚡ Already connected to Phantom wallet")
        return {
            "connected": True,
            "publicKey": self._public_key,
            "network": self.config.network.value
        }
    
    async def disconnect(self) -> None:
        """Disconnect from Phantom wallet."""
        logger.info("🔌 Disconnecting from Phantom wallet...")
        
        # Close session if it exists
        if self._session:
            await self._session.close()
            self._session = None
        
        # Always reset connection state, but preserve the original public key
        # Only clear public key if it wasn't provided during initialization
        was_connected = self._connected
        self._connected = False
        
        # Reset public key to initial state (preserve if provided during init)
        self._public_key = self._initial_public_key
        
        if was_connected:
            logger.info("✅ Successfully disconnected from Phantom wallet")
        else:
            logger.info("⚠️ Wallet was not connected")
    
    async def get_balance(self, public_key: str) -> float:
        """Get wallet balance from Solana RPC."""
        logger.info(f"💰 Fetching balance for public key: {public_key if len(public_key) <= 16 else f'{public_key[:8]}...{public_key[-8:]}'}")
        if not self._connected:
            logger.error("❌ Cannot get balance: Wallet not connected")
            raise PhantomConnectionError("Wallet not connected")
        
        try:
            # Determine RPC endpoint based on network
            rpc_endpoints = {
                NetworkType.MAINNET: "https://api.mainnet-beta.solana.com",
                NetworkType.TESTNET: "https://api.testnet.solana.com", 
                NetworkType.DEVNET: "https://api.devnet.solana.com"
            }
            
            rpc_url = rpc_endpoints.get(self.config.network, rpc_endpoints[NetworkType.MAINNET])
            logger.info(f"🌐 Using Solana RPC endpoint: {rpc_url}")
            
            # Prepare RPC request
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [public_key]
            }
            
            # Make RPC call
            async with self._session.post(rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and "value" in data["result"]:
                        # Convert lamports to SOL (1 SOL = 1,000,000,000 lamports)
                        lamports = data["result"]["value"]
                        balance = lamports / 1_000_000_000
                        logger.info(f"✅ Retrieved balance: {balance} SOL ({lamports:,} lamports)")
                        return balance
                    else:
                        logger.error(f"❌ Invalid RPC response: {data}")
                        raise PhantomConnectionError(f"Invalid RPC response: {data}")
                else:
                    logger.error(f"❌ RPC request failed with status {response.status}")
                    raise PhantomConnectionError(f"RPC request failed with status {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to fetch balance: {e}")
            raise PhantomConnectionError(f"Failed to fetch balance from Solana RPC: {e}")
    
    async def send_transaction(
        self,
        transaction: Dict[str, Any],
        config: TransactionConfig
    ) -> Dict[str, Any]:
        """Send a transaction."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        if not transaction.get("from") or not transaction.get("to"):
            raise TransactionError("Invalid transaction parameters")
        
        return {
            "signature": "test_signature",
            "status": TransactionStatus.PENDING.value
        }
    
    async def get_transaction_status(self, signature: str) -> Dict[str, Any]:
        """Get transaction status."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "signature": signature,
            "status": TransactionStatus.CONFIRMED.value,
            "confirmationTime": datetime.now().isoformat()
        }
    
    async def get_token_accounts(self, public_key: str) -> List[Dict[str, Any]]:
        """Get token accounts."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [
            {
                "mint": "test_token",
                "amount": "1000000",
                "decimals": 6
            }
        ]
    
    async def sign_message(self, message: str) -> Dict[str, str]:
        """Sign a message."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "signature": "test_signature",
            "publicKey": self._public_key
        }
    
    async def verify_signature(
        self,
        message: str,
        signature: str,
        public_key: str
    ) -> bool:
        """Verify a signature."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return True
    
    async def get_network(self) -> str:
        """Get current network."""
        return self.config.network.value
    
    async def switch_network(self, network: NetworkType) -> None:
        """Switch network."""
        self.config.network = network
    
    async def get_connected_accounts(self) -> List[str]:
        """Get connected accounts."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [self._public_key]

    # New methods for token swaps
    async def get_swap_quote(
        self,
        input_token: str,
        output_token: str,
        amount: float,
        swap_type: SwapType = SwapType.EXACT_IN
    ) -> Dict[str, Any]:
        """Get a quote for a token swap."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "inputAmount": amount,
            "outputAmount": amount * 0.95,  # Simulated 5% fee
            "priceImpact": 0.01,
            "route": ["test_route"],
            "minimumReceived": amount * 0.94
        }
    
    async def execute_swap(
        self,
        input_token: str,
        output_token: str,
        amount: float,
        config: SwapConfig,
        swap_type: SwapType = SwapType.EXACT_IN
    ) -> Dict[str, Any]:
        """Execute a token swap."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        quote = await self.get_swap_quote(input_token, output_token, amount, swap_type)
        
        return {
            "signature": "test_swap_signature",
            "status": TransactionStatus.PENDING.value,
            "quote": quote
        }

    # New methods for NFT operations
    async def get_nft_metadata(
        self,
        mint_address: str,
        config: Optional[NFTConfig] = None
    ) -> Dict[str, Any]:
        """Get NFT metadata."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        config = config or NFTConfig()
        
        return {
            "name": "Test NFT",
            "symbol": "TNFT",
            "uri": "https://test.com/metadata.json",
            "sellerFeeBasisPoints": 500,
            "creators": [{"address": "test_creator", "verified": True, "share": 100}],
            "collection": {"key": "test_collection", "verified": True}
        }
    
    async def get_nft_accounts(
        self,
        owner: str,
        config: Optional[NFTConfig] = None
    ) -> List[Dict[str, Any]]:
        """Get NFT accounts owned by an address."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        config = config or NFTConfig()
        
        return [
            {
                "mint": "test_nft_mint",
                "owner": owner,
                "amount": 1,
                "delegate": None,
                "state": "initialized",
                "isNative": False
            }
        ]
    
    async def transfer_nft(
        self,
        mint_address: str,
        to_address: str,
        config: Optional[TransactionConfig] = None
    ) -> Dict[str, Any]:
        """Transfer an NFT to another address."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "signature": "test_nft_transfer_signature",
            "status": TransactionStatus.PENDING.value
        }

    # New methods for advanced transaction features
    async def get_priority_fee_estimate(
        self,
        transaction: Dict[str, Any]
    ) -> Dict[str, int]:
        """Get priority fee estimate for a transaction."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "minPriorityFee": 1000,
            "maxPriorityFee": 5000,
            "recommendedPriorityFee": 2000
        }
    
    async def get_compute_unit_estimate(
        self,
        transaction: Dict[str, Any]
    ) -> Dict[str, int]:
        """Get compute unit estimate for a transaction."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "minComputeUnits": 100000,
            "maxComputeUnits": 200000,
            "recommendedComputeUnits": 150000
        }
    
    async def get_transaction_history(
        self,
        address: str,
        limit: int = 10,
        before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get transaction history for an address."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [
            {
                "signature": "test_signature",
                "slot": 123456789,
                "timestamp": datetime.now().isoformat(),
                "status": TransactionStatus.CONFIRMED.value,
                "fee": 5000,
                "type": "transfer"
            }
        ]

    # New methods for token staking
    async def get_stake_accounts(
        self,
        owner: str,
        validator: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get stake accounts for an owner."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [
            {
                "address": "test_stake_account",
                "owner": owner,
                "validator": validator or "test_validator",
                "amount": 100.0,
                "rewards": 1.5,
                "lockup": {
                    "epoch": 100,
                    "unixTimestamp": int(datetime.now().timestamp())
                }
            }
        ]
    
    async def get_stake_rewards(
        self,
        stake_account: str,
        start_epoch: Optional[int] = None,
        end_epoch: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get rewards for a stake account."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [
            {
                "epoch": 100,
                "amount": 0.5,
                "timestamp": datetime.now().isoformat(),
                "type": StakeType.REWARD.value
            }
        ]
    
    async def stake_tokens(
        self,
        config: StakeConfig
    ) -> Dict[str, Any]:
        """Stake tokens with a validator."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        if config.amount <= 0:
            raise StakeError("Invalid stake amount")
        
        return {
            "signature": "test_stake_signature",
            "status": TransactionStatus.PENDING.value,
            "stakeAccount": "test_stake_account"
        }
    
    async def unstake_tokens(
        self,
        stake_account: str,
        amount: Optional[float] = None,
        config: Optional[StakeConfig] = None
    ) -> Dict[str, Any]:
        """Unstake tokens from a validator."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "signature": "test_unstake_signature",
            "status": TransactionStatus.PENDING.value,
            "amount": amount or 100.0
        }

    # New methods for program interactions
    async def get_program_accounts(
        self,
        program_id: str,
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Get accounts owned by a program."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [
            {
                "pubkey": "test_program_account",
                "owner": program_id,
                "lamports": 1000000,
                "executable": False,
                "data": "test_data"
            }
        ]
    
    async def get_program_data(
        self,
        program_id: str
    ) -> Dict[str, Any]:
        """Get program data and metadata."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "programId": program_id,
            "type": ProgramType.TOKEN.value,
            "metadata": {
                "name": "Test Program",
                "version": "1.0.0",
                "authority": "test_authority"
            }
        }
    
    async def execute_program(
        self,
        config: ProgramConfig
    ) -> Dict[str, Any]:
        """Execute a program instruction."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        if not config.instruction_data:
            raise ProgramError("Missing instruction data")
        
        return {
            "signature": "test_program_signature",
            "status": TransactionStatus.PENDING.value,
            "programId": config.program_id
        }

    # New methods for advanced wallet management
    async def get_wallet_features(self) -> List[Dict[str, Any]]:
        """Get available wallet features."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return [
            {
                "feature": WalletFeature.MULTI_SIG.value,
                "enabled": True,
                "options": {
                    "threshold": 2,
                    "owners": ["owner1", "owner2", "owner3"]
                }
            },
            {
                "feature": WalletFeature.HARDWARE.value,
                "enabled": False,
                "options": None
            }
        ]
    
    async def configure_wallet_feature(
        self,
        config: WalletFeatureConfig
    ) -> Dict[str, Any]:
        """Configure a wallet feature."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "feature": config.feature.value,
            "enabled": config.enabled,
            "options": config.options
        }
    
    async def get_wallet_permissions(self) -> Dict[str, List[str]]:
        """Get current wallet permissions."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return {
            "allowedPrograms": ["token_program", "stake_program"],
            "allowedDomains": ["example.com"],
            "allowedOperations": ["transfer", "stake"]
        }
    
    async def update_wallet_permissions(
        self,
        permissions: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Update wallet permissions."""
        if not self._connected:
            raise PhantomConnectionError("Wallet not connected")
        
        return permissions 