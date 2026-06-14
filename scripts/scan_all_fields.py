import yaml
from pathlib import Path
from collections import defaultdict

sr_dir = Path('sigma-rules')
all_fields = defaultdict(list)

for f in sorted(sr_dir.glob('*.yml')):
    txt = f.read_text(encoding='utf-8')
    parsed = yaml.safe_load(txt) or {}
    det = parsed.get('detection', {})
    
    # Collect fields from selection
    selection = det.get('selection', {})
    if isinstance(selection, dict):
        for field in selection.keys():
            all_fields[field].append(f.stem)

print('Field usage across all 8 rules:\n')
for field in sorted(all_fields.keys()):
    rules = ', '.join(all_fields[field])
    print(f'  {field:25} used in: {rules}')
