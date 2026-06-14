import json
from pathlib import Path
import os

os.environ.setdefault('PYTHONPATH', 'backend')

from app.ingestion.normalizer import normalize

SAMPLE = Path('sample-logs') / 'mixed_events.json'
found = {}
with open(SAMPLE, 'r', encoding='utf-8') as fh:
    for line in fh:
        obj = json.loads(line)
        src = obj.get('log.source_type')
        if src in ('windows_security','sysmon','powershell','linux_auth') and src not in found:
            found[src] = normalize(obj)
        if len(found) == 4:
            break

print(json.dumps(found, indent=2, default=str))
