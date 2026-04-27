from enum import Enum
from pydantic import BaseModel
from typing import Optional


class OrbitMode(str, Enum):
    """
    static_orbit  – 高清靜態環繞
                    輸入: 短影片 (3-10s, 繞頭部前半圓)
                    輸出: 72 幀 Sprite Atlas (9×8), 無時間軸
                    視角: 水平 ±90°
                    適合: 3D 模型感的展示、商品頁

    live_orbit    – 動態頭部跟隨 (主打功能)
                    輸入: 5-20s 自然動作影片
                    輸出: 複合資產包:
                          · 36 個角度 × N 時間幀 的幀序列 (angle_grid)
                          · 自動偵測「頭部追蹤瞬間」highlight 段落
                          · 毛髮/動態 mask 資訊 (fur_mask_frames)
                    Viewer 行為:
                          · 陀螺儀/滑鼠控制水平視角 (azimuth)
                          · 同時播放時間軸動畫 (呼吸、毛髮飄動、眨眼)
                          · 「頭部始終對著畫面」鎖定模式
    """
    static_orbit = "static_orbit"
    live_orbit   = "live_orbit"


class JobStatus(str, Enum):
    queued      = "queued"
    extracting  = "extracting"
    uploading   = "uploading"
    generating  = "generating"
    packaging   = "packaging"
    done        = "done"
    failed      = "failed"


STATUS_LABEL = {
    JobStatus.queued:     "排隊中…",
    JobStatus.extracting: "抽取影格中…",
    JobStatus.uploading:  "上傳素材中…",
    JobStatus.generating: "AI 生成多視角中…",
    JobStatus.packaging:  "打包互動資產中…",
    JobStatus.done:       "完成！",
    JobStatus.failed:     "失敗，請重試",
}


class JobCreateResponse(BaseModel):
    job_id: str
    mode:   OrbitMode
    status: JobStatus
    credits_used: int


class JobResultResponse(BaseModel):
    job_id:       str
    status:       JobStatus
    status_label: str
    mode:         Optional[OrbitMode] = None
    # static_orbit assets
    sprite_url:   Optional[str] = None
    manifest_url: Optional[str] = None
    # live_orbit assets
    angle_grid_url:     Optional[str] = None   # angle_grid/{azimuth_idx}/{frame_idx}.jpg
    highlight_clip_url: Optional[str] = None   # 最佳「頭部跟隨」highlight 短片
    fur_mask_url:       Optional[str] = None   # 毛髮遮罩 JSON
    # shared
    viewer_url:   Optional[str] = None
    error:        Optional[str] = None
