import os
import json
from datetime import datetime
import redis
import pika

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
RABBIT_USER = os.getenv("RABBIT_USER", "appuser")
RABBIT_PASS = os.getenv("RABBIT_PASS", "apppass")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

ALERTS_KEY = "csw:alerts"
NOTIFICATIONS_KEY = "csw:notifications"

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="prices", durable=False)

def check_alerts(price_msg):
    symbol = price_msg["symbol"]
    price = float(price_msg["price"])
    alerts_raw = r.lrange(ALERTS_KEY, 0, -1)
    for a_raw in alerts_raw:
        alert = json.loads(a_raw)
        if alert["symbol"] != symbol:
            continue
        direction = alert["direction"]
        threshold = float(alert["threshold"])
        should_trigger = (
            (direction == "above" and price > threshold) or
            (direction == "below" and price < threshold)
        )
        if should_trigger:
            notif_id = int(r.incr("csw:notifications:id"))
            notif = {
                "id": notif_id,
                "alert_id": alert["id"],
                "symbol": symbol,
                "direction": direction,
                "threshold": threshold,
                "price": price,
                "triggered_at": datetime.utcnow().isoformat() + "Z"
            }
            r.rpush(NOTIFICATIONS_KEY, json.dumps(notif))
            print("Triggered notification:", notif)

def on_message(ch, method, properties, body):
    msg = json.loads(body.decode("utf-8"))
    print("Received price", msg)
    check_alerts(msg)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue="prices", on_message_callback=on_message)
print("Alert engine waiting for messages...")
channel.start_consuming()
