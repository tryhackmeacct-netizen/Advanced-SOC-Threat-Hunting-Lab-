import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.app.services.sigma_converter import convert_sigma_file_to_opensearch, build_predicate_from_sigma

RULE_DIR = Path('sigma-rules')
SAMPLE_LOGS = Path('sample-logs/mixed_events.json')

# Load sample events
events = []
with SAMPLE_LOGS.open('r', encoding='utf-8') as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))

# Helper to simulate simple query_string matching for converted DSLs
import re

def simple_matches(converted):
    """Return True if any event matches the very simple converted query representation."""
    if not converted:
        return False
    # converted is typically a list of query dicts
    for item in converted:
        if not isinstance(item, dict):
            continue
        q = item.get('query') or {}
        # drill for query_string
        qs = None
        if isinstance(q, dict):
            if 'bool' in q and isinstance(q['bool'], dict):
                must = q['bool'].get('must', [])
                for m in must:
                    if 'query_string' in m:
                        qs = m['query_string'].get('query')
            elif 'query_string' in q:
                qs = q['query_string'].get('query')
        if qs:
            # Very simple parsing: look for event_id:<num> and process.name:<name>
            eid = None
            pname = None
            m = re.search(r'event_id:(\d+)', qs)
            if m:
                eid = int(m.group(1))
            m = re.search(r'process\.name:([\w\.-]+)', qs)
            if m:
                pname = m.group(1)
            # Check events for match
            for ev in events:
                if eid is not None and ev.get('event_id') == eid:
                    return True
                if pname is not None:
                    p = ev.get('process', {})
                    if isinstance(p, dict) and p.get('name') == pname:
                        return True
    return False

# Run checks for two rules
proc_rule = RULE_DIR / 'suspicious_process.yml'
acct_rule = RULE_DIR / 'account_enumeration.yml'

proc_conv = convert_sigma_file_to_opensearch(str(proc_rule))
acct_conv = convert_sigma_file_to_opensearch(str(acct_rule))

proc_json = json.dumps(proc_conv)
acct_json = json.dumps(acct_conv)

assert 'process.name' in proc_json or 'mimikatz' in proc_json, 'Process-based rule did not map to process.name in DSL'
assert '4720' in acct_json or 'event_id' in acct_json, 'Auth/account rule did not map to event_id in DSL'

# Parity check: ensure pySigma conversions would match same set of rules as legacy predicate
all_rules = list(RULE_DIR.glob('*.yml'))
legacy_matches = set()
pysigma_matches = set()
for rf in all_rules:
    pred = build_predicate_from_sigma(str(rf))
    legacy_hit = any(pred({'raw': e, **e}) for e in events)
    if legacy_hit:
        legacy_matches.add(rf.name)
    conv = convert_sigma_file_to_opensearch(str(rf))
    # Our converter returns {"query": [...]}
    converted = conv.get('query')
    pysigma_hit = simple_matches(converted)
    if pysigma_hit:
        pysigma_matches.add(rf.name)

print('legacy_matches_count', len(legacy_matches))
print('pysigma_matches_count', len(pysigma_matches))
print('legacy:', sorted(legacy_matches))
print('pysigma:', sorted(pysigma_matches))

# Expect parity
assert len(legacy_matches) == len(pysigma_matches), 'Parity mismatch between legacy predicate and pySigma conversions'
print('Parity OK: both matched', len(legacy_matches), 'rules')
