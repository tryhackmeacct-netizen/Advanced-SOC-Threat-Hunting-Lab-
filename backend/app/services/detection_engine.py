import json
from opensearchpy import OpenSearch
from pymongo import MongoClient
from app.core.config import settings
from pathlib import Path
from .sigma_converter import convert_sigma_file_to_opensearch, build_predicate_from_sigma, parse_sigma_rule
from datetime import datetime, timedelta


class DetectionEngine:
    def __init__(self):
        self.os_client = None
        self.mongo = None
        self.db = None
        # Lazy init so tests without services can still run
        try:
            self.os_client = OpenSearch(settings.opensearch_url)
        except Exception:
            self.os_client = None
        try:
            self.mongo = MongoClient(settings.mongo_uri)
            self.db = self.mongo[settings.mongo_db]
        except Exception:
            self.mongo = None
            self.db = None

    def load_sigma_rules(self, dir_path: str = None):
        dir_path = Path(dir_path or Path.cwd() / 'sigma-rules')
        rules = []
        for f in dir_path.glob('*.yml'):
            rules.append(str(f))
        return rules

    def _create_or_update_alert(self, rule_id: str, rule_name: str, metadata: dict, matched_hits: list):
        if self.db is None:
            return None
        now = datetime.utcnow()
        # timeframe from matched events
        times = [h.get('@timestamp') or h.get('created_at') or now.isoformat() for h in matched_hits]
        # naive parse to datetime where possible
        parsed = []
        for t in times:
            try:
                parsed.append(datetime.fromisoformat(t))
            except Exception:
                pass
        start = min(parsed).isoformat() if parsed else now.isoformat()
        end = max(parsed).isoformat() if parsed else now.isoformat()

        # dedupe: existing open alert with same rule_id and overlapping timeframe/host
        hostnames = set([h.get('host', {}).get('name') for h in matched_hits if h.get('host')])
        query = {"rule_id": rule_id}
        existing = self.db.alerts.find_one(query)
        if existing and existing.get('status','new') != 'closed':
            # increment
            self.db.alerts.update_one({'_id': existing['_id']}, {'$inc': {'match_count': 1}, '$set': {'updated_at': now.isoformat()}})
            return existing

        alert = {
            'rule_id': rule_id,
            'rule_name': rule_name,
            'severity': metadata.get('level') or metadata.get('severity') or 'medium',
            'mitre_tactics': metadata.get('tags', []),
            'matched_event_ids': [h.get('_id') or h.get('event_uuid') for h in matched_hits],
            'matched_event_summary': [ { 'host': h.get('host'), 'user': h.get('user'), 'message': h.get('message') } for h in matched_hits],
            'timestamp_range': {'start': start, 'end': end},
            'recommended_response': metadata.get('recommended_response',''),
            'status': 'new',
            'match_count': 1,
            'created_at': now.isoformat()
        }
        self.db.alerts.insert_one(alert)
        return alert

    def run_once(self, sigma_dir: str = None, dry_run_events: list = None):
        rules = self.load_sigma_rules(sigma_dir)
        alerts_created = 0
        for rpath in rules:
            rule_meta = parse_sigma_rule(rpath)
            rule_id = rule_meta.get('id') or Path(rpath).stem
            rule_name = rule_meta.get('title') or Path(rpath).stem
            # build opensearch query and python predicate
            q = convert_sigma_file_to_opensearch(rpath)
            predicate = build_predicate_from_sigma(rpath)

            matched_hits = []
            # If OpenSearch client available, run query there
            if self.os_client is not None:
                try:
                    res = self.os_client.search(index='soc-logs-*', body=q, size=100)
                    hits = res.get('hits', {}).get('hits', [])
                    matched_hits = [h['_source'] for h in hits]
                except Exception:
                    matched_hits = []

            # If no OpenSearch or for dry-run, evaluate predicate over provided events
            if dry_run_events is not None:
                for ev in dry_run_events:
                    try:
                        if predicate(ev):
                            matched_hits.append(ev)
                    except Exception:
                        pass

            if matched_hits:
                self._create_or_update_alert(rule_id, rule_name, rule_meta, matched_hits)
                alerts_created += 1

        return alerts_created

