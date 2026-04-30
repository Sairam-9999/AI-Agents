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

    # Step 1: Normal execution
    print("Step 1: Executing order (no stop)")
    print(orchestrator.execute(order))

    # Step 2: Engage stop
    print("\nStep 2: Engaging emergency stop")
    emergency_stop_engage()
    print("Stop active:", is_emergency_engaged())

    # Step 3: Blocked execution
    print("\nStep 3: Attempt execution (should block)")
    print(orchestrator.execute(order))

    # Step 4: Release stop
    print("\nStep 4: Releasing stop")
    emergency_stop_release()
    print("Stop active:", is_emergency_engaged())

    # Step 5: Execute again
    print("\nStep 5: Executing again")
    print(orchestrator.execute(order))

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
