"""Background job worker — orchestrates the full generation pipeline."""
import time
from services.frame_extractor import extract_frames
from services.nvs_client import get_nvs_client
from services.interpolator import interpolate_frames
from services.spritesheet import pack_spritesheet


def enqueue_job(job: dict) -> None:
    """
    Stub enqueue. In production:
        from rq import Queue
        from redis import Redis
        q = Queue(connection=Redis())
        q.enqueue(process_job, job)
    """
    # For demo: just print
    print(f"[queue] Enqueued job {job['job_id']}")


def process_job(job: dict) -> None:
    """
    Full generation pipeline executed by a worker process.

    Steps:
    1. Extract key frames from video
    2. Run NVS model to generate sparse angle views (12–36 frames)
    3. Interpolate to dense sequence (72 frames)
    4. Pack into spritesheet
    5. Upload to CDN (S3 / GCS)
    6. Update job status in DB/Redis
    7. Optionally render orbit video (ffmpeg)
    """
    job_id = job["job_id"]
    output_frames = job.get("output_frames", 72)
    angle_range = job.get("angle_range", 85)

    print(f"[worker] Starting job {job_id}")

    # Step 1: Extract frames
    key_frames = extract_frames(
        video_bytes=job["content"],
        filename=job["filename"],
        target_frames=12,
    )
    print(f"[worker] Extracted {len(key_frames)} key frames")

    # Step 2: NVS generation
    target_angles = [
        round(-angle_range + i * (2 * angle_range / 35), 1)
        for i in range(36)
    ]
    nvs = get_nvs_client()
    generated = nvs.generate_views(key_frames, target_angles, job_id)
    print(f"[worker] Generated {len(generated)} NVS frames")

    # Step 3: Interpolate to dense sequence
    sparse = list(zip(target_angles, generated))
    dense = interpolate_frames(sparse, target_count=output_frames)
    print(f"[worker] Interpolated to {len(dense)} frames")

    # Step 4: Pack spritesheet
    frame_paths = [f for _, f in dense]
    meta = pack_spritesheet(frame_paths, f"/tmp/{job_id}_sprite.webp")
    print(f"[worker] Spritesheet: {meta}")

    # Step 5–7: Upload to CDN + update job status (stub)
    print(f"[worker] Job {job_id} complete")
