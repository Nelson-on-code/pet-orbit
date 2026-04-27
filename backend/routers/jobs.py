import uuid, os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.models import OrbitMode, JobStatus, JobCreateResponse

router = APIRouter(prefix="/api", tags=["jobs"])

# 各模式消耗積分
CREDITS = {
    OrbitMode.static_orbit: 1,
    OrbitMode.live_orbit:   2,
}

# 各模式支援的影片長度上限(秒)
MAX_DURATION = {
    OrbitMode.static_orbit: 10,
    OrbitMode.live_orbit:   20,
}


@router.post("/jobs", response_model=JobCreateResponse)
async def create_job(
    video: UploadFile = File(..., description="寵物影片 (mp4/mov, ≤100MB)"),
    purchase_token: str = Form(..., description="單次購買驗證 token"),
    mode: OrbitMode = Form(
        OrbitMode.live_orbit,
        description=(
            "static_orbit: 高清靜態環繞 (1 積分) | "
            "live_orbit:  動態頭部跟隨＋毛髮 (2 積分, 主打)"
        ),
    ),
):
    # --- 基本驗證 ---
    if not video.content_type in ("video/mp4", "video/quicktime", "video/x-m4v"):
        raise HTTPException(400, "請上傳 MP4 或 MOV 影片")

    # TODO: 驗證 purchase_token (串接金流後啟用)
    if not purchase_token:
        raise HTTPException(402, "需要有效的購買 token")

    job_id = str(uuid.uuid4())
    video_bytes = await video.read()

    # 非同步推入 worker queue (Redis / Zeabur Queue)
    from backend.queue_worker import enqueue_job
    await enqueue_job(
        job_id=job_id,
        video_bytes=video_bytes,
        filename=video.filename or "input.mp4",
        mode=mode,
    )

    return JobCreateResponse(
        job_id=job_id,
        mode=mode,
        status=JobStatus.queued,
        credits_used=CREDITS[mode],
    )
