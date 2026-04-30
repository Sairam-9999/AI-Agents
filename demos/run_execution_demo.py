from agents.portfolio import PortfolioManager
from tools.execution_tool import place_order

pm = PortfolioManager()

# Valid order
valid_order = pm.to_order({
    "symbol": "AAPL",
    "signal": "BUY",
    "quantity": 10,
    "details": {"reason": "Positive earnings"}
})

print("Attempting valid order:")
print(place_order(valid_order))

# Invalid order
invalid_order = {
    "symbol": "TSLA",
    "signal": "SELL"
}

print("\nAttempting invalid order:")
print(place_order(invalid_order))
