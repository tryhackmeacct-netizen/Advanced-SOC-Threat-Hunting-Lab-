# Advanced SOC Threat Hunting Lab

A modular, incremental build of a Security Operations Center (SOC) platform demonstrating real-world threat detection, enrichment, and response workflows.

## Current Status

**Phase 3: Detection Engine & pySigma Integration** ✅ COMPLETE
- Sigma rule parsing and conversion (pySigma + custom field mapping)
- Detection engine with dry-run support (8 detection rules validated)
- Automated alert generation and MongoDB persistence
- Legacy predicate fallback for rules with correlation conditions
- Comprehensive test suite with parity validation (8/8 rules matched)

**Phase 4: MITRE ATT&CK Mapping & SOC Dashboard** 🔄 IN PROGRESS

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for OpenSearch/MongoDB)

### Setup (Backend)

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### Run Detection Engine (Dry-Run)

```bash
# Validate all 8 rules match sample events
python backend/tests/test_sigma_pysigma_integration.py
```

Expected output:
```
legacy_matches_count 8
Parity OK: legacy predicate matched all 8 rules
```

## Architecture

```
backend/
  app/
    core/
      config.py           # pydantic v2 BaseSettings
    services/
      detection_engine.py # Rule execution, alert generation
      sigma_converter.py  # pySigma integration + fallback
      sigma_pipeline.py   # Field mapping, processing pipeline
  tests/
    test_sigma_pysigma_integration.py  # Parity validation
sigma-rules/
  *.yml                   # 8 sample Sigma detection rules
sample-logs/
  mixed_events.json       # Synthetic test events
```

## Phase 3: pySigma Integration Summary

### Field Mapping (sigma_pipeline.py)
Maps Sigma-native field names to normalized ECS-like fields:

```python
{
    "event_id": "event.id",           # Critical for all 8 rules
    "Image": "process.name",
    "CommandLine": "process.command_line",
    "TargetUserName": "user.name",
    ...
}
```

### Known Limitations

**pySigma Lucene Backend:**
- Correlation conditions (e.g., `count(selection) by source.ip > 5`) cannot be converted to Lucene queries
- **Workaround:** Falls back to legacy Python predicate matching (guarantees 100% coverage)
- All 8 sample rules validated with 8/8 parity via predicate fallback

**Test Results:**
- ✅ parity_test.py: 8/8 rules matched (legacy predicate baseline)
- ✅ Field mapping: event_id, event.action, script_block_text added
- ✅ Pydantic v2 compatibility: BaseSettings imported from pydantic_settings

## Testing

```bash
# Parity validation (predicate vs pySigma)
python backend/tests/test_sigma_pysigma_integration.py

# Diagnostic: inspect pySigma conversions for brute_force_windows.yml
python scripts/comprehensive_diagnostic.py

# Scan all rules for field usage across 8 rules
python scripts/scan_all_fields.py
```

## Phase 4: Next Steps

1. MITRE ATT&CK coverage mapping (tactic/technique heatmap)
2. Threat intelligence enrichment (VirusTotal API, IOC database)
3. SOC dashboard with detection analytics
4. Incident response automation playbooks

## References

- [Sigma Rules](https://github.com/SigmaHQ/sigma)
- [pySigma](https://github.com/SigmaHQ/pySigma)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [ECS Fields](https://www.elastic.co/guide/en/ecs/current/index.html)
