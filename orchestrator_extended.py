import json
import os
import time
from typing import Dict

from audit.audit_logger import audit_record
from orchestrator import Orchestrator, MCPAdapter


QUEUE_FILE = os.getenv("HITL_QUEUE_FILE", "hitl_queue.jsonl")


class HITLQueue:
    """
    Persistent human-approval queue for high-value orders.
    Writes/reads JSONL file for durability.
    """

    def __init__(self, file=QUEUE_FILE):
        self.file = file

    def add(self, item: Dict):
        rec = {
            "ts": time.time(),
            "item": item,
            "status": "pending"
        }

        with open(self.file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

        audit_record("hitl_enqueue", rec)
        return rec

    def list_pending(self):
        items = []

        if not os.path.exists(self.file):
            return items

        with open(self.file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line.strip())
                    if j.get("status", "pending") == "pending":
                        items.append(j)
                except Exception:
                    continue

        return items

    def update_status(self, ts, status, reviewer=None):
        if not os.path.exists(self.file):
            return False

        updated = []
        changed = False

        with open(self.file, "r", encoding="utf-8") as f:
            for line in f:
                j = json.loads(line.strip())

                if j.get("ts") == ts:
                    j["status"] = status
                    j["reviewer"] = reviewer
                    changed = True

                updated.append(j)

        with open(self.file, "w", encoding="utf-8") as f:
            for j in updated:
                f.write(json.dumps(j) + "\n")

        audit_record("hitl_update", {
            "ts": ts,
            "status": status,
            "reviewer": reviewer
        })

        return changed


class ExtendedOrchestrator:
    """
    Adds preflight checks, HITL queueing, and MCP adapter support.
    """

    def __init__(self, base_orchestrator: Orchestrator, hitl_threshold_notional=10000):
        self.base = base_orchestrator
        self.hitl = HITLQueue()
        self.hitl_threshold = hitl_threshold_notional
        self.mcp = MCPAdapter(self.base)

    def preflight_and_maybe_enqueue(self, order: Dict):
        qty = order.get("quantity", order.get("qty", 0))
        price = order.get("price", order.get("limit_price", 0) or 0)
        notional = qty * price

        audit_record("orchestrator_preflight", {
            "order": order,
            "notional": notional
        })

        if notional >= self.hitl_threshold:
            rec = self.hitl.add({
                "order": order,
                "notional": notional
            })

            return {
                "status": "queued_for_approval",
                "queue_record": rec
            }

        res = self.base.execute(order)

        audit_record("orchestrator_execute", {
            "order": order,
            "result": res
        })

        return {
            "status": "executed",
            "result": res
        }

    def mcp_execute(self, order: Dict):
        return self.mcp.call("execute", order)

    def mcp_list_queue(self):
        return self.mcp.call("list_queue", {})

    def mcp_approve(self, ts, reviewer="mcp_bot"):
        return self.mcp.call("approve", {
            "id": ts,
            "reviewer": reviewer
        })

    def mcp_reject(self, ts, reviewer="mcp_bot"):
        return self.mcp.call("reject", {
            "id": ts,
            "reviewer": reviewer
        })

    def mcp_emergency_stop(self):
        return self.mcp.call("emergency_stop", {})

    def mcp_release_stop(self):
        return self.mcp.call("release_stop", {})


def main(prompt: str):
    try:
        base_orch = Orchestrator()
        ext_orch = ExtendedOrchestrator(base_orch)

        return (
            f"Extended Orchestrator received: {prompt}\n\n"
            "Supports human-in-the-loop approval queue. "
            "Ready to process orders with review."
        )

    except Exception as e:
        return f"Error in extended orchestrator main: {e}"
