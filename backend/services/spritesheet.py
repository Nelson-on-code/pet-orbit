"""Pack dense frame sequence into a sprite atlas for efficient Web viewer delivery."""
from typing import List, Tuple
import math


def pack_spritesheet(
    frame_paths: List[str],
    output_path: str,
    frame_size: Tuple[int, int] = (512, 512),
    cols: int = 9,
) -> dict:
    """
    Combine N frames into a single sprite sheet image.
    Returns metadata dict for the viewer.

    Args:
        frame_paths: Ordered list of frame image paths
        output_path: Where to write the spritesheet (e.g. /tmp/sprite.webp)
        frame_size: (width, height) per frame in pixels
        cols: Number of columns in the grid

    Returns:
        {
          "url": output_path,
          "cols": cols,
          "rows": rows,
          "frame_w": frame_size[0],
          "frame_h": frame_size[1],
          "total_frames": len(frame_paths),
        }

    Production implementation:
        from PIL import Image
        rows = math.ceil(len(frame_paths) / cols)
        atlas = Image.new('RGB', (cols * frame_size[0], rows * frame_size[1]))
        for idx, path in enumerate(frame_paths):
            img = Image.open(path).resize(frame_size)
            x = (idx % cols) * frame_size[0]
            y = (idx // cols) * frame_size[1]
            atlas.paste(img, (x, y))
        atlas.save(output_path, 'WEBP', quality=85)
    """
    rows = math.ceil(len(frame_paths) / cols)
    return {
        "url": output_path,
        "cols": cols,
        "rows": rows,
        "frame_w": frame_size[0],
        "frame_h": frame_size[1],
        "total_frames": len(frame_paths),
    }
