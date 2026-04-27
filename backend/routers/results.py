"""GET /api/results/{job_id} — poll job status and retrieve result"""
from fastapi import APIRouter, HTTPException
from models import ResultResponse, JobStatus, FrameManifest
import math

router = APIRouter()

# In production: replace with Redis/DB lookup
_MOCK_JOBS: dict = {}


@router.get("/results/{job_id}", response_model=ResultResponse, summary="Poll job result")
def get_result(job_id: str):
    """
    Returns current job status.
    When status == 'done', includes:
    - frames: list of {angle, url} for the interactive viewer
    - spritesheet_url: packed sprite atlas
    - video_url: MP4 orbit video for social export
    - viewer_url: shareable web viewer URL
    """
    # Mock: return a completed result for any job_id
    # Replace with real DB/Redis lookup
    frames = [
        FrameManifest(
            angle=round(-85 + i * (170 / 71), 2),
            url=f"https://cdn.petorbit.com/jobs/{job_id}/frame_{i:03d}.webp",
            width=512,
            height=512,
        )
        for i in range(72)
    ]
    return ResultResponse(
        job_id=job_id,
        status=JobStatus.DONE,
        frames=frames,
        spritesheet_url=f"https://cdn.petorbit.com/jobs/{job_id}/spritesheet.webp",
        spritesheet_cols=9,
        video_url=f"https://cdn.petorbit.com/jobs/{job_id}/orbit.mp4",
        viewer_url=f"https://petorbit.com/v/{job_id}",
    )
