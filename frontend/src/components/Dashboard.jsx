import React, { useState, useEffect } from 'react';

function Dashboard() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [positions, setPositions] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Fetch initial data
    fetchSystemStatus();
    fetchPositions();

    // Connect WebSocket
    const websocket = new WebSocket('ws://localhost:8000/ws');

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const fetchSystemStatus = async () => {
    const response = await fetch('http://localhost:8000/api/v1/system/status');
    const data = await response.json();
    setSystemStatus(data);
  };

  const fetchPositions = async () => {
    const response = await fetch('http://localhost:8000/api/v1/positions');
    const data = await response.json();
    setPositions(data);
  };

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'position_update':
        fetchPositions();
        break;
      case 'system_status':
        setSystemStatus(message.data);
        break;
      default:
        break;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-6">Bitcoin Autotrader</h1>

      {/* System Status */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        {systemStatus && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-400">Status</p>
              <p className="text-2xl font-bold text-green-500">{systemStatus.status}</p>
            </div>
            <div>
              <p className="text-gray-400">Balance</p>
              <p className="text-2xl font-bold">${systemStatus.account_balance.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-400">Daily P&L</p>
              <p className={`text-2xl font-bold ${systemStatus.daily_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${systemStatus.daily_pnl.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-400">Total P&L</p>
              <p className={`text-2xl font-bold ${systemStatus.total_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${systemStatus.total_pnl.toFixed(2)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Positions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Open Positions</h2>
        {positions.length === 0 ? (
          <p className="text-gray-400">No open positions</p>
        ) : (
          <div className="space-y-4">
            {positions.map((position) => (
              <div key={position.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{position.symbol}</p>
                    <p className="text-sm text-gray-400">Entry: ${position.entry_price.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${position.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      ${position.unrealized_pnl.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-400">Current: ${position.current_price.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
