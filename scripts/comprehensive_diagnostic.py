#!/usr/bin/env python3
"""
Comprehensive diagnostic for pySigma parity issue.
Loads brute_force_windows.yml, applies pipeline, prints field mappings and conversion output.
"""
import json
import yaml
import sys
from pathlib import Path

# Ensure repo root on path for backend imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import pySigma and project components
try:
    from sigma.collection import SigmaCollection
    from sigma.backends.opensearch.opensearch import OpensearchLuceneBackend
    from backend.app.services.sigma_pipeline import DEFAULT_FIELD_MAPPING, get_default_processing_pipeline
    PYSIGMA_OK = True
except Exception as e:
    print(f'Import failed: {e}')
    sys.exit(1)

RULE_PATH = 'sigma-rules/brute_force_windows.yml'

def sanitize_yaml(text: str) -> str:
    """Ensure tags have namespace (dot)."""
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
                if changed:
                    doc['tags'] = new_tags
    if not changed:
        return text
    return '\n'.join([yaml.dump(d) for d in docs])


def main():
    print('='*80)
    print('STEP 1: Load rule YAML and extract detection field names')
    print('='*80)
    
    p = Path(RULE_PATH)
    raw_yaml = p.read_text(encoding='utf-8')
    parsed = yaml.safe_load(raw_yaml)
    
    print(f'\nRule file: {RULE_PATH}')
    print(f'Rule title: {parsed.get("title")}')
    print(f'Rule id: {parsed.get("id")}')
    
    detection = parsed.get('detection', {})
    print(f'\nRaw detection section keys: {list(detection.keys())}')
    print(f'\nFull detection YAML:\n{yaml.dump(detection)}')
    
    # Extract field names used in detection.selection
    sigma_fields_in_rule = set()
    selection = detection.get('selection', {})
    if isinstance(selection, dict):
        sigma_fields_in_rule.update(selection.keys())
    
    print(f'\nSigma field names used in rule: {sorted(sigma_fields_in_rule)}')
    
    print('\n' + '='*80)
    print('STEP 2: Load DEFAULT_FIELD_MAPPING from pipeline')
    print('='*80)
    
    print(f'\nDEFAULT_FIELD_MAPPING keys (pySigma will map FROM these):')
    for k in sorted(DEFAULT_FIELD_MAPPING.keys()):
        print(f'  {k:25} -> {DEFAULT_FIELD_MAPPING[k]}')
    
    print('\n' + '='*80)
    print('STEP 3: Compare field names (DIFF)')
    print('='*80)
    
    mapping_keys = set(DEFAULT_FIELD_MAPPING.keys())
    print(f'\nSigma fields in rule:      {sorted(sigma_fields_in_rule)}')
    print(f'pySigma mapping keys:      {sorted(mapping_keys)}')
    
    missing_in_mapping = sigma_fields_in_rule - mapping_keys
    unmapped = mapping_keys - sigma_fields_in_rule
    
    if missing_in_mapping:
        print(f'\n*** DIFF FOUND ***')
        print(f'Fields in rule BUT NOT in DEFAULT_FIELD_MAPPING: {sorted(missing_in_mapping)}')
    else:
        print(f'\n[OK] All rule fields are in DEFAULT_FIELD_MAPPING')
    
    if unmapped:
        print(f'\nFields in DEFAULT_FIELD_MAPPING but NOT used in rule: {sorted(unmapped)[:5]}...')
    
    print('\n' + '='*80)
    print('STEP 4: Load rule via pySigma and apply pipeline')
    print('='*80)
    
    try:
        # Sanitize and load
        def before_load(p):
            txt = p.read_text(encoding='utf-8')
            if txt != sanitize_yaml(txt):
                import tempfile
                import os
                fd, tmp_path = tempfile.mkstemp(suffix='.yml', text=True)
                os.close(fd)
                tmp = Path(tmp_path)
                tmp.write_text(sanitize_yaml(txt), encoding='utf-8')
                return tmp
            return p
        
        collection = SigmaCollection.load_ruleset([RULE_PATH], collect_errors=True, on_beforeload=before_load)
        print(f'Loaded {len(collection.rules)} rule(s)')
        
        rule = collection.rules[0]
        print(f'Rule type: {type(rule)}')
        print(f'Rule title: {rule.title}')
        print(f'Rule detection object: {type(rule.detection)}')
        
    except Exception as e:
        print(f'Failed to load rule: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print('\n' + '='*80)
    print('STEP 5: Convert rule via pySigma with custom pipeline')
    print('='*80)
    
    try:
        backend = OpensearchLuceneBackend(
            processing_pipeline=get_default_processing_pipeline(),
            collect_errors=True
        )
        print(f'Backend formats available: {list(backend.formats.keys())}')
        
        print('\nAttempting conversions for each format:')
        all_results = {}
        for fmt in backend.formats.keys():
            try:
                result = backend.convert_rule(rule, output_format=fmt)
                all_results[fmt] = result
                print(f'\n  {fmt}:')
                print(f'    Type: {type(result)}')
                print(f'    Repr (first 200 chars): {repr(result)[:200]}')
                if result:
                    print(f'    [NON-EMPTY]')
                else:
                    print(f'    [EMPTY]')
            except Exception as e:
                print(f'\n  {fmt}: FAILED - {e}')
        
        print('\n' + '-'*80)
        print('Summary: Non-empty conversion results:')
        for fmt, result in all_results.items():
            if result:
                print(f'\n  Format: {fmt}')
                print(f'  Type: {type(result)}')
                try:
                    print(f'  JSON dump (first 500 chars):\n    {json.dumps(result, indent=2, default=str)[:500]}')
                except Exception:
                    print(f'  Repr:\n    {repr(result)[:500]}')
    
    except Exception as e:
        print(f'Conversion failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print('\n' + '='*80)
    print('DIAGNOSTIC COMPLETE')
    print('='*80)


if __name__ == '__main__':
    main()
