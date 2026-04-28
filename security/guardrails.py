class PreExecutionChecks:
    def __init__(self, max_qty=1000):
        self.max_qty = max_qty

    def check(self, order):
        if order.get("qty", 0) > self.max_qty:
            return False, f"qty_exceeds_max ({self.max_qty})"

        if order.get("side") not in ("BUY", "SELL"):
            return False, "invalid_side"

        return True, None


class EmergencyStop:
    def __init__(self):
        self._triggered = False

    def trigger(self):
        self._triggered = True

    def reset(self):
        self._triggered = False

    def is_triggered(self):
        return self._triggered
