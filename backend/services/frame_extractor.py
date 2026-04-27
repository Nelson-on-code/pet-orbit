"""Extract key frames from uploaded video, covering the angle range."""
import os
import math
from pathlib import Path
from typing import List


def extract_frames(
    video_bytes: bytes,
    filename: str,
    target_frames: int = 12,
    tmp_dir: str = "/tmp",
) -> List[str]:
    """
    Extract `target_frames` key frames from a video that covers
    a head sweep (front to side). Returns list of image file paths.

    Production implementation:
    - Write video bytes to tmp file
    - Use ffmpeg to extract evenly-spaced frames:
        ffmpeg -i input.mp4 -vf fps=1 -frames:v {target_frames} frame_%03d.jpg
    - Run pet head detection (e.g. YOLOv8 + pet head model) to filter
      frames where head is clearly visible and not blurred
    - Select N frames with most even angular distribution
    """
    # Stub implementation — returns mock paths
    frames = []
    for i in range(target_frames):
        path = os.path.join(tmp_dir, f"frame_{i:03d}.jpg")
        frames.append(path)
    return frames


def estimate_head_angle(frame_path: str) -> float:
    """
    Estimate horizontal head rotation angle from a frame.
    Use MediaPipe Face Mesh or a dog-specific landmark model to
    get yaw angle. Returns degrees (-90 to +90).
    """
    # Stub — replace with actual landmark-based pose estimation
    return 0.0
