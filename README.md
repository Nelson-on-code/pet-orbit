# 🐾 PetOrbit

**讓寵物活生生地對著你。** 上傳影片，AI 重建 180° 真實寵物頭部視角。

## 兩種模式

| | **Live Orbit** 🐾 | **Static Orbit** 🔹 |
|---|---|---|
| **定位** | 主打功能 | 標準功能 |
| **售價** | NT\$199 / 寵物 | NT\$99 / 寵物 |
| **輸入** | 5–20秒自然影片 | 3–10秒環繞影片 |
| **輸出** | 36角度 × N時間幀網格 + 毛髮 Mask | 72幀 9×8 Sprite Atlas |
| **動態** | 呼吸、毛髮飄動、眨眼 **同時播放** | 無 |
| **視角控制** | 陀螺儀 / 滑鼠 | 陀螺儀 / 滑鼠 |
| **毛髮 Blur** | ✅ | ❌ |
| **頭部鎖定模式** | ✅ | ❌ |

## 技術架構

```
手機 / 網頁前端
    ↓ POST /api/jobs (video + mode)
Zeabur FastAPI 後端
    ↓ 抽幀 (Static: 30幀 | Live: scene+10fps動態幀)
    ↓ 上傳 Cloudflare R2
    ↓ fal.ai SEVA (Novel View Synthesis)
    ↓ 打包 (Static: Sprite Atlas | Live: 角度網格 Manifest)
    ↓ 生成 Viewer HTML → R2
GET /api/results/{job_id} → viewer_url
```

## 目錄結構

```
pet-orbit/
├── backend/
│   ├── main.py               FastAPI 入口
│   ├── models.py             OrbitMode / JobStatus Pydantic 模型
│   ├── queue_worker.py       非同步任務圖
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── routers/
│   │   ├── jobs.py             POST /api/jobs
│   │   └── results.py          GET  /api/results/{job_id}
│   └── services/
│       ├── frame_extractor.py  影片抽幀 (OpenCV)
│       ├── nvs_client.py       fal.ai SEVA / Mock 可插拔
│       ├── spritesheet.py      Static Orbit Sprite 打包
│       ├── live_packager.py    Live Orbit 角度網格打包
│       ├── viewer_builder.py   Viewer HTML 生成 (雙模式)
│       └── r2_client.py        Cloudflare R2 上傳
├── viewer/
│   └── index.html            Landing Page 含 Canvas Demo
└── docs/
    ├── ARCHITECTURE.md
    └── PRICING.md
```

## 現地開發

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
# API Docs: http://localhost:8080/docs
```

## 環境變數（Zeabur Dashboard 填入）

| 變數 | 說明 |
|---|---|
| `FAL_KEY` | fal.ai API Key |
| `R2_ACCOUNT_ID` | Cloudflare R2 帳號 ID |
| `R2_ACCESS_KEY` | R2 存取金鑰 |
| `R2_SECRET_KEY` | R2 密鑰 |
| `R2_BUCKET` | R2 Bucket 名稱 |
| `R2_PUBLIC_DOMAIN` | R2 公開網域 |
| `NVS_BACKEND` | `seva` (預設) 或 `mock` |
| `WEBHOOK_BASE_URL` | 本服務 HTTPS 網址 |

## API

```
POST /api/jobs
  body: video (file), purchase_token (str),
        mode (static_orbit | live_orbit)
  → { job_id, mode, status, credits_used }

GET /api/results/{job_id}
  → Static Orbit: { sprite_url, manifest_url, viewer_url }
  → Live Orbit:   { angle_grid_url, fur_mask_url, viewer_url }
```
