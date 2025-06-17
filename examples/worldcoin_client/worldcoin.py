import asyncio
import logging
import sys
from pathlib import Path

# Add the parent directory to Python path to allow importing the module
sys.path.append(str(Path(__file__).parent.parent.parent))
from pipeiq_framework.worldcoin_client.worldcoin import WorldcoinClient, WorldcoinJWKSError, WorldcoinMetadataError, WorldcoinVerifyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Example usage of WorldcoinClient demonstrating:
    1. JWKS retrieval
    2. Action metadata retrieval
    3. Proof verification
    """
    # Replace with your actual app_id
    APP_ID = "<your app id here>"
    ACTION = "<your action here>"

    async with WorldcoinClient(app_id=APP_ID) as wc:
        # Example 1: Get JWKS
        try:
            jwks = await wc.get_jwks()
            print("\n=== JWKS ===")
            print(jwks)
        except WorldcoinJWKSError as e:
            logger.error("JWKS error: %s", e)

        # Example 2: Get action metadata
        try:
            meta = await wc.get_action_metadata(action=ACTION)
            print("\n=== Action metadata ===")
            print(meta)
        except WorldcoinMetadataError as e:
            logger.error("Metadata error: %s", e)

        # Example 3: Verify proof
        sample = dict(
            nullifier_hash="0x1004b481f0859419b7ad5b8b42f43d6095eea434ad3576c2104a81fac473b8d4",
            merkle_root="0x0377e1cad94947bc30964dbf23ccce08488f33aafc586692897c324e03ef9531",
            proof="0x22a0d38550a020800c3b533d58eaf5d3eac0ddd20d384338…7e7c0d747db1fce8d23d928198f7823a07c1a6a2b6d31e27f",  # Replace with actual proof
            action=ACTION,
            signal_hash="0x00c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a4",
            verification_level="orb",
        )
        try:
            res = await wc.verify_proof(**sample)
            print("\n=== Proof verification ===")
            print(res)
        except WorldcoinVerifyError as e:
            logger.warning("Verify error: %s", e)

if __name__ == "__main__":
    asyncio.run(main()) 