import importlib
import threading
import uuid
import time
from collections import defaultdict

from tools.execution_tool import ExecutionTool
from security.guardrails import PreExecutionChecks, EmergencyStop
from audit.audit_logger import audit_record


class Orchestrator:
    def __init__(self):
        self.exec_tool = ExecutionTool(simulate=True)
        self.guard = PreExecutionChecks()
        self.stop = EmergencyStop()

    def execute(self, order: dict):
        audit_record("orchestrator_request", order)

        if self.stop.is_triggered():
            audit_record("orchestrator_blocked", {"reason": "emergency_stop"})
            return {
                "status": "blocked",
                "reason": "emergency_stop"
            }

        if order.get("side") == "HOLD":
            return {
                "status": "skipped",
                "reason": "HOLD signal does not create an executable order"
            }

        ok, reason = self.guard.check(order)

        if not ok:
            audit_record("orchestrator_failed_checks", {
                "reason": reason,
                "order": order
            })

            return {
                "status": "rejected",
                "reason": reason
            }

        normalized_order = {
            "symbol": order["symbol"],
            "side": order["side"],
            "quantity": order.get("quantity", order.get("qty", 0)),
            "limit_price": order.get("limit_price", order.get("price")),
            "order_type": order.get("order_type", "market")
        }

        res = self.exec_tool.place_order(normalized_order)

        audit_record("orchestrator_executed", {
            "order": normalized_order,
            "result": res
        })

        return res


def run_agent(agent_name: str, prompt: str, **kwargs):
    try:
        module_name = f"agents.{agent_name}"
        module = importlib.import_module(module_name)

        if hasattr(module, "respond"):
            return getattr(module, "respond")(prompt)

        for fn_name in ("main", "run", "handle"):
            if hasattr(module, fn_name):
                try:
                    return getattr(module, fn_name)(prompt)
                except Exception as e:
                    return f"Error in agent {agent_name}.{fn_name}: {e}"

        return f"Agent '{agent_name}' found but no respond/main/run/handle method present."

    except Exception as e:
        return f"Error running agent '{agent_name}': {e}"


_emergency_stop = {"engaged": False}


def emergency_stop_engage():
    _emergency_stop["engaged"] = True
    return {"status": "engaged"}


def emergency_stop_release():
    _emergency_stop["engaged"] = False
    return {"status": "released"}


def is_emergency_engaged():
    return _emergency_stop.get("engaged", False)


_human_approval_queue = []


def submit_for_approval(order: dict):
    order_id = str(uuid.uuid4())

    _human_approval_queue.insert(0, {
        "id": order_id,
        "order": order,
        "timestamp": time.time(),
        "status": "pending"
    })

    audit_record("hitl_enqueue", {
        "id": order_id,
        "order": order
    })

    return {
        "id": order_id,
        "status": "pending"
    }


def list_approval_queue():
    return list(_human_approval_queue)


def approve_order(order_id: str, reviewer: str = "admin"):
    for item in _human_approval_queue:
        if item["id"] == order_id:
            item["status"] = "approved"
            item["reviewer"] = reviewer
            return {
                "id": order_id,
                "status": "approved"
            }

    return {
        "id": order_id,
        "status": "not_found"
    }


def reject_order(order_id: str, reviewer: str = "admin"):
    for item in _human_approval_queue:
        if item["id"] == order_id:
            item["status"] = "rejected"
            item["reviewer"] = reviewer
            return {
                "id": order_id,
                "status": "rejected"
            }

    return {
        "id": order_id,
        "status": "not_found"
    }


class MCPAdapter:
    """
    Standard MCP-compatible wrapper around orchestrator/HITL actions.
    """

    def __init__(self, orchestrator: Orchestrator):
        self.orch = orchestrator

    def call(self, action: str, payload: dict):
        action = action.lower()

        if action == "execute":
            return self.orch.execute(payload)

        elif action == "emergency_stop":
            return emergency_stop_engage()

        elif action == "release_stop":
            return emergency_stop_release()

        elif action == "list_queue":
            return list_approval_queue()

        elif action == "approve":
            order_id = payload.get("id")
            reviewer = payload.get("reviewer", "mcp_bot")
            return approve_order(order_id, reviewer)

        elif action == "reject":
            order_id = payload.get("id")
            reviewer = payload.get("reviewer", "mcp_bot")
            return reject_order(order_id, reviewer)

        else:
            return {
                "status": "unknown_action",
                "action": action
            }


class ConsensusAgent:
    def __init__(self, threshold=0.6):
        self.threshold = threshold

    def consensus(self, signals: list):
        scores = defaultdict(float)

        for s in signals:
            sig = s.get("signal", "HOLD").upper()
            conf = float(s.get("confidence", 0.5))
            scores[sig] += conf

        total = sum(scores.values()) or 1.0

        for k in scores.keys():
            scores[k] /= total

        decision = max(scores.items(), key=lambda kv: kv[1])[0]
        support = dict(scores)
        approved = support.get(decision, 0) >= self.threshold

        return {
            "decision": decision,
            "support": support,
            "threshold": self.threshold,
            "approved": approved
        }


def main(prompt: str):
    try:
        if "analyst" in prompt.lower():
            return run_agent("analyst", prompt)

        elif "researcher" in prompt.lower():
            return run_agent("researcher", prompt)

        elif "portfolio" in prompt.lower():
            return run_agent("portfolio_manager", prompt)

        else:
            return (
                f"Orchestrator received: {prompt}\n\n"
                "Ready to run analyst, researcher, or portfolio_manager. "
                "Specify which in your prompt."
            )

    except Exception as e:
        return f"Error in orchestrator main: {e}"
