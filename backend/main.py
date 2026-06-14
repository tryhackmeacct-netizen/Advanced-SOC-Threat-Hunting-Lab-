from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from uuid import uuid4

app = FastAPI(title="Advanced SOC - MVP")

class Incident(BaseModel):
    id: Optional[str]
    title: str
    severity: str
    source_ip: Optional[str] = None
    destination_host: Optional[str] = None
    attack_technique: Optional[str] = None
    mitre_id: Optional[str] = None
    status: str = "open"

class IOC(BaseModel):
    value: str
    type: str
    threat_score: Optional[int] = 0
    source: Optional[str] = None

class Detection(BaseModel):
    rule_name: str
    severity: str
    mitre_id: Optional[str] = None
    description: Optional[str] = None
    response_action: Optional[str] = None

# In-memory stores (MVP)
INCIDENTS = {}
IOCS = {}
DETECTIONS = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/incidents", response_model=Incident)
def create_incident(i: Incident):
    iid = str(uuid4())
    i.id = iid
    INCIDENTS[iid] = i.dict()
    return INCIDENTS[iid]

@app.get("/incidents", response_model=List[Incident])
def list_incidents():
    return list(INCIDENTS.values())

@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: str):
    if incident_id not in INCIDENTS:
        raise HTTPException(status_code=404, detail="Incident not found")
    return INCIDENTS[incident_id]

@app.post("/iocs", response_model=IOC)
def create_ioc(i: IOC):
    key = i.value
    IOCS[key] = i.dict()
    return IOCS[key]

@app.get("/iocs", response_model=List[IOC])
def list_iocs():
    return list(IOCS.values())

@app.post("/detections", response_model=Detection)
def create_detection(d: Detection):
    key = d.rule_name
    DETECTIONS[key] = d.dict()
    return DETECTIONS[key]

@app.get("/detections", response_model=List[Detection])
def list_detections():
    return list(DETECTIONS.values())
