import pytest
from unittest.mock import patch, Mock
from pipeiq.solana import SolanaWallet, SolanaWalletError
import asyncio

@pytest.mark.asyncio
async def test_wallet_init_and_public_key():
    wallet = SolanaWallet()
    assert wallet.public_key is not None

@pytest.mark.asyncio
async def test_wallet_sign_message_success():
    wallet = SolanaWallet()
    message = "hello world"
    signature = await wallet.sign_message(message)
    assert isinstance(signature, str)
    assert len(signature) > 0

@pytest.mark.asyncio
async def test_wallet_sign_message_failure():
    wallet = SolanaWallet()
    with patch.object(wallet.keypair, "sign", side_effect=Exception("fail")):
        with pytest.raises(SolanaWalletError):
            await wallet.sign_message("fail")

@pytest.mark.asyncio
async def test_wallet_get_balance_success():
    wallet = SolanaWallet()
    with patch.object(wallet._client, "get_balance", return_value={"result": {"value": 12345}}):
        balance = await wallet.get_balance()
        assert balance == 12345

@pytest.mark.asyncio
async def test_wallet_get_balance_rpc_error():
    wallet = SolanaWallet()
    with patch.object(wallet._client, "get_balance", return_value={"error": "rpc error"}):
        with pytest.raises(SolanaWalletError):
            await wallet.get_balance()

@pytest.mark.asyncio
async def test_wallet_get_account_info_success():
    wallet = SolanaWallet()
    with patch.object(wallet._client, "get_account_info", return_value={"result": {"value": {"lamports": 100}}}):
        info = await wallet.get_account_info()
        assert info["lamports"] == 100

@pytest.mark.asyncio
async def test_wallet_get_account_info_rpc_error():
    wallet = SolanaWallet()
    with patch.object(wallet._client, "get_account_info", return_value={"error": "rpc error"}):
        with pytest.raises(SolanaWalletError):
            await wallet.get_account_info()

@pytest.mark.asyncio
async def test_wallet_close_success():
    wallet = SolanaWallet()
    with patch.object(wallet._client, "close", return_value=None) as mock_close:
        await wallet.close()
        mock_close.assert_called_once()

@pytest.mark.asyncio
async def test_wallet_close_failure():
    wallet = SolanaWallet()
    with patch.object(wallet._client, "close", side_effect=Exception("fail")):
        with pytest.raises(SolanaWalletError):
            await wallet.close() 