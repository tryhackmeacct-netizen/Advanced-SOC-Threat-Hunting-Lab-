from app.core.config import settings
from opensearchpy import OpenSearch


def setup_template():
    client = OpenSearch(settings.opensearch_url)
    template = {
        "index_patterns": ["soc-logs-*"],
        "template": {
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "host.name": {"type": "keyword"},
                    "host.os": {"type": "keyword"},
                    "user.name": {"type": "keyword"},
                    "source.ip": {"type": "ip"},
                    "destination.ip": {"type": "ip"},
                    "process.name": {"type": "keyword"},
                    "process.command_line": {"type": "text"},
                    "log.source_type": {"type": "keyword"}
                }
            }
        }
    }
    client.indices.put_index_template(name="soc-logs-template", body=template)
    print("Index template applied from backend container")


if __name__ == "__main__":
    setup_template()
