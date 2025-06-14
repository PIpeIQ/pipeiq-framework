import pytest
import asyncio
from unittest.mock import Mock, patch
from pipeiq import PipeIQClient, ModelConfig, MCPConfig, SolanaWallet
from pipeiq.client import ConnectionError, AuthenticationError

@pytest.fixture
def mock_wallet():
    wallet = Mock(spec=SolanaWallet)
    wallet.public_key = "mock_public_key"
    wallet.sign_message.return_value = "mock_signature"
    return wallet

@pytest.fixture
def client(mock_wallet):
    return PipeIQClient(
        api_key="test_api_key",
        solana_wallet=mock_wallet,
        network="devnet"
    )

@pytest.fixture
def model_config():
    return ModelConfig(
        model_id="test-model",
        model_type="llm",
        parameters={"temperature": 0.7}
    )

@pytest.fixture
def mcp_config():
    return MCPConfig(
        server_url="https://test-mcp.com",
        api_key="test_mcp_key"
    )

@pytest.mark.asyncio
async def test_connect_to_model_success(client, model_config, mcp_config):
    with patch("requests.Session.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        
        result = await client.connect_to_model(model_config, mcp_config)
        
        assert result == {"status": "success"}
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_connect_to_model_auth_error(client, model_config):
    with patch("requests.Session.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationError):
            await client.connect_to_model(model_config)

@pytest.mark.asyncio
async def test_connect_to_model_connection_error(client, model_config):
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = ConnectionError("Failed to connect")
        
        with pytest.raises(ConnectionError):
            await client.connect_to_model(model_config)

@pytest.mark.asyncio
async def test_connect_to_model_server_error(client, model_config):
    with patch("requests.Session.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(ConnectionError):
            await client.connect_to_model(model_config)

@pytest.mark.asyncio
async def test_connect_to_model_unexpected_error(client, model_config):
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = Exception("Unexpected error")
        
        from pipeiq.client import PipeIQError
        with pytest.raises(PipeIQError):
            await client.connect_to_model(model_config)

@pytest.mark.asyncio
async def test_close(client):
    with patch.object(client._solana_client, "close") as mock_close:
        await client.close()
        mock_close.assert_called_once()
        client._session.close.assert_called_once()

@pytest.mark.asyncio
async def test_wallet_sign_message_error():
    from pipeiq.solana import SolanaWallet, SolanaWalletError
    wallet = SolanaWallet()
    with patch.object(wallet.keypair, "sign", side_effect=Exception("sign error")):
        with pytest.raises(SolanaWalletError):
            await wallet.sign_message("test")

@pytest.mark.asyncio
async def test_wallet_get_balance_error():
    from pipeiq.solana import SolanaWallet, SolanaWalletError
    wallet = SolanaWallet()
    with patch.object(wallet._client, "get_balance", side_effect=Exception("balance error")):
        with pytest.raises(SolanaWalletError):
            await wallet.get_balance() 