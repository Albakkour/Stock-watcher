
from flask import Flask, request, jsonify, Response
import threading, time, random, requests, collections, os

# Config
BASE_URL = os.environ.get("WORKLOAD_BASE_URL", "http://129.192.82.232:30081")
DEFAULT_RPS = float(os.environ.get("WORKLOAD_DEFAULT_RPS", "1.0"))
PORT = int(os.environ.get("WORKLOAD_API_PORT", "9000"))

app = Flask(__name__, static_folder=None)

# Shared state
state = {
    "rps": DEFAULT_RPS,
    "running": False,
    "success": 0,
    "fail": 0,
    "latencies": collections.deque(maxlen=1000),
    "last_error": None,
}

lock = threading.Lock()

def worker_loop():
    while True:
        with lock:
            running = state["running"]
            rps = state["rps"]
        if not running:
            time.sleep(0.2)
            continue

        interval = 1.0 / max(rps, 0.0001)
        start = time.time()
        try:
            # choose endpoint
            choice = random.random()
            if choice < 0.5:
                resp = requests.get(f"{BASE_URL}/api/stocks", timeout=5)
                resp.raise_for_status()
            elif choice < 0.8:
                resp = requests.get(f"{BASE_URL}/api/notifications", timeout=5)
                resp.raise_for_status()
            else:
                body = {
                    "symbol": random.choice(["TSLA", "AAPL", "MSFT"]),
                    "direction": random.choice(["above", "below"]),
                    "threshold": round(random.uniform(150, 250), 2),
                }
                resp = requests.post(f"{BASE_URL}/api/alerts", json=body, timeout=5)
                resp.raise_for_status()

            latency = time.time() - start
            with lock:
                state["success"] += 1
                state["latencies"].append(latency)
        except Exception as e:
            with lock:
                state["fail"] += 1
                state["last_error"] = str(e)

        time.sleep(interval)

# start background thread
t = threading.Thread(target=worker_loop, daemon=True)
t.start()

# ---------------- API endpoints ----------------

@app.route("/set_rps", methods=["POST"])
def set_rps():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        new_rps = float(payload.get("rps", DEFAULT_RPS))
        if new_rps < 0:
            raise ValueError("rps must be >= 0")
    except Exception as e:
        return jsonify({"error": "invalid rps", "detail": str(e)}), 400
    with lock:
        state["rps"] = new_rps
    return jsonify({"rps": state["rps"]})

@app.route("/start", methods=["POST"])
def start_load():
    with lock:
        state["running"] = True
    return jsonify({"status": "started", "rps": state["rps"]})

@app.route("/stop", methods=["POST"])
def stop_load():
    with lock:
        state["running"] = False
    return jsonify({"status": "stopped"})

@app.route("/stats", methods=["GET"])
def stats():
    with lock:
        lat_list = list(state["latencies"])
        avg_latency = sum(lat_list) / len(lat_list) if lat_list else None
        last_error = state["last_error"]
        out = {
            "rps": state["rps"],
            "running": state["running"],
            "success": state["success"],
            "fail": state["fail"],
            "avg_latency_sec": avg_latency,
            "last_error": last_error
        }
    return jsonify(out)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# ---------------- Modern React UI ----------------

_UI_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workload Controller</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
    <style>
        body { background-color: #0f172a; color: #e2e8f0; }
        .card { background-color: #1e293b; border-radius: 0.75rem; border: 1px solid #334155; }
        .btn { transition: all 0.2s; }
        .btn:active { transform: scale(0.95); }
    </style>
</head>
<body class="antialiased min-h-screen flex flex-col items-center py-10">

    <div id="root" class="w-full max-w-4xl px-4"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        const App = () => {
            const [stats, setStats] = useState({
                rps: 1,
                running: false,
                success: 0,
                fail: 0,
                avg_latency_sec: null,
                last_error: null
            });
            const [rpsInput, setRpsInput] = useState(1);
            const [baseUrl, setBaseUrl] = useState("");

            useEffect(() => {
                setBaseUrl(window.location.origin);
                fetchStats();
                const interval = setInterval(fetchStats, 1000);
                return () => clearInterval(interval);
            }, []);

            // Sync input with stats when stats load for the first time
            useEffect(() => {
                // simple check to update input if it hasn't been touched much
                // or just to init it.
                if (Math.abs(stats.rps - rpsInput) > 0.1) {
                   // Optional: keep them synced or let user drift. 
                   // Let's rely on manual set.
                }
            }, [stats.rps]);

            const fetchStats = async () => {
                try {
                    const res = await fetch('/stats');
                    const data = await res.json();
                    setStats(data);
                } catch (e) {
                    console.error(e);
                }
            };

            const handleSetRps = async () => {
                await fetch('/set_rps', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ rps: parseFloat(rpsInput) })
                });
                fetchStats();
            };

            const toggleRun = async () => {
                const endpoint = stats.running ? '/stop' : '/start';
                await fetch(endpoint, { method: 'POST' });
                fetchStats();
            };

            const formatLatency = (val) => {
                if (val === null || val === undefined) return "N/A";
                // Convert to ms if < 1s, else keep s
                if (val < 1) return (val * 1000).toFixed(1) + " ms";
                return val.toFixed(3) + " s";
            };

            return (
                <div className="space-y-6">
                    {/* Header */}
                    <div className="flex justify-between items-center pb-4 border-b border-gray-700">
                        <div>
                            <h1 className="text-3xl font-bold text-white tracking-tight">Cloud Workload Gen</h1>
                            <p className="text-gray-400 text-sm mt-1 font-mono">{baseUrl}</p>
                        </div>
                        <div className="flex items-center space-x-3">
                            <span className={`h-3 w-3 rounded-full ${stats.running ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
                            <span className="font-semibold uppercase text-sm tracking-wider">
                                {stats.running ? 'Running' : 'Stopped'}
                            </span>
                        </div>
                    </div>

                    {/* Controls */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        
                        {/* RPS Control */}
                        <div className="card p-6 flex flex-col justify-between">
                            <label className="text-gray-400 text-sm font-semibold uppercase mb-2">Target Load (RPS)</label>
                            <div className="flex space-x-2">
                                <input 
                                    type="number" 
                                    min="0" 
                                    step="0.1"
                                    value={rpsInput}
                                    onChange={(e) => setRpsInput(e.target.value)}
                                    className="flex-1 bg-gray-800 border border-gray-600 text-white px-4 py-2 rounded focus:outline-none focus:border-blue-500 font-mono text-lg"
                                />
                                <button 
                                    onClick={handleSetRps}
                                    className="btn bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-6 rounded"
                                >
                                    Set
                                </button>
                            </div>
                            <div className="mt-2 text-xs text-gray-500">Current Config: {stats.rps} RPS</div>
                        </div>

                        {/* Power Button */}
                        <div className="card p-6 flex items-center justify-center">
                            <button 
                                onClick={toggleRun}
                                className={`btn w-full h-full py-4 text-xl font-bold rounded shadow-lg uppercase tracking-widest ${
                                    stats.running 
                                    ? 'bg-red-600 hover:bg-red-500 text-white border border-red-700' 
                                    : 'bg-emerald-600 hover:bg-emerald-500 text-white border border-emerald-700'
                                }`}
                            >
                                {stats.running ? 'Stop Generator' : 'Start Generator'}
                            </button>
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="card p-6 text-center">
                            <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-1">Successful Requests</div>
                            <div className="text-4xl font-mono text-emerald-400">{stats.success}</div>
                        </div>
                        <div className="card p-6 text-center">
                            <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-1">Failed Requests</div>
                            <div className="text-4xl font-mono text-red-400">{stats.fail}</div>
                        </div>
                        <div className="card p-6 text-center">
                            <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-1">Avg Latency</div>
                            <div className="text-4xl font-mono text-yellow-400">{formatLatency(stats.avg_latency_sec)}</div>
                        </div>
                    </div>

                    {/* Error Log */}
                    <div className="card p-6">
                        <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-3">Last System Error</div>
                        <div className="bg-black rounded p-4 font-mono text-sm text-red-300 min-h-[80px] overflow-auto border border-gray-800">
                            {stats.last_error ? `> ${stats.last_error}` : '> No errors logged.'}
                        </div>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

@app.route("/ui", methods=["GET"])
def ui():
    return Response(_UI_HTML, mimetype="text/html")

if __name__ == "__main__":
    print("Workload API base:", BASE_URL)
    app.run(host="0.0.0.0", port=PORT)
PY