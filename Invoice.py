import asyncio
import sys
import secrets
from web3 import Web3, Account
from web3.middleware import geth_poa_middleware

class Invoice:
    def __init__(self, provider_url, payout_wallet):
        print("Initializing Invoice")
        self.provider_url = provider_url
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.payout_wallet = payout_wallet

    async def create_invoice(self, amount_ether):
        try:
            print("Creating invoice")
            private_key, public_key = self.generate_wallet_keys()
            print(f"Send {amount_ether} ETH to {public_key}")

            await self.await_payment(public_key, amount_ether)
            print("Payment received. Transferring to payout wallet...")
            await self.transfer_to_payout_wallet(private_key, public_key)
        except Exception as e:
            print(f"An error occurred during invoice creation: {e}")
            sys.exit(1)

    @staticmethod
    def generate_wallet_keys():
        print("Generating wallet keys")
        private_key = "0x" + secrets.token_hex(32)
        public_key = Account.from_key(private_key).address
        return private_key, public_key

    async def await_payment(self, public_key, amount_ether):
        print("Awaiting payment")
        initial_balance = self.web3.eth.get_balance(public_key)
        required_balance_increase = self.web3.toWei(amount_ether, 'ether')

        while True:
            current_balance = self.web3.eth.get_balance(public_key)
            if (current_balance - initial_balance) >= required_balance_increase:
                break
            await asyncio.sleep(1)

    async def transfer_to_payout_wallet(self, private_key, public_key):
        try:
            balance = self.web3.eth.get_balance(public_key)
            gas_estimate = self.web3.eth.estimate_gas({
                'from': public_key,
                'to': self.payout_wallet,
                'value': balance
            })

            gas_price = self.web3.eth.gas_price
            gas_cost = gas_estimate * gas_price
            amount_to_send = balance - gas_cost

            print("Transferring to payout wallet")

            if amount_to_send <= 0:
                raise ValueError("Not enough balance to cover gas costs.")

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
        except Exception as e:
            print(f"An error occurred during the transfer: {e}")
            sys.exit(1)

