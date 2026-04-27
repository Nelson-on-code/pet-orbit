"""spritesheet.py  –  Static Orbit 專用 Sprite Atlas 打包器

輸出: 9×8 = 72 幀的 sprite PNG + manifest JSON
每幀 512×512, atlas 總尺寸 4608×4096
"""
import asyncio, httpx, io, json
from PIL import Image
from backend.services.r2_client import upload_bytes

COLS, ROWS = 9, 8
FRAME_W = FRAME_H = 512


async def build_sprite(job_id: str, nvs_result: dict) -> dict:
    urls = nvs_result.get("output_urls", [])
    if not urls:
        raise ValueError("NVS 未回傳任何圖片")

    # 下載所有幀
    frames = await _download_frames(urls[:COLS * ROWS])

    # 拼 Atlas
    atlas = Image.new("RGB", (COLS * FRAME_W, ROWS * FRAME_H))
    for idx, img in enumerate(frames):
        col = idx % COLS
        row = idx // COLS
        img_resized = img.resize((FRAME_W, FRAME_H), Image.LANCZOS)
        atlas.paste(img_resized, (col * FRAME_W, row * FRAME_H))

    # 上傳 Atlas PNG
    buf = io.BytesIO()
    atlas.save(buf, format="PNG", optimize=True)
    sprite_url = await upload_bytes(
        key=f"results/{job_id}/sprite_atlas.png",
        data=buf.getvalue(),
        content_type="image/png",
    )

    # 上傳 Manifest JSON
    manifest = {
        "mode":    "static_orbit",
        "job_id":  job_id,
        "cols":    COLS,
        "rows":    ROWS,
        "total":   len(frames),
        "frame_w": FRAME_W,
        "frame_h": FRAME_H,
        "sprite":  sprite_url,
    }
    manifest_url = await upload_bytes(
        key=f"results/{job_id}/manifest.json",
        data=json.dumps(manifest).encode(),
        content_type="application/json",
    )

    return {"sprite_url": sprite_url, "manifest_url": manifest_url}


async def _download_frames(urls: list[str]) -> list[Image.Image]:
    async with httpx.AsyncClient(timeout=60) as cli:
        tasks = [cli.get(u) for u in urls]
        responses = await asyncio.gather(*tasks)
    imgs = []
    for r in responses:
        if r.status_code == 200:
            imgs.append(Image.open(io.BytesIO(r.content)).convert("RGB"))
    return imgs
