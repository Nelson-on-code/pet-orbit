"""Pydantic schemas for PetOrbit API"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
import uuid
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    GENERATING = "generating"
    INTERPOLATING = "interpolating"
    PACKAGING = "packaging"
    DONE = "done"
    FAILED = "failed"


class CreateJobRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    credit_token: str = Field(..., description="Pre-authorized credit token from IAP")
    output_frames: int = Field(default=72, ge=24, le=120, description="Target frame count")
    angle_range: int = Field(default=85, ge=45, le=90, description="Max rotation angle (degrees)")


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    estimated_seconds: int


class FrameManifest(BaseModel):
    angle: float
    url: str
    width: int
    height: int


class ResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    frames: Optional[List[FrameManifest]] = None
    spritesheet_url: Optional[str] = None
    spritesheet_cols: Optional[int] = None
    video_url: Optional[str] = None
    viewer_url: Optional[str] = None
    error: Optional[str] = None
