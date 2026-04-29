import json
import os
import datetime
import uuid


AUDIT_FILE = os.getenv("AUDIT_FILE", "audit_trail.jsonl")

audit_dir = os.path.dirname(AUDIT_FILE)
if audit_dir and not os.path.exists(audit_dir):
    os.makedirs(audit_dir, exist_ok=True)


def audit_record(event_type: str, payload: dict, actor: str = None):
    """Writes down what happened, when, and who did it - our digital paper trail."""
    rec = {
        "id": str(uuid.uuid4()),
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        "payload": payload
    }

    if actor:
        rec["actor"] = actor

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

    return rec
