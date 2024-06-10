import asyncio
import sqlite3
from Invoice import Invoice

class AsyncInvoice(Invoice):
    def __init__(self, provider_url, payout_wallet, socketio):
        print("Initializing AsyncInvoice")
        super().__init__(provider_url, payout_wallet)
        self.socketio = socketio

    async def create_invoice(self, amount_ether):
        print("Creating async invoice")
        private_key, public_key = self.generate_wallet_keys()
        self.socketio.emit('update', f"Send {amount_ether} ETH to {public_key}")
        print(f"Send {amount_ether} ETH to {public_key}")

        # Store invoice creation in database
        self.store_invoice(self.provider_url, self.payout_wallet, amount_ether, public_key, "pending")

        await self.await_payment(public_key, amount_ether)
        self.socketio.emit('update', "Payment received. Transferring to payout wallet...")
        print("Payment received. Transferring to payout wallet...")

        await self.transfer_to_payout_wallet(private_key, public_key)

        # Update invoice status in database
        self.update_invoice_status(public_key, "completed")

    def store_invoice(self, provider_url, payout_wallet, amount_ether, public_key, status):
        print("Storing invoice in database")
        conn = sqlite3.connect('invoices.db')
        try:
            with conn:
                conn.execute('''
                    INSERT INTO invoices (provider_url, payout_wallet, amount_ether, public_key, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (provider_url, payout_wallet, amount_ether, public_key, status))
        except sqlite3.Error as e:
            print(f"An error occurred while storing the invoice: {e}")
        finally:
            conn.close()

    def update_invoice_status(self, public_key, status):
        print("Updating invoice status in database")
        conn = sqlite3.connect('invoices.db')
        try:
            with conn:
                conn.execute('''
                    UPDATE invoices
                    SET status = ?
                    WHERE public_key = ?
                ''', (status, public_key))
        except sqlite3.Error as e:
            print(f"An error occurred while updating the invoice status: {e}")
        finally:
            conn.close()
