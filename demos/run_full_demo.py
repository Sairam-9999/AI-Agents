import time
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.portfolio import PortfolioManager
from orchestrator import Orchestrator
from orchestrator_extended import ExtendedOrchestrator
from audit.audit_logger import audit_record

def main():
    print("\n=== Full MCP Multi-Agent Demo ===\n")

    # Step 1: Research
    researcher = ResearcherAgent()
    research_data = researcher.research("AAPL")
    audit_record("research", research_data)
    print("Research:", research_data)

    time.sleep(1)

    # Step 2: Analysis
    analyst = AnalystAgent()
    analysis = analyst.analyze(research_data)
    audit_record("analysis", analysis)
    print("Analysis:", analysis)

    time.sleep(1)

    # Step 3: Portfolio
    pm = PortfolioManager()
    order = pm.to_order(analysis)

    if "qty" in order:
        order["quantity"] = order.pop("qty")

    audit_record("order_generated", order)
    print("Order:", order)

    time.sleep(1)

    # Step 4: Execution via Extended Orchestrator
    base = Orchestrator()
    ext = ExtendedOrchestrator(base, hitl_threshold_notional=10000)

    result = ext.mcp_execute(order)
    audit_record("execution", result)

    print("Execution Result:", result)

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
