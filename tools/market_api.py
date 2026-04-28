import os
import datetime


USE_REAL = os.getenv("REAL_MARKET_API", "0") == "1"


def get_stock_quote(symbol: str):
    seed = sum(ord(c) for c in symbol) % 1000
    price = 50 + (seed % 50) + (seed % 10) * 0.1
    ts = datetime.datetime.utcnow().isoformat() + "Z"

    return {
        "symbol": symbol,
        "price": round(price, 2),
        "bid": round(price - 0.1, 2),
        "ask": round(price + 0.1, 2),
        "timestamp": ts
    }


def get_news(symbol: str, n=3):
    seed = sum(ord(c) for c in symbol) % 100

    items = []
    for i in range(n):
        items.append({
            "title": f"{symbol} - News #{i + 1}",
            "summary": f"Mock summary for {symbol}, seed={seed}, item={i}",
            "published_at": (
                datetime.datetime.utcnow()
                - datetime.timedelta(minutes=5 * i)
            ).isoformat() + "Z"
        })

    return items
