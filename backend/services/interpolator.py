"""Expand sparse NVS frames to a dense angle sequence via interpolation."""
from typing import List, Tuple
import math


def interpolate_frames(
    sparse_frames: List[Tuple[float, str]],
    target_count: int = 72,
) -> List[Tuple[float, str]]:
    """
    Given a sparse list of (angle, image_path) pairs,
    return a denser list with `target_count` entries.

    Strategies (in order of quality):
    1. RIFE / FILM optical-flow frame interpolation — best temporal consistency
    2. Alpha crossfade between nearest neighbors — fast fallback
    3. Nearest-neighbor with no interpolation — lowest quality, zero cost

    Args:
        sparse_frames: List of (angle_degrees, image_path) sorted by angle
        target_count: Desired number of output frames

    Returns:
        Dense list of (angle_degrees, image_path_or_blend_spec)
    """
    if not sparse_frames:
        return []

    sparse_frames = sorted(sparse_frames, key=lambda x: x[0])
    min_angle = sparse_frames[0][0]
    max_angle = sparse_frames[-1][0]
    step = (max_angle - min_angle) / (target_count - 1)

    result = []
    for i in range(target_count):
        angle = min_angle + i * step
        # Find nearest source frame
        nearest = min(sparse_frames, key=lambda f: abs(f[0] - angle))
        result.append((round(angle, 2), nearest[1]))

    return result


def build_angle_index(dense_frames: List[Tuple[float, str]]) -> dict:
    """
    Build a lookup dict: { angle_str -> image_url }
    for the Web viewer's JSON manifest.
    """
    return {str(a): path for a, path in dense_frames}
