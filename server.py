from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import asyncio
import threading
from invoice import Invoice  # Ensure your Invoice class is adapted to work with SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allows all origins; be cautious with this in production

class AsyncInvoice(Invoice):
    def __init__(self, provider_url, payout_wallet, socketio):
        super().__init__(provider_url, payout_wallet)
        self.socketio = socketio

    async def create_invoice(self, amount_ether):
        # Override or extend create_invoice to emit WebSocket events
        print("creating invoice")
        private_key, public_key = self.generate_wallet_keys()
        # Emit to all connected clients by default
        self.socketio.emit('update', f"Send {amount_ether} ETH to {public_key}")

        await self.await_payment(public_key, amount_ether)
        self.socketio.emit('update', "Payment received. Transferring to payout wallet...")
        await self.transfer_to_payout_wallet(private_key, public_key)


@app.route('/create_invoice', methods=['POST'])
def create_invoice_api():
    data = request.json
    provider_url = data.get('provider_url')
    payout_wallet = data.get('payout_wallet')
    amount_ether = data.get('amount_ether')

    if not (provider_url and payout_wallet and amount_ether):
        return jsonify({"error": "Missing required parameters"}), 400

    eth_invoice = AsyncInvoice(provider_url, payout_wallet, socketio)

    def run_async_invoice():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(eth_invoice.create_invoice(amount_ether))
        loop.run_until_complete(task)

    # Use a thread to handle the asynchronous invoice creation to not block Flask's main thread
    thread = threading.Thread(target=run_async_invoice)
    thread.start()

    return jsonify({"message": "Invoice creation initiated"}), 20

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)
