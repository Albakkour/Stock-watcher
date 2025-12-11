# from flask import Flask, request, jsonify, Response
# import threading, time, random, requests, collections, os

# # Config
# BASE_URL = os.environ.get("WORKLOAD_BASE_URL", "http://129.192.82.232:30081")
# DEFAULT_RPS = float(os.environ.get("WORKLOAD_DEFAULT_RPS", "1.0"))
# PORT = int(os.environ.get("WORKLOAD_API_PORT", "9000"))

# app = Flask(__name__, static_folder=None)

# # Shared state
# state = {
#     "rps": DEFAULT_RPS,
#     "running": False,
#     "success": 0,
#     "fail": 0,
#     "latencies": collections.deque(maxlen=1000),
#     "last_error": None,
# }

# lock = threading.Lock()

# def worker_loop():
#     while True:
#         with lock:
#             running = state["running"]
#             rps = state["rps"]
#         if not running:
#             time.sleep(0.2)
#             continue

#         interval = 1.0 / max(rps, 0.0001)
#         start = time.time()
#         try:
#             # choose endpoint
#             choice = random.random()
#             if choice < 0.5:
#                 resp = requests.get(f"{BASE_URL}/api/stocks", timeout=5)
#                 resp.raise_for_status()
#             elif choice < 0.8:
#                 resp = requests.get(f"{BASE_URL}/api/notifications", timeout=5)
#                 resp.raise_for_status()
#             else:
#                 body = {
#                     "symbol": random.choice(["TSLA", "AAPL", "MSFT"]),
#                     "direction": random.choice(["above", "below"]),
#                     "threshold": round(random.uniform(150, 250), 2),
#                 }
#                 resp = requests.post(f"{BASE_URL}/api/alerts", json=body, timeout=5)
#                 resp.raise_for_status()

#             latency = time.time() - start
#             with lock:
#                 state["success"] += 1
#                 state["latencies"].append(latency)
#         except Exception as e:
#             with lock:
#                 state["fail"] += 1
#                 state["last_error"] = str(e)

#         time.sleep(interval)

# # start background thread
# t = threading.Thread(target=worker_loop, daemon=True)
# t.start()

# # ---------------- API endpoints ----------------

# @app.route("/set_rps", methods=["POST"])
# def set_rps():
#     payload = request.get_json(force=True, silent=True) or {}
#     try:
#         new_rps = float(payload.get("rps", DEFAULT_RPS))
#         if new_rps < 0:
#             raise ValueError("rps must be >= 0")
#     except Exception as e:
#         return jsonify({"error": "invalid rps", "detail": str(e)}), 400
#     with lock:
#         state["rps"] = new_rps
#     return jsonify({"rps": state["rps"]})

# @app.route("/start", methods=["POST"])
# def start_load():
#     with lock:
#         state["running"] = True
#     return jsonify({"status": "started", "rps": state["rps"]})

# @app.route("/stop", methods=["POST"])
# def stop_load():
#     with lock:
#         state["running"] = False
#     return jsonify({"status": "stopped"})

# @app.route("/stats", methods=["GET"])
# def stats():
#     with lock:
#         lat_list = list(state["latencies"])
#         avg_latency = sum(lat_list) / len(lat_list) if lat_list else None
#         last_error = state["last_error"]
#         out = {
#             "rps": state["rps"],
#             "running": state["running"],
#             "success": state["success"],
#             "fail": state["fail"],
#             "avg_latency_sec": avg_latency,
#             "last_error": last_error
#         }
#     return jsonify(out)

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"ok": True})

# # ---------------- Modern React UI ----------------

# _UI_HTML = """
# <!doctype html>
# <html lang="en">
# <head>
#     <meta charset="utf-8"/>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Workload Controller</title>
#     <script src="https://cdn.tailwindcss.com"></script>
#     <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
#     <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
#     <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
#     <style>
#         body { background-color: #0f172a; color: #e2e8f0; }
#         .card { background-color: #1e293b; border-radius: 0.75rem; border: 1px solid #334155; }
#         .btn { transition: all 0.2s; }
#         .btn:active { transform: scale(0.95); }
#     </style>
# </head>
# <body class="antialiased min-h-screen flex flex-col items-center py-10">

#     <div id="root" class="w-full max-w-4xl px-4"></div>

#     <script type="text/babel">
#         const { useState, useEffect } = React;

#         const App = () => {
#             const [stats, setStats] = useState({
#                 rps: 1,
#                 running: false,
#                 success: 0,
#                 fail: 0,
#                 avg_latency_sec: null,
#                 last_error: null
#             });
#             const [rpsInput, setRpsInput] = useState(1);
#             const [baseUrl, setBaseUrl] = useState("");

#             useEffect(() => {
#                 setBaseUrl(window.location.origin);
#                 fetchStats();
#                 const interval = setInterval(fetchStats, 1000);
#                 return () => clearInterval(interval);
#             }, []);

#             // Sync input with stats when stats load for the first time
#             useEffect(() => {
#                 // simple check to update input if it hasn't been touched much
#                 // or just to init it.
#                 if (Math.abs(stats.rps - rpsInput) > 0.1) {
#                    // Optional: keep them synced or let user drift. 
#                    // Let's rely on manual set.
#                 }
#             }, [stats.rps]);

#             const fetchStats = async () => {
#                 try {
#                     const res = await fetch('/stats');
#                     const data = await res.json();
#                     setStats(data);
#                 } catch (e) {
#                     console.error(e);
#                 }
#             };

#             const handleSetRps = async () => {
#                 await fetch('/set_rps', {
#                     method: 'POST',
#                     headers: {'Content-Type': 'application/json'},
#                     body: JSON.stringify({ rps: parseFloat(rpsInput) })
#                 });
#                 fetchStats();
#             };

#             const toggleRun = async () => {
#                 const endpoint = stats.running ? '/stop' : '/start';
#                 await fetch(endpoint, { method: 'POST' });
#                 fetchStats();
#             };

#             const formatLatency = (val) => {
#                 if (val === null || val === undefined) return "N/A";
#                 // Convert to ms if < 1s, else keep s
#                 if (val < 1) return (val * 1000).toFixed(1) + " ms";
#                 return val.toFixed(3) + " s";
#             };

#             return (
#                 <div className="space-y-6">
#                     {/* Header */}
#                     <div className="flex justify-between items-center pb-4 border-b border-gray-700">
#                         <div>
#                             <h1 className="text-3xl font-bold text-white tracking-tight">Cloud Workload Gen</h1>
#                             <p className="text-gray-400 text-sm mt-1 font-mono">{baseUrl}</p>
#                         </div>
#                         <div className="flex items-center space-x-3">
#                             <span className={`h-3 w-3 rounded-full ${stats.running ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
#                             <span className="font-semibold uppercase text-sm tracking-wider">
#                                 {stats.running ? 'Running' : 'Stopped'}
#                             </span>
#                         </div>
#                     </div>

#                     {/* Controls */}
#                     <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        
#                         {/* RPS Control */}
#                         <div className="card p-6 flex flex-col justify-between">
#                             <label className="text-gray-400 text-sm font-semibold uppercase mb-2">Target Load (RPS)</label>
#                             <div className="flex space-x-2">
#                                 <input 
#                                     type="number" 
#                                     min="0" 
#                                     step="0.1"
#                                     value={rpsInput}
#                                     onChange={(e) => setRpsInput(e.target.value)}
#                                     className="flex-1 bg-gray-800 border border-gray-600 text-white px-4 py-2 rounded focus:outline-none focus:border-blue-500 font-mono text-lg"
#                                 />
#                                 <button 
#                                     onClick={handleSetRps}
#                                     className="btn bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-6 rounded"
#                                 >
#                                     Set
#                                 </button>
#                             </div>
#                             <div className="mt-2 text-xs text-gray-500">Current Config: {stats.rps} RPS</div>
#                         </div>

#                         {/* Power Button */}
#                         <div className="card p-6 flex items-center justify-center">
#                             <button 
#                                 onClick={toggleRun}
#                                 className={`btn w-full h-full py-4 text-xl font-bold rounded shadow-lg uppercase tracking-widest ${
#                                     stats.running 
#                                     ? 'bg-red-600 hover:bg-red-500 text-white border border-red-700' 
#                                     : 'bg-emerald-600 hover:bg-emerald-500 text-white border border-emerald-700'
#                                 }`}
#                             >
#                                 {stats.running ? 'Stop Generator' : 'Start Generator'}
#                             </button>
#                         </div>
#                     </div>

#                     {/* Stats Grid */}
#                     <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
#                         <div className="card p-6 text-center">
#                             <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-1">Successful Requests</div>
#                             <div className="text-4xl font-mono text-emerald-400">{stats.success}</div>
#                         </div>
#                         <div className="card p-6 text-center">
#                             <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-1">Failed Requests</div>
#                             <div className="text-4xl font-mono text-red-400">{stats.fail}</div>
#                         </div>
#                         <div className="card p-6 text-center">
#                             <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-1">Avg Latency</div>
#                             <div className="text-4xl font-mono text-yellow-400">{formatLatency(stats.avg_latency_sec)}</div>
#                         </div>
#                     </div>

#                     {/* Error Log */}
#                     <div className="card p-6">
#                         <div className="text-gray-400 text-xs uppercase font-bold tracking-wider mb-3">Last System Error</div>
#                         <div className="bg-black rounded p-4 font-mono text-sm text-red-300 min-h-[80px] overflow-auto border border-gray-800">
#                             {stats.last_error ? `> ${stats.last_error}` : '> No errors logged.'}
#                         </div>
#                     </div>
#                 </div>
#             );
#         };

#         const root = ReactDOM.createRoot(document.getElementById('root'));
#         root.render(<App />);
#     </script>
# </body>
# </html>
# """

# @app.route("/ui", methods=["GET"])
# def ui():
#     return Response(_UI_HTML, mimetype="text/html")

# if __name__ == "__main__":
#     print("Workload API base:", BASE_URL)
#     app.run(host="0.0.0.0", port=PORT)
# PY

#!/usr/bin/env python3
"""
Modernized workload-api.py

Endpoints:
  GET  /ui
  GET  /health
  POST /start
  POST /stop
  POST /set_rps    JSON {"rps": <number>}
  GET  /stats
  GET  /metrics    -> JSON with kubectl top pod values for namespace cloud-stock-watcher

Notes:
- Uses a background worker thread to generate traffic.
- Uses requests.Session with retries for stability.
- UI is modern and orange-themed; Chart.js used for CPU chart.
"""
from __future__ import annotations

import collections
import dataclasses
import json
import logging
import os
import random
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Deque, Dict, List, Optional

import requests
from flask import Flask, Response, jsonify, request

# ---------------- Configuration ----------------
BASE_URL = os.environ.get("WORKLOAD_BASE_URL", "http://129.192.82.232:30081")
DEFAULT_RPS = float(os.environ.get("WORKLOAD_DEFAULT_RPS", "1.0"))
PORT = int(os.environ.get("WORKLOAD_API_PORT", "9000"))
K8S_NAMESPACE = os.environ.get("K8S_NAMESPACE", "cloud-stock-watcher")
LATENCY_HISTORY = int(os.environ.get("WORKLOAD_LATENCY_HISTORY", "2000"))
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("WORKLOAD_REQ_TIMEOUT", "5.0"))
WORKER_SLEEP_WHEN_STOPPED = float(os.environ.get("WORKLOAD_SLEEP_STOPPED", "0.25"))

# ---------------- Logging ----------------
logging.basicConfig(
    level=os.environ.get("WORKLOAD_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("workload-api")

# ---------------- HTTP session with retries ----------------
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=0.3, status_forcelist=(429, 500, 502, 503, 504))
_adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)


# ---------------- State dataclass ----------------
@dataclasses.dataclass
class State:
    rps: float = DEFAULT_RPS
    running: bool = False
    success: int = 0
    fail: int = 0
    latencies: Deque[float] = dataclasses.field(default_factory=lambda: collections.deque(maxlen=LATENCY_HISTORY))
    last_error: Optional[str] = None


state = State()
_state_lock = threading.Lock()

# Use an event to signal worker to run/stop gracefully
_worker_should_run = threading.Event()
_worker_should_stop = threading.Event()

# small executor for future parallel work (keeps design flexible)
_executor = ThreadPoolExecutor(max_workers=4)

# ---------------- Worker implementation ----------------
def _make_choice_and_call() -> None:
    """Perform one request cycle: GET /api/stocks, GET /api/notifications or POST /api/alerts"""
    now = time.time()
    try:
        choice = random.random()
        if choice < 0.5:
            resp = _session.get(f"{BASE_URL}/api/stocks", timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
        elif choice < 0.8:
            resp = _session.get(f"{BASE_URL}/api/notifications", timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
        else:
            body = {
                "symbol": random.choice(["TSLA", "AAPL", "MSFT", "GOOG"]),
                "direction": random.choice(["above", "below"]),
                "threshold": round(random.uniform(120, 260), 2),
            }
            resp = _session.post(f"{BASE_URL}/api/alerts", json=body, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()

        latency = time.time() - now
        with _state_lock:
            state.success += 1
            state.latencies.append(latency)
    except Exception as exc:
        with _state_lock:
            state.fail += 1
            state.last_error = f"{type(exc).__name__}: {str(exc)}"
        logger.debug("Request failed: %s", exc)


def worker_loop() -> None:
    logger.info("Worker thread starting")
    while not _worker_should_stop.is_set():
        if not _worker_should_run.is_set():
            time.sleep(WORKER_SLEEP_WHEN_STOPPED)
            continue

        with _state_lock:
            rps = max(0.0, state.rps)

        # calculate interval per request; allow fractional rps
        interval = 1.0 / (rps if rps > 0 else 1.0)
        start = time.time()
        # perform one request (synchronous). This keeps behavior identical to original but with cleaner control.
        _make_choice_and_call()
        elapsed = time.time() - start
        # sleep remaining time of interval (don't sleep negative)
        to_sleep = max(0.0, interval - elapsed)
        time.sleep(to_sleep)

    logger.info("Worker thread stopping")


_worker_thread = threading.Thread(target=worker_loop, daemon=True)
_worker_thread.start()

# ---------------- Flask app ----------------
app = Flask(__name__)


@app.route("/set_rps", methods=["POST"])
def set_rps():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        new_rps = float(payload.get("rps", DEFAULT_RPS))
        if new_rps < 0:
            raise ValueError("rps must be >= 0")
    except Exception as exc:
        logger.warning("Invalid rps payload: %s (%s)", payload, exc)
        return jsonify({"error": "invalid rps", "detail": str(exc)}), 400

    with _state_lock:
        state.rps = new_rps
    logger.info("RPS set to %.3f", new_rps)
    return jsonify({"rps": state.rps})


@app.route("/start", methods=["POST"])
def start_load():
    with _state_lock:
        state.running = True
    _worker_should_run.set()
    logger.info("Load started (rps=%.3f)", state.rps)
    return jsonify({"status": "started", "rps": state.rps})


@app.route("/stop", methods=["POST"])
def stop_load():
    with _state_lock:
        state.running = False
    _worker_should_run.clear()
    logger.info("Load stopped")
    return jsonify({"status": "stopped"})


@app.route("/stats", methods=["GET"])
def stats():
    with _state_lock:
        lat_list = list(state.latencies)
        avg_latency = sum(lat_list) / len(lat_list) if lat_list else None
        out = {
            "rps": state.rps,
            "running": state.running,
            "success": state.success,
            "fail": state.fail,
            "avg_latency_sec": round(avg_latency, 6) if avg_latency is not None else None,
            "last_error": state.last_error,
        }
    return jsonify(out)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


# ---------------- kubectl parsing / metrics ----------------
def parse_kubectl_top_output(text: str) -> List[Dict]:
    """
    Parse `kubectl top pod -n <ns> --no-headers` output into list of dicts.
    Tolerant to extra columns and to CPU units like "12m", "0", "1", "250m".
    """
    pods = []
    for raw in filter(None, (line.strip() for line in text.splitlines())):
        parts = raw.split()
        if len(parts) < 3:
            continue
        name = parts[0]
        cpu_raw = parts[1]
        mem_raw = parts[2]
        cpu_m = None
        try:
            if cpu_raw.endswith("m"):
                cpu_m = int(cpu_raw[:-1])
            else:
                # could be "0" or "1" or "0.5"
                cpu_m = int(float(cpu_raw) * 1000)
        except Exception:
            cpu_m = None
        pods.append({"name": name, "cpu_m": cpu_m, "cpu_raw": cpu_raw, "mem_raw": mem_raw})
    return pods


@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        cmd = ["kubectl", "top", "pod", "-n", K8S_NAMESPACE, "--no-headers"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if proc.returncode != 0:
            logger.warning("kubectl top failed: %s", proc.stderr.strip())
            return jsonify({"error": "kubectl top failed", "detail": proc.stderr.strip()}), 500
        pods = parse_kubectl_top_output(proc.stdout)
        return jsonify({"namespace": K8S_NAMESPACE, "pods": pods})
    except Exception as exc:
        logger.exception("Exception while running kubectl")
        return jsonify({"error": "exception", "detail": str(exc)}), 500


# ---------------- UI (orange, modern) ----------------
_UI_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Workload Controller • Cloud Stock Watcher</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>
    :root{
      --bg:#ff8a00; /* modern orange */
      --card:#ffffff;
      --muted: rgba(0,0,0,0.55);
      --glass: rgba(255,255,255,0.12);
      --accent: rgba(0,0,0,0.08);
      --radius: 12px;
    }
    html,body { height:100%; margin:0; font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background: linear-gradient(135deg,var(--bg), #ffae33); color:#111; }
    .container{ max-width:1100px; margin:32px auto; padding:20px; }
    header { display:flex; align-items:center; gap:16px; margin-bottom:18px; }
    .logo { width:56px; height:56px; border-radius:12px; background:rgba(255,255,255,0.15); display:flex; align-items:center; justify-content:center; font-weight:700; color:#fff; box-shadow:0 6px 20px rgba(0,0,0,0.12); }
    h1{ margin:0; font-size:20px; color:#fff; font-weight:600;}
    .grid { display:grid; gap:18px; grid-template-columns: 360px 1fr; align-items:start; }

    .card { background: var(--card); border-radius: var(--radius); padding:16px; box-shadow: 0 6px 18px rgba(16,24,40,0.08); }
    .control-row { display:flex; gap:8px; align-items:center; margin-bottom:10px; }
    label.small { font-size:13px; color:var(--muted); width:72px; }
    input[type=number] { padding:8px 10px; border-radius:8px; border:1px solid #e6e6e6; width:120px; font-weight:600; }
    button { padding:8px 12px; border-radius:10px; border: none; font-weight:600; cursor:pointer; }
    .btn-primary { background: #ff6f00; color: #fff; box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
    .btn-ghost { background: transparent; color: #333; border:1px solid #eee; }
    .stat { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px dashed #f0f0f0; }
    .stat:last-child { border-bottom: none; }
    pre.err { background:#fff6f0; padding:10px; border-radius:8px; color:#7a1f00; margin:8px 0 0; white-space:pre-wrap; font-size:13px; }

    .chart-wrap { padding:8px; }
    .meta { font-size:13px; color:var(--muted); margin-top:8px; }

    @media (max-width:880px){
      .grid { grid-template-columns: 1fr; }
    }

  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">WS</div>
      <div>
        <h1>Workload Controller — Cloud Stock Watcher</h1>
        <div style="color:rgba(255,255,255,0.95); font-size:13px;">Control test traffic, inspect stats and pod CPU usage</div>
      </div>
    </header>

    <div class="grid">
      <div class="card" id="controls">
        <div class="control-row"><label class="small">Base URL</label><div id="baseUrl"></div></div>

        <div class="control-row">
          <label class="small">RPS</label>
          <input id="rps" type="number" min="0" step="0.1" value="1"/>
          <button class="btn-primary" id="btnSet">Set</button>
        </div>

        <div class="control-row">
          <label class="small">Control</label>
          <button class="btn-primary" id="btnStart">Start</button>
          <button class="btn-ghost" id="btnStop">Stop</button>
        </div>

        <hr style="border:none;margin:12px 0;border-top:1px solid #f3f3f3"/>

        <div class="stat"><div style="color:var(--muted)">Running</div><div id="running">false</div></div>
        <div class="stat"><div style="color:var(--muted)">Success</div><div id="success">0</div></div>
        <div class="stat"><div style="color:var(--muted)">Fail</div><div id="fail">0</div></div>
        <div class="stat"><div style="color:var(--muted)">Avg latency</div><div id="avg">N/A</div></div>

        <div style="margin-top:12px">
          <div style="color:var(--muted); font-size:13px;">Last error</div>
          <pre class="err" id="err">-</pre>
        </div>
      </div>

      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div><strong>CPU usage (millicores)</strong><div class="meta">Chart refreshes every 2s — 1000m = 1 CPU core</div></div>
          <div style="font-size:13px;color:var(--muted)">Namespace: <strong>{ns}</strong></div>
        </div>
        <div class="chart-wrap">
          <canvas id="cpuChart" height="120"></canvas>
        </div>
      </div>
    </div>
  </div>

<script>
  const base = window.location.origin;
  document.getElementById('baseUrl').innerText = base;
  // replace placeholder namespace in UI
  document.body.innerHTML = document.body.innerHTML.replace("{ns}", "{k8s}");

  async function fetchStats(){
    try{
      const res = await fetch(base + '/stats');
      const j = await res.json();
      document.getElementById('running').innerText = j.running;
      document.getElementById('success').innerText = j.success;
      document.getElementById('fail').innerText = j.fail;
      document.getElementById('avg').innerText = j.avg_latency_sec !== null ? j.avg_latency_sec.toFixed(3) + 's' : 'N/A';
      document.getElementById('err').innerText = j.last_error || '-';
      document.getElementById('rps').value = j.rps;
    }catch(e){
      console.warn('stats fetch error', e);
    }
  }

  document.getElementById('btnSet').addEventListener('click', async ()=>{
    const v = Number(document.getElementById('rps').value);
    await fetch(base + '/set_rps', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({rps: v})});
    await fetchStats();
  });

  document.getElementById('btnStart').addEventListener('click', async ()=>{
    await fetch(base + '/start', {method:'POST'});
    await fetchStats();
  });

  document.getElementById('btnStop').addEventListener('click', async ()=>{
    await fetch(base + '/stop', {method:'POST'});
    await fetchStats();
  });

  // Chart setup
  const ctx = document.getElementById('cpuChart').getContext('2d');
  const cpuChart = new Chart(ctx, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'CPU (m)', data: [], backgroundColor: 'rgba(0,0,0,0.12)' }] },
    options: {
      responsive: true,
      animation: false,
      scales: { y: { beginAtZero: true } }
    }
  });

  async function fetchMetricsAndUpdateChart(){
    try{
      const res = await fetch(base + '/metrics');
      const j = await res.json();
      if (j.error) {
        console.warn('metrics error', j);
        return;
      }
      const names = j.pods.map(p => p.name);
      const cpus = j.pods.map(p => p.cpu_m === null ? 0 : p.cpu_m);
      cpuChart.data.labels = names;
      cpuChart.data.datasets[0].data = cpus;
      cpuChart.update();
    }catch(e){
      console.warn('metrics fetch error', e);
    }
  }

  setInterval(fetchStats, 1000);
  setInterval(fetchMetricsAndUpdateChart, 2000);
  fetchStats();
  fetchMetricsAndUpdateChart();
</script>
</body>
</html>
""".replace("{k8s}", K8S_NAMESPACE)

@app.route("/ui", methods=["GET"])
def ui():
    return Response(_UI_HTML, mimetype="text/html")


# ---------------- Graceful shutdown helper (optional) ----------------
def _shutdown_worker():
    logger.info("Shutdown requested")
    _worker_should_stop.set()
    _worker_should_run.set()  # wake it if sleeping
    _worker_thread.join(timeout=2)
    _executor.shutdown(wait=False)
    logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        logger.info("Starting Workload API (base=%s) on 0.0.0.0:%d", BASE_URL, PORT)
        # If you want the worker to be running by default, uncomment the next two lines:
        # with _state_lock:
        #     state.running = True; _worker_should_run.set()
        app.run(host="0.0.0.0", port=PORT)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        _shutdown_worker()
