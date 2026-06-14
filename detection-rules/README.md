Detection Rules
================

Each detection rule has:
- Sigma source in `sigma-rules/`.
- A markdown doc here describing the rule, severity, MITRE mapping, and recommended response.

Use `backend/app/services/sigma_converter.py` to convert Sigma to OpenSearch DSL (requires pySigma).
