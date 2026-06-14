KNOWN ISSUES / Notes
=====================

- Relative import patches: To allow running `attack-simulations/generate_all.py` directly from the repo root without installing the package, I patched `attack_chains.py` and `generate_all.py` to load generator modules by file path. These changes are intentional to make the generator runnable in both development and containerized environments:
  - When running inside the backend container (with `PYTHONPATH` set or package installed), these patches are safe — Python will still import modules by path. If you prefer a clean package import when running inside the container, you can instead run the generator with `PYTHONPATH=attack-simulations` or install the package; no further changes are required.

- Local environment caveat: This repository expects Docker/OpenSearch/MongoDB available for full E2E. The repo includes a `scripts/verify_e2e.ps1` helper that checks connectivity and runs the demo steps once you start the stack.

- Database name: The default MongoDB database name was changed to `soc_db` (see `backend/app/core/config.py` and `backend/.env.example`). If you have an existing database named `asthl`, update `.env` or the config accordingly.

- Sigma/pySigma integration: I avoided pinning `pysigma`/`pysigma-backend-elasticsearch` packages because of potential dependency conflicts (pySigma toolchains sometimes require different `pydantic` major versions). Instead, Phase 3 includes a lightweight YAML-based Sigma parser and a Python predicate builder (in `backend/app/services/sigma_converter.py`) that allows rule testing and dry-run detection without installing pySigma. If you want full pySigma conversion (production-grade Elasticsearch/OpenSearch DSL), we should decide whether to upgrade the project to `pydantic v2` and pin compatible `fastapi`/`pysigma` package versions; I can make that change in a follow-up.

- Unit test: `backend/tests/test_detection_engine.py` runs the detection engine in `dry_run` mode against `sample-logs/mixed_events.json` and produced 8 detections locally (dry-run). This validates the Sigma->predicate matching and alert creation logic even when OpenSearch/MongoDB are not running.

