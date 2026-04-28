import time
import random
from typing import Optional
from pydantic import BaseModel, Field


class OrderSchema(BaseModel):
    symbol: str
    side: str
    quantity: int = Field(..., gt=0)
    limit_price: Optional[float] = None
    order_type: str = "market"


class ExecutionTool:
    def __init__(self, simulate=True):
        self.simulate = simulate

    def place_order(self, order: dict):
        o = OrderSchema(**order)

        if self.simulate:
            exec_price = o.limit_price if o.limit_price else 100.0

            return {
                "success": True,
                "status": "filled",
                "symbol": o.symbol,
                "side": o.side,
                "quantity": o.quantity,
                "exec_price": exec_price,
                "timestamp": time.time()
            }

        raise NotImplementedError("Real broker adapter not implemented")


def normalize_order(order: dict):
    return {
        "symbol": order["symbol"],
        "side": order["side"],
        "quantity": order.get("quantity", order.get("qty", 0)),
        "order_type": order.get("order_type", "market"),
        "limit_price": order.get("limit_price", order.get("price"))
    }


def validate_order(order: dict):
    required = ["symbol", "side", "quantity", "order_type"]

    for k in required:
        if k not in order:
            raise ValueError(f"Missing order field: {k}")

    if order["side"] not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")

    if not isinstance(order["quantity"], (int, float)) or order["quantity"] <= 0:
        raise ValueError("quantity must be positive number")

    if order["order_type"] not in ("market", "limit"):
        raise ValueError("order_type must be market or limit")

    return True


def pre_execution_checks(order: dict, market_price: float, max_slippage_pct: float = 0.02):
    if order.get("order_type") == "limit" and order.get("limit_price") is not None:
        limit = float(order["limit_price"])
        allowed_low = market_price * (1 - max_slippage_pct)
        allowed_high = market_price * (1 + max_slippage_pct)

        if not (allowed_low <= limit <= allowed_high):
            return False, {
                "reason": "limit_price_out_of_slippage",
                "allowed_low": allowed_low,
                "allowed_high": allowed_high,
                "limit": limit
            }

    return True, {"reason": "ok"}


def place_order(order: dict, market_price: float = None):
    order = normalize_order(order)
    validate_order(order)

    if market_price is None:
        market_price = round(100 + (random.random() - 0.5) * 5, 2)

    ok, meta = pre_execution_checks(order, market_price)

    if not ok:
        return {
            "success": False,
            "error": "pre_execution_failed",
            "meta": meta
        }

    exec_price = (
        market_price
        if order["order_type"] == "market"
        else float(order.get("limit_price") or market_price)
    )

    return {
        "success": True,
        "exec_price": exec_price,
        "filled": order["quantity"],
        "meta": meta,
        "timestamp": time.time()
    }
