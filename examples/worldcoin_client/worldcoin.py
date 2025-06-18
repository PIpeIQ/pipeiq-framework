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
    APP_ID = "app_staging_fa5303a638554d31e1a461c95b92d68f"
    ACTION = "proof_verification"

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
            merkle_root="0x13fd28feaef242a222144e868d10f11b9a9424a2faa9c6c18170b35ad8d7cff8",
            proof="0x110221434a32a563d04e342aa468eb0ad28ddaf7dc59dfaf43d9478b75aec243127ef70080d8606d21d3a3b7b686dfc73175d6e9be3aecbc6c07f3dbdea1a065265952627a1a916912c055c23220c9096354fbfe1c40db1eac1d5aa6f62731501966269f18e31fedbf7e21de692eccb1a2382a79a1e25cc8679306c12e3cf72a126de2b8c7a67bced158ff8a79cebd85610aab827ff5eb7fc2eaae7eb511635d2014e20229d2419278867eb5957098cd83945e3ff0109c3a45abed64c8564b901b4007e79258b5a0c40a1b59c8bd93bdf3c79ddec8397b4015df2e0c4dadf2f11cc52e416477c39c301e98ca508d2cbc43423606c7c7c502ab5fa899e821f0af",  # Replace with actual proof
            action=ACTION,
            # signal_hash="0x00c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a4",
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