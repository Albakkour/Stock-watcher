import { useEffect, useState } from "react";
import "./App.css"; 

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [stocks, setStocks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [symbol, setSymbol] = useState("TSLA");
  const [direction, setDirection] = useState("above");
  const [threshold, setThreshold] = useState(200);

  // fetch functions.

  async function fetchStocks() {
    try {
      const res = await fetch(`${API_BASE}/api/stocks`);
      const data = await res.json();
      setStocks(data.stocks || []);
    } catch (e) {
      console.error("Failed to fetch stocks");
    }
  }

  async function fetchAlerts() {
    try {
      const res = await fetch(`${API_BASE}/api/alerts`);
      const data = await res.json();
      setAlerts(data.alerts || []);
    } catch (e) {
      console.error("Failed to fetch alerts");
    }
  }

  async function fetchNotifications() {
    try {
      const res = await fetch(`${API_BASE}/api/notifications`);
      const data = await res.json();
      setNotifications(data.notifications || []);
    } catch (e) {
      console.error("Failed to fetch notifications");
    }
  }

  // do functions 

  async function createAlert(e) {
    e.preventDefault();
    await fetch(`${API_BASE}/api/alerts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, direction, threshold: Number(threshold) }),
    });

    await fetchAlerts();
    setSymbol(""); 
  }

  async function resetSystem() {
    const confirmed = window.confirm(
      "DANGER ZONE \n\nAre you sure? This will delete ALL stocks, alerts, and notifications history."
    );
    
    if (!confirmed) return;

    try {
      await fetch(`${API_BASE}/api/reset`, { method: "DELETE" });
      setStocks([]);
      setAlerts([]);
      setNotifications([]);
    } catch (e) {
      console.error("Failed to reset system", e);
    }
  }



  useEffect(() => {

    fetchStocks();
    fetchAlerts();
    fetchNotifications();

    const id = setInterval(() => {
      fetchStocks();
      fetchNotifications();
    }, 5000);

    return () => clearInterval(id);
  }, []);


  const formatDate = (dateString) => {
    if (!dateString) return "";
    return new Date(dateString).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  return (
    <div className="app-container">
      <header>
        <h1>Cloud Stock Watcher</h1>
        {/* Reset Button positioned in the header */}
        <button onClick={resetSystem} className="danger-btn">
          Reset System
        </button>
      </header>

      <div className="dashboard-grid">
        {/* Left Column: Stocks */}
        <section className="card">
          <h2>Live Market Data</h2>
          {stocks.length === 0 ? (
            <p style={{ color: '#666', fontStyle: 'italic' }}>Waiting for stock data...</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Price</th>
                  <th style={{ textAlign: 'right' }}>Last Update</th>
                </tr>
              </thead>
              <tbody>
                {stocks.map((s) => (
                  <tr key={s.symbol}>
                    <td style={{ fontWeight: 'bold', color: '#fff' }}>{s.symbol}</td>
                    <td className="price-cell">${Number(s.price).toFixed(2)}</td>
                    <td style={{ textAlign: 'right', color: '#888' }}>
                      {formatDate(s.updated_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        {/* Right Column: Create Alert Form */}
        <section className="card">
          <h2>Create New Alert</h2>
          <form onSubmit={createAlert} className="form-group">
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <label style={{ fontSize: '0.8rem', marginBottom: '4px', color: '#aaa' }}>Symbol</label>
              <input 
                placeholder="e.g. AAPL"
                value={symbol} 
                onChange={(e) => setSymbol(e.target.value.toUpperCase())} 
                required
              />
            </div>
            
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: '0.8rem', marginBottom: '4px', color: '#aaa' }}>Condition</label>
                <select 
                  value={direction} 
                  onChange={(e) => setDirection(e.target.value)}
                  style={{ width: '100%' }}
                >
                  <option value="above">Above</option>
                  <option value="below">Below</option>
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: '0.8rem', marginBottom: '4px', color: '#aaa' }}>Price Target</label>
                <input
                  type="number"
                  placeholder="0.00"
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  style={{ width: '100%', boxSizing: 'border-box' }}
                  required
                />
              </div>
            </div>

            <button type="submit" className="primary-btn">
              Set Alert
            </button>
          </form>
        </section>
      </div>

      {/* Bottom Section: Notifications Log */}
      <section className="card">
        <h2>Alert Logs</h2>
        {notifications.length === 0 ? (
           <div style={{ padding: '1rem', textAlign: 'center', color: '#555' }}>No alerts triggered yet.</div>
        ) : (
          <ul className="notification-list">
            {notifications.map((n) => (
              <li key={n.id} className="notification-item">
                <span>
                  <strong style={{ color: '#4caf50' }}>{n.symbol}</strong> went {n.direction} <span style={{color: '#fff'}}>${n.threshold}</span> 
                  <span style={{ marginLeft: '8px', color: '#ccc', fontSize: '0.85em' }}>(Triggered at ${n.price})</span>
                </span>
                <span className="time-badge">{formatDate(n.triggered_at)}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;