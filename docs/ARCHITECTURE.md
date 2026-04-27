# PetOrbit — 系統架構

## 雙模式資料流

```
┌───────────────────────────────────────────────────┐
│                    用戶端                       │
│  viewer/index.html (Landing + Canvas Demo)      │
│  陀螺儀 / 滑鼠  →  azimuth 視角控制            │
└─────────────────┬───────────────────────────────┘
                │ POST /api/jobs
┌─────────────────▼───────────────────────────────┐
│              Zeabur FastAPI (backend/main.py)       │
│  /api/jobs       → enqueue_job(mode)                │
│  /api/results    → job_store[job_id]                │
└─────────────────┬───────────────────────────────┘
                │ queue_worker._process()
         ┌─────┴─────┐
         │ static_orbit│ live_orbit
         ▼             ▼
┌──────────┐  ┌───────────────────────┐
│  30 幀均勻 │  │ Phase-A: 1fps scene        │
│  extract   │  │ Phase-B: 10fps dynamic     │
└────┬─────┘  └───────┬───────────────┘
         │             │
         ▼             ▼
┌───────────────────────────┐
│       Cloudflare R2                 │
│  uploads/{job_id}/{frame}.jpg       │
└────────────┬───────────────┘
               │ frame_urls
┌─────────────▼─────────────┐
│     fal.ai SEVA (NVS)              │
│  static: 72 output views          │
│  live:   36 az x N time views     │
└───────────┬──────────────┘
            │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌──────────────────┐
│spritesheet│ │  live_packager        │
│9x8 Atlas  │ │  angle_grid manifest  │
│manifest   │ │  fur_mask.json        │
└─────────┘ └──────────────────┘
             │ viewer_builder
┌────────────▼────────────┐
│  R2: viewers/{job_id}/index.html  │
│  公開 URL 回傳 → 用戶分享          │
└──────────────────────────┘
```

## Live Orbit Viewer 雙執行緒

```
Thread-A (時間軸):  requestAnimationFrame @ 12fps
                       timeIdx → 0, 1, 2, …, N-1, 0, …
                       播放呼吸、毛髮飄動、眨眼

Thread-B (視角軸):  DeviceOrientation | PointerMove
                       azimuth → az_idx (0-35)
                       preloadNear() 預載鄰近 ±3 列

Canvas 選擇:
  grid[az_idx][timeIdx] → 展示圖片
  fur_mask → applyFurBlur() 疊加層
```
