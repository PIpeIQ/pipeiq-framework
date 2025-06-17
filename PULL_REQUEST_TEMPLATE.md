# Phantom Wallet Integration

## Overview
This PR relates to the Phantom wallet integration for the PipeIQ framework, enabling seamless interaction with Solana blockchain through the Phantom wallet for transactions, balance checks, token swaps, NFT operations, and more.

## 🔧 Setup Instructions

### 1. Install Phantom Wallet Extension
- **Download**: Visit [phantom.com/download](https://phantom.com/download)
- **Browser Support**: Available for Chrome, Firefox, Brave, Edge

### 2. Create or Import Wallet
- **New Wallet**: Open Phantom → "Create New Wallet" → Set password → **Save your Secret Recovery Phrase**
- **Existing Wallet**: Open Phantom → "I already have a wallet" → Enter your Secret Recovery Phrase

### 3. Get Your Public Key (Wallet Address)
1. Open Phantom wallet extension
2. Click on your wallet name at the top
3. Click **"Copy Address"** or click the copy icon next to your address

### 4. Environment Configuration
Create a `.env` file in the project root directory (`pipeiq-framework/.env`):

```bash
# Required: Your Phantom wallet public key
PHANTOM_PUBLIC_KEY=your_public_key_here_without_quotes

# Optional: Network configuration (defaults to mainnet)
# PHANTOM_NETWORK=mainnet  # or testnet, devnet
```

**⚠️ Important**: 
- **Never share your Secret Recovery Phrase** - only use your public key
- The public key is safe to share (it's just your wallet address)

## 🧪 Testing

### Basic Functionality Tests
Run the following commands to verify Phantom integration:

```bash
# Run all Phantom wallet tests
python tests/test_phantom.py

```

### Expected Test Results
- ✅ **Wallet Connection**: Should connect to Phantom wallet
- ✅ **Balance Retrieval**: Should fetch real SOL balance from Solana RPC
- ✅ **Network Selection**: Should work with mainnet/testnet/devnet
- ✅ **Error Handling**: Should handle connection errors gracefully

### Manual Testing Checklist
- [ ] Phantom extension is installed
- [ ] `.env` file contains valid `PHANTOM_PUBLIC_KEY`
- [ ] Tests pass with real Solana RPC calls
- [ ] Balance shows correct SOL amount (may be 0.0 for new wallets)
- [ ] Connection and disconnection work properly

## 🌐 Network Types

### **MAINNET** (Production)
- **Use for**: Live applications, real trading
- **RPC**: `https://api.mainnet-beta.solana.com`
- **Tokens**: Real SOL with actual value
- **Fees**: Real transaction costs

### **TESTNET** (Testing)
- **Use for**: Application testing before mainnet
- **RPC**: `https://api.testnet.solana.com`
- **Tokens**: Test SOL (no real value)
- **Fees**: Test transaction costs

### **DEVNET** (Development)
- **Use for**: Development and experimentation
- **RPC**: `https://api.devnet.solana.com`
- **Tokens**: Free test SOL from faucets
- **Fees**: Minimal test costs

## 🔍 Code Review Focus Areas

### 1. **Security**
- Verify no private keys or secret phrases are exposed
- Check proper error handling for RPC failures
- Ensure environment variables are properly validated

### 2. **Error Handling**
- Network connection failures
- Invalid public keys
- RPC timeout scenarios
- Wallet not connected states

### 3. **Performance**
- Async/await patterns properly implemented
- HTTP session management
- Proper resource cleanup (connection closing)

### 4. **Testing**
- Real RPC calls vs mocked responses
- Edge cases covered
- Network switching functionality

## 📝 Usage Example

```python
from pipeiq.phantom import PhantomWallet, WalletConfig, NetworkType

# Initialize wallet
config = WalletConfig(network=NetworkType.MAINNET)
wallet = PhantomWallet(config)

# Connect and get balance
async def main():
    # Connect to wallet
    result = await wallet.connect()
    print(f"Connected: {result['connected']}")
    print(f"Public Key: {result['publicKey']}")
    
    # Get balance
    balance = await wallet.get_balance(result['publicKey'])
    print(f"Balance: {balance} SOL")
    
    # Disconnect
    await wallet.disconnect()
```

## ⚠️ Troubleshooting

### Common Issues
1. **"Wallet not connected"**: Ensure `await wallet.connect()` is called first
2. **"Invalid public key"**: Verify your `PHANTOM_PUBLIC_KEY` in `.env` file
3. **"RPC request failed"**: Check network connection and RPC endpoint
4. **"0.0 SOL balance"**: Normal for new wallets - send SOL to test

## 🔗 Related Links
- [Phantom Wallet Official Site](https://phantom.com)
- [Solana Official Documentation](https://docs.solana.com)
- [Solana RPC API Reference](https://docs.solana.com/api)
