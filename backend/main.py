import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

from . import db as dbmod

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

# fallback in-memory stores (used if no MONGO_URI provided)
INCIDENTS = {}
IOCS = {}
DETECTIONS = {}


def _serialize(doc: dict) -> dict:
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


@app.on_event("startup")
def startup_event():
    dbmod.init_db()


@app.on_event("shutdown")
def shutdown_event():
    dbmod.close_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/incidents", response_model=Incident)
async def create_incident(i: Incident):
    if dbmod.db:
        data = i.dict(exclude={"id"})
        res = await dbmod.db.incidents.insert_one(data)
        doc = await dbmod.db.incidents.find_one({"_id": res.inserted_id})
        return _serialize(doc)
    iid = str(uuid4())
    i.id = iid
    INCIDENTS[iid] = i.dict()
    return INCIDENTS[iid]


@app.get("/incidents", response_model=List[Incident])
async def list_incidents():
    if dbmod.db:
        cursor = dbmod.db.incidents.find()
        docs = []
        async for d in cursor:
            docs.append(_serialize(d))
        return docs
    return list(INCIDENTS.values())


@app.get("/incidents/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str):
    if dbmod.db:
        from bson.objectid import ObjectId

        try:
            oid = ObjectId(incident_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid id")
        doc = await dbmod.db.incidents.find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="Incident not found")
        return _serialize(doc)
    if incident_id not in INCIDENTS:
        raise HTTPException(status_code=404, detail="Incident not found")
    return INCIDENTS[incident_id]


@app.post("/iocs", response_model=IOC)
async def create_ioc(i: IOC):
    if dbmod.db:
        data = i.dict()
        await dbmod.db.iocs.replace_one({"value": i.value}, data, upsert=True)
        doc = await dbmod.db.iocs.find_one({"value": i.value})
        return _serialize(doc)
    key = i.value
    IOCS[key] = i.dict()
    return IOCS[key]


@app.get("/iocs", response_model=List[IOC])
async def list_iocs():
    if dbmod.db:
        cursor = dbmod.db.iocs.find()
        docs = []
        async for d in cursor:
            docs.append(_serialize(d))
        return docs
    return list(IOCS.values())


@app.post("/detections", response_model=Detection)
async def create_detection(d: Detection):
    if dbmod.db:
        data = d.dict()
        await dbmod.db.detections.replace_one({"rule_name": d.rule_name}, data, upsert=True)
        doc = await dbmod.db.detections.find_one({"rule_name": d.rule_name})
        return _serialize(doc)
    key = d.rule_name
    DETECTIONS[key] = d.dict()
    return DETECTIONS[key]


@app.get("/detections", response_model=List[Detection])
async def list_detections():
    if dbmod.db:
        cursor = dbmod.db.detections.find()
        docs = []
        async for d in cursor:
            docs.append(_serialize(d))
        return docs
    return list(DETECTIONS.values())

