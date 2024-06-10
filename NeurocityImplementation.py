import requests
from neurosity import Neurosity

# Initialize Neurosity device connection
neurosity = Neurosity({
    "deviceId": "YOUR_DEVICE_ID"
})

# Define the condition and action
def on_focus_change(focus):
    if focus > 0.7:  # Change threshold as needed
        trigger_invoice_creation()

def trigger_invoice_creation():
    url = "http://127.0.0.1:5000/create_invoice"
    data = {
        "provider_url": "https://sepolia.infura.io/v3/30ad9316ff3b4c8c9b6448e673b842fe",
        "payout_wallet": "0xF02e2c016B00E7937da63f29F22581E7d0873209",
        "amount_ether": 0.1
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Authenticate to the device
neurosity.login({
    "email": "YOUR_EMAIL",
    "password": "YOUR_PASSWORD"
})

# Subscribe to focus changes
neurosity.focus().subscribe(on_focus_change)

# Keep the script running to listen for focus changes
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Script stopped.")
