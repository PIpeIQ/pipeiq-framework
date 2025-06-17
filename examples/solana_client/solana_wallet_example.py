from pipeiq_framework.solana_client.solana_wallet import SolanaWallet
import asyncio

PRIVATE_KEY = "GIVE_YOUR_PRIVATE_KEY_HERE"
wallet = SolanaWallet(private_key=PRIVATE_KEY)

async def main():
    account_info = await wallet.get_account_info()
    print(account_info)
    balance = await wallet.get_balance()
    print(balance)

asyncio.run(main())
