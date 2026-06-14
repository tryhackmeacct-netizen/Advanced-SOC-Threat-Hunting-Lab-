from fastapi import APIRouter, HTTPException
from typing import List
from app.core.db import get_db
from app.models.schemas import Alert
from bson import ObjectId

router = APIRouter()


def _serialize(doc: dict) -> dict:
    if not doc:
        return {}
    doc["_id"] = str(doc.get("_id"))
    return doc


@router.post("/", response_model=Alert)
async def create_alert(payload: Alert):
    db = get_db()
    item = payload.dict(by_alias=True, exclude_none=True)
    item["created_at"] = payload.created_at or __import__("datetime").datetime.utcnow()
    res = await db.alerts.insert_one(item)
    doc = await db.alerts.find_one({"_id": res.inserted_id})
    return _serialize(doc)


@router.get("/", response_model=List[Alert])
async def list_alerts(limit: int = 50):
    db = get_db()
    cursor = db.alerts.find().sort("created_at", -1).limit(limit)
    docs = []
    async for d in cursor:
        docs.append(_serialize(d))
    return docs


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    db = get_db()
    doc = await db.alerts.find_one({"_id": ObjectId(alert_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _serialize(doc)
