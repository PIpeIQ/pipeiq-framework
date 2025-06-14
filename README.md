# PIPEIQ Framework

> A decentralized agent protocol to connect AI tools across Web2 and Web3—models, MCP servers, decentralized compute, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Solana](https://img.shields.io/badge/built%20on-Solana-orange)](https://solana.com/)

---

## Overview
PIPEIQ is an open-source framework that enables developers to seamlessly connect and orchestrate AI tools across the Web2 and Web3 ecosystems. It abstracts away the complexities of identity, messaging, and orchestration by providing standardized primitives for agent coordination, tool invocation, and cross-network integration.

With native support for models, MCP servers, decentralized compute providers, and on-chain identity frameworks, PIPEIQ aims to serve as a universal protocol layer for the AI economy—supporting autonomous, composable, and verifiable AI agents.

---

## Key Features

### 🔗 Web2 + Web3 Interop
- Unified routing for AI tools—OpenAI, HuggingFace, MCP servers, Filecoin compute, etc.
- Tool registration and capability exposure via agent profiles

### 🔑 Identity & Wallets
- On-chain agent identities (machine & human-aligned)
- Verifiable credentials & optional proof-of-personhood

### 📊 Staking & Reputation
- Reputation-linked staking mechanisms
- Trust scores based on usage history & task completion

### ⚖️ Agent Task Market
- Publish & bid on decentralized agent tasks
- Support for escrow, arbitration, and bounty resolution

### 🌐 Context Anchoring
- Persistent agent memory using IPFS / Arweave
- Modular context schemas for task recall & chaining

### 🤷 Intent Signaling & Routing
- Message schema for goal-driven task delegation
- Modular routing system between agents & services

---

## Architecture

The framework is built on two foundational layers:

### 1. Blockchain-Native Primitives
- ✅ Solana Smart Contracts (Rust)
- ✨ Token Programs for $PIPEIQ
- ⚖️ DAO governance (via Realms)

### 2. Agent-Centric Primitives
- 🤖 Agent Profiles & Permissions
- 🚧 Task Markets & Context Anchors
- 📢 Intent Signaling System

---

## Contributing
We welcome contributions from framework developers, cryptographers, and AI researchers. To get started:

1. Fork this repository
2. Read the [CONTRIBUTING.md](CONTRIBUTING.md) guide
3. Open a Pull Request (PR) with clear description

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

## Links
- 🔗 [Whitepaper](https://pipeiq.ai/whitepaper)
- 🌐 [Website](https://pipeiq.ai)
- ✉️ Join our community: `discord.gg/pipeiq`  
- 📰 Blog: [Coming Soon]  

---

*PIPEIQ is building the decentralized substrate for AI. Join us.*

# PipeIQ SDK

A Solana-compatible SDK for building decentralized applications.

## Features

- Solana wallet integration
- Attestation service with versioning and audit logging
- World Chain integration for human verification and mini apps
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

### World Chain Integration

The World Chain integration provides functionality for human verification, mini app deployment, and gas fee management.

```python
from pipeiq import WorldChainService
from pipeiq.solana import SolanaWallet

# Initialize wallet
wallet = SolanaWallet(private_key="your_private_key")

# Create World Chain service
service = WorldChainService(
    wallet,
    base_url="https://api.world.org/v1",
    rate_limit=100,
    enable_audit_logging=True
)

# Verify a human using World ID
verification = await service.verify_human(
    proof={
        "type": "world_id",
        "data": "your_proof_data"
    }
)

# Check gas fee status
gas_status = await service.get_gas_status()
if gas_status["free_gas_available"]:
    print("Free gas available!")

# Deploy a mini app
app = await service.deploy_mini_app(
    app_data={
        "name": "My Mini App",
        "version": "1.0.0",
        "config": {
            "key": "value"
        }
    },
    metadata={
        "description": "A test mini app",
        "category": "social"
    }
)

# Get app status
status = await service.get_mini_app_status(app["id"])

# Get network information
network_info = await service.get_network_info()
```

### World Chain Features

#### Human Verification
- Verify users using World ID
- Check verification status
- Handle verification errors

#### Mini App Deployment
- Deploy apps to World Chain
- Track deployment status
- Manage app metadata
- Get deployment URLs

#### Gas Fee Management
- Check free gas availability
- Monitor gas balance
- Track gas usage

#### Network Information
- Get network status
- Monitor block height
- Check gas prices
- View network load

#### Audit Logging
- Track all operations
- Filter logs by operation type
- Filter logs by time range
- Export logs for compliance

### Error Handling

```python
from pipeiq.world_chain import (
    WorldChainError,
    WorldChainValidationError,
    WorldChainNetworkError
)

try:
    # Verify a human
    await service.verify_human(proof={"type": "world_id", "data": "invalid"})
except WorldChainValidationError as e:
    print(f"Validation error: {e}")
except WorldChainNetworkError as e:
    print(f"Network error: {e}")
except WorldChainError as e:
    print(f"General error: {e}")
```

### Using Context Manager

```python
async with WorldChainService(wallet) as service:
    # Service is automatically initialized
    result = await service.verify_human(proof={"type": "world_id", "data": "test"})
    # Session is automatically closed when done
```

### Audit Logging

```python
# Get all audit logs
logs = await service.get_audit_logs()

# Filter logs by operation
verify_logs = await service.get_audit_logs(operation="verify_human")

# Filter logs by time range
recent_logs = await service.get_audit_logs(
    start_time=datetime.now() - timedelta(days=1)
)

# Export logs
for log in logs:
    print(f"Operation: {log['operation']}")
    print(f"Timestamp: {log['timestamp']}")
    print(f"Details: {log['details']}")
```

## Features

### World Chain Integration
- Human verification via World ID
- Mini app deployment and management
- Gas fee tracking and management
- Network status monitoring
- Comprehensive audit logging

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