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

A Solana-compatible SDK for connecting to different models and MCP servers. This SDK provides a simple interface for developers to interact with various AI models while leveraging Solana's blockchain capabilities for authentication and payments.

## Installation

```bash
pip install pipeiq
```

## Quick Start

```python
import asyncio
from pipeiq import PipeIQClient, ModelConfig, MCPConfig, SolanaWallet

async def main():
    # Initialize a Solana wallet (or use your existing one)
    wallet = SolanaWallet()
    
    # Create the PipeIQ client
    client = PipeIQClient(
        api_key="your_api_key",
        solana_wallet=wallet,
        network="devnet"  # Use 'mainnet-beta' for production
    )
    
    # Configure your model
    model_config = ModelConfig(
        model_id="gpt-4",
        model_type="llm",
        parameters={
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )
    
    # Optionally configure an MCP server
    mcp_config = MCPConfig(
        server_url="https://your-mcp-server.com",
        api_key="your_mcp_api_key"
    )
    
    try:
        # Connect to the model
        result = await client.connect_to_model(model_config, mcp_config)
        print(f"Connection successful: {result}")
        
        # Check wallet balance
        balance = await wallet.get_balance()
        print(f"Wallet balance: {balance} lamports")
        
    finally:
        # Clean up
        await client.close()
        await wallet.close()

if __name__ == "__main__":
    asyncio.run(main())
```

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Error Handling

The SDK raises custom exceptions for different error scenarios:
- `PipeIQError`: Base exception for all SDK errors
- `ConnectionError`: Raised for network/API connection issues
- `AuthenticationError`: Raised for authentication/authorization failures
- `SolanaWalletError`: Raised for Solana wallet-specific errors

Example:
```python
from pipeiq.client import PipeIQError, ConnectionError, AuthenticationError
from pipeiq.solana import SolanaWalletError

try:
    # ... use the SDK ...
except AuthenticationError:
    print("Invalid API key or permissions.")
except ConnectionError:
    print("Network or server error.")
except SolanaWalletError as e:
    print(f"Wallet error: {e}")
except PipeIQError as e:
    print(f"General SDK error: {e}")

## Logging

The SDK uses Python's built-in logging module. You can configure logging as follows:

```python
from pipeiq.logger import setup_logger
logger = setup_logger(level="DEBUG", log_file="pipeiq.log")
```

## Testing

To run the test suite:

```bash
pip install -e ".[dev]"
pytest tests/
```

Test coverage includes:
- Client connection and error handling
- Solana wallet operations and error handling
- Retry logic and session management

## Advanced Usage

- **Retry Logic:**
  - The client automatically retries failed requests (configurable via `max_retries` and `retry_backoff`).
- **Custom Endpoints:**
  - You can specify custom model endpoints in `ModelConfig`.
- **Account Info:**
  - Use `wallet.get_account_info()` to fetch detailed Solana account data.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
