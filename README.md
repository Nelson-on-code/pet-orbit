# 🐾 PetOrbit

> **Turn your pet's stare into an interactive 180° head-tracking experience.**

PetOrbit lets pet owners upload a short video of their pet, uses AI novel view synthesis to generate a multi-angle image sequence, and delivers an interactive viewer where the pet's head follows your mouse or phone gyroscope.

---

## ✨ Product Vision

| Step | What happens |
|---|---|
| 1. Capture | User records a 5–10s guided video of their pet (front to ±45° side) |
| 2. Upload | App extracts key frames and sends to the generation API |
| 3. Generate | AI generates 36–72 consistent angle images using NVS model |
| 4. Deliver | Web viewer plays the correct frame based on mouse/gyroscope input |
| 5. Share | User gets a shareable link; friends can interact without installing anything |

---

## 🗂 Project Structure

```
pet-orbit/
├── viewer/                  # Frontend interactive viewer (pure HTML/JS)
│   ├── index.html           # Landing page + demo
│   ├── viewer.html          # Standalone interactive viewer
│   └── assets/
│       └── demo-frames/     # Sample generated frames for demo
│
├── backend/                 # FastAPI backend
│   ├── main.py              # API entry point
│   ├── routers/
│   │   ├── jobs.py          # POST /jobs (create generation job)
│   │   └── results.py       # GET /results/{job_id}
│   ├── services/
│   │   ├── frame_extractor.py   # Extract key frames from video
│   │   ├── nvs_client.py        # NVS model API client (Higgsfield / custom)
│   │   ├── interpolator.py      # Frame interpolation to increase density
│   │   └── spritesheet.py       # Pack frames into spritesheet
│   ├── models.py            # Pydantic schemas
│   ├── queue_worker.py      # Background job worker
│   └── requirements.txt
│
├── docs/
│   ├── ARCHITECTURE.md      # System architecture
│   ├── BUSINESS_MODEL.md    # Commercial model & pricing
│   └── API_SPEC.md          # API endpoint spec
│
└── docker-compose.yml       # Local dev stack (API + Redis)
```

---

## 🚀 Quick Start

### Frontend viewer (no backend needed)

```bash
# Just open the viewer in your browser
open viewer/index.html
```

The demo uses pre-generated sample frames. Drag left/right (desktop) or tilt your phone (mobile) to rotate.

### Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Or with Docker:

```bash
docker-compose up
```

API docs auto-generated at: `http://localhost:8000/docs`

---

## 🤖 AI Generation Pipeline

```
Input video
    │
    ▼
[Frame Extractor]     → selects N key frames across angle range
    │
    ▼
[NVS Model]           → generates 12–36 target-angle images
    │                   (Higgsfield Angles API / SV3D / Free3D)
    ▼
[Interpolator]        → expands to 72 frames via image interpolation
    │
    ▼
[Spritesheet Packer]  → packs into single sprite atlas + index.json
    │
    ▼
CDN delivery → Viewer
```

**NVS Model options (pluggable):**
- `HiggsfieldAnglesClient` — Higgsfield Angles V2 API (recommended for production)
- `SV3DClient` — Stability AI SV3D (open-weight, self-hostable)
- `Free3DClient` — Free3D (no explicit 3D repr, multi-view consistent)
- `MockClient` — For local development / testing without GPU

---

## 💰 Business Model

See [`docs/BUSINESS_MODEL.md`](docs/BUSINESS_MODEL.md) for full details.

| Product | Type | Description |
|---|---|---|
| Free trial | Free | 1 generation, low-res, watermarked |
| Credit pack S | Consumable IAP | 3 generations |
| Credit pack M | Consumable IAP | 10 generations (unit discount) |
| Credit pack L | Consumable IAP | 30 generations (best value) |
| HD Unlock | Non-consumable IAP | Permanent: HD export + no watermark |
| Video Export | Non-consumable IAP | Permanent: export as MP4/GIF for social |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Mobile App | React Native / Flutter (future) |
| Web Viewer | Vanilla HTML + Canvas + JS |
| Backend API | Python / FastAPI |
| Job Queue | Redis + RQ (or Celery) |
| AI Model | Higgsfield API / SV3D / Free3D |
| Storage | AWS S3 / Google Cloud Storage |
| CDN | Cloudflare |
| Deployment | Railway / Zeabur / Docker |

---

## 📄 License

MIT
