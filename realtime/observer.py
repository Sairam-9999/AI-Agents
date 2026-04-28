"""
Real-time observer module for live market monitoring.
Provides high-level interface for streaming price data.
"""

from modules.data_feeds import stream_prices, get_latest_price


class RealtimeObserver:
    def __init__(self):
        self.active_streams = {}

    def get_price(self, symbol: str):
        return get_latest_price(symbol)

    def stream(self, symbol: str, steps: int = 100, delay: float = 1.0):
        return stream_prices(symbol, steps=steps, delay=delay)

    def watch(self, symbol: str, callback, steps: int = 50):
        """Watch a symbol and call callback on each observation."""
        for obs in stream_prices(symbol, steps=steps, delay=1.0):
            callback(obs)
