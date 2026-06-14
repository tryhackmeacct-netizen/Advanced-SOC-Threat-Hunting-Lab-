from datetime import datetime, timedelta
import importlib.util
from pathlib import Path
gen_dir = Path(__file__).resolve().parent.parent / "generators"

def _load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

linux_auth = _load_mod("linux_auth", gen_dir / "linux_auth.py")
windows_security = _load_mod("windows_security", gen_dir / "windows_security.py")
sysmon = _load_mod("sysmon", gen_dir / "sysmon.py")
powershell = _load_mod("powershell", gen_dir / "powershell.py")

import random
import json


def ssh_bruteforce_sequence(src_ip, target_host, user_prefix, start_ts, attempts=10):
    events = []
    for i in range(attempts):
        ts = start_ts + timedelta(seconds=i * 10)
        user = f"{user_prefix}{random.randint(1,50)}"
        events.append(linux_auth.generate_ssh_event if False else linux_auth.gen_ssh_event(target_host, user, src_ip, ts, success=(i==attempts-1)))
    return events


def windows_bruteforce_sequence(src_ip, target_host, user, start_ts, attempts=8):
    events = []
    for i in range(attempts):
        ts = start_ts + timedelta(seconds=i * 5)
        events.append(windows_security.generate_login_failure(target_host, user, src_ip, ts))
    # final success
    events.append(windows_security.generate_login_success(target_host, user, src_ip, start_ts + timedelta(seconds=attempts * 5)))
    return events


def privilege_escalation_chain(host, user, ip, start_ts):
    events = []
    events.append(windows_security.generate_priv_esc(host, user, ip, start_ts))
    events.append(sysmon.process_create(host, user, start_ts + timedelta(seconds=2), "mimikatz.exe", "mimikatz.exe sekurlsa::logonpasswords", 4321))
    events.append(sysmon.lsass_access(host, user, start_ts + timedelta(seconds=3)))
    return events


def powershell_encoded_download(host, user, ip, start_ts, url):
    script = powershell.sample_download_execute(url)
    events = []
    events.append(powershell.gen_powershell_script(host, user, start_ts, script, encoded=True))
    events.append(sysmon.process_create(host, user, start_ts + timedelta(seconds=1), "powershell.exe", script, 5555))
    return events


def persistence_registry(host, user, ip, start_ts):
    events = []
    events.append(sysmon.reg_change(host, user, start_ts, r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run\\Updater", reg_op="set"))
    events.append(windows_security.generate_scheduled_task(host, user, ip, start_ts + timedelta(seconds=1), task_name="UpdaterJob"))
    return events
