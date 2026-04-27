"""r2_client.py  –  Cloudflare R2 上傳工具"""
import os, boto3, asyncio
from botocore.config import Config

ACCOUNT_ID    = os.getenv("R2_ACCOUNT_ID",    "")
ACCESS_KEY    = os.getenv("R2_ACCESS_KEY",    "")
SECRET_KEY    = os.getenv("R2_SECRET_KEY",    "")
BUCKET        = os.getenv("R2_BUCKET",        "pet-orbit")
PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN", "https://pub.r2.example.com")


def _s3():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


async def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    def _put():
        _s3().put_object(
            Bucket=BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
    await asyncio.to_thread(_put)
    return f"{PUBLIC_DOMAIN}/{key}"


async def upload_frames(job_id: str, frames: dict) -> list[str]:
    """上傳 scene_frames，回傳 URL 列表"""
    import pathlib
    scene = frames.get("scene_frames", [])
    urls = []
    for p in scene:
        data = pathlib.Path(p).read_bytes()
        name = pathlib.Path(p).name
        url  = await upload_bytes(
            key=f"uploads/{job_id}/{name}",
            data=data,
            content_type="image/jpeg",
        )
        urls.append(url)
    return urls


async def upload_json(key: str, obj: dict) -> str:
    import json
    return await upload_bytes(key, json.dumps(obj).encode(), "application/json")
