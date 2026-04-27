# PetOrbit API Specification

Base URL: `https://api.petorbit.com/api`  
Local dev: `http://localhost:8000/api`

All endpoints return JSON. File uploads use `multipart/form-data`.

---

## POST /jobs

Create a new orbit generation job.

### Request

```
Content-Type: multipart/form-data
```

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | ✅ | Pet video (MP4/MOV) or image (JPG/PNG) |
| `user_id` | string | ✅ | User identifier |
| `credit_token` | string | ✅ | IAP receipt / pre-authorized token |
| `output_frames` | int | ✗ | Target frame count (24–120, default: 72) |
| `angle_range` | int | ✗ | Max rotation degrees (45–90, default: 85) |

### Response `201`

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2026-04-27T13:00:00Z",
  "estimated_seconds": 60
}
```

### Error Responses

| Status | Reason |
|---|---|
| `400` | Empty file or invalid params |
| `402` | Invalid / expired credit token |
| `422` | Validation error |

---

## GET /results/{job_id}

Poll generation status. Poll every 5s until `status == "done"` or `"failed"`.

### Response `200` — in progress

```json
{
  "job_id": "550e8400-...",
  "status": "generating",
  "frames": null,
  "error": null
}
```

### Response `200` — done

```json
{
  "job_id": "550e8400-...",
  "status": "done",
  "frames": [
    { "angle": -85.0, "url": "https://cdn.petorbit.com/jobs/.../frame_000.webp", "width": 512, "height": 512 },
    { "angle": -82.6, "url": "https://cdn.petorbit.com/jobs/.../frame_001.webp", "width": 512, "height": 512 }
  ],
  "spritesheet_url": "https://cdn.petorbit.com/jobs/.../spritesheet.webp",
  "spritesheet_cols": 9,
  "video_url": "https://cdn.petorbit.com/jobs/.../orbit.mp4",
  "viewer_url": "https://petorbit.com/v/550e8400-..."
}
```

### Status Values

| Status | Meaning |
|---|---|
| `pending` | Job queued, not started |
| `extracting` | Extracting key frames from video |
| `generating` | NVS model generating angle views |
| `interpolating` | Expanding to dense frame sequence |
| `packaging` | Building spritesheet + video |
| `done` | Complete, results available |
| `failed` | Error occurred (see `error` field) |

---

## GET /health

Health check.

```json
{ "status": "ok", "service": "pet-orbit-api" }
```

---

## Viewer Integration

Once `status == "done"`, the web viewer can be loaded with:

```html
<script>
const manifest = await fetch('/api/results/{job_id}').then(r => r.json());
// Use manifest.spritesheet_url + manifest.spritesheet_cols
// to drive the interactive canvas
</script>
```

Or simply redirect users to `viewer_url` for the hosted interactive page.
