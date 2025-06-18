from typing import Dict, Optional, Union, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from .models import ModelConfig, MCPConfig
from .solana import SolanaWallet
from .logger import logger
import asyncio
from datetime import datetime

class PipeIQError(Exception):
    """Base exception for PipeIQ errors."""
    pass

class ConnectionError(PipeIQError):
    """Raised when there's an error connecting to the API."""
    pass

class AuthenticationError(PipeIQError):
    """Raised when there's an authentication error."""
    pass

class PipeIQClient:
    def __init__(
        self,
        api_key: str,
        solana_wallet: Optional[SolanaWallet] = None,
        network: str = "mainnet-beta",
        base_url: str = "https://api.pipeiq.io/v1",
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 0.5
    ):
        """
        Initialize the PipeIQ client.
        
        Args:
            api_key: Your PipeIQ API key
            solana_wallet: Optional Solana wallet instance
            network: Solana network to use (mainnet-beta, testnet, devnet)
            base_url: Base URL for the PipeIQ API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff: Backoff factor for retries
        """
        self.api_key = api_key
        self.base_url = base_url
        self.network = network
        self.timeout = timeout
        self.solana_wallet = solana_wallet or SolanaWallet()
        self._solana_client = AsyncClient(f"https://api.{network}.solana.com")
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure session with retry strategy
        self._session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        
        logger.info(f"Initialized PipeIQ client for network: {network}")
        
    async def connect_to_model(
        self,
        model_config: ModelConfig,
        mcp_config: Optional[MCPConfig] = None
    ) -> Dict[str, Any]:
        """
        Connect to a model with optional MCP server configuration.
        
        Args:
            model_config: Configuration for the model to connect to
            mcp_config: Optional MCP server configuration
            
        Returns:
            Dict containing connection details and status
            
        Raises:
            ConnectionError: If there's an error connecting to the API
            AuthenticationError: If there's an authentication error
            PipeIQError: For other PipeIQ-related errors
        """
        start_time = datetime.now()
        logger.info(f"Connecting to model: {model_config.model_id}")
        
        try:
            # Prepare the connection request
            payload = {
                "model_config": model_config.dict(),
                "network": self.network,
                "wallet_address": str(self.solana_wallet.public_key),
                "timestamp": int(datetime.now().timestamp())
            }
            
            if mcp_config:
                payload["mcp_config"] = mcp_config.dict()
                
            # Sign the request with Solana wallet
            signature = await self.solana_wallet.sign_message(str(payload))
            payload["signature"] = signature
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Request-ID": f"req_{int(datetime.now().timestamp())}"
            }
            
            logger.debug(f"Making API request to {self.base_url}/connect")
            response = self._session.post(
                f"{self.base_url}/connect",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Handle different response status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code >= 500:
                raise ConnectionError(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Successfully connected to model in {duration:.2f}s")
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            raise ConnectionError("Request timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to API")
            raise ConnectionError("Failed to connect to API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise PipeIQError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise PipeIQError(f"Unexpected error: {str(e)}")
        
    async def close(self):
        """Close the Solana client connection and session."""
        logger.info("Closing PipeIQ client")
        await self._solana_client.close()
        self._session.close() 