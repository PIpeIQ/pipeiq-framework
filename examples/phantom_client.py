import asyncio
import os
import sys
import logging

# Add the pipeiq_framework to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeiq_framework.phantom_client.phantom_wallet import PhantomWallet
from pipeiq_framework.phantom_client.errors import PhantomConnectionError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Initialize with your API key - REPLACE WITH YOUR ACTUAL PHANTOM WALLET PUBLIC KEY
    PHANTOM_PUBLIC_KEY = "REPLACE_WITH_YOUR_ACTUAL_PHANTOM_PUBLIC_KEY"
    
    # Validate that user has set their key
    if PHANTOM_PUBLIC_KEY == "REPLACE_WITH_YOUR_ACTUAL_PHANTOM_PUBLIC_KEY":
        logger.error("❌ Please replace PHANTOM_PUBLIC_KEY with your actual Phantom wallet public key!")
        return
    

    
    logger.info("🎯 Running Phantom Wallet example usage...")
    
    try:
        # Example 1: Wallet Initialization
        logger.info("🚀 Example 1: Wallet initialization")
        wallet = PhantomWallet(public_key=PHANTOM_PUBLIC_KEY)
        logger.info("✅ Wallet initialized successfully")
        
        # Example 2: Connection
        logger.info("🔗 Example 2: Wallet connection")
        result = await wallet.connect()
        logger.info(f"Connection result: {result}")
        assert result["connected"] == True
        assert "publicKey" in result
        assert "network" in result
        logger.info(f"✅ Wallet connected successfully to {result.get('network')} network")
        logger.info(f"   Public Key: {result.get('publicKey')}")
        
        # Example 3: Network Information
        logger.info("🌐 Example 3: Network verification")
        network = await wallet.get_network()
        logger.info(f"Current network: {network}")
        logger.info("✅ Network information retrieved")
        
        # Example 4: Connected Accounts
        logger.info("👥 Example 4: Connected accounts")
        accounts = await wallet.get_connected_accounts()
        logger.info(f"Connected accounts: {accounts}")
        assert len(accounts) > 0
        logger.info("✅ Connected accounts retrieved")
        
        # Example 5: Balance Check
        logger.info("💰 Example 5: Balance retrieval")
        public_key = result.get("publicKey")
        balance = await wallet.get_balance(public_key)
        logger.info(f"Account balance: {balance} SOL")
        assert isinstance(balance, (int, float))
        assert balance >= 0
        logger.info("✅ Balance retrieval successful")
        
        # Example 6: Message Signing
        logger.info("✍️ Example 6: Message signing")
        test_message = "Hello Phantom Wallet!"
        sign_result = await wallet.sign_message(test_message)
        assert "signature" in sign_result
        assert "publicKey" in sign_result
        logger.info("✅ Message signing successful")
        
        # Example 7: Signature Verification
        logger.info("🔍 Example 7: Signature verification")
        verification = await wallet.verify_signature(
            test_message,
            sign_result["signature"],
            sign_result["publicKey"]
        )
        assert verification == True
        logger.info("✅ Signature verification successful")
        
        # Example 8: Reconnection
        logger.info("🔄 Example 8: Reconnection")
        reconnect_result = await wallet.connect()  # Should return existing connection
        assert reconnect_result["connected"] == True
        logger.info("✅ Reconnection handled correctly")
        
        # Example 9: Disconnection
        logger.info("🔌 Example 9: Wallet disconnection")
        await wallet.disconnect()
        assert not wallet._connected
        logger.info("✅ Wallet disconnected successfully")
        
        logger.info("🎉 ALL EXAMPLES COMPLETED! Phantom Wallet integration is working correctly!")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {str(e)}")
        logger.error(f"   Example failed at: {e.__class__.__name__}")
        # Clean up on error
        try:
            await wallet.disconnect()
        except:
            pass
        raise

if __name__ == "__main__":
    asyncio.run(main()) 
