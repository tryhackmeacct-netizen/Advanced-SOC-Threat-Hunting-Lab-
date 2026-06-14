import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json
import importlib.util
from pathlib import Path
scenarios_path = Path(__file__).resolve().parent / "scenarios" / "attack_chains.py"
spec = importlib.util.spec_from_file_location("attack_chains", scenarios_path)
scenarios = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenarios)
windows_bruteforce_sequence = scenarios.windows_bruteforce_sequence
privilege_escalation_chain = scenarios.privilege_escalation_chain
powershell_encoded_download = scenarios.powershell_encoded_download
persistence_registry = scenarios.persistence_registry
import random


SAMPLE_DIR = Path(__file__).resolve().parents[1] / "sample-logs"


def write_ndjson(filename, events):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e))
            f.write("\n")


def generate(args):
    now = datetime.utcnow()
    events = []
    # benign noise
    for i in range(args.noise):
        ts = now - timedelta(seconds=random.randint(0, 3600))
        events.append({"@timestamp": ts.isoformat(), "log.source_type": "system", "message": "Routine system event", "host": {"name": f"host{random.randint(1,5)}"}})

    # attack chains
    events += windows_bruteforce_sequence("10.0.0.5", "host1", "svc", now - timedelta(minutes=30), attempts=6)
    events += privilege_escalation_chain("host1", "svc01", "10.0.0.5", now - timedelta(minutes=29))
    events += powershell_encoded_download("host1", "svc01", "10.0.0.5", now - timedelta(minutes=28), "http://malicious.example/payload.ps1")
    events += persistence_registry("host1", "svc01", "10.0.0.5", now - timedelta(minutes=27))

    out = SAMPLE_DIR / "mixed_events.json"
    write_ndjson(out, events)
    print(f"Wrote {len(events)} events to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--noise", type=int, default=50)
    args = parser.parse_args()
    generate(args)
