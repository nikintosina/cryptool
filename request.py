import requests

url = "http://127.0.0.1:5000/create_invoice"
data = {
    "provider_url": "https://sepolia.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe",
    "payout_wallet": "0xF02e2c016B00E7937da63f29F22581E7d0873209",
    "amount_ether": 0.1
}
print(1)
response = requests.post(url, json=data)
print(response.json())

