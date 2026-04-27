"""queue_worker.py

輕量版 in-process worker（開發用）
生產環境請改用 Zeabur Cron / Redis Queue / Celery。
"""
import asyncio, os, tempfile, pathlib
from backend.models import OrbitMode, JobStatus

job_store: dict = {}  # { job_id: { status, mode, ... } }


async def enqueue_job(
    job_id: str,
    video_bytes: bytes,
    filename: str,
    mode: OrbitMode,
):
    job_store[job_id] = {"status": JobStatus.queued, "mode": mode}
    asyncio.create_task(_process(job_id, video_bytes, filename, mode))


async def _process(job_id, video_bytes, filename, mode):
    store = job_store[job_id]
    try:
        # 1. 寫入臨時檔
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = pathlib.Path(tmpdir) / filename
            video_path.write_bytes(video_bytes)

            # 2. 抽幀
            store["status"] = JobStatus.extracting
            from backend.services.frame_extractor import extract_frames
            frames = await asyncio.to_thread(
                extract_frames, str(video_path), tmpdir, mode
            )

            # 3. 上傳原始幀到 R2
            store["status"] = JobStatus.uploading
            from backend.services.r2_client import upload_frames
            frame_urls = await upload_frames(job_id, frames)

            # 4. 呼叫 NVS API
            store["status"] = JobStatus.generating
            from backend.services.nvs_client import generate_views
            nvs_result = await generate_views(job_id, frame_urls, mode)

            # 5. 打包資產
            store["status"] = JobStatus.packaging
            if mode == OrbitMode.static_orbit:
                from backend.services.spritesheet import build_sprite
                assets = await build_sprite(job_id, nvs_result)
                store.update(assets)
            else:  # live_orbit
                from backend.services.live_packager import build_live_assets
                assets = await build_live_assets(job_id, nvs_result)
                store.update(assets)

            # 6. 生成 viewer HTML
            from backend.services.viewer_builder import build_viewer
            viewer_url = await build_viewer(job_id, mode, store)
            store["viewer_url"] = viewer_url
            store["status"] = JobStatus.done

    except Exception as exc:
        store["status"] = JobStatus.failed
        store["error"]  = str(exc)
        raise
