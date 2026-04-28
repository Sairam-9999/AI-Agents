def sma(prices, window):
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / window


def classify_signal(prices):
    short_w = 3
    long_w = 7

    short = sma(prices, short_w)
    long = sma(prices, long_w)

    if short is None or long is None:
        return "HOLD", {
            "reason": "insufficient_data",
            "short_sma": short,
            "long_sma": long
        }

    if short > long:
        return "BUY", {"short_sma": short, "long_sma": long}
    elif short < long:
        return "SELL", {"short_sma": short, "long_sma": long}
    else:
        return "HOLD", {"short_sma": short, "long_sma": long}
