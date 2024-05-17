import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

const socket = io('http://127.0.0.1:5000');  // Ensure this matches your backend URL

function App() {
  const [status, setStatus] = useState('Waiting to create an invoice...');
  const [providerUrl, setProviderUrl] = useState('');
  const [payoutWallet, setPayoutWallet] = useState('');
  const [amount, setAmount] = useState('');

  useEffect(() => {
    socket.on('update', (message) => {
      setStatus(message);
    });

    return () => {
      socket.off('update');
    };
  }, []);

  const handleCreateInvoice = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/create_invoice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',  // Ensure this header is present
        },
        body: JSON.stringify({
          provider_url: providerUrl,
          payout_wallet: payoutWallet,
          amount_ether: amount,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        setStatus(`Error: ${data.error}`);
        return;
      }

      const data = await response.json();
      setStatus('Invoice creation initiated');
    } catch (error) {
      setStatus(`Fetch error: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Ethereum Invoice Tracker</h1>
        <div className="input-container">
          <input
            type="text"
            placeholder="Provider URL"
            value={providerUrl}
            onChange={(e) => setProviderUrl(e.target.value)}
          />
          <input
            type="text"
            placeholder="Payout Wallet"
            value={payoutWallet}
            onChange={(e) => setPayoutWallet(e.target.value)}
          />
          <input
            type="text"
            placeholder="Amount in ETH"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <button onClick={handleCreateInvoice}>Create Invoice</button>
        </div>
        <div className="status-container">
          <h2>Status</h2>
          <p>{status}</p>
        </div>
      </header>
    </div>
  );
}

export default App;
