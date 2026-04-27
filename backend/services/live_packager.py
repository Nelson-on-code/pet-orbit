"""live_packager.py

Live Orbit 專屬資產打包器

輸入 (nvs_result):
  output_urls   : list[str]  – NVS 生成的所有視角圖片 URL
  angle_grid    : dict       – { geo_urls: [...] }
  fur_mask      : dict|None  – 毛髮遮罩資料

輸出 (assets):
  angle_grid_url     : str   – R2 上的 manifest JSON URL
                               內含 {azimuth}→{time}→image_url 查找表
  highlight_clip_url : str   – 自動剪輯的「頭部跟隨」highlight 短片 URL
  fur_mask_url       : str   – 毛髮遮罩 JSON URL

角度網格規格:
  azimuth:  0°, 5°, 10°, ..., 175° (36 個方向, 左 -90° → 右 +90°)
  time_idx: 0 .. N-1 (動態幀數量, 通常 ≤ 200)

播放邏輯:
  · Viewer 根據陀螺儀/滑鼠 azimuth 選擇對應列
  · 同時以固定幀率(預設 12fps)播放 time_idx, 形成「頭部看你 + 身體自然動」
  · fur_mask 用於在 Canvas 上加強毛髮 motion blur, 提升真實感
"""
import json, asyncio
from backend.services.r2_client import upload_json, upload_bytes


async def build_live_assets(job_id: str, nvs_result: dict) -> dict:
    output_urls = nvs_result.get("output_urls", [])
    angle_grid  = nvs_result.get("angle_grid") or {}
    fur_mask    = nvs_result.get("fur_mask")

    # ── 建立角度網格 Manifest ──────────────────────────────────────────────────
    # 格式: { "azimuths": [deg, ...], "grid": { "0": [url_t0, url_t1, ...], ... } }
    n_azimuth = 36
    n_time    = max(1, len(output_urls) // n_azimuth)

    grid_manifest = {
        "mode":      "live_orbit",
        "job_id":    job_id,
        "n_azimuth": n_azimuth,
        "n_time":    n_time,
        "fps":       12,
        "azimuths":  [round(-90 + i * (180 / (n_azimuth - 1)), 1) for i in range(n_azimuth)],
        "grid":      {},
    }

    for az_idx in range(n_azimuth):
        time_slice = []
        for t_idx in range(n_time):
            flat_idx = az_idx * n_time + t_idx
            url = output_urls[flat_idx] if flat_idx < len(output_urls) else ""
            time_slice.append(url)
        grid_manifest["grid"][str(az_idx)] = time_slice

    manifest_bytes = json.dumps(grid_manifest, ensure_ascii=False).encode()
    angle_grid_url = await upload_bytes(
        key=f"results/{job_id}/live_manifest.json",
        data=manifest_bytes,
        content_type="application/json",
    )

    # ── 毛髮遮罩 ─────────────────────────────────────────────────────────────
    fur_mask_url = None
    if fur_mask:
        mask_bytes = json.dumps(fur_mask, ensure_ascii=False).encode()
        fur_mask_url = await upload_bytes(
            key=f"results/{job_id}/fur_mask.json",
            data=mask_bytes,
            content_type="application/json",
        )

    # ── Highlight clip (TODO: 真實實作需 ffmpeg 剪輯) ─────────────────────────
    highlight_clip_url = None  # 未來串接頭部偵測分數 → 自動剪輯最佳段落

    return {
        "angle_grid_url":     angle_grid_url,
        "highlight_clip_url": highlight_clip_url,
        "fur_mask_url":       fur_mask_url,
    }
