import time
import random
import datetime


def get_latest_price(symbol: str):
    seed = abs(hash(symbol)) % 1000
    base = 100 + (seed % 50)
    price = base + (random.random() - 0.5) * 5
    return round(price, 2)


def stream_prices(symbol: str, steps: int = 10, delay: float = 0.5):
    for _ in range(steps):
        yield {
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "symbol": symbol,
            "price": get_latest_price(symbol)
        }
        time.sleep(delay)


def get_news_headlines(symbol: str, max_items: int = 5):
    headlines = [
        f"{symbol}: Company beats expectations on revenue.",
        f"{symbol}: New product launch drives investor interest.",
        f"{symbol}: Regulatory headlines cause caution among analysts.",
        f"{symbol}: Executive changes announced in leadership team.",
        f"{symbol}: Partnerships expand market reach."
    ]
    return headlines[:max_items]
