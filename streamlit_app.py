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

# Agent modules with respond functions
from agents import analyst as analyst_module
from agents import researcher as researcher_module
from agents import portfolio as portfolio_module
from agents import consensus as consensus_module


st.set_page_config(
    page_title="Financial Agents Using MCP",
    layout="wide"
)

st.title("Financial Agents Using MCP")

# Sidebar stuff - controls live here
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
        "Extended Orchestrator",
    ],
)

show_logs = st.sidebar.checkbox("Show logs", value=True)

if "last_agent_output" not in st.session_state:
    st.session_state["last_agent_output"] = None

if "display_mode" not in st.session_state:
    st.session_state["display_mode"] = None

# Observer Agent - our background watcher
st.sidebar.divider()
st.sidebar.subheader("Observer Agent")

observer_symbol = st.sidebar.text_input(
    "Symbol to monitor",
    value=st.session_state.get("observer_symbol", "")
)

if "observer_running" not in st.session_state:
    st.session_state["observer_running"] = False

if "active_observer_symbol" not in st.session_state:
    st.session_state["active_observer_symbol"] = observer_symbol

if "show_last_observations" not in st.session_state:
    st.session_state["show_last_observations"] = False


if st.sidebar.button("Start Observer"):
    start_background_observer(observer_symbol)
    st.session_state["observer_running"] = True
    st.session_state["active_observer_symbol"] = observer_symbol
    st.session_state["show_last_observations"] = False
    st.session_state["display_mode"] = "live"
    st.sidebar.success(f"Observer started for {observer_symbol}")


if st.sidebar.button("Stop Observer"):
    stop_background_observer(st.session_state["active_observer_symbol"])
    st.session_state["observer_running"] = False
    st.session_state["display_mode"] = None
    st.sidebar.warning(f"Observer stopped for {st.session_state['active_observer_symbol']}")


if st.sidebar.button("Show Observations"):
    st.session_state["show_last_observations"] = True
    st.session_state["display_mode"] = "last"


# Helper functions we need upfront
def extract_symbol_from_query(query: str):
    """Extract stock symbol from query (handles tickers and common company names)."""
    import re
    query_lower = query.lower()

    # Common company name to ticker mapping
    company_to_ticker = {
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'tesla': 'TSLA',
        'amazon': 'AMZN',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'meta': 'META',
        'facebook': 'META',
        'netflix': 'NFLX',
        'nvidia': 'NVDA',
        'amd': 'AMD',
        'intel': 'INTC',
        'ibm': 'IBM',
        'oracle': 'ORCL',
        'salesforce': 'CRM',
        'adobe': 'ADBE',
        'paypal': 'PYPL',
        'visa': 'V',
        'mastercard': 'MA',
        'disney': 'DIS',
        'walmart': 'WMT',
        'target': 'TGT',
        'costco': 'COST',
        'starbucks': 'SBUX',
        'mcdonalds': 'MCD',
        'nike': 'NKE',
        'coca-cola': 'KO',
        'pepsi': 'PEP',
        'johnson': 'JNJ',
        'pfizer': 'PFE',
        'boeing': 'BA',
        'ford': 'F',
        'general motors': 'GM',
        'gm': 'GM',
        'exxon': 'XOM',
        'chevron': 'CVX',
        'att': 'T',
        'verizon': 'VZ',
        't-mobile': 'TMUS',
    }

    # First check for company names
    for company, ticker in company_to_ticker.items():
        if company in query_lower:
            return ticker

    # Then look for uppercase ticker symbols (1-5 letters)
    matches = re.findall(r'\b[A-Z]{1,5}\b', query)
    common_words = {'I', 'A', 'AN', 'THE', 'AND', 'OR', 'TO', 'FOR', 'OF', 'IN', 'ON', 'AT', 'BY', 'WITH', 'IS', 'IT', 'BE', 'AS', 'MY'}
    symbols = [m for m in matches if m not in common_words]

    return symbols[0] if symbols else None


# Main input area - where users type stuff
st.subheader("Run Agent or Orchestrator")

prompt = st.text_area(
    "Query / Prompt",
    value="",
    height=140,
)

# Try to guess the stock symbol from what the user typed
symbol = extract_symbol_from_query(prompt) or ""
if symbol:
    st.session_state["observer_symbol"] = symbol

run_clicked = st.button("Run")


# More helper functions
def normalize_order(order: dict):
    if "qty" in order and "quantity" not in order:
        order["quantity"] = order.pop("qty")
    return order


def render_result(title, data):
    st.markdown(f"### {title}")
    st.json(data)


def render_agent_response(agent_name, response, prompt, extra_details=None):
    st.markdown(f"### {agent_name} Response")
    st.code(response, language=None)

    if show_logs:
        st.markdown("#### Detailed Reasoning / Debug Info")

        log_data = {
            "agent": agent_name,
            "prompt": prompt,
        }

        if extra_details:
            filtered_details = {
                k: v for k, v in extra_details.items()
                if k != "method"
            }
            log_data.update(filtered_details)

        st.json(log_data)


# The actual work happens here
if run_clicked:
    st.session_state["display_mode"] = "run"

    if agent_choice == "-- choose --":
        st.warning("Please select an agent from the sidebar.")

    else:
        try:
            audit_record("ui_run_started", {
                "agent": agent_choice,
                "symbol": symbol,
                "prompt": prompt
            })

            # Let's get this party started with the Researcher!
            if agent_choice == "Researcher":
                response = researcher_module.respond(prompt)
                st.session_state["last_agent_output"] = {
                    "agent_name": "Researcher",
                    "response": response,
                    "prompt": prompt,
                    "extra_details": {
                        "extracted_symbol": symbol,
                        "method": "respond()",
                        "logic": "Grabs stock price and digs through docs for relevant info",
                    }
                }

            # Now it's the Analyst's turn to shine!
            elif agent_choice == "Analyst":
                response = analyst_module.respond(prompt)
                st.session_state["last_agent_output"] = {
                    "agent_name": "Analyst",
                    "response": response,
                    "prompt": prompt,
                    "extra_details": {
                        "extracted_symbol": symbol,
                        "method": "respond()",
                        "logic": "Simple rules: expensive=SELL, cheap=BUY, middle=HOLD",
                    }
                }

            # Time for the Portfolio Manager to turn signals into orders!
            elif agent_choice == "Portfolio Manager":
                response = portfolio_module.respond(prompt)
                st.session_state["last_agent_output"] = {
                    "agent_name": "Portfolio Manager",
                    "response": response,
                    "prompt": prompt,
                    "extra_details": {
                        "extracted_symbol": symbol,
                        "method": "respond()",
                        "logic": "Turns the signal into an actual order (always 10 shares for now)",
                    }
                }

            # Consensus time - let's get everyone on the same page!
            elif agent_choice == "Consensus":
                response = consensus_module.respond(prompt)
                st.session_state["last_agent_output"] = {
                    "agent_name": "Consensus",
                    "response": response,
                    "prompt": prompt,
                    "extra_details": {
                        "extracted_symbol": symbol,
                        "method": "respond()",
                        "logic": "Combines multiple signals and figures out if we should trust it",
                    }
                }

            # Full pipeline - let's run the whole shebang!
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

            # Basic orchestrator test - let's see what it can do!
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

            # Extended orchestrator - the fancy version with HITL
            elif agent_choice == "Extended Orchestrator":
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


# Display area - show results here
display_mode = st.session_state.get("display_mode")

if display_mode == "run":
    if st.session_state.get("last_agent_output"):
        output = st.session_state["last_agent_output"]

        render_agent_response(
            output["agent_name"],
            output["response"],
            output["prompt"],
            output.get("extra_details")
        )

elif display_mode == "last":
    active_symbol = st.session_state.get("active_observer_symbol", observer_symbol)
    observations = get_observations(active_symbol)

    st.markdown(f"### Last Observations: {active_symbol}")

    if observations:
        st.json(observations[-10:])
    else:
        st.info("No observations available yet. Start the observer first.")

elif display_mode == "live":
    active_symbol = st.session_state.get("active_observer_symbol", observer_symbol)

    if st.session_state.get("observer_running"):
        st.markdown(f"## Live Stream: {active_symbol}")

        live_placeholder = st.empty()
        observations = get_observations(active_symbol)

        with live_placeholder.container():
            if observations:
                st.json(observations[-10:])
            else:
                st.info("Waiting for observations...")


# Keeping it clean - no footer clutter