import random
import uuid
from datetime import datetime

def gen_ssh_event(host, user, ip, ts, success=False):
    base = {
        "@timestamp": ts.isoformat(),
        "log.source_type": "linux_auth",
        "host": {"name": host, "os": "linux"},
        "user": {"name": user},
        "source": {"ip": ip},
        "message": "sshd: " + ("Accepted" if success else "Failed" ) + " password for {} from {}".format(user, ip),
        "event_uuid": str(uuid.uuid4()),
    }
    base["event.action"] = "ssh_login_success" if success else "ssh_login_failure"
    return base
