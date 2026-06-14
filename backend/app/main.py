from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core import db as db_core
from app.api.routers import alerts, incidents, iocs, detection_rules, ingest, detections

app = FastAPI(title="Advanced SOC Threat Hunting Lab - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await db_core.init_db(settings.mongo_uri, settings.mongo_db)


@app.get("/health")
async def health():
    ok = await db_core.ping()
    return {"status": "ok" if ok else "degraded"}


app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(iocs.router, prefix="/api/iocs", tags=["iocs"])
app.include_router(detection_rules.router, prefix="/api/detection-rules", tags=["detection_rules"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(detections.router, prefix="/api/detections", tags=["detections"])
