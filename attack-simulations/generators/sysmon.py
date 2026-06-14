import random
import uuid
from datetime import datetime

def gen_sysmon(event_id: int, host: str, user: str, ts: datetime, extra=None):
    base = {
        "@timestamp": ts.isoformat(),
        "log.source_type": "sysmon",
        "event_id": event_id,
        "host": {"name": host, "os": "windows"},
        "user": {"name": user},
        "message": f"Sysmon Event {event_id} on {host}",
        "event_uuid": str(uuid.uuid4()),
    }
    if extra:
        base.update(extra)
    return base


def process_create(host, user, ts, process_name, cmdline, pid, parent_pid=None):
    return gen_sysmon(1, host, user, ts, {"event.action": "process_create", "process": {"name": process_name, "command_line": cmdline, "pid": pid, "parent_pid": parent_pid}})


def network_connect(host, user, ts, src_ip, dst_ip, dst_port, process_name):
    return gen_sysmon(3, host, user, ts, {"event.action": "network_connect", "source": {"ip": src_ip}, "destination": {"ip": dst_ip, "port": dst_port}, "process": {"name": process_name}})


def lsass_access(host, user, ts, process_name="lsass.exe", target_process="lsass.exe"):
    return gen_sysmon(10, host, user, ts, {"event.action": "lsass_access", "process": {"name": process_name}, "target": {"process": target_process}})


def reg_change(host, user, ts, reg_path, reg_op="set"):
    return gen_sysmon(13, host, user, ts, {"event.action": "registry_change", "registry": {"path": reg_path, "operation": reg_op}})
