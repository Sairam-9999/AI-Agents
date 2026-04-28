class PortfolioManager:
    def __init__(self):
        pass

    def to_order(self, signal):
        qty = 10

        side = (
            "BUY" if signal["signal"] == "BUY"
            else "SELL" if signal["signal"] == "SELL"
            else "HOLD"
        )

        price = signal.get("details", {}).get("quote", {}).get("price", None)

        return {
            "symbol": signal["symbol"],
            "side": side,
            "qty": qty,
            "price": price
        }


def respond(prompt):
    return (
        "Recommended allocation: 40% equities (15% AAPL), 30% bonds, "
        "20% alternatives, 10% cash — maintain 15% AAPL for moderate-risk "
        "long-term growth."
    )
