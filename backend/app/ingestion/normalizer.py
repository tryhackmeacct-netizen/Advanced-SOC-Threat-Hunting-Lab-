from datetime import datetime


def normalize(event: dict) -> dict:
    # Basic ECS-like mapping
    out = {}
    ts = event.get("@timestamp") or event.get("timestamp")
    try:
        out["@timestamp"] = ts
    except Exception:
        out["@timestamp"] = datetime.utcnow().isoformat()

    out["log.source_type"] = event.get("log.source_type")
    out["event"] = {
        "kind": event.get("event.kind", "event"),
        "category": event.get("event.category"),
        "action": event.get("event.action"),
    }
    out["host"] = event.get("host", {})
    out["user"] = event.get("user", {})
    out["source"] = event.get("source", {})
    out["destination"] = event.get("destination", {})
    out["process"] = event.get("process", {})
    out["raw"] = event
    return out
