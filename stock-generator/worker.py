# import os
# import time
# import json
# import random
# from datetime import datetime
# from dotenv import load_dotenv

# import redis
# import pika
# import yfinance as yf

# load_dotenv()  

# REDIS_HOST = os.getenv("REDIS_HOST", "redis")
# REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
# RABBIT_USER = os.getenv("RABBIT_USER", "appuser")
# RABBIT_PASS = os.getenv("RABBIT_PASS", "apppass")

# SYMBOLS = os.getenv("STOCK_SYMBOLS", "TSLA,AAPL,MSFT,NVDA,GOOG").split(",")
# PERIOD = float(os.getenv("UPDATE_PERIOD", "15.0"))

# r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
# params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
# connection = pika.BlockingConnection(params)
# channel = connection.channel()
# channel.queue_declare(queue="prices", durable=False)

# STOCKS_KEY = "csw:stocks"

# prices = {
#     "TSLA": 250.0,
#     "AAPL": 180.0,
#     "MSFT": 380.0,
#     "NVDA": 850.0,
#     "GOOG": 140.0,
# }

# def fetch_price_from_api(symbol: str, fallback: float) -> float:
#     """Fetch real price from yfinance with fallback"""
#     try:
#         ticker = yf.Ticker(symbol)
        
#         if hasattr(ticker, 'info') and ticker.info:
#             price = ticker.info.get("currentPrice") or ticker.info.get("regularMarketPrice")
#             if price and price > 0:
#                 print(f"[OK] {symbol}: ${price}")
#                 return float(price)
        
#         hist = ticker.history(period="1d")
#         if not hist.empty:
#             price = float(hist['Close'].iloc[-1])
#             print(f"[OK] {symbol}: ${price} (from history)")
#             return price
        
#         print(f"[WARN] {symbol}: No data, using fallback ${fallback}")
#         return fallback

#     except Exception as e:
#         print(f"[ERROR] {symbol}: {e}")
#         new_price = fallback + random.uniform(-2, 2)
#         return max(new_price, 1.0)

# print("Starting stock generator (yfinance mode)")

# while True:
#     for sym in SYMBOLS:
#         prices[sym] = fetch_price_from_api(sym, prices[sym])

#         now = datetime.utcnow().isoformat() + "Z"

#         msg = {
#             "symbol": sym,
#             "price": round(prices[sym], 2),
#             "timestamp": now,
#         }

#         try:
#             channel.basic_publish(
#                 exchange="",
#                 routing_key="prices",
#                 body=json.dumps(msg).encode("utf-8"),
#             )
#         except Exception as e:
#             print(f"[ERROR] RabbitMQ publish failed: {e}")

#         try:
#             r.hset(
#                 STOCKS_KEY,
#                 sym,
#                 json.dumps({
#                     "symbol": sym,
#                     "price": msg["price"],
#                     "updated_at": now,
#                 }),
#             )
#         except Exception as e:
#             print(f"[ERROR] Redis hset failed: {e}")

#         print(f"Published {msg}")

#     time.sleep(PERIOD)

import os
import time
import json
import random
from datetime import datetime
from dotenv import load_dotenv

import redis
import pika
import yfinance as yf

# --------------------------------------------------
# Configuration (12-Factor: config via env vars)
# --------------------------------------------------
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_USER = os.getenv("RABBIT_USER", "appuser")
RABBIT_PASS = os.getenv("RABBIT_PASS", "apppass")

SYMBOLS = os.getenv(
    "STOCK_SYMBOLS",
    "TSLA,AAPL,MSFT,NVDA,GOOG"
).split(",")

UPDATE_PERIOD = float(os.getenv("UPDATE_PERIOD", "15.0"))

STOCKS_KEY = "csw:stocks"

# --------------------------------------------------
# Redis connection
# --------------------------------------------------
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

# --------------------------------------------------
# RabbitMQ connection
# --------------------------------------------------
credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)

connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="prices", durable=False)

# --------------------------------------------------
# Initial fallback prices (can be extended dynamically)
# --------------------------------------------------
prices = {
    "TSLA": 250.0,
    "AAPL": 180.0,
    "MSFT": 380.0,
    "NVDA": 850.0,
    "GOOG": 140.0,
}

# --------------------------------------------------
# Fetch stock price with safe fallbacks
# --------------------------------------------------
def fetch_price_from_api(symbol: str, fallback: float) -> float:
    try:
        ticker = yf.Ticker(symbol)

        # Try current price
        if hasattr(ticker, "info") and ticker.info:
            price = (
                ticker.info.get("currentPrice")
                or ticker.info.get("regularMarketPrice")
            )
            if price and price > 0:
                print(f"[OK] {symbol}: ${price}")
                return float(price)

        # Fallback to latest close
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
            print(f"[OK] {symbol}: ${price} (from history)")
            return price

        print(f"[WARN] {symbol}: No data, using fallback ${fallback}")
        return fallback

    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        jittered = fallback + random.uniform(-2, 2)
        return max(jittered, 1.0)

# --------------------------------------------------
# Main loop
# --------------------------------------------------
print("Starting stock generator (yfinance mode)")
print(f"Tracking symbols: {SYMBOLS}")
print(f"Update period: {UPDATE_PERIOD} seconds")

while True:
    for sym in SYMBOLS:
        # SAFE fallback: prevents KeyError (AMZN bug fixed)
        fallback_price = prices.get(sym, random.uniform(100, 500))
        prices[sym] = fetch_price_from_api(sym, fallback_price)

        now = datetime.utcnow().isoformat() + "Z"

        msg = {
            "symbol": sym,
            "price": round(prices[sym], 2),
            "timestamp": now,
        }

        # Publish to RabbitMQ
        try:
            channel.basic_publish(
                exchange="",
                routing_key="prices",
                body=json.dumps(msg).encode("utf-8"),
            )
        except Exception as e:
            print(f"[ERROR] RabbitMQ publish failed: {e}")

        # Store latest price in Redis
        try:
            r.hset(
                STOCKS_KEY,
                sym,
                json.dumps({
                    "symbol": sym,
                    "price": msg["price"],
                    "updated_at": now,
                }),
            )
        except Exception as e:
            print(f"[ERROR] Redis hset failed: {e}")

        print(f"Published {msg}")

    time.sleep(UPDATE_PERIOD)
