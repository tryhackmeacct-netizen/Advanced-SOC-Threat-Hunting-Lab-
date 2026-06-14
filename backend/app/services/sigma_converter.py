import yaml
from pathlib import Path
from typing import Callable, Tuple, Dict, Any


def parse_sigma_rule(sigma_path: str) -> dict:
    """Load Sigma YAML and return its dict representation and useful metadata."""
    with open(sigma_path, 'r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh)
    return data or {}


def convert_sigma_file_to_opensearch(sigma_path: str) -> dict:
    """Best-effort conversion: create a simple OpenSearch DSL query based on event_id and script_block_text presence.

    This function returns a dict representing an OpenSearch query body. It's intentionally conservative;
    for full fidelity use pySigma backends (not pinned here to avoid dependency conflicts).
    """
    rule = parse_sigma_rule(sigma_path)
    detection = rule.get('detection', {})
    # Look for explicit event_id tokens in detection selectors
    ids = set()
    def collect_ids(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == 'event_id':
                    if isinstance(v, list):
                        for x in v: ids.add(int(x))
                    else:
                        try:
                            ids.add(int(v))
                        except Exception:
                            pass
                else:
                    collect_ids(v)
        elif isinstance(node, list):
            for it in node:
                collect_ids(it)

    collect_ids(detection)

    if ids:
        should = [{"term": {"raw.event_id": i}} for i in ids]
        return {"query": {"bool": {"should": should}}}

    # fallback: match script_block_text contains common tokens
    txt = yaml.dump(rule)
    if 'IEX' in txt or 'DownloadString' in txt or 'script_block_text' in txt:
        return {"query": {"match": {"raw.script_block_text": "IEX"}}}

    return {"query": {"match_all": {}}}


def build_predicate_from_sigma(sigma_path: str) -> Callable[[dict], bool]:
    """Construct a simple Python predicate to test a normalized event against the sigma rule.

    This is used for unit testing without OpenSearch available.
    """
    rule = parse_sigma_rule(sigma_path)
    detection = rule.get('detection', {})

    # Very small subset: check event_id equality and script_block_text contains
    ids = []
    if isinstance(detection, dict):
        for k, v in detection.items():
            if k == 'selection' and isinstance(v, dict):
                eid = v.get('event_id')
                if eid:
                    if isinstance(eid, list):
                        ids.extend([int(x) for x in eid])
                    else:
                        try:
                            ids.append(int(eid))
                        except Exception:
                            pass
                # script text
                sb = v.get('script_block_text')
                if sb:
                    token = sb if isinstance(sb, str) else None

    def predicate(event: dict) -> bool:
        raw = event.get('raw', {})
        if ids:
            try:
                if int(raw.get('event_id', -1)) in ids:
                    return True
            except Exception:
                pass
        # script block check
        s = raw.get('script_block_text') or raw.get('message','')
        if isinstance(s, str) and ('IEX' in s or 'DownloadString' in s or 'IEX' in raw.get('script_block_decoded','')):
            return True
        return False

    return predicate

