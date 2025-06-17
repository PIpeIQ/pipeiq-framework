# worldcoin_client.py
from typing import Dict, Any, Optional
import httpx
import logging
from datetime import datetime
import asyncio
import json
import os
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
APP_ID = os.getenv("WORLDCOIN_APP_ID")


# Validate required environment variables
if not APP_ID:
    raise ValueError("WORLDCOIN_APP_ID environment variable is required")

class WorldcoinError(Exception):
    """Base exception for Worldcoin client errors."""

class WorldcoinVerifyError(WorldcoinError):
    """Raised when the proof‑verification request fails."""

class WorldcoinMetadataError(WorldcoinError):
    """Raised when the Get‑Action‑Metadata request fails."""

class WorldcoinJWKSError(WorldcoinError):
    """Raised when the JWKS request fails."""


class WorldcoinClient:
    """
    Async client that supports:

      • POST /api/v2/verify/{app_id}       (verify ZK proof)
      • POST /api/v1/precheck/{app_id}     (get action metadata)
      • GET  /api/v1/jwks                  (get JSON Web Key Set)

    Works for **both** staging and production; your app_id determines the env.
    """

    def __init__(
        self,
        app_id: str,
        base_url: str = "https://developer.worldcoin.org",
        timeout: float = 10.0,
        user_agent: str = "worldcoin-client/0.1",
    ):
        self.app_id = app_id
        self._verify_ep = f"{base_url}/api/v2/verify/{app_id}"
        self._meta_ep   = f"{base_url}/api/v1/precheck/{app_id}"
        self._jwks_ep   = f"{base_url}/api/v1/jwks"
        
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": user_agent,
            },
        )
        logger.info(f"WorldcoinClient ready for app_id {app_id}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def get_jwks(self) -> Dict[str, Any]:
        """
        Get the JWKS (JSON Web Key Set) from the World ID API.

        Returns:
            Dictionary containing the JWKS

        Raises:
            WorldcoinJWKSError: If the request fails
        """
        start = datetime.now()
        try:
            r = await self._client.get(self._jwks_ep)
        except Exception as e:
            raise WorldcoinJWKSError(f"Network error: {e}") from e

        logger.debug("JWKS HTTP %s in %.2fs", r.status_code,
                     (datetime.now() - start).total_seconds())

        if r.status_code != 200:
            raise WorldcoinJWKSError(f"HTTP {r.status_code}: {r.text}")

        data = r.json()
        logger.info("JWKS retrieved")
        return data

    async def get_action_metadata(self, action: str) -> Dict[str, Any]:
        """
        Get the metadata for a specific action from the World ID API.

        Args:
            action: The action to get metadata for

        Returns:
            Dictionary containing the action metadata

        Raises:
            WorldcoinMetadataError: If the request fails
        """
        start = datetime.now()
        payload = {"action": action}
        
        logger.debug("POST /precheck payload: %s", json.dumps(payload, indent=2))
        
        try:
            r = await self._client.post(self._meta_ep, json=payload)
        except Exception as e:
            raise WorldcoinMetadataError(f"Network error: {e}") from e

        logger.debug("Metadata HTTP %s in %.2fs", r.status_code,
                     (datetime.now() - start).total_seconds())

        if r.status_code != 200:
            raise WorldcoinMetadataError(f"HTTP {r.status_code}: {r.text}")

        data = r.json()
        logger.info("Action metadata retrieved")
        return data

    async def verify_proof(
        self,
        nullifier_hash: str,
        merkle_root: str,
        proof: str,
        action: str,
        signal_hash: str,
        verification_level: str = "orb",  # Default to "orb" verification level
    ) -> Dict[str, Any]:
        """
        Verify a World ID proof.

        Args:
            nullifier_hash: The nullifier hash
            merkle_root: The merkle root
            proof: The proof
            action: The action
            signal_hash: The signal hash
            verification_level: The verification level (default: "orb")

        Returns:
            Dictionary containing the verification result

        Raises:
            WorldcoinVerifyError: If the request fails
        """
        start = datetime.now()
        payload = {
            "nullifier_hash": nullifier_hash,
            "merkle_root": merkle_root,
            "proof": proof,
            "action": action,
            "signal_hash": signal_hash,
            "verification_level": verification_level,
        }

        logger.debug("POST /verify payload: %s", json.dumps(payload, indent=2))

        try:
            r = await self._client.post(self._verify_ep, json=payload)
        except Exception as e:
            raise WorldcoinVerifyError(f"Network error: {e}") from e

        logger.debug("Verify HTTP %s in %.2fs", r.status_code,
                     (datetime.now() - start).total_seconds())

        if r.status_code != 200:
            raise WorldcoinVerifyError(f"HTTP {r.status_code}: {r.text}")

        data = r.json()
        logger.info("Proof verified")
        return data


if __name__ == "__main__":
    async def main():
        ACTION = "proof_verification"

        async with WorldcoinClient(app_id=APP_ID) as wc:
            try:
                jwks = await wc.get_jwks()
                print("\n=== JWKS ===")
                print(jwks)
            except WorldcoinJWKSError as e:
                logger.error("JWKS error: %s", e)

            try:
                meta = await wc.get_action_metadata(action=ACTION)
                print("\n=== Action metadata ===")
                print(meta)
            except WorldcoinMetadataError as e:
                logger.error("Metadata error: %s", e)

            sample = dict(
                nullifier_hash="0x2bf8406809dcefb1486dadc96c0a897db9bab002053054cf64272db512c6fbd8",
                merkle_root="0x2264a66d162d7893e12ea8e3c072c51e785bc085ad655f64c10c1a61e00f0bc2",
                proof="0x" + "0"*512,  # <-- replace with full proof
                action=ACTION,
                signal_hash="0x00c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a4",
                verification_level="orb",  # Add verification level
            )
            try:
                res = await wc.verify_proof(**sample)
                print("\n=== Proof verification ===")
                print(res)
            except WorldcoinVerifyError as e:
                logger.warning("Verify error: %s", e)

    asyncio.run(main())