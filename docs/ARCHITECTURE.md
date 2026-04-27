# PetOrbit — System Architecture

## Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│                                                          │
│  ┌─────────────────┐      ┌──────────────────────────┐  │
│  │  Mobile App     │      │  Web Viewer (shareable)  │  │
│  │  (React Native) │      │  viewer.html + sprite    │  │
│  │                 │      │                          │  │
│  │ • Guided capture│      │ • Mouse drag → angle     │  │
│  │ • IAP credits   │      │ • Gyroscope → angle      │  │
│  │ • View results  │      │ • Spritesheet playback   │  │
│  └────────┬────────┘      └────────────┬─────────────┘  │
└───────────┼────────────────────────────┼────────────────┘
            │ HTTPS                       │ CDN
            ▼                             ▼
┌──────────────────────┐    ┌────────────────────────────┐
│   FastAPI Backend    │    │  CDN (Cloudflare / S3)     │
│                      │    │                            │
│  POST /api/jobs      │    │  • Frame images (.webp)    │
│  GET  /api/results   │    │  • Spritesheet atlas       │
│  IAP token verify    │    │  • Orbit video (.mp4)      │
│  Job status DB       │    │  • viewer_manifest.json    │
└──────────┬───────────┘    └────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│                  Worker Layer (GPU)                      │
│                                                          │
│  Redis Queue  →  Worker Process                         │
│                      │                                  │
│              ┌───────▼────────┐                        │
│              │  Pipeline      │                        │
│              │                │                        │
│              │ 1. Frame       │                        │
│              │    Extractor   │  (ffmpeg + head detect)│
│              │                │                        │
│              │ 2. NVS Client  │  Higgsfield Angles API │
│              │    (pluggable) │  or SV3D self-hosted   │
│              │                │                        │
│              │ 3. Interpolator│  RIFE / FILM / nearest │
│              │                │                        │
│              │ 4. Spritesheet │  Pillow atlas packer   │
│              │    Packer      │                        │
│              │                │                        │
│              │ 5. CDN Upload  │  S3 presigned PUT      │
│              └────────────────┘                        │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

1. **User uploads** a pet video (5–10s) via mobile app.
2. **API** validates IAP credit token, creates job, pushes to Redis queue.
3. **Worker** picks up job:
   - Extracts 12 key frames across the angle sweep.
   - Calls NVS model (Higgsfield Angles or SV3D) for 36 target-angle views.
   - Interpolates to 72 frames for smooth interaction.
   - Packs into a spritesheet + exports orbit MP4.
   - Uploads all to CDN, updates job status to `done`.
4. **Mobile app** polls `GET /api/results/{job_id}` until `done`.
5. **Viewer** loads manifest, maps user input → angle → spritesheet frame.

## Scalability Notes

- Workers can be scaled horizontally (GPU autoscaling on Modal / RunPod).
- CDN caches all static assets; only the API needs to scale on load spikes.
- Job queue provides back-pressure; credits consumed only on job completion.

## NVS Backend Comparison

| Backend | Latency | Quality | Cost | Self-host |
|---|---|---|---|---|
| Higgsfield Angles V2 | ~30s | ★★★★★ | API pricing | No |
| SV3D (Stability) | ~60s | ★★★★ | GPU cost | Yes |
| Free3D | ~90s | ★★★☆ | GPU cost | Yes |
| MockClient | <1s | Demo only | Free | Yes |
