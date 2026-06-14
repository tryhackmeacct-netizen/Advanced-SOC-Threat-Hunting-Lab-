from fastapi import APIRouter, HTTPException
from typing import List
from app.core.db import get_db
from app.models.schemas import DetectionRule
from bson import ObjectId

router = APIRouter()


def _serialize(doc: dict) -> dict:
    if not doc:
        return {}
    doc["_id"] = str(doc.get("_id"))
    return doc


@router.post("/", response_model=DetectionRule)
async def create_rule(payload: DetectionRule):
    db = get_db()
    item = payload.dict(by_alias=True, exclude_none=True)
    item["created_at"] = payload.created_at or __import__("datetime").datetime.utcnow()
    res = await db.detection_rules.insert_one(item)
    doc = await db.detection_rules.find_one({"_id": res.inserted_id})
    return _serialize(doc)


@router.get("/", response_model=List[DetectionRule])
async def list_rules(limit: int = 100):
    db = get_db()
    cursor = db.detection_rules.find().sort("created_at", -1).limit(limit)
    docs = []
    async for d in cursor:
        docs.append(_serialize(d))
    return docs


@router.get("/{rule_id}", response_model=DetectionRule)
async def get_rule(rule_id: str):
    db = get_db()
    doc = await db.detection_rules.find_one({"_id": ObjectId(rule_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Rule not found")
    return _serialize(doc)
