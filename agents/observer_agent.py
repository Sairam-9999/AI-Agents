"""
Observer Agent: simulates continuous monitoring of a symbol and writes observations.
Provides a lightweight interface for starting a short demo stream.
"""

import time
import threading
from modules import data_feeds as feeds


_running = {}


def observe_once(symbol: str, steps: int = 10, delay: float = 0.5):
    observations = []

    for obs in feeds.stream_prices(symbol, steps=steps, delay=delay):
        observations.append(obs)

    return observations


def start_background_observer(symbol: str, steps: int = 100, delay: float = 1.0, name: str = None):
    global _running

    key = name or symbol

    if key in _running and _running[key].get("alive"):
        return {"status": "already_running", "key": key}

    stop_flag = {"alive": True}
    observations = []

    def run():
        for obs in feeds.stream_prices(symbol, steps=steps, delay=delay):
            observations.append(obs)

            if not stop_flag["alive"]:
                break

        stop_flag["alive"] = False

    t = threading.Thread(target=run, daemon=True)

    _running[key] = {
        "thread": t,
        "stop": stop_flag,
        "observations": observations
    }

    t.start()

    return {
        "status": "started",
        "key": key
    }


def stop_background_observer(key: str):
    global _running

    if key not in _running:
        return {
            "status": "not_found",
            "key": key
        }

    _running[key]["stop"]["alive"] = False

    return {
        "status": "stopping",
        "key": key
    }


def get_observations(key: str):
    global _running

    if key not in _running:
        return []

    return list(_running[key]["observations"])
