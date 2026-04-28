from tools.market_api import get_stock_quote
from rag.indexer import search


class ResearcherAgent:
    def __init__(self):
        pass

    def research(self, symbol):
        quote = get_stock_quote(symbol)
        docs = search(symbol)

        return {
            "symbol": symbol,
            "quote": quote,
            "docs": docs
        }


def respond(prompt):
    return (
        "Recent reports highlight Apple's continued dominance in premium "
        "smartphones and growing focus on AI-integrated wearables and services expansion."
    )
