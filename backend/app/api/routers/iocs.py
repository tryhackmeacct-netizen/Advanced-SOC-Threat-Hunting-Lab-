from fastapi import APIRouter, HTTPException
from typing import List
from app.core.db import get_db
from app.models.schemas import IOC
from bson import ObjectId

router = APIRouter()


def _serialize(doc: dict) -> dict:
    if not doc:
        return {}
    doc["_id"] = str(doc.get("_id"))
    return doc


@router.post("/", response_model=IOC)
async def create_ioc(payload: IOC):
    db = get_db()
    item = payload.dict(by_alias=True, exclude_none=True)
    item["created_at"] = payload.created_at or __import__("datetime").datetime.utcnow()
    res = await db.iocs.insert_one(item)
    doc = await db.iocs.find_one({"_id": res.inserted_id})
    return _serialize(doc)


@router.get("/", response_model=List[IOC])
async def list_iocs(limit: int = 100):
    db = get_db()
    cursor = db.iocs.find().sort("created_at", -1).limit(limit)
    docs = []
    async for d in cursor:
        docs.append(_serialize(d))
    return docs


@router.get("/{ioc_id}", response_model=IOC)
async def get_ioc(ioc_id: str):
    db = get_db()
    doc = await db.iocs.find_one({"_id": ObjectId(ioc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="IOC not found")
    return _serialize(doc)
