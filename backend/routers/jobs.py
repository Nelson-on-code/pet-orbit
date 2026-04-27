"""POST /api/jobs — create a new generation job"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models import CreateJobRequest, JobResponse, JobStatus
from services.frame_extractor import extract_frames
from queue_worker import enqueue_job
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/jobs", response_model=JobResponse, summary="Create generation job")
async def create_job(
    file: UploadFile = File(..., description="Pet video or image file"),
    user_id: str = Form(...),
    credit_token: str = Form(...),
    output_frames: int = Form(default=72),
    angle_range: int = Form(default=85),
):
    """
    1. Validate credit token (stub — integrate with IAP verification)
    2. Extract key frames from uploaded video
    3. Enqueue NVS generation job
    4. Return job_id for polling
    """
    # Stub credit validation
    if not credit_token or len(credit_token) < 8:
        raise HTTPException(status_code=402, detail="Invalid or expired credit token")

    # Read upload
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    job_id = str(uuid.uuid4())

    # Enqueue background job (Redis + RQ in production)
    enqueue_job({
        "job_id": job_id,
        "user_id": user_id,
        "filename": file.filename,
        "content": content,
        "output_frames": output_frames,
        "angle_range": angle_range,
    })

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
        estimated_seconds=60,
    )
