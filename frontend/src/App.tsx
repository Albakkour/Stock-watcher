import React, { useEffect, useState, useCallback } from "react";
import { Stock, Alert, Notification, APIResponse } from "./types";
import { StockCard } from "./components/StockCard";
import { AlertForm } from "./components/AlertForm";
import { NotificationLog } from "./components/NotificationLog";
import { AlertList } from "./components/AlertList";
import { RefreshCw, Trash2, Zap, WifiOff } from "lucide-react";
// import { mockAlerts, mockNotifications } from "./mockData";

const API_BASE = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  // Form State
  const [symbol, setSymbol] = useState("TSLA");
  const [direction, setDirection] = useState("above");
  const [threshold, setThreshold] = useState<number | string>(200);

  // Status for polling indicator
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isOffline, setIsOffline] = useState(false);

  const fetchStocks = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/stocks`);
      if (!res.ok) throw new Error("API Error");
      const data: APIResponse<Stock[]> = await res.json();
      
      // Only show stocks if we got real data
      if (data.stocks && data.stocks.length > 0) {
        setStocks(data.stocks);
        setIsOffline(false);
      } else {
        // No data yet, show empty state
        setStocks([]);
        setIsOffline(true);
      }
    } catch (e) {
      console.warn("Backend unreachable or no stock data yet.");
      setIsOffline(true);
      setStocks([]);  // Don't show mock data
    } finally {
      setLastUpdated(new Date());
    }
  }, []);

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/alerts`);
      if (!res.ok) throw new Error("API Error");
      const data: APIResponse<Alert[]> = await res.json();
      setAlerts(data.alerts || []);
    } catch (e) {
      console.warn("Failed to fetch alerts");
      setAlerts([]);
    }
  }, []);

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/notifications`);
      if (!res.ok) throw new Error("API Error");
      const data: APIResponse<Notification[]> = await res.json();
      setNotifications(data.notifications || []);
    } catch (e) {
      console.warn("Failed to fetch notifications");
      setNotifications([]);
    }
  }, []);

  const createAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol || !threshold) return;

    if (isOffline) {
      alert("Backend is offline. Cannot create alert.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/alerts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, direction, threshold: Number(threshold) }),
      });
      
      if (!res.ok) throw new Error("Failed to create alert");
      
      await fetchAlerts();
      setSymbol("");
      setThreshold(""); 
    } catch (error) {
      console.error("Error creating alert", error);
      alert("Failed to create alert");
    }
  };

  const resetSystem = async () => {
    const confirmed = window.confirm(
      "DANGER ZONE\n\nAre you sure? This will delete ALL stocks, alerts, and notifications history."
    );
    
    if (!confirmed) return;

    if (isOffline) {
      alert("Backend is offline. Cannot reset.");
      return;
    }

    try {
      await fetch(`${API_BASE}/api/reset`, { method: "DELETE" });
      setStocks([]);
      setAlerts([]);
      setNotifications([]);
    } catch (e) {
      console.error("Failed to reset system", e);
    }
  };

  useEffect(() => {
    fetchStocks();
    fetchAlerts();
    fetchNotifications();

    const id = setInterval(() => {
      fetchStocks();
      fetchNotifications();
    }, 5000);

    return () => clearInterval(id);
  }, [fetchStocks, fetchAlerts, fetchNotifications]);

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <div className="main-container">
          <div className="header-content">
            <div className="brand">
              <div className="brand-icon">
                <Zap size={28} />
              </div>
              <h1>Cloud <span>Stock</span> Watcher</h1>
            </div>

            <div className="header-actions">
              {isOffline && (
                <div className="status-badge">
                  <WifiOff size={14} />
                  <span>Offline</span>
                </div>
              )}
              <div className="update-info">
                <RefreshCw size={12} className={!isOffline ? "spin" : ""} /> 
                Updated: {lastUpdated.toLocaleTimeString()}
              </div>
              <button onClick={resetSystem} className="btn-danger">
                <Trash2 size={16} />
                <span>Reset System</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="main-container">
        
        <section>
          <div className="section-title">
            <h2>Live Markets</h2>
            <span className="section-tag">Real-time Feed</span>
          </div>
          
          {isOffline ? (
             <div className="card" style={{ textAlign: 'center', borderStyle: 'dashed', color: 'var(--text-muted)', padding: '2rem' }}>
                <p>⏳ Waiting for stock data...</p>
                <p style={{ fontSize: '0.9rem' }}>Make sure stock-generator is running and publishing prices to Redis.</p>
             </div>
          ) : stocks.length === 0 ? (
             <div className="card" style={{ textAlign: 'center', borderStyle: 'dashed', color: 'var(--text-muted)', padding: '2rem' }}>
                <p>No stock data available.</p>
             </div>
          ) : (
            <div className="stocks-grid">
              {stocks.map((s) => (
                <StockCard key={s.symbol} stock={s} />
              ))}
            </div>
          )}
        </section>

        <section className="control-grid">
          <div>
            <AlertForm 
              symbol={symbol}
              setSymbol={setSymbol}
              direction={direction}
              setDirection={setDirection}
              threshold={threshold}
              setThreshold={setThreshold}
              onSubmit={createAlert}
            />
          </div>
          <div>
            <AlertList alerts={alerts} />
          </div>
        </section>

        <section>
          <NotificationLog notifications={notifications} />
        </section>

      </main>
    </div>
  );
}

export default App;