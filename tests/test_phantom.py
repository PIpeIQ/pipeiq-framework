import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from pipeiq.phantom import (
    PhantomWallet,
    NetworkType,
    TransactionStatus,
    SwapType,
    NFTStandard,
    StakeType,
    ProgramType,
    WalletFeature,
    WalletConfig,
    TransactionConfig,
    SwapConfig,
    NFTConfig,
    StakeConfig,
    ProgramConfig,
    WalletFeatureConfig,
    PhantomError,
    ConnectionError,
    TransactionError,
    SwapError,
    NFTError,
    StakeError,
    ProgramError,
    FeatureError
)

@pytest.mark.asyncio
async def test_wallet_initialization():
    """Test wallet initialization with default and custom config."""
    # Test with default config
    wallet = PhantomWallet()
    assert wallet.config.network == NetworkType.MAINNET
    assert not wallet.config.auto_approve
    assert wallet.config.timeout == 30000

    # Test with custom config
    custom_config = WalletConfig(
        network=NetworkType.TESTNET,
        auto_approve=True,
        timeout=60000
    )
    wallet = PhantomWallet(config=custom_config)
    assert wallet.config.network == NetworkType.TESTNET
    assert wallet.config.auto_approve
    assert wallet.config.timeout == 60000

@pytest.mark.asyncio
async def test_connect():
    """Test wallet connection."""
    wallet = PhantomWallet()
    result = await wallet.connect()
    assert result["connected"]
    assert "publicKey" in result
    assert wallet._connected

@pytest.mark.asyncio
async def test_disconnect():
    """Test wallet disconnection."""
    wallet = PhantomWallet()
    await wallet.connect()
    await wallet.disconnect()
    assert not wallet._connected

@pytest.mark.asyncio
async def test_get_balance():
    """Test getting wallet balance."""
    wallet = PhantomWallet()
    await wallet.connect()
    balance = await wallet.get_balance("test_public_key")
    assert isinstance(balance, float)
    assert balance >= 0

@pytest.mark.asyncio
async def test_get_balance_not_connected():
    """Test getting balance when not connected."""
    wallet = PhantomWallet()
    with pytest.raises(ConnectionError):
        await wallet.get_balance("test_public_key")

@pytest.mark.asyncio
async def test_send_transaction():
    """Test sending a transaction."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    transaction = {
        "from": "sender_public_key",
        "to": "recipient_public_key",
        "amount": 1.0
    }
    
    config = TransactionConfig(
        fee_payer="sender_public_key",
        recent_blockhash="test_blockhash"
    )
    
    result = await wallet.send_transaction(transaction, config)
    assert "signature" in result
    assert "status" in result
    assert result["status"] == TransactionStatus.PENDING.value

@pytest.mark.asyncio
async def test_get_transaction_status():
    """Test getting transaction status."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    result = await wallet.get_transaction_status("test_signature")
    assert "signature" in result
    assert "status" in result
    assert "confirmationTime" in result
    assert result["status"] == TransactionStatus.CONFIRMED.value

@pytest.mark.asyncio
async def test_get_token_accounts():
    """Test getting token accounts."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    accounts = await wallet.get_token_accounts("test_public_key")
    assert isinstance(accounts, list)
    if accounts:
        assert "mint" in accounts[0]
        assert "amount" in accounts[0]
        assert "decimals" in accounts[0]

@pytest.mark.asyncio
async def test_sign_message():
    """Test signing a message."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    result = await wallet.sign_message("test message")
    assert "signature" in result
    assert "publicKey" in result

@pytest.mark.asyncio
async def test_verify_signature():
    """Test verifying a signature."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    result = await wallet.verify_signature(
        "test message",
        "test_signature",
        "test_public_key"
    )
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_get_network():
    """Test getting current network."""
    wallet = PhantomWallet()
    network = await wallet.get_network()
    assert network == NetworkType.MAINNET.value

@pytest.mark.asyncio
async def test_switch_network():
    """Test switching networks."""
    wallet = PhantomWallet()
    await wallet.switch_network(NetworkType.TESTNET)
    network = await wallet.get_network()
    assert network == NetworkType.TESTNET.value

@pytest.mark.asyncio
async def test_get_connected_accounts():
    """Test getting connected accounts."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    accounts = await wallet.get_connected_accounts()
    assert isinstance(accounts, list)
    assert len(accounts) > 0

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling."""
    wallet = PhantomWallet()
    
    # Test not connected error
    with pytest.raises(ConnectionError):
        await wallet.get_balance("test_public_key")
    
    # Test transaction error
    await wallet.connect()
    with pytest.raises(TransactionError):
        await wallet.send_transaction({})  # Invalid transaction

@pytest.mark.asyncio
async def test_wallet_config_validation():
    """Test wallet configuration validation."""
    with pytest.raises(ValueError):
        WalletConfig(network="invalid_network")  # type: ignore

@pytest.mark.asyncio
async def test_transaction_config_validation():
    """Test transaction configuration validation."""
    with pytest.raises(ValueError):
        TransactionConfig(fee_payer="")  # Empty fee payer

@pytest.mark.asyncio
async def test_get_swap_quote():
    """Test getting a swap quote."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    quote = await wallet.get_swap_quote(
        input_token="SOL",
        output_token="USDC",
        amount=1.0,
        swap_type=SwapType.EXACT_IN
    )
    
    assert "inputAmount" in quote
    assert "outputAmount" in quote
    assert "priceImpact" in quote
    assert "route" in quote
    assert "minimumReceived" in quote
    assert quote["inputAmount"] == 1.0
    assert quote["outputAmount"] == 0.95  # 5% fee

@pytest.mark.asyncio
async def test_execute_swap():
    """Test executing a token swap."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = SwapConfig(
        slippage=0.01,
        deadline=int(datetime.now().timestamp()) + 3600
    )
    
    result = await wallet.execute_swap(
        input_token="SOL",
        output_token="USDC",
        amount=1.0,
        config=config,
        swap_type=SwapType.EXACT_IN
    )
    
    assert "signature" in result
    assert "status" in result
    assert "quote" in result
    assert result["status"] == TransactionStatus.PENDING.value

@pytest.mark.asyncio
async def test_get_nft_metadata():
    """Test getting NFT metadata."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = NFTConfig(
        standard=NFTStandard.METAPLEX,
        verify_ownership=True,
        include_metadata=True
    )
    
    metadata = await wallet.get_nft_metadata("test_nft_mint", config)
    
    assert "name" in metadata
    assert "symbol" in metadata
    assert "uri" in metadata
    assert "sellerFeeBasisPoints" in metadata
    assert "creators" in metadata
    assert "collection" in metadata

@pytest.mark.asyncio
async def test_get_nft_accounts():
    """Test getting NFT accounts."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = NFTConfig(
        standard=NFTStandard.METAPLEX,
        verify_ownership=True
    )
    
    accounts = await wallet.get_nft_accounts("test_owner", config)
    
    assert isinstance(accounts, list)
    assert len(accounts) > 0
    assert "mint" in accounts[0]
    assert "owner" in accounts[0]
    assert "amount" in accounts[0]
    assert "state" in accounts[0]

@pytest.mark.asyncio
async def test_transfer_nft():
    """Test transferring an NFT."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = TransactionConfig(
        fee_payer="test_payer",
        recent_blockhash="test_blockhash"
    )
    
    result = await wallet.transfer_nft(
        mint_address="test_nft_mint",
        to_address="test_recipient",
        config=config
    )
    
    assert "signature" in result
    assert "status" in result
    assert result["status"] == TransactionStatus.PENDING.value

@pytest.mark.asyncio
async def test_get_priority_fee_estimate():
    """Test getting priority fee estimate."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    transaction = {
        "from": "test_sender",
        "to": "test_recipient",
        "amount": 1.0
    }
    
    estimate = await wallet.get_priority_fee_estimate(transaction)
    
    assert "minPriorityFee" in estimate
    assert "maxPriorityFee" in estimate
    assert "recommendedPriorityFee" in estimate
    assert estimate["minPriorityFee"] <= estimate["recommendedPriorityFee"] <= estimate["maxPriorityFee"]

@pytest.mark.asyncio
async def test_get_compute_unit_estimate():
    """Test getting compute unit estimate."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    transaction = {
        "from": "test_sender",
        "to": "test_recipient",
        "amount": 1.0
    }
    
    estimate = await wallet.get_compute_unit_estimate(transaction)
    
    assert "minComputeUnits" in estimate
    assert "maxComputeUnits" in estimate
    assert "recommendedComputeUnits" in estimate
    assert estimate["minComputeUnits"] <= estimate["recommendedComputeUnits"] <= estimate["maxComputeUnits"]

@pytest.mark.asyncio
async def test_get_transaction_history():
    """Test getting transaction history."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    history = await wallet.get_transaction_history(
        address="test_address",
        limit=5,
        before="test_signature"
    )
    
    assert isinstance(history, list)
    assert len(history) > 0
    assert "signature" in history[0]
    assert "slot" in history[0]
    assert "timestamp" in history[0]
    assert "status" in history[0]
    assert "fee" in history[0]
    assert "type" in history[0]

@pytest.mark.asyncio
async def test_swap_error_handling():
    """Test swap error handling."""
    wallet = PhantomWallet()
    
    # Test not connected error
    with pytest.raises(ConnectionError):
        await wallet.get_swap_quote("SOL", "USDC", 1.0)
    
    # Test invalid swap parameters
    await wallet.connect()
    with pytest.raises(SwapError):
        await wallet.execute_swap("SOL", "USDC", -1.0, SwapConfig())

@pytest.mark.asyncio
async def test_nft_error_handling():
    """Test NFT error handling."""
    wallet = PhantomWallet()
    
    # Test not connected error
    with pytest.raises(ConnectionError):
        await wallet.get_nft_metadata("test_mint")
    
    # Test invalid NFT parameters
    await wallet.connect()
    with pytest.raises(NFTError):
        await wallet.transfer_nft("", "test_recipient")

@pytest.mark.asyncio
async def test_swap_config_validation():
    """Test swap configuration validation."""
    with pytest.raises(ValueError):
        SwapConfig(slippage=-0.01)  # Invalid slippage
    
    with pytest.raises(ValueError):
        SwapConfig(deadline=0)  # Invalid deadline

@pytest.mark.asyncio
async def test_nft_config_validation():
    """Test NFT configuration validation."""
    with pytest.raises(ValueError):
        NFTConfig(standard="invalid_standard")  # type: ignore 

@pytest.mark.asyncio
async def test_get_stake_accounts():
    """Test getting stake accounts."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    accounts = await wallet.get_stake_accounts(
        owner="test_owner",
        validator="test_validator"
    )
    
    assert isinstance(accounts, list)
    assert len(accounts) > 0
    assert "address" in accounts[0]
    assert "owner" in accounts[0]
    assert "validator" in accounts[0]
    assert "amount" in accounts[0]
    assert "rewards" in accounts[0]
    assert "lockup" in accounts[0]

@pytest.mark.asyncio
async def test_get_stake_rewards():
    """Test getting stake rewards."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    rewards = await wallet.get_stake_rewards(
        stake_account="test_stake_account",
        start_epoch=100,
        end_epoch=200
    )
    
    assert isinstance(rewards, list)
    assert len(rewards) > 0
    assert "epoch" in rewards[0]
    assert "amount" in rewards[0]
    assert "timestamp" in rewards[0]
    assert "type" in rewards[0]
    assert rewards[0]["type"] == StakeType.REWARD.value

@pytest.mark.asyncio
async def test_stake_tokens():
    """Test staking tokens."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = StakeConfig(
        validator_address="test_validator",
        amount=100.0,
        lockup_period=3600,
        auto_compound=True
    )
    
    result = await wallet.stake_tokens(config)
    
    assert "signature" in result
    assert "status" in result
    assert "stakeAccount" in result
    assert result["status"] == TransactionStatus.PENDING.value

@pytest.mark.asyncio
async def test_unstake_tokens():
    """Test unstaking tokens."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    result = await wallet.unstake_tokens(
        stake_account="test_stake_account",
        amount=50.0
    )
    
    assert "signature" in result
    assert "status" in result
    assert "amount" in result
    assert result["status"] == TransactionStatus.PENDING.value
    assert result["amount"] == 50.0

@pytest.mark.asyncio
async def test_get_program_accounts():
    """Test getting program accounts."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    filters = [
        {"memcmp": {"offset": 0, "bytes": "test"}}
    ]
    
    accounts = await wallet.get_program_accounts(
        program_id="test_program",
        filters=filters
    )
    
    assert isinstance(accounts, list)
    assert len(accounts) > 0
    assert "pubkey" in accounts[0]
    assert "owner" in accounts[0]
    assert "lamports" in accounts[0]
    assert "executable" in accounts[0]
    assert "data" in accounts[0]

@pytest.mark.asyncio
async def test_get_program_data():
    """Test getting program data."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    data = await wallet.get_program_data("test_program")
    
    assert "programId" in data
    assert "type" in data
    assert "metadata" in data
    assert "name" in data["metadata"]
    assert "version" in data["metadata"]
    assert "authority" in data["metadata"]

@pytest.mark.asyncio
async def test_execute_program():
    """Test executing a program instruction."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = ProgramConfig(
        program_id="test_program",
        program_type=ProgramType.TOKEN,
        instruction_data={"action": "transfer"},
        accounts=[
            {"pubkey": "account1", "isSigner": True},
            {"pubkey": "account2", "isSigner": False}
        ],
        signers=["account1"]
    )
    
    result = await wallet.execute_program(config)
    
    assert "signature" in result
    assert "status" in result
    assert "programId" in result
    assert result["status"] == TransactionStatus.PENDING.value

@pytest.mark.asyncio
async def test_get_wallet_features():
    """Test getting wallet features."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    features = await wallet.get_wallet_features()
    
    assert isinstance(features, list)
    assert len(features) > 0
    assert "feature" in features[0]
    assert "enabled" in features[0]
    assert "options" in features[0]

@pytest.mark.asyncio
async def test_configure_wallet_feature():
    """Test configuring a wallet feature."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    config = WalletFeatureConfig(
        feature=WalletFeature.MULTI_SIG,
        enabled=True,
        options={"threshold": 2, "owners": ["owner1", "owner2"]}
    )
    
    result = await wallet.configure_wallet_feature(config)
    
    assert "feature" in result
    assert "enabled" in result
    assert "options" in result
    assert result["feature"] == WalletFeature.MULTI_SIG.value
    assert result["enabled"] is True

@pytest.mark.asyncio
async def test_get_wallet_permissions():
    """Test getting wallet permissions."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    permissions = await wallet.get_wallet_permissions()
    
    assert "allowedPrograms" in permissions
    assert "allowedDomains" in permissions
    assert "allowedOperations" in permissions
    assert isinstance(permissions["allowedPrograms"], list)
    assert isinstance(permissions["allowedDomains"], list)
    assert isinstance(permissions["allowedOperations"], list)

@pytest.mark.asyncio
async def test_update_wallet_permissions():
    """Test updating wallet permissions."""
    wallet = PhantomWallet()
    await wallet.connect()
    
    new_permissions = {
        "allowedPrograms": ["new_program"],
        "allowedDomains": ["new_domain.com"],
        "allowedOperations": ["new_operation"]
    }
    
    result = await wallet.update_wallet_permissions(new_permissions)
    
    assert result == new_permissions
    assert "allowedPrograms" in result
    assert "allowedDomains" in result
    assert "allowedOperations" in result

@pytest.mark.asyncio
async def test_stake_error_handling():
    """Test staking error handling."""
    wallet = PhantomWallet()
    
    # Test not connected error
    with pytest.raises(ConnectionError):
        await wallet.get_stake_accounts("test_owner")
    
    # Test invalid stake amount
    await wallet.connect()
    with pytest.raises(StakeError):
        await wallet.stake_tokens(StakeConfig(
            validator_address="test_validator",
            amount=-1.0
        ))

@pytest.mark.asyncio
async def test_program_error_handling():
    """Test program interaction error handling."""
    wallet = PhantomWallet()
    
    # Test not connected error
    with pytest.raises(ConnectionError):
        await wallet.get_program_accounts("test_program")
    
    # Test missing instruction data
    await wallet.connect()
    with pytest.raises(ProgramError):
        await wallet.execute_program(ProgramConfig(
            program_id="test_program",
            program_type=ProgramType.TOKEN,
            instruction_data={},
            accounts=[]
        ))

@pytest.mark.asyncio
async def test_feature_error_handling():
    """Test wallet feature error handling."""
    wallet = PhantomWallet()
    
    # Test not connected error
    with pytest.raises(ConnectionError):
        await wallet.get_wallet_features()
    
    # Test invalid feature configuration
    await wallet.connect()
    with pytest.raises(FeatureError):
        await wallet.configure_wallet_feature(WalletFeatureConfig(
            feature="invalid_feature"  # type: ignore
        )) 