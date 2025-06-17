import pytest
from pipeiq_framework.solana_client.solana_wallet import SolanaWallet
from solders.keypair import Keypair
import base58

@pytest.mark.asyncio
async def test_wallet_initialization_without_key():
    wallet = SolanaWallet(network="devnet")
    assert wallet.public_key is not None
    await wallet.close()

@pytest.mark.asyncio
async def test_wallet_initialization_with_base58_string():
    keypair = Keypair()
    private_key_bytes = bytes(keypair)  # 64 bytes
    base58_str = base58.b58encode(private_key_bytes).decode("utf-8")
    
    wallet = SolanaWallet(private_key=base58_str, network="devnet")
    assert wallet.public_key == keypair.pubkey()
    await wallet.close()

@pytest.mark.asyncio
async def test_wallet_initialization_with_bytes():
    keypair = Keypair()
    byte_key = bytes(keypair)
    
    wallet = SolanaWallet(private_key=byte_key, network="devnet")
    assert wallet.public_key == keypair.pubkey()
    await wallet.close()

@pytest.mark.asyncio
async def test_sign_message():
    wallet = SolanaWallet(network="devnet")
    message = "Hello, Solana!"
    
    signature = await wallet.sign_message(message)
    assert isinstance(signature, str)
    assert len(signature) > 0
    await wallet.close()

@pytest.mark.asyncio
async def test_get_balance():
    wallet = SolanaWallet(network="devnet")
    balance = await wallet.get_balance()
    
    assert isinstance(balance, int)
    assert balance >= 0
    await wallet.close()

@pytest.mark.asyncio
async def test_get_account_info():
    wallet = SolanaWallet(network="devnet")
    info = await wallet.get_account_info()
    
    assert isinstance(info, dict) or info is None
    await wallet.close()

@pytest.mark.asyncio
async def test_close_method():
    wallet = SolanaWallet(network="devnet")
    await wallet.close()
