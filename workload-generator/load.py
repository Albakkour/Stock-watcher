import argparse
import time
import random
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="http://129.192.82.232:30081",
        help="Base URL of the backend API (without trailing slash)",
    )
    parser.add_argument(
        "--rps",
        type=float,
        default=1.0,
        help="Requests per second (approximate)",
    )
    args = parser.parse_args()

    interval = 1.0 / args.rps
    print(f"Starting load against {args.base_url} with ~{args.rps} RPS")

    while True:
        try:
            endpoint = random.choice(["stocks", "alerts_get", "alerts_post", "notifications"])
            if endpoint == "stocks":
                requests.get(f"{args.base_url}/api/stocks", timeout=2)
            elif endpoint == "alerts_get":
                requests.get(f"{args.base_url}/api/alerts", timeout=2)
            elif endpoint == "alerts_post":
                body = {
                    "symbol": random.choice(["TSLA", "AAPL", "MSFT"]),
                    "direction": random.choice(["above", "below"]),
                    "threshold": random.uniform(150, 250),
                }
                requests.post(f"{args.base_url}/api/alerts", json=body, timeout=2)
            else: 
                requests.get(f"{args.base_url}/api/notifications", timeout=2)

        except Exception as e:
            print("Request error:", e)

        time.sleep(interval)

if __name__ == "__main__":
    main()
