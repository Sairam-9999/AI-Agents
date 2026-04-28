import time
from orchestrator import Orchestrator
from orchestrator_extended import ExtendedOrchestrator

def main():
    print("\n=== Time-Based Demo ===\n")

    base = Orchestrator()
    ext = ExtendedOrchestrator(base, hitl_threshold_notional=10000)

    order = {"symbol": "AAPL", "quantity": 500, "price": 50, "side": "BUY"}

    print("Submitting order:")
    print(ext.preflight_and_maybe_enqueue(order))

    pending = ext.hitl.list_pending()
    print("\nPending:", pending)

    print("\nWaiting 5 seconds for auto-approval...")
    time.sleep(5)

    for item in pending:
        ts = item["ts"]
        ext.hitl.update_status(ts, "approved", reviewer="auto_deadline")

    print("\nFinal Queue:", ext.hitl.list_pending())

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
