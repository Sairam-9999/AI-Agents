from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.portfolio import PortfolioManager
from agents.consensus import ConsensusAgent

if __name__ == "__main__":
    r = ResearcherAgent()
    a = AnalystAgent()
    pm = PortfolioManager()
    c = ConsensusAgent()

    data = r.research("TEST")

    s1 = a.analyze(data)
    s2 = a.analyze(data)

    signals = [s1, s2]
    cons = c.consensus(signals)

    print("Signals:", signals)
    print("Consensus:", cons)

    if cons["approved"]:
        order = pm.to_order({
            "symbol": "TEST",
            "signal": cons["decision"],
            "details": data
        })
        print("Order:", order)
    else:
        print("Not approved")
