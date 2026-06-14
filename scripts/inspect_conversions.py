import sys
sys.path.insert(0, '.')
from backend.app.services.sigma_converter import convert_sigma_file_to_opensearch
from pathlib import Path
for fn in ['sigma-rules/account_enumeration.yml','sigma-rules/brute_force_windows.yml','sigma-rules/lateral_movement.yml']:
    print('\n====',fn)
    print(convert_sigma_file_to_opensearch(fn))
