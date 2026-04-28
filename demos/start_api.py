import streamlit as st

from orchestrator import Orchestrator
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


# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Financial Agents Using MCP",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
        .hero {
            padding: 4rem 2rem;
            border-radius: 28px;
            background:
                radial-gradient(circle at top left, rgba(80, 140, 255, 0.25), transparent 35%),
                radial-gradient(circle at bottom right, rgba(0, 255, 180, 0.12), transparent 30%),
                linear-gradient(135deg, #07111f 0%, #020617 100%);
            border: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 2rem;
        }

        .hero h1 {
            font-size: 3.6rem;
            line-height: 1.05;
            font-weight: 800;
            color: white;
            margin-bottom: 1rem;
        }

        .hero p {
            font-size: 1.15rem;
            color: rgba(255,255,255,0.72);
            max-width: 780px;
        }

        .glass-card {
            padding: 1.4rem;
            border-radius: 22px;
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.12);
            backdrop-filter: blur(16px);
            min-height: 150px;
        }

        .glass-card h3 {
            color: white;
            margin-bottom: 0.5rem;
        }

        .glass-card p {
            color: rgba(255,255,255,0.68);
            font-size: 0.95rem;
        }

        .section-title {
            margin-top: 3rem;
            margin-bottom: 1rem;
            font-size: 2rem;
            font-weight: 750;
        }

        .flow-box {
            text-align: center;
            padding: 1rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.12);
        }

        .small-muted {
            color: rgba(255,255,255,0.58);
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("⚙️ Controls")

page = st.sidebar.radio(
    "Navigate",
    [
        "Landing Page",
        "Run Dashboard",
        "Observer Agent",
        "Architecture",
    ]
)

show_logs = st.sidebar.checkbox("Show logs", value=True)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def normalize_order(order: dict):
    if order and "qty" in order and "quantity" not in order:
        order["quantity"] = order.pop("qty")
    return order


def render_json(title, data):
    st.markdown(f"### {title}")
    st.json(data)


def run_full_pipeline(symbol: str):
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    consensus_agent = ConsensusAgent()
    portfolio = PortfolioManager()
    orchestrator = Orchestrator()

    research_data = researcher.research(symbol)
    signal_1 = analyst.analyze(research_data)
    signal_2 = analyst.analyze(research_data)

    consensus = consensus_agent.consensus([signal_1, signal_2])

    if consensus["approved"]:
        order = portfolio.to_order({
            "symbol": symbol,
            "signal": consensus["decision"],
            "details": research_data,
        })

        order = normalize_order(order)

        if order.get("side") == "HOLD":
            execution_result = {
                "status": "skipped",
                "reason": "HOLD signal does not create a trade order"
            }
        else:
            execution_result = orchestrator.execute(order)
    else:
        order = None
        execution_result = {
            "status": "not_executed",
            "reason": "Consensus not approved"
        }

    return {
        "research": research_data,
        "signals": [signal_1, signal_2],
        "consensus": consensus,
        "order": order,
        "execution": execution_result,
    }


# --------------------------------------------------
# Landing Page
# --------------------------------------------------
if page == "Landing Page":
    st.markdown(
        """
        <div class="hero">
            <h1>Autonomous Financial Intelligence.<br/>Real-Time Decisions.</h1>
            <p>
                AI agents that research, analyze, decide, and execute —
                with built-in guardrails, human oversight, and live market awareness.
            </p>
            <p>
                From signal generation to execution, everything runs as a coordinated system —
                not isolated models.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        if st.button("🚀 Launch Dashboard", use_container_width=True):
            st.session_state["go_dashboard"] = True

    with c2:
        if st.button("🧭 View Architecture", use_container_width=True):
            st.session_state["go_architecture"] = True

    if st.session_state.get("go_dashboard"):
        st.info("Open the sidebar and select **Run Dashboard**.")

    if st.session_state.get("go_architecture"):
        st.info("Open the sidebar and select **Architecture**.")

    st.markdown('<div class="section-title">Financial workflows are fragmented across tools and time.</div>', unsafe_allow_html=True)

    st.write(
        """
        Market data, analysis, signals, and execution often live in separate systems.
        Decisions are delayed. Context is lost. Risk increases.

        Financial Agents unify this into a single continuous intelligence layer.
        """
    )

    st.markdown('<div class="section-title">How Intelligence Operates in Real Time</div>', unsafe_allow_html=True)

    card1, card2, card3 = st.columns(3)

    with card1:
        st.markdown(
            """
            <div class="glass-card">
                <h3>Research</h3>
                <p>Continuously gathers market data, reports, and contextual signals.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with card2:
        st.markdown(
            """
            <div class="glass-card">
                <h3>Analyze</h3>
                <p>Transforms raw financial data into structured insights and trading signals.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with card3:
        st.markdown(
            """
            <div class="glass-card">
                <h3>Decide</h3>
                <p>Applies consensus logic and confidence scoring before action.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    card4, card5, card6 = st.columns(3)

    with card4:
        st.markdown(
            """
            <div class="glass-card">
                <h3>Execute</h3>
                <p>Places simulated trades with validation, limits, and execution safety.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with card5:
        st.markdown(
            """
            <div class="glass-card">
                <h3>Observe</h3>
                <p>Streams real-time market updates and captures live system reactions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with card6:
        st.markdown(
            """
            <div class="glass-card">
                <h3>Control</h3>
                <p>Supports human approval queues, emergency stop, and audit trails.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">Run the System. Not Just a Model.</div>', unsafe_allow_html=True)

    st.write(
        """
        Operate agents directly through a unified dashboard.
        Select an agent, enter a financial query, run the system, and inspect structured outputs.
        """
    )

    st.code("Analyze Apple stock and generate a buy, sell, or hold signal with confidence.")

    st.markdown('<div class="section-title">Built for Safe Autonomous Execution</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric("Guardrails", "Enabled")

    with s2:
        st.metric("HITL", "Available")

    with s3:
        st.metric("MCP", "Ready")

    with s4:
        st.metric("Audit Trail", "Active")


# --------------------------------------------------
# Dashboard
# --------------------------------------------------
elif page == "Run Dashboard":
    st.title("📊 Financial Agents Dashboard")

    st.write(
        """
        Select an agent, enter a query, and run the financial AI workflow.
        """
    )

    agent_choice = st.selectbox(
        "Choose Agent",
        [
            "-- choose --",
            "Researcher",
            "Analyst",
            "Portfolio Manager",
            "Consensus",
            "Orchestrator",
            "Extended Orchestrator / MCP",
            "Full Pipeline",
        ]
    )

    symbol = st.text_input("Stock Symbol", value="AAPL")

    prompt = st.text_area(
        "Query / Prompt",
        value=f"Analyze {symbol} stock and generate a buy, sell, or hold signal with confidence.",
        height=130
    )

    if st.button("Run", type="primary"):
        if agent_choice == "-- choose --":
            st.warning("Please choose an agent first.")
        else:
            try:
                audit_record("ui_run_started", {
                    "agent": agent_choice,
                    "symbol": symbol,
                    "prompt": prompt
                })

                if agent_choice == "Researcher":
                    researcher = ResearcherAgent()
                    result = researcher.research(symbol)
                    render_json("Research Output", result)

                elif agent_choice == "Analyst":
                    researcher = ResearcherAgent()
                    analyst = AnalystAgent()

                    research_data = researcher.research(symbol)
                    result = analyst.analyze(research_data)

                    render_json("Research Input", research_data)
                    render_json("Analyst Output", result)

                elif agent_choice == "Portfolio Manager":
                    researcher = ResearcherAgent()
                    analyst = AnalystAgent()
                    portfolio = PortfolioManager()

                    research_data = researcher.research(symbol)
                    signal = analyst.analyze(research_data)
                    order = portfolio.to_order(signal)

                    render_json("Signal", signal)
                    render_json("Generated Order", order)

                elif agent_choice == "Consensus":
                    researcher = ResearcherAgent()
                    analyst = AnalystAgent()
                    consensus_agent = ConsensusAgent()

                    research_data = researcher.research(symbol)
                    signal_1 = analyst.analyze(research_data)
                    signal_2 = analyst.analyze(research_data)

                    result = consensus_agent.consensus([signal_1, signal_2])

                    render_json("Signals", [signal_1, signal_2])
                    render_json("Consensus Output", result)

                elif agent_choice == "Orchestrator":
                    orchestrator = Orchestrator()

                    order = {
                        "symbol": symbol,
                        "side": "BUY",
                        "quantity": 10,
                        "price": 100,
                        "order_type": "market"
                    }

                    result = orchestrator.execute(order)

                    render_json("Sample Order", order)
                    render_json("Orchestrator Result", result)

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
                        "order_type": "market"
                    }

                    result = ext.preflight_and_maybe_enqueue(order)
                    pending = ext.hitl.list_pending()

                    render_json("MCP / HITL Order", order)
                    render_json("Extended Orchestrator Result", result)
                    render_json("Pending HITL Queue", pending)

                elif agent_choice == "Full Pipeline":
                    result = run_full_pipeline(symbol)

                    render_json("Research Data", result["research"])
                    render_json("Signals", result["signals"])
                    render_json("Consensus", result["consensus"])
                    render_json("Order", result["order"])
                    render_json("Execution Result", result["execution"])

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

    if show_logs:
        st.divider()
        st.info(
            "Full Pipeline runs: Researcher → Analyst → Consensus → Portfolio Manager → Orchestrator."
        )


# --------------------------------------------------
# Observer Agent
# --------------------------------------------------
elif page == "Observer Agent":
    st.title("📡 Real-Time Observer Agent")

    st.write(
        """
        Simulate live market observation by streaming time-stamped price updates.
        """
    )

    observer_symbol = st.text_input("Symbol to monitor", value="AAPL")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Start Observer", use_container_width=True):
            result = start_background_observer(observer_symbol)
            st.success(result)

    with c2:
        if st.button("Stop Observer", use_container_width=True):
            result = stop_background_observer(observer_symbol)
            st.warning(result)

    with c3:
        if st.button("Show Observations", use_container_width=True):
            observations = get_observations(observer_symbol)
            st.json(observations[-20:])

    st.caption("Use Start Observer, wait a few seconds, then click Show Observations.")


# --------------------------------------------------
# Architecture
# --------------------------------------------------
elif page == "Architecture":
    st.title("🧭 System Architecture")

    st.markdown('<div class="section-title">A Coordinated Multi-Agent System</div>', unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        st.markdown('<div class="flow-box">Researcher</div>', unsafe_allow_html=True)

    with f2:
        st.markdown('<div class="flow-box">Analyst</div>', unsafe_allow_html=True)

    with f3:
        st.markdown('<div class="flow-box">Consensus</div>', unsafe_allow_html=True)

    with f4:
        st.markdown('<div class="flow-box">Portfolio</div>', unsafe_allow_html=True)

    with f5:
        st.markdown('<div class="flow-box">Orchestrator</div>', unsafe_allow_html=True)

    st.code(
        """
Researcher
   ↓
Analyst
   ↓
Consensus
   ↓
Portfolio Manager
   ↓
Orchestrator
   ↓
Execution / HITL / MCP / Audit
        """
    )

    st.markdown('<div class="section-title">System Capabilities</div>', unsafe_allow_html=True)

    st.write(
        """
        - Researcher gathers quotes and RAG documents.
        - Analyst creates BUY, SELL, or HOLD signals.
        - Consensus aggregates confidence-weighted signals.
        - Portfolio Manager converts decisions into orders.
        - Orchestrator validates and executes safely.
        - Extended Orchestrator adds HITL review and MCP-style control.
        - Audit Logger records important system actions.
        """
    )