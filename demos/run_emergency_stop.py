import time
from orchestrator import (
    Orchestrator,
    emergency_stop_engage,
    emergency_stop_release,
    is_emergency_engaged,
)

def main():
    orchestrator = Orchestrator()

    order = {
        "symbol": "AAPL",
        "quantity": 200,
        "price": 150,
        "side": "BUY",
    }

    print("\n=== Emergency Stop Demo ===\n")

    # First - business as usual, everything works
    print("Step 1: Executing order (no stop)")
    print(orchestrator.execute(order))

    # Hit the big red button! Stop everything!
    print("\nStep 2: Engaging emergency stop")
    emergency_stop_engage()
    print("Stop active:", is_emergency_engaged())

    # Try to trade - should get blocked cold
    print("\nStep 3: Attempt execution (should block)")
    print(orchestrator.execute(order))

    # Okay crisis over, release the stop
    print("\nStep 4: Releasing stop")
    emergency_stop_release()
    print("Stop active:", is_emergency_engaged())

    # Back to normal - trades working again
    print("\nStep 5: Executing again")
    print(orchestrator.execute(order))

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
