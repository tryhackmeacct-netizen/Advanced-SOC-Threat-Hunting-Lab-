import sys, json
sys.path.insert(0, '.')
from backend.app.services.sigma_converter import convert_sigma_file_to_opensearch
for fn in ['sigma-rules/account_enumeration.yml','sigma-rules/brute_force_windows.yml','sigma-rules/lateral_movement.yml','sigma-rules/suspicious_process.yml']:
    print('\n====',fn)
    print(json.dumps(convert_sigma_file_to_opensearch(fn), indent=2))
