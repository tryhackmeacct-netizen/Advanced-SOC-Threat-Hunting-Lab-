from opensearchpy import OpenSearch
from pymongo import MongoClient
from app.core.config import settings
from pathlib import Path
from .sigma_converter import convert_sigma_file_to_opensearch
import json


class DetectionEngine:
    def __init__(self):
        self.os_client = OpenSearch(settings.opensearch_url)
        self.mongo = MongoClient(settings.mongo_uri)
        self.db = self.mongo[settings.mongo_db]

    def load_sigma_rules(self, dir_path: str = None):
        dir_path = dir_path or Path.cwd() / 'sigma-rules'
        rules = []
        for f in Path(dir_path).glob('*.yml'):
            rules.append(str(f))
        return rules

    def run_once(self, sigma_dir: str = None):
        rules = self.load_sigma_rules(sigma_dir)
        alerts_created = 0
        for rpath in rules:
            try:
                q = convert_sigma_file_to_opensearch(rpath)
            except ImportError:
                # no converter available; use a fallback that searches for event IDs mentioned in YAML
                with open(rpath, 'r', encoding='utf-8') as fh:
                    txt = fh.read()
                # naive: look for numbers like 4625, 4672, 1, 3, 10, 4698
                ids = []
                for token in ['4625','4624','4672','1','3','10','4698','4104','4720']:
                    if token in txt:
                        ids.append(token)
                if ids:
                    body = {"query": {"bool": {"should": [{"match": {"raw.event_id": int(i)}} for i in ids]}}}
                else:
                    body = {"query": {"match_all": {}}}
            else:
                body = q

            # run the query
            res = self.os_client.search(index="soc-logs-*", body=body, size=100)
            hits = res.get('hits', {}).get('hits', [])
            for h in hits:
                alert = {
                    "rule_name": Path(rpath).stem,
                    "severity": "high",
                    "mitre": [],
                    "matched_events": [h['_source']],
                    "description": f"Auto-detected by rule {Path(rpath).stem}",
                    "created_at": __import__('datetime').datetime.utcnow().isoformat()
                }
                self.db.alerts.insert_one(alert)
                alerts_created += 1

        return alerts_created
