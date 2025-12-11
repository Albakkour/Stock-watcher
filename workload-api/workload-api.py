
#!/usr/bin/env python3
from flask import Flask, request, jsonify, Response
import threading, time, random, requests, collections, os, html

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

# ---------------- Simple Web UI ----------------

_UI_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Workload Controller</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 1rem; }
    .row { margin-bottom: 0.5rem; }
    label { display:inline-block; width: 90px; }
    input[type=number] { width: 120px; }
    button { margin-left: 0.5rem; }
    pre { background:#f6f8fa; padding:10px; border-radius:6px; }
  </style>
</head>
<body>
  <h2>Workload Controller</h2>

  <div class="row">
    <label>Base URL</label>
    <span id="baseUrl"></span>
  </div>

  <div class="row">
    <label>RPS</label>
    <input id="rps" type="number" value="1" step="0.5" min="0"/>
    <button id="btnSet">Set RPS</button>
  </div>

  <div class="row">
    <button id="btnStart">Start</button>
    <button id="btnStop">Stop</button>
  </div>

  <div class="row">
    <label>Running</label>
    <span id="running">false</span>
  </div>

  <h3>Stats</h3>
  <div class="row">
    <label>Success</label><span id="success">0</span>
  </div>
  <div class="row">
    <label>Fail</label><span id="fail">0</span>
  </div>
  <div class="row">
    <label>Avg latency</label><span id="avg">N/A</span>
  </div>
  <div class="row">
    <label>Last error</label><pre id="err">-</pre>
  </div>

  <script>
    const base = window.location.origin; // same-origin
    document.getElementById('baseUrl').innerText = base;

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
        console.error('stats error', e);
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

    // auto-refresh stats every 1s
    setInterval(fetchStats, 1000);
    fetchStats();
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
