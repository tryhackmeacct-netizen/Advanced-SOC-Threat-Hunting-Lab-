<#
Verify end-to-end demo steps (best-effort). Requires Docker, OpenSearch, and MongoDB.
Usage: .\scripts\verify_e2e.ps1
#>
Set-StrictMode -Version Latest

function Test-OpenSearch {
    try {
        $r = Invoke-WebRequest -Uri http://localhost:9200 -UseBasicParsing -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

Write-Host "1) Check OpenSearch reachable..."
if (-not (Test-OpenSearch)) {
    Write-Host "OpenSearch not reachable at http://localhost:9200. Start docker-compose first." -ForegroundColor Red
    exit 2
}
Write-Host "OpenSearch reachable"

Write-Host "2) Apply index template"
try {
    docker-compose exec backend python scripts/setup_opensearch.py
    Write-Host "Applied template via backend container"
} catch {
    Write-Host "Attempting to apply template from host..."
    python scripts/setup_opensearch.py
}

Write-Host "3) Generate sample logs"
python attack-simulations/generate_all.py --noise 50

Write-Host "4) Ingest logs"
try {
    docker-compose exec backend python -m backend.app.ingestion.pipeline --path /app/sample-logs/
    Write-Host "Ingestion run inside backend container"
} catch {
    Write-Host "Running ingestion from host..."
    $env:PYTHONPATH='backend'
    python -m backend.app.ingestion.pipeline --path sample-logs/
}

Write-Host "5) Verify OpenSearch indices"
$indices = curl http://localhost:9200/_cat/indices/soc-logs-*?v | Select-String -Pattern 'soc-logs-'
Write-Host $indices

Write-Host "6) Verify MongoDB log_events count"
$env:PYTHONPATH='backend'
python - <<'PY'
from pymongo import MongoClient
from app.core.config import settings
cli = MongoClient('mongodb://localhost:27017')
db = cli[settings.mongo_db]
print('mongo_db=', settings.mongo_db, 'log_events_count=', db.log_events.count_documents({}))
PY

Write-Host "7) Fetch one sample normalized doc per source type"
$env:PYTHONPATH='backend'
python tools/preview_normalized.py

Write-Host "Verify complete"
