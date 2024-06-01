from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import threading
import sqlite3
from invoice import Invoice

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

def init_db():
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_url TEXT NOT NULL,
            payout_wallet TEXT NOT NULL,
            amount_ether REAL NOT NULL,
            public_key TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class AsyncInvoice(Invoice):
    def __init__(self, provider_url, payout_wallet, socketio):
        super().__init__(provider_url, payout_wallet)
        self.socketio = socketio

    async def create_invoice(self, amount_ether):
        print("creating invoice")
        private_key, public_key = self.generate_wallet_keys()
        self.socketio.emit('update', f"Send {amount_ether} ETH to {public_key}")
        print(f"Send {amount_ether} ETH to {public_key}")

        self.store_invoice(self.provider_url, self.payout_wallet, amount_ether, public_key, "pending")

        await self.await_payment(public_key, amount_ether)
        self.socketio.emit('update', "Payment received. Transferring to payout wallet...")
        print("Payment received. Transferring to payout wallet...")

        await self.transfer_to_payout_wallet(private_key, public_key)
        self.update_invoice_status(public_key, "completed")

    def store_invoice(self, provider_url, payout_wallet, amount_ether, public_key, status):
        conn = sqlite3.connect('invoices.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO invoices (provider_url, payout_wallet, amount_ether, public_key, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (provider_url, payout_wallet, amount_ether, public_key, status))
        conn.commit()
        conn.close()

    def update_invoice_status(self, public_key, status):
        conn = sqlite3.connect('invoices.db')
        c = conn.cursor()
        c.execute('''
            UPDATE invoices
            SET status = ?
            WHERE public_key = ?
        ''', (status, public_key))
        conn.commit()
        conn.close()

@app.route('/create_invoice', methods=['POST', 'GET'])
def create_invoice_api():
    print('testing')
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()

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

    thread = threading.Thread(target=run_async_invoice)
    thread.start()

    return jsonify({"message": "Invoice creation initiated"}), 202

@app.route('/invoices', methods=['GET'])
def get_invoices():
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute('SELECT * FROM invoices')
    invoices = c.fetchall()
    conn.close()
    return jsonify(invoices)

def build_cors_preflight_response():
    response = jsonify({"message": "CORS preflight successful"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
