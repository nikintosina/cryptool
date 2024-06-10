# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import threading
import sqlite3
from AsyncInvoice import AsyncInvoice  # Ensure correct import

class FlaskServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", logger=True, engineio_logger=True)
        self._initialize_database()
        self._register_routes()
        self._register_socketio_events()

    def _initialize_database(self):
        connection = sqlite3.connect('invoices.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_url TEXT NOT NULL,
                payout_wallet TEXT NOT NULL,
                amount_ether REAL NOT NULL,
                public_key TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        connection.commit()
        connection.close()

    def _register_routes(self):
        @self.app.route('/create_invoice', methods=['POST'])
        def create_invoice_api():
            print('Received request to create invoice')
            if request.method == 'OPTIONS':
                return self._build_cors_preflight_response()

            data = request.json
            provider_url = data.get('provider_url')
            payout_wallet = data.get('payout_wallet')
            amount_ether = data.get('amount_ether')

            if not (provider_url and payout_wallet and amount_ether):
                return jsonify({"error": "Missing required parameters"}), 400

            eth_invoice = AsyncInvoice(provider_url, payout_wallet, self.socketio)

            def run_async_invoice():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                task = loop.create_task(eth_invoice.create_invoice(amount_ether))
                loop.run_until_complete(task)

            thread = threading.Thread(target=run_async_invoice)
            thread.start()

            return jsonify({"message": "Invoice creation initiated"}), 202

        @self.app.route('/invoices', methods=['GET'])
        def get_invoices():
            connection = sqlite3.connect('invoices.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM invoices')
            invoices = cursor.fetchall()
            connection.close()
            return jsonify(invoices)

    def _build_cors_preflight_response(self):
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    def _register_socketio_events(self):
        @self.socketio.on('connect')
        def on_connect():
            emit('my_response', {'data': 'Connected'})

    def run(self):
        self.socketio.run(self.app, debug=True, allow_unsafe_werkzeug=True)
