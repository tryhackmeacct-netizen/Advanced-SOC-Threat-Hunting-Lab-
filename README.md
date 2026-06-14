Advanced SOC Threat Hunting Lab (MVP scaffold)

This repository contains a minimal scaffold for the Advanced SOC Threat Hunting Lab. It includes a small FastAPI backend MVP and a frontend stub so you can get a working demo quickly.

Quick start (backend):

1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

2. Run the API

```powershell
uvicorn backend.main:app --reload --port 8000
```

The API exposes simple in-memory endpoints for `incidents`, `iocs`, and `detections` for early demoing.

Next steps:
- Wire MongoDB models and CRUD
- Add frontend SOC overview dashboard
- Add sample Sigma and Wazuh rules
- Add CI and instructions to push to GitHub

To push this scaffold to your GitHub repository, run the commands in the `Pushing` section below.

Pushing (example):

```powershell
cd "c:/Users/Sanket/SOC PROject/Advanced-SOC-Threat-Hunting-Lab"
git init
git add .
git commit -m "Initial scaffold: FastAPI MVP"
git remote add origin https://github.com/tryhackmeacct-netizen/Advanced-SOC-Threat-Hunting-Lab-
git branch -M main
git push -u origin main
```
