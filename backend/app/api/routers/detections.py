from fastapi import APIRouter, BackgroundTasks
from app.services.detection_engine import DetectionEngine

router = APIRouter()


@router.post("/run")
async def run_detections(background_tasks: BackgroundTasks):
    engine = DetectionEngine()
    background_tasks.add_task(engine.run_once)
    return {"status": "detection_started"}


@router.get("/run_sync")
async def run_detections_sync():
    engine = DetectionEngine()
    cnt = engine.run_once()
    return {"status": "completed", "alerts_created": cnt}
