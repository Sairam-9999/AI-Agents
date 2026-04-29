import time
from orchestrator import Orchestrator
from orchestrator_extended import ExtendedOrchestrator

def main():
    print("\n=== Human Oversight Demo ===\n")

    base = Orchestrator()
    ext = ExtendedOrchestrator(base, hitl_threshold_notional=10000)

    # Normal-sized order - should sail right through
    order1 = {"symbol": "AAPL", "quantity": 50, "price": 150, "side": "BUY"}
    print("Regular Order:")
    print(ext.preflight_and_maybe_enqueue(order1))

    time.sleep(1)

    # Big money order - this one's gonna need approval
    order2 = {"symbol": "GOOG", "quantity": 200, "price": 100, "side": "BUY"}
    print("\nHigh-value Order:")
    print(ext.preflight_and_maybe_enqueue(order2))

    # Show what's waiting in the approval queue
    pending = ext.hitl.list_pending()
    print("\nPending:", pending)

    # Approve the first one and let it run
    if pending:
        ts = pending[0]["ts"]
        ext.hitl.update_status(ts, "approved", reviewer="DemoUser")

        approved_order = pending[0]["item"]["order"]
        print("\nExecuting approved order:")
        print(base.execute(approved_order))


if __name__ == "__main__":
    main()
