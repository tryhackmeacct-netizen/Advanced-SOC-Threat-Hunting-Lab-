import random
import uuid
from datetime import datetime, timedelta

def gen_event(event_id: int, host: str, user: str, ip: str, ts: datetime, extra=None):
    base = {
        "@timestamp": ts.isoformat(),
        "log.source_type": "windows_security",
        "event_id": event_id,
        "host": {"name": host, "os": "windows"},
        "user": {"name": user},
        "source": {"ip": ip},
        "message": f"Windows Event {event_id} on {host}",
        "event_uuid": str(uuid.uuid4()),
    }
    if extra:
        base.update(extra)
    return base


def generate_login_success(host, user, ip, ts):
    return gen_event(4624, host, user, ip, ts, {"event.action": "logon_success"})


def generate_login_failure(host, user, ip, ts, failure_reason="Unknown"):
    return gen_event(4625, host, user, ip, ts, {"event.action": "logon_failure", "failure_reason": failure_reason})


def generate_priv_esc(host, user, ip, ts):
    return gen_event(4672, host, user, ip, ts, {"event.action": "privilege_elevation"})


def generate_scheduled_task(host, user, ip, ts, task_name="MaliciousTask"):
    return gen_event(4698, host, user, ip, ts, {"event.action": "create_scheduled_task", "task_name": task_name})
