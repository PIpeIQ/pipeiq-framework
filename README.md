## Warning

The software is in active development, and was not audited. Use at your own risk.

# PIPEIQ Framework

A decentralized agent protocol to connect AI tools across Web2 and Web3—models, MCP servers, decentralized compute, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Solana](https://img.shields.io/badge/built%20on-Solana-orange)](https://solana.com/)

---

## Overview
PIPEIQ is an open-source framework that enables developers to seamlessly connect and orchestrate AI tools across the Web2 and Web3 ecosystems. It abstracts away the complexities of identity, messaging, and orchestration by providing standardized primitives for agent coordination, tool invocation, and cross-network integration.

With native support for models, MCP servers, decentralized compute providers, and on-chain identity frameworks, PIPEIQ aims to serve as a universal protocol layer for the AI economy—supporting autonomous, composable, and verifiable AI agents.

---

## 📦 Installation

You can install `pipeiq` directly from PyPI:

```bash
pip install pipeiq
```

## Key Features

1. Integration with Phantom Wallet 
2. Integration with Prime Intellect for Decentralized Compute
3. Integration with Worldcoin for proof-of-personhood authentication
4. Integration for Know Your Customer (KYC) operation with Persona

---

## 🚀 Usage

We currently support a way to connect to decentralized resources. Usage examples can be found in the [`examples/`](./examples) folder.

---

## Contributing
We welcome contributions from framework developers, cryptographers, and AI researchers. To get started:

1. Fork this repository
2. Open a Pull Request (PR) with clear description

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

## Links
- 🔗 [Whitepaper](https://pipeiq.ai/whitepaper)
- 🌐 [Website](https://pipeiq.ai)
- ✉️ Join our community: `discord.gg/pipeiq`
- X.com/pipeiqai

---

*PIPEIQ is building the decentralized substrate for AI. Join us.*

# PipeIQ SDK

A Solana-compatible SDK for building decentralized applications.

## Features

- Solana wallet integration
- Attestation service with versioning and audit logging
- Rate limiting and retry logic
- Comprehensive error handling
- Webhook support
- Template-based attestations

## Installation

```bash
pip install pipeiq
```

## Usage

### Basic Usage

```python
from pipeiq import PipeIQClient
from pipeiq.solana import SolanaWallet

# Initialize wallet
wallet = SolanaWallet(private_key="your_private_key")

# Create client
client = PipeIQClient(wallet)

# Use the client
result = await client.some_method()
```

### Attestation Service

The attestation service provides a robust way to create, verify, and manage attestations with versioning and audit logging.

```python
from pipeiq import AttestationService, AttestationTemplate
from pipeiq.solana import SolanaWallet

# Initialize wallet
wallet = SolanaWallet(private_key="your_private_key")

# Create attestation service with audit logging enabled
service = AttestationService(
    wallet,
    rate_limit=100,
    webhook_secret="your_webhook_secret",
    enable_audit_logging=True
)

# Create an attestation
attestation = await service.create_attestation(
    data={"name": "John Doe", "age": 30},
    attestation_type="identity"
)

# Update an attestation
updated = await service.update_attestation(
    attestation_id=attestation["id"],
    data={"name": "John Doe", "age": 31},
    reason="Age update"
)

# Get attestation versions
versions = await service.get_attestation_versions(attestation["id"])
for version in versions:
    print(f"Version: {version.version}")
    print(f"Changes: {version.changes}")

# Get audit logs
logs = await service.get_audit_logs(
    attestation_id=attestation["id"],
    operation="update",
    start_time=datetime.now() - timedelta(days=7)
)
for log in logs:
    print(f"Operation: {log.operation}")
    print(f"Timestamp: {log.timestamp}")
    print(f"Details: {log.details}")
```

### Attestation Templates

Create reusable templates for attestations:

```python
template = AttestationTemplate(
    name="identity_verification",
    schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "document_id": {"type": "string"}
        }
    },
    required_fields=["name", "age", "document_id"],
    default_metadata={"version": "1.0"},
    default_tags=["identity", "verification"],
    default_expiry_days=30,
    version="1.0.0"
)

# Create attestation from template
attestation = await service.create_attestation_from_template(
    template=template,
    data={
        "name": "John Doe",
        "age": 30,
        "document_id": "12345"
    }
)
```

### Error Handling

The SDK provides comprehensive error handling:

```python
from pipeiq.attestation import (
    AttestationError,
    AttestationValidationError,
    AttestationVersionError
)

try:
    # Create attestation with invalid data
    await service.create_attestation_from_template(
        template=template,
        data={"name": "John Doe"}  # Missing required fields
    )
except AttestationValidationError as e:
    print(f"Validation error: {e}")
except AttestationVersionError as e:
    print(f"Version conflict: {e}")
except AttestationError as e:
    print(f"General error: {e}")
```

### Webhook Support

Handle attestation events via webhooks:

```python
from pipeiq.attestation import WebhookHandler

async def handle_attestation_created(event):
    print(f"New attestation created: {event['id']}")

async def handle_attestation_updated(event):
    print(f"Attestation updated: {event['id']}")
    print(f"New version: {event['version']}")

# Create webhook handler
handler = WebhookHandler(
    webhook_secret="your_webhook_secret",
    handlers={
        "attestation.created": handle_attestation_created,
        "attestation.updated": handle_attestation_updated
    }
)

# Handle webhook request
await handler.handle_webhook(request_data, request_signature)
```

## Features

### Attestation Versioning

- Track changes to attestations over time
- Maintain version history with metadata
- Compare different versions
- Roll back to previous versions if needed

### Audit Logging

- Comprehensive audit trail of all operations
- Track who made changes and when
- Filter logs by operation type, time range, and more
- Export logs for compliance and auditing

### Enhanced Error Handling

- Specific error types for different scenarios
- Detailed error messages and context
- Validation errors for data integrity
- Version conflict handling

### Rate Limiting and Retries

- Automatic rate limiting to prevent API abuse
- Configurable retry logic for failed requests
- Exponential backoff for retries
- Customizable retry conditions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Features

- Solana wallet integration for secure authentication
- Support for multiple model types (LLM, Image, Audio, etc.)
- MCP (Model Control Protocol) server integration
- Async/await support for better performance
- Type hints and validation using Pydantic
- Easy-to-use API for model connections

## Configuration

### Model Configuration

The `ModelConfig` class allows you to specify:
- Model ID and type
- Custom parameters
- Optional custom endpoint

### MCP Configuration

The `MCPConfig` class supports:
- Server URL
- API key
- Timeout settings
- Retry attempts
- Custom headers

### Solana Wallet

The `SolanaWallet` class provides:
- Keypair management
- Message signing
- Balance checking
- Network selection (mainnet-beta, testnet, devnet)

## Error Handling

The SDK raises custom exceptions for different error scenarios:
- `PipeIQError`: Base exception for all SDK errors
- `ConnectionError`: Raised for network/API connection issues
- `AuthenticationError`: Raised for authentication/authorization failures