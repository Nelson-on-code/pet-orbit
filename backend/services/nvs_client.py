"""Novel View Synthesis client — pluggable NVS backend."""
from abc import ABC, abstractmethod
from typing import List
import os


class NVSClient(ABC):
    """Abstract base for novel view synthesis backends."""

    @abstractmethod
    def generate_views(
        self,
        source_frames: List[str],
        target_angles: List[float],
        job_id: str,
    ) -> List[str]:
        """
        Given source frame paths and a list of target angles (degrees),
        return paths to generated view images.
        """
        ...


class HiggsfieldAnglesClient(NVSClient):
    """
    Uses Higgsfield Angles V2 API.
    https://docs.higgsfield.ai/

    Set env: HIGGSFIELD_API_KEY
    """

    def __init__(self):
        self.api_key = os.environ.get("HIGGSFIELD_API_KEY", "")
        self.endpoint = "https://api.higgsfield.ai/v1/angles"

    def generate_views(
        self,
        source_frames: List[str],
        target_angles: List[float],
        job_id: str,
    ) -> List[str]:
        """
        POST each source frame + target angle to Higgsfield Angles API.
        Collect generated image URLs.

        Example payload:
        {
          "image_url": "<presigned-s3-url>",
          "target_yaw": 45.0,
          "style": "realistic"
        }
        """
        # Production: upload frame to S3, call API, download result
        raise NotImplementedError("Integrate Higgsfield Angles API here")


class SV3DClient(NVSClient):
    """
    Uses Stability AI SV3D (open-weight, self-hostable).
    Generates a 360° orbit video from a single image, then
    extracts frames at target angles.
    """

    def generate_views(
        self,
        source_frames: List[str],
        target_angles: List[float],
        job_id: str,
    ) -> List[str]:
        raise NotImplementedError("Integrate SV3D pipeline here")


class MockClient(NVSClient):
    """Returns placeholder paths for local development."""

    def generate_views(
        self,
        source_frames: List[str],
        target_angles: List[float],
        job_id: str,
    ) -> List[str]:
        return [f"/tmp/mock_{job_id}_{i:03d}.jpg" for i in range(len(target_angles))]


def get_nvs_client() -> NVSClient:
    """Factory: select client from NVS_BACKEND env var."""
    backend = os.environ.get("NVS_BACKEND", "mock")
    if backend == "higgsfield":
        return HiggsfieldAnglesClient()
    elif backend == "sv3d":
        return SV3DClient()
    else:
        return MockClient()
