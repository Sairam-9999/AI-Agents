import time
import json
from realtime.observer import Observer
from tools.market_api import get_stock_quote

def handler(data):
    print("Received:", data)

if __name__ == "__main__":
    obs = Observer(handler=handler)

    symbols = ["AAPL", "TSLA", "TEST"]

    for s in symbols:
        quote = get_stock_quote(s)

        msg = json.dumps({
            "symbol": s,
            "price": quote["price"],
            "ts": quote["timestamp"]
        })

        obs.consume(msg)
        time.sleep(0.2)
