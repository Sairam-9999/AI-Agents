class AnalystAgent:
    def __init__(self):
        pass

    def analyze(self, research_output):
        price = research_output["quote"]["price"]

        if price > 60:
            signal = "SELL"
            confidence = min(0.9, (price - 60) / 40)
        elif price < 55:
            signal = "BUY"
            confidence = min(0.9, (55 - price) / 40)
        else:
            signal = "HOLD"
            confidence = 0.5

        return {
            "symbol": research_output["symbol"],
            "signal": signal,
            "confidence": confidence,
            "details": research_output
        }


def respond(prompt):
    return (
        "Apple's Q3 revenue increased 12% YoY, driven by strong iPhone 15 demand "
        "and services growth. Margins improved slightly, with EPS beating expectations."
    )
