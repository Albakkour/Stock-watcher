import os
import time
import json
import random
from datetime import datetime
import redis
import pika

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_USER = os.getenv("RABBIT_USER", "appuser")
RABBIT_PASS = os.getenv("RABBIT_PASS", "apppass")

SYMBOLS = os.getenv("STOCK_SYMBOLS", "TSLA,AAPL,MSFT,NVDA,GOOG").split(",")
PERIOD = float(os.getenv("UPDATE_PERIOD", "5.0"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="prices", durable=False)

STOCKS_KEY = "csw:stocks"

prices = {sym: random.uniform(100, 300) for sym in SYMBOLS}
# I just wanted to make it simple with using external libraries to get the real pice of stocks. If I have time later, I will improve it.
while True:
    for sym in SYMBOLS:
        prices[sym] += random.uniform(-2, 2)
        prices[sym] = max(prices[sym], 1.0)
        now = datetime.utcnow().isoformat() + "Z"
        msg = {
            "symbol": sym,
            "price": round(prices[sym], 2),
            "timestamp": now
        }
        #RabbitMQ
        channel.basic_publish(
            exchange="",
            routing_key="prices",
            body=json.dumps(msg).encode("utf-8")
        )
        #Redis
        r.hset(STOCKS_KEY, sym, json.dumps({
            "symbol": sym,
            "price": msg["price"],
            "updated_at": now
        }))
        print("Published price", msg)

    time.sleep(PERIOD)
