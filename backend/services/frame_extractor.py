"""frame_extractor.py

Static Orbit : 均勻抽取 30 幀（整段影片涵蓋前半圓環繞）
Live Orbit   : 兩階段抽幀
  Phase-A: 場景幀 (1fps) 供 NVS 重建幾何
  Phase-B: 動態幀 (10fps) 供時間軸動畫生成
"""
import cv2, pathlib, os
from backend.models import OrbitMode


def extract_frames(
    video_path: str,
    out_dir: str,
    mode: OrbitMode,
) -> dict:
    cap = cv2.VideoCapture(video_path)
    fps      = cap.get(cv2.CAP_PROP_FPS) or 30
    total_f  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_f / fps
    cap.release()

    if mode == OrbitMode.static_orbit:
        return _extract_uniform(video_path, out_dir, n=30)
    else:
        return _extract_live(video_path, out_dir, fps, total_f, duration)


def _extract_uniform(video_path, out_dir, n=30) -> dict:
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step  = max(1, total // n)
    paths = []
    for i in range(n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ok, frame = cap.read()
        if not ok:
            break
        p = str(pathlib.Path(out_dir) / f"scene_{i:03d}.jpg")
        cv2.imwrite(p, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        paths.append(p)
    cap.release()
    return {"scene_frames": paths, "dynamic_frames": []}


def _extract_live(video_path, out_dir, fps, total_f, duration) -> dict:
    """Phase-A: 1fps scene frames  |  Phase-B: 10fps dynamic frames"""
    cap = cv2.VideoCapture(video_path)
    scene_paths, dyn_paths = [], []

    # Phase-A
    scene_interval = max(1, int(fps))
    for idx in range(0, total_f, scene_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            continue
        p = str(pathlib.Path(out_dir) / f"scene_{idx:06d}.jpg")
        cv2.imwrite(p, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        scene_paths.append(p)

    # Phase-B (10fps)
    dyn_interval = max(1, int(fps // 10))
    for idx in range(0, total_f, dyn_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            continue
        p = str(pathlib.Path(out_dir) / f"dyn_{idx:06d}.jpg")
        cv2.imwrite(p, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        dyn_paths.append(p)

    cap.release()
    return {"scene_frames": scene_paths, "dynamic_frames": dyn_paths}
