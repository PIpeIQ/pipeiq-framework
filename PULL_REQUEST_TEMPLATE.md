# World Chain Integration

## Overview
This PR integrates World ID's verification system into our application. The integration allows us to verify user proofs using World ID's API.

## Changes
- Added `WorldcoinClient` class for interacting with World ID's API
- Implemented proof verification functionality
- Added JWKS (JSON Web Key Set) retrieval
- Added action metadata retrieval

## API Endpoints
The integration uses the following World ID API endpoints that are available [here](https://docs.world.org/world-id/reference/api):
- `POST /api/v2/verify/{app_id}` - Verify user proofs
- `POST /api/v1/precheck/{app_id}` - Get action metadata
- `GET /api/v1/jwks` - Get JSON Web Key Set

## Usage Example
```python
async with WorldcoinClient(app_id="your_app_id") as wc:
    # Get JWKS
    jwks = await wc.get_jwks()
    
    # Get action metadata
    meta = await wc.get_action_metadata(action="your_action")
    
    # Verify proof
    result = await wc.verify_proof(
        nullifier_hash="0x...",
        merkle_root="0x...",
        proof="0x...",
        action="your_action",
        signal_hash="0x...",
        verification_level="orb"  # Optional, defaults to "orb"
    )
```

## Error Handling
The integration includes specific error classes for different types of failures:
- `WorldcoinError` - Base class for all World ID related errors
- `WorldcoinJWKSError` - JWKS retrieval failures
- `WorldcoinMetadataError` - Action metadata retrieval failures
- `WorldcoinVerifyError` - Proof verification failures


## Configuration
Required environment variables:
- `WORLDCOIN_APP_ID` - Your World ID app ID. Update it in your .env file.


## Additional Notes
- The integration supports both staging and production environments
- The app_id determines which environment is used
- All API calls are asynchronous for better performance 