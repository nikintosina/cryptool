"""
web3 = Web3(Web3.HTTPProvider('https://polygon-mumbai.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe'))
sender_address = '0xcC053440fad9386e4BC774aa660600A8039efA93'
recipient_address = '0xdC908FB55154194be4494c76a076F4dBe7806D78'
private_key = 'bd5c69dcc39fcbeb36300ba7765b66b50f2a89c62aabe53e5941ef636a7ca3c8'

"""

from web3 import Web3
import os

# Connect to Goerli Testnet
goerli_provider_url = 'https://goerli.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe'  # Replace with your provider URL
web3 = Web3(Web3.HTTPProvider(goerli_provider_url))

# Verify connection
if web3.isConnected():
    print("Connected to Goerli Testnet")
else:
    print("Failed to connect to Goerli Testnet")
    exit()

sender_address = '0xcC053440fad9386e4BC774aa660600A8039efA93'
recipient_address = '0xdC908FB55154194be4494c76a076F4dBe7806D78'
private_key = 'bd5c69dcc39fcbeb36300ba7765b66b50f2a89c62aabe53e5941ef636a7ca3c8'

# Ensure your account has ETH for gas
balance = web3.eth.get_balance(sender_address)
print(f"Sender balance: {web3.fromWei(balance, 'ether')} ETH")

# Transaction Parameters
nonce = web3.eth.getTransactionCount(sender_address)
tx = {
    'nonce': nonce, 
    'to': recipient_address,
    'value': web3.toWei(0.01, 'ether'),  # Sending 0.01 ETH
    'gas': 2000000,
    'gasPrice': web3.toWei('50', 'gwei')
}

# Sign Transaction
signed_tx = web3.eth.account.sign_transaction(tx, private_key)

# Send Transaction
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Transaction hash: {web3.toHex(tx_hash)}")

# Wait for Transaction Receipt
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Transaction receipt: {tx_receipt}")
