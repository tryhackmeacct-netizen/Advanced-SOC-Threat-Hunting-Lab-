from fastapi import APIRouter, BackgroundTasks
from app.ingestion.pipeline import ingest_path

router = APIRouter()


@router.post("/")
async def trigger_ingest(path: str = "../sample-logs/", background_tasks: BackgroundTasks = None):
    # Run ingestion in background to avoid blocking
    if background_tasks is not None:
        background_tasks.add_task(ingest_path, path)
        return {"status": "started", "path": path}
    else:
        cnt = ingest_path(path)
        return {"status": "completed", "count": cnt}
