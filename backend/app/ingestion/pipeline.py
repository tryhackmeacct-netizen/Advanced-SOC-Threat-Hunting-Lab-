import argparse
import json
from pathlib import Path
from datetime import datetime
from opensearchpy import OpenSearch, helpers
from pymongo import MongoClient
from app.core.config import settings
from app.ingestion.normalizer import normalize


def get_opensearch_client():
    return OpenSearch(settings.opensearch_url)


def get_mongo_client():
    return MongoClient(settings.mongo_uri)


def index_events(events):
    os_client = get_opensearch_client()
    actions = []
    for e in events:
        ts = e.get("@timestamp", datetime.utcnow().isoformat())
        index_name = "soc-logs-" + ts.split("T")[0]
        actions.append({"_index": index_name, "_source": e})
    if actions:
        helpers.bulk(os_client, actions)


def store_raw_mongo(events):
    mc = get_mongo_client()
    db = mc[settings.mongo_db]
    docs = [{"raw": e.get("raw", e), "normalized": e} for e in events]
    if docs:
        db.log_events.insert_many(docs)


def ingest_path(path: str):
    p = Path(path)
    all_events = []
    for f in p.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                norm = normalize(obj)
                all_events.append(norm)
    index_events(all_events)
    store_raw_mongo(all_events)
    return len(all_events)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="../sample-logs/", help="Path to NDJSON logs")
    args = parser.parse_args()
    cnt = ingest_path(args.path)
    print(f"Indexed {cnt} events")


if __name__ == "__main__":
    main()
