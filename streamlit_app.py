import streamlit as st

from orchestrator import Orchestrator, run_agent
from orchestrator_extended import ExtendedOrchestrator
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.consensus import ConsensusAgent
from agents.portfolio import PortfolioManager
from agents.observer_agent import (
    start_background_observer,
    stop_background_observer,
    get_observations,
)
from audit.audit_logger import audit_record


st.set_page_config(
    page_title="Financial Agents Using MCP",
    layout="wide"
)

st.title("Financial Agents Using MCP")

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Controls")

agent_choice = st.sidebar.selectbox(
    "Select agent",
    [
        "-- choose --",
        "Researcher",
        "Analyst",
        "Portfolio Manager",
        "Consensus",
        "Full Pipeline",
        "Orchestrator",
        "Extended Orchestrator / MCP",
    ],
)

show_logs = st.sidebar.checkbox("Show logs", value=True)

st.sidebar.divider()
st.sidebar.subheader("Observer Agent")

observer_symbol = st.sidebar.text_input("Symbol to monitor", value="AAPL")

if st.sidebar.button("Start Observer"):
    result = start_background_observer(observer_symbol)
    st.sidebar.success(result)

if st.sidebar.button("Stop Observer"):
    result = stop_background_observer(observer_symbol)
    st.sidebar.warning(result)

if st.sidebar.button("Show Observations"):
    observations = get_observations(observer_symbol)
    st.sidebar.json(observations[-10:])


# -----------------------------
# Main Input
# -----------------------------
st.subheader("Run Agent or Orchestrator")

symbol = st.text_input("Stock Symbol", value="AAPL")

prompt = st.text_area(
    "Query / Prompt",
    value=f"Analyze {symbol} and generate a trading recommendation.",
    height=140,
)

run_clicked = st.button("Run")


# -----------------------------
# Helpers
# -----------------------------
def normalize_order(order: dict):
    if "qty" in order and "quantity" not in order:
        order["quantity"] = order.pop("qty")
    return order


def render_result(title, data):
    st.markdown(f"### {title}")
    st.json(data)


# -----------------------------
# Execution Logic
# -----------------------------
if run_clicked:
    if agent_choice == "-- choose --":
        st.warning("Please select an agent from the sidebar.")

    else:
        try:
            audit_record("ui_run_started", {
                "agent": agent_choice,
                "symbol": symbol,
                "prompt": prompt
            })

            # -----------------------------
            # Researcher
            # -----------------------------
            if agent_choice == "Researcher":
                researcher = ResearcherAgent()
                result = researcher.research(symbol)

                render_result("Research Output", result)

            # -----------------------------
            # Analyst
            # -----------------------------
            elif agent_choice == "Analyst":
                researcher = ResearcherAgent()
                research_data = researcher.research(symbol)

                analyst = AnalystAgent()
                result = analyst.analyze(research_data)

                render_result("Research Input", research_data)
                render_result("Analyst Output", result)

            # -----------------------------
            # Portfolio Manager
            # -----------------------------
            elif agent_choice == "Portfolio Manager":
                researcher = ResearcherAgent()
                research_data = researcher.research(symbol)

                analyst = AnalystAgent()
                analysis = analyst.analyze(research_data)

                pm = PortfolioManager()
                order = pm.to_order(analysis)

                render_result("Analyst Signal", analysis)
                render_result("Generated Order", order)

            # -----------------------------
            # Consensus
            # -----------------------------
            elif agent_choice == "Consensus":
                researcher = ResearcherAgent()
                research_data = researcher.research(symbol)

                analyst = AnalystAgent()
                signal_1 = analyst.analyze(research_data)
                signal_2 = analyst.analyze(research_data)

                consensus_agent = ConsensusAgent()
                result = consensus_agent.consensus([signal_1, signal_2])

                render_result("Signals", [signal_1, signal_2])
                render_result("Consensus Output", result)

            # -----------------------------
            # Full Pipeline
            # -----------------------------
            elif agent_choice == "Full Pipeline":
                researcher = ResearcherAgent()
                analyst = AnalystAgent()
                consensus_agent = ConsensusAgent()
                pm = PortfolioManager()
                orchestrator = Orchestrator()

                research_data = researcher.research(symbol)
                signal_1 = analyst.analyze(research_data)
                signal_2 = analyst.analyze(research_data)

                consensus = consensus_agent.consensus([signal_1, signal_2])

                if consensus["approved"]:
                    order = pm.to_order({
                        "symbol": symbol,
                        "signal": consensus["decision"],
                        "details": research_data,
                    })

                    order = normalize_order(order)

                    if order.get("side") == "HOLD":
                        execution_result = {
                            "status": "skipped",
                            "reason": "HOLD signal does not execute"
                        }
                    else:
                        execution_result = orchestrator.execute(order)

                else:
                    order = None
                    execution_result = {
                        "status": "not_executed",
                        "reason": "Consensus not approved"
                    }

                render_result("Research Data", research_data)
                render_result("Signals", [signal_1, signal_2])
                render_result("Consensus", consensus)
                render_result("Order", order)
                render_result("Execution Result", execution_result)

            # -----------------------------
            # Orchestrator
            # -----------------------------
            elif agent_choice == "Orchestrator":
                orchestrator = Orchestrator()

                order = {
                    "symbol": symbol,
                    "side": "BUY",
                    "quantity": 10,
                    "price": 100,
                    "order_type": "market",
                }

                result = orchestrator.execute(order)

                render_result("Sample Order", order)
                render_result("Orchestrator Result", result)

            # -----------------------------
            # Extended Orchestrator / MCP
            # -----------------------------
            elif agent_choice == "Extended Orchestrator / MCP":
                base = Orchestrator()
                ext = ExtendedOrchestrator(
                    base_orchestrator=base,
                    hitl_threshold_notional=10000
                )

                order = {
                    "symbol": symbol,
                    "side": "BUY",
                    "quantity": 200,
                    "price": 100,
                    "order_type": "market",
                }

                result = ext.preflight_and_maybe_enqueue(order)
                pending = ext.hitl.list_pending()

                render_result("MCP / HITL Order", order)
                render_result("Extended Orchestrator Result", result)
                render_result("Pending HITL Queue", pending)

            audit_record("ui_run_completed", {
                "agent": agent_choice,
                "symbol": symbol
            })

        except Exception as e:
            st.error(f"Error: {e}")
            audit_record("ui_run_error", {
                "agent": agent_choice,
                "symbol": symbol,
                "error": str(e)
            })


# -----------------------------
# Logs
# -----------------------------
if show_logs:
    st.divider()
    st.subheader("System Notes")

    st.info(
        "Use Full Pipeline to run: Researcher → Analyst → Consensus → "
        "Portfolio Manager → Orchestrator."
    )

    st.caption(
        "This is a simulated trading system for learning. "
        "Do not use it for real financial trading."
    )