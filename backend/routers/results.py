from fastapi import APIRouter, HTTPException
from backend.models import JobResultResponse, JobStatus, STATUS_LABEL

router = APIRouter(prefix="/api", tags=["results"])

# job_store 由 queue_worker 維護；生產環境用 Redis hash
from backend.queue_worker import job_store


@router.get("/results/{job_id}", response_model=JobResultResponse)
async def get_result(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} 不存在")

    return JobResultResponse(
        job_id=job_id,
        status=job["status"],
        status_label=STATUS_LABEL.get(job["status"], ""),
        mode=job.get("mode"),
        sprite_url=job.get("sprite_url"),
        manifest_url=job.get("manifest_url"),
        angle_grid_url=job.get("angle_grid_url"),
        highlight_clip_url=job.get("highlight_clip_url"),
        fur_mask_url=job.get("fur_mask_url"),
        viewer_url=job.get("viewer_url"),
        error=job.get("error"),
    )
