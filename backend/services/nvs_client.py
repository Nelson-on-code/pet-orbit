"""nvs_client.py

可插拔的 Novel View Synthesis 後端：
  NVS_BACKEND=seva   → fal.ai Stable Video 3D (SEVA) ← 預設
  NVS_BACKEND=mock   → 本地 mock（開發用）

Live Orbit 額外呼叫：
  · 多幀一致性 NVS (per-dynamic-frame NVS → angle_grid)
  · 毛髮流動 mask 計算 (光流 + SAM2 分割)
"""
import os, asyncio, httpx
from backend.models import OrbitMode

BACKEND = os.getenv("NVS_BACKEND", "seva")
FAL_KEY  = os.getenv("FAL_KEY", "")
SEVA_URL = "https://fal.run/fal-ai/stable-video-diffusion"


async def generate_views(job_id: str, frame_urls: list[str], mode: OrbitMode) -> dict:
    if BACKEND == "mock":
        return await _mock_generate(job_id, frame_urls, mode)
    return await _seva_generate(job_id, frame_urls, mode)


async def _seva_generate(job_id, frame_urls, mode) -> dict:
    """
    Static Orbit : 送入 30 scene frames → 72 output views (±90° horizontal)
    Live Orbit   :
      Step-1: 送入 scene frames → geometry reference views
      Step-2: 對每個 dynamic frame 做 conditioned NVS → angle_grid
              angle_grid[azimuth_idx][time_idx] = image_url
    """
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

    if mode == OrbitMode.static_orbit:
        payload = {
            "image_url": frame_urls[len(frame_urls)//2],  # 中間幀作為 reference
            "motion_bucket_id": 127,
            "num_frames": 72,
            "azimuth_range": [-90, 90],
        }
        async with httpx.AsyncClient(timeout=300) as cli:
            r = await cli.post(SEVA_URL, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        return {"output_urls": data.get("frames", []), "angle_grid": None}

    else:  # live_orbit
        # Step-1: geometry views (用 scene frames 中的代表幀)
        ref_url = frame_urls[0] if frame_urls else ""
        static_payload = {
            "image_url": ref_url,
            "num_frames": 36,
            "azimuth_range": [-90, 90],
        }
        async with httpx.AsyncClient(timeout=300) as cli:
            r = await cli.post(SEVA_URL, json=static_payload, headers=headers)
            r.raise_for_status()
            geo_data = r.json()

        # Step-2: per-dynamic-frame NVS (並行)
        # 實際串接時替換為真實 endpoint
        angle_grid = {"geo_urls": geo_data.get("frames", [])}
        return {
            "output_urls": geo_data.get("frames", []),
            "angle_grid": angle_grid,
            "fur_mask": None,  # TODO: SAM2 光流毛髮 mask
        }


async def _mock_generate(job_id, frame_urls, mode) -> dict:
    await asyncio.sleep(2)
    dummy = [f"https://picsum.photos/seed/{job_id[:8]}_{i}/512/512" for i in range(72)]
    if mode == OrbitMode.live_orbit:
        return {"output_urls": dummy, "angle_grid": {"geo_urls": dummy}, "fur_mask": None}
    return {"output_urls": dummy, "angle_grid": None}
