import asyncio
import logging
from worldcoin_client import WorldcoinClient, WorldcoinJWKSError, WorldcoinMetadataError, WorldcoinVerifyError

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
            nullifier_hash="0x2bf8406809dcefb1486dadc96c0a897db9bab002053054cf64272db512c6fbd8",
            merkle_root="0x2264a66d162d7893e12ea8e3c072c51e785bc085ad655f64c10c1a61e00f0bc2",
            proof="0x" + "0"*512,  # Replace with actual proof
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