from collections import defaultdict


class ConsensusAgent:
    def __init__(self, threshold=0.6):
        self.threshold = threshold

    def consensus(self, signals):
        scores = defaultdict(float)

        for s in signals:
            sig = s.get("signal", "HOLD").upper()
            conf = float(s.get("confidence", 0.5))
            scores[sig] += conf

        total = sum(scores.values()) or 1.0

        for k in list(scores.keys()):
            scores[k] = scores[k] / total

        decision = max(scores.items(), key=lambda kv: kv[1])[0]
        support = dict(scores)

        return {
            "decision": decision,
            "support": support,
            "threshold": self.threshold,
            "approved": support.get(decision, 0) >= self.threshold
        }


def respond(prompt):
    return (
        "Consensus: Apple shows strong fundamentals, steady revenue diversification, "
        "consistent cash flow, and positive analyst sentiment for the upcoming quarter."
    )
