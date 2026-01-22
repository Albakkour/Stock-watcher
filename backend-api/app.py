from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import redis
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

#a
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

r = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    password=REDIS_PASSWORD,
    decode_responses=True
)

app = FastAPI(
    title="Cloud Stock Watcher API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Stock(BaseModel):
    symbol: str
    price: float
    updated_at: datetime

class AlertCreateRequest(BaseModel):
    symbol: str
    direction: str  # "above" or "below"
    threshold: float

class Alert(BaseModel):
    id: int
    symbol: str
    direction: str
    threshold: float
    created_at: datetime

class Notification(BaseModel):
    id: int
    alert_id: int
    symbol: str
    direction: str
    threshold: float
    price: float
    triggered_at: datetime


ALERTS_KEY = "csw:alerts"         
NOTIFICATIONS_KEY = "csw:notifications" 
STOCKS_KEY = "csw:stocks"         

def get_next_id(counter_key: str) -> int:
    return int(r.incr(counter_key))



@app.get("/api/stocks")
def list_stocks():
    stocks_raw = r.hvals(STOCKS_KEY)  
    stocks = []
    for s in stocks_raw:
        data = json.loads(s)
        stocks.append(data)
    return {"stocks": stocks}

@app.get("/api/alerts")
def list_alerts():
    alerts_raw = r.lrange(ALERTS_KEY, 0, -1)
    alerts = [json.loads(a) for a in alerts_raw]
    return {"alerts": alerts}

@app.post("/api/alerts", status_code=201)
def create_alert(req: AlertCreateRequest):
    if req.direction not in ("above", "below"):
        raise HTTPException(status_code=400, detail="direction must be 'above' or 'below'")
    alert_id = get_next_id("csw:alerts:id")
    alert = {
        "id": alert_id,
        "symbol": req.symbol,
        "direction": req.direction,
        "threshold": req.threshold,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    r.rpush(ALERTS_KEY, json.dumps(alert))
    return {"alert": alert}

@app.get("/api/notifications")
def list_notifications():
    notifs_raw = r.lrange(NOTIFICATIONS_KEY, 0, -1)
    notifs = [json.loads(n) for n in notifs_raw]
    return {"notifications": notifs}

@app.delete("/api/reset")
def reset_all():
    r.flushdb()
    return {"status": "ok", "message": "all data cleared"}
