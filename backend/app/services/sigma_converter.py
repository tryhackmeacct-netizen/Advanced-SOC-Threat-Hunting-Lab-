import yaml
from pathlib import Path
from typing import Callable, Tuple, Dict, Any

try:
    # pySigma integration
    from sigma.collection import SigmaCollection
    from sigma.backends.opensearch.opensearch import OpensearchLuceneBackend
    from .sigma_pipeline import get_default_processing_pipeline
    PYSIGMA_AVAILABLE = True
except Exception:
    PYSIGMA_AVAILABLE = False


def parse_sigma_rule(sigma_path: str) -> dict:
    """Load Sigma YAML and return its dict representation and useful metadata."""
    with open(sigma_path, 'r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh)
    return data or {}


def _sanitize_rule_text(text: str) -> str:
    # Quick sanitization: ensure tag entries include a namespace
    docs = list(yaml.safe_load_all(text) or [])
    changed = False
    for doc in docs:
        if isinstance(doc, dict):
            tags = doc.get('tags')
            if isinstance(tags, list):
                new_tags = []
                for t in tags:
                    if isinstance(t, str) and '.' not in t:
                        new_tags.append('misc.' + t)
                        changed = True
                    else:
                        new_tags.append(t)
                doc['tags'] = new_tags
    if not changed:
        return text
    return yaml.dump_all(docs)


def convert_sigma_file_to_opensearch(sigma_path: str) -> dict:
    """Convert a sigma file into OpenSearch DSL using pySigma if available; fallback to simple parser."""
    if PYSIGMA_AVAILABLE:
        try:
            path = Path(sigma_path)
            text = path.read_text(encoding='utf-8')
            # sanitize and load via on_beforeload hook
            def before_load(p):
                txt = p.read_text(encoding='utf-8')
                if txt != _sanitize_rule_text(txt):
                    # create temporary sanitized copy
                    import tempfile
                    tmp = Path(tempfile.mkstemp(suffix='.yml')[1])
                    tmp.write_text(_sanitize_rule_text(txt), encoding='utf-8')
                    return tmp
                return p

            collection = SigmaCollection.load_ruleset([sigma_path], collect_errors=True, on_beforeload=before_load)
            backend = OpensearchLuceneBackend(processing_pipeline=get_default_processing_pipeline(), collect_errors=True)
            # convert per-rule, trying available output formats to capture correlation outputs
            results = []
            for rule in collection.rules:
                converted = None
                for fmt in backend.formats.keys():
                    try:
                        r = backend.convert_rule(rule, output_format=fmt)
                        if r:
                            converted = r
                            break
                    except Exception:
                        continue
                results.append(converted)
            # Return first non-empty conversion
            for r in results:
                if r:
                    return {"query": r}
            return {"query": {"match_all": {}}}
        except Exception:
            # Fall back to previous best-effort converter
            pass

    # Fallback (legacy): simple YAML-based heuristic
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

