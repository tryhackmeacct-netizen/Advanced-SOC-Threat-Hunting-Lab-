from pathlib import Path
import json
from sigma.collection import SigmaCollection
from sigma.backends.opensearch.opensearch import OpensearchLuceneBackend
import yaml
import tempfile


def sanitize_rule_file(path: Path) -> Path:
    """Read a YAML rule file and ensure tags have a namespace (contain a dot).
    Returns path to a temporary sanitized copy used for loading by pySigma."""
    with path.open('r', encoding='utf-8') as fh:
        docs = list(yaml.safe_load_all(fh) or [])

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
        return path

    tmp = Path(tempfile.mkstemp(suffix='.yml')[1])
    with tmp.open('w', encoding='utf-8') as fh:
        yaml.dump_all(docs, fh)
    return tmp

RULE_DIR = Path("sigma-rules")
OUT_DIR = Path("scripts/generated_dsl")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def before_load(path: Path) -> Path | None:
    return sanitize_rule_file(path)


# Load all rules (collect_errors=True to tolerate non-UUID ids in repo rules)
collection = SigmaCollection.load_ruleset([str(RULE_DIR)], collect_errors=True, on_beforeload=before_load)
backend = OpensearchLuceneBackend(collect_errors=True)

# Convert ruleset per-rule to tolerate conversion errors on individual rules
for i, rule in enumerate(collection.rules):
    try:
        converted = backend.convert_rule(rule, output_format='dsl_lucene')
    except Exception as e:
        print(f"Conversion failed for rule '{getattr(rule,'title',str(i))}':", e)
        converted = None

    out_path = OUT_DIR / (getattr(rule, 'title', f'rule_{i}').replace(' ', '_')[:200] + '.json')
    try:
        with out_path.open('w', encoding='utf-8') as fh:
            json.dump({'title': getattr(rule, 'title', None), 'converted': converted}, fh, indent=2)
    except Exception as e:
        print('Failed to write', out_path, e)

print('Wrote DSL outputs to', OUT_DIR)
