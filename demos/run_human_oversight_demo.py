import time
from orchestrator import Orchestrator
from orchestrator_extended import ExtendedOrchestrator

def main():
    print("\n=== Human Oversight Demo ===\n")

    base = Orchestrator()
    ext = ExtendedOrchestrator(base, hitl_threshold_notional=10000)

    # Regular order
    order1 = {"symbol": "AAPL", "quantity": 50, "price": 150, "side": "BUY"}
    print("Regular Order:")
    print(ext.preflight_and_maybe_enqueue(order1))

    time.sleep(1)

    # High-value order
    order2 = {"symbol": "GOOG", "quantity": 200, "price": 100, "side": "BUY"}
    print("\nHigh-value Order:")
    print(ext.preflight_and_maybe_enqueue(order2))

    # List queue
    pending = ext.hitl.list_pending()
    print("\nPending:", pending)

    # Approve first
    if pending:
        ts = pending[0]["ts"]
        ext.hitl.update_status(ts, "approved", reviewer="DemoUser")

        approved_order = pending[0]["item"]["order"]
        print("\nExecuting approved order:")
        print(base.execute(approved_order))


if __name__ == "__main__":
    main()
