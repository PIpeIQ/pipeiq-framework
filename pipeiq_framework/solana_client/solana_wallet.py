from typing import Optional, Union, Dict, Any
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import base58
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class SolanaWalletError(Exception):
    """Base exception for Solana wallet errors."""
    pass

class SolanaWallet:
    def __init__(
        self,
        private_key: Optional[Union[str, bytes]] = None,
        network: str = "mainnet-beta",
        commitment: Commitment = Commitment("confirmed")
    ):
        """
        Initialize a Solana wallet.
        
        Args:
            private_key: Optional private key (can be base58 string or bytes)
            network: Solana network to use
            commitment: Solana commitment level
        """
        try:
            if private_key:
                if isinstance(private_key, str):
                    self.keypair = Keypair.from_base58_string(private_key)
                elif isinstance(private_key, bytes):
                    self.keypair = Keypair.from_bytes(private_key)
                else:
                    raise ValueError("private_key must be either a string or bytes")
                logger.info("Initialized wallet with provided private key")
            else:
                self.keypair = Keypair()
                logger.info("Generated new wallet keypair")
                
            self.public_key = self.keypair.pubkey()
            self._client = AsyncClient(
                f"https://api.{network}.solana.com",
                commitment=commitment
            )
            logger.info(f"Connected to Solana network: {network}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Solana wallet: {str(e)}")
            raise SolanaWalletError(f"Failed to initialize wallet: {str(e)}")
        
    async def sign_message(self, message: str) -> str:
        """
        Sign a message with the wallet's private key.
        
        Args:
            message: Message to sign
            
        Returns:
            Base58 encoded signature
            
        Raises:
            SolanaWalletError: If signing fails
        """
        try:
            start_time = datetime.now()
            logger.debug(f"Signing message of length {len(message)}")
            
            signature = self.keypair.sign_message(message.encode())
            encoded_signature = base58.b58encode(bytes(signature)).decode()
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Message signed in {duration:.2f}s")
            
            return encoded_signature
            
        except Exception as e:
            logger.error(f"Failed to sign message: {str(e)}")
            raise SolanaWalletError(f"Failed to sign message: {str(e)}")
        
    async def get_balance(self) -> int:
        """
        Get the wallet's SOL balance.
        
        Returns:
            Balance in lamports
            
        Raises:
            SolanaWalletError: If balance check fails
        """
        try:
            start_time = datetime.now()
            logger.debug(f"Fetching balance for {self.public_key}")
            
            response = await self._client.get_balance(self.public_key)
                
            balance = response.value
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Balance: {balance} lamports (fetched in {duration:.2f}s)")
            
            return balance
            
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise SolanaWalletError(f"Failed to get balance: {str(e)}")
            
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get detailed account information.
        
        Returns:
            Account information dictionary
            
        Raises:
            SolanaWalletError: If account info fetch fails
        """
        try:
            start_time = datetime.now()
            logger.debug(f"Fetching account info for {self.public_key}")
            response = await self._client.get_account_info(self.public_key) 
                
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Account info fetched in {duration:.2f}s")
            
            return response.value
            
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise SolanaWalletError(f"Failed to get account info: {str(e)}")
        
    async def close(self):
        """Close the Solana client connection."""
        try:
            logger.info("Closing Solana client connection")
            await self._client.close()
        except Exception as e:
            logger.error(f"Error closing Solana client: {str(e)}")
            raise SolanaWalletError(f"Failed to close client: {str(e)}") 