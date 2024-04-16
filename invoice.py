"""
web3 = Web3(Web3.HTTPProvider('https://polygon-mumbai.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe'))
sender_address = '0xcC053440fad9386e4BC774aa660600A8039efA93'
recipient_address = '0xdC908FB55154194be4494c76a076F4dBe7806D78'
private_key = 'bd5c69dcc39fcbeb36300ba7765b66b50f2a89c62aabe53e5941ef636a7ca3c8'
"""
import asyncio
import sys
import secrets
from web3 import Web3, Account
from web3.middleware import geth_poa_middleware

class Invoice:
    def __init__(self, provider_url, payout_wallet):
        print("initializing")
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.payout_wallet = payout_wallet

    async def create_invoice(self, amount_ether):
        print("creating invoice")
        private_key, public_key = self.generate_wallet_keys()
        print(f"Send {amount_ether} ETH to {public_key}")

        await self.await_payment(public_key, amount_ether)
        print("Payment received. Transferring to payout wallet...")
        await self.transfer_to_payout_wallet(private_key, public_key)

    @staticmethod
    def generate_wallet_keys():
        print("generating wallet keys")
        priv = secrets.token_hex(32)
        private_key = "0x" + priv
        public_key = Account.from_key(private_key).address
        return private_key, public_key

    async def await_payment(self, public_key, amount_ether):
        print("awaiting payment")
        unpaid = True
        initial_balance = self.web3.eth.get_balance(public_key)
        required_balance_increase = self.web3.toWei(amount_ether, 'ether')

        while unpaid:
            current_balance = self.web3.eth.get_balance(public_key)
            if (current_balance - initial_balance) >= required_balance_increase:
                unpaid = False
            else:
                await asyncio.sleep(1)

    async def transfer_to_payout_wallet(self, private_key, public_key):



        balance = self.web3.eth.get_balance(public_key)
        gas_estimate = self.web3.eth.estimate_gas({
            'from': public_key,
            'to': self.payout_wallet,
            'value': balance
        })


        gas_price = self.web3.eth.gas_price
        gas_cost = gas_estimate * gas_price

        amount_to_send = balance - gas_cost

        print("transferring to payout wallet")

        if amount_to_send <= 0:
            print("Not enough balance to cover gas costs.")
            sys.exit(1)

        tx = {
            'from': public_key,
            'to': self.payout_wallet,
            'value': amount_to_send,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': self.web3.eth.get_transaction_count(public_key),
        }

        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"Transaction hash: {tx_hash.hex()}")

# Usage
provider_url = 'https://goerli.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe'
payout_wallet = '0xF02e2c016B00E7937da63f29F22581E7d0873209'
eth_invoice = Invoice(provider_url, payout_wallet)

# This runs the async function in an event loop

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = loop.create_task(eth_invoice.create_invoice(0.1))
    loop.run_until_complete(task)





