import time
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.portfolio import PortfolioManager
from orchestrator import Orchestrator
from orchestrator_extended import ExtendedOrchestrator
from audit.audit_logger import audit_record

def main():
    print("\n=== Full MCP Multi-Agent Demo ===\n")

    # Fire up the researcher to dig up some data
    researcher = ResearcherAgent()
    research_data = researcher.research("AAPL")
    audit_record("research", research_data)
    print("Research:", research_data)

    time.sleep(1)

    # Analyst crunches the numbers and makes a call
    analyst = AnalystAgent()
    analysis = analyst.analyze(research_data)
    audit_record("analysis", analysis)
    print("Analysis:", analysis)

    time.sleep(1)

    # Portfolio manager turns the signal into an order
    pm = PortfolioManager()
    order = pm.to_order(analysis)

    if "qty" in order:
        order["quantity"] = order.pop("qty")

    audit_record("order_generated", order)
    print("Order:", order)

    time.sleep(1)

    # Execute it through the fancy orchestrator with all the safety checks
    base = Orchestrator()
    ext = ExtendedOrchestrator(base, hitl_threshold_notional=10000)

    result = ext.mcp_execute(order)
    audit_record("execution", result)

    print("Execution Result:", result)

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
