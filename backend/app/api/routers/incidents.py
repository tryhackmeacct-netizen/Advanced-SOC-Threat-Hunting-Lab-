from fastapi import APIRouter, HTTPException
from typing import List
from app.core.db import get_db
from app.models.schemas import Incident
from bson import ObjectId

router = APIRouter()


def _serialize(doc: dict) -> dict:
    if not doc:
        return {}
    doc["_id"] = str(doc.get("_id"))
    return doc


@router.post("/", response_model=Incident)
async def create_incident(payload: Incident):
    db = get_db()
    item = payload.dict(by_alias=True, exclude_none=True)
    item["created_at"] = payload.created_at or __import__("datetime").datetime.utcnow()
    res = await db.incidents.insert_one(item)
    doc = await db.incidents.find_one({"_id": res.inserted_id})
    return _serialize(doc)


@router.get("/", response_model=List[Incident])
async def list_incidents(limit: int = 50):
    db = get_db()
    cursor = db.incidents.find().sort("created_at", -1).limit(limit)
    docs = []
    async for d in cursor:
        docs.append(_serialize(d))
    return docs


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str):
    db = get_db()
    doc = await db.incidents.find_one({"_id": ObjectId(incident_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _serialize(doc)
