"""viewer_builder.py  –  動態生成 viewer HTML 並上傳到 R2

Static Orbit viewer:
  · 載入 sprite_atlas.png + manifest.json
  · 滑鼠左右拖 / 手機陀螺儀 → 切換幀
  · 一個 Canvas 直接貼幀

Live Orbit viewer (主打):
  · 載入 live_manifest.json (angle_grid)
  · 雙執行緒動畫:
      Thread-A: 時間軸 requestAnimationFrame (12fps 動態)
      Thread-B: 陀螺儀/滑鼠 → azimuth → 選角度列
  · 毛髮 motion blur: 讀 fur_mask_url → Canvas 疊加層
  · 「頭部鎖定」badge: 右下角顯示 👀
"""
import os
from backend.models import OrbitMode
from backend.services.r2_client import upload_bytes


async def build_viewer(job_id: str, mode: OrbitMode, store: dict) -> str:
    if mode == OrbitMode.static_orbit:
        html = _static_viewer_html(
            manifest_url=store.get("manifest_url", ""),
            sprite_url=store.get("sprite_url", ""),
        )
    else:
        html = _live_viewer_html(
            manifest_url=store.get("angle_grid_url", ""),
            fur_mask_url=store.get("fur_mask_url") or "",
        )

    url = await upload_bytes(
        key=f"viewers/{job_id}/index.html",
        data=html.encode("utf-8"),
        content_type="text/html; charset=utf-8",
    )
    return url


# ─────────────────────────────────────────────────────────────────────────────
# Static Orbit HTML
# ─────────────────────────────────────────────────────────────────────────────
def _static_viewer_html(manifest_url: str, sprite_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PetOrbit · Static</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0d0d0d;display:flex;flex-direction:column;align-items:center;
        justify-content:center;min-height:100dvh;font-family:system-ui;color:#fff}}
  canvas{{border-radius:16px;box-shadow:0 0 40px #0008;cursor:grab;touch-action:none}}
  canvas:active{{cursor:grabbing}}
  #badge{{margin-top:12px;font-size:13px;opacity:.5}}
</style>
</head>
<body>
<canvas id="c" width="512" height="512"></canvas>
<p id="badge">← 拖曳旋轉 · 或左右傾斜手機 →</p>
<script>
const MANIFEST_URL = "{manifest_url}";
const SPRITE_URL   = "{sprite_url}";
const c = document.getElementById('c');
const ctx = c.getContext('2d');
let manifest, sprite, currentFrame = 0;

// Load assets
Promise.all([
  fetch(MANIFEST_URL).then(r=>r.json()),
  new Promise(res=>{{ const img=new Image(); img.crossOrigin='anonymous';
    img.onload=()=>res(img); img.src=SPRITE_URL; }})
]).then(([m, img]) => {{
  manifest = m; sprite = img;
  render();
}});

function render() {{
  if (!manifest || !sprite) return;
  const {{cols, frame_w, frame_h}} = manifest;
  const col = currentFrame % cols;
  const row = Math.floor(currentFrame / cols);
  ctx.drawImage(sprite, col*frame_w, row*frame_h, frame_w, frame_h, 0, 0, 512, 512);
}}

// Mouse drag
let dragging=false, lastX=0;
c.addEventListener('pointerdown', e=>{{ dragging=true; lastX=e.clientX; }});
window.addEventListener('pointerup', ()=>dragging=false);
window.addEventListener('pointermove', e=>{{
  if (!dragging || !manifest) return;
  const dx = e.clientX - lastX;
  lastX = e.clientX;
  currentFrame = (currentFrame + (dx>0?1:-1) + manifest.total) % manifest.total;
  render();
}});

// Gyroscope
if (window.DeviceOrientationEvent?.requestPermission) {{
  document.body.addEventListener('click', ()=>DeviceOrientationEvent.requestPermission().then(s=>{{ if(s==='granted') window.addEventListener('deviceorientation', onOrient); }}), {{once:true}});
}} else {{
  window.addEventListener('deviceorientation', onOrient);
}}
function onOrient(e) {{
  if (!manifest) return;
  const gamma = Math.max(-90, Math.min(90, e.gamma||0));
  currentFrame = Math.round((gamma+90)/180*(manifest.total-1));
  render();
}}
</script>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Live Orbit HTML  ← 主打 viewer
# ─────────────────────────────────────────────────────────────────────────────
def _live_viewer_html(manifest_url: str, fur_mask_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PetOrbit · Live</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0a0a0a;display:flex;flex-direction:column;align-items:center;
        justify-content:center;min-height:100dvh;font-family:system-ui;color:#fff;
        user-select:none}}
  #wrap{{position:relative;width:min(90vw,480px)}}
  canvas{{width:100%;border-radius:20px;box-shadow:0 8px 48px #000a;display:block;
          cursor:grab;touch-action:none}}
  canvas:active{{cursor:grabbing}}
  #lock-badge{{position:absolute;bottom:12px;right:12px;background:#fff2;backdrop-filter:blur(6px);
                border-radius:99px;padding:4px 10px;font-size:13px}}
  #bar{{margin-top:14px;display:flex;gap:8px;align-items:center;opacity:.55;font-size:13px}}
  #az-label{{min-width:48px;text-align:right}}
  #loading{{font-size:15px;opacity:.6;margin-bottom:20px}}
</style>
</head>
<body>
<div id="loading">載入互動資產中…</div>
<div id="wrap" style="display:none">
  <canvas id="c" width="512" height="512"></canvas>
  <div id="lock-badge">👀 盯著你</div>
</div>
<div id="bar"><span>← 拖曳·傾斜手機 →</span><span id="az-label">0°</span></div>

<script>
const MANIFEST_URL  = "{manifest_url}";
const FUR_MASK_URL  = "{fur_mask_url}";

const c   = document.getElementById('c');
const ctx = c.getContext('2d');
const loading = document.getElementById('loading');
const wrap    = document.getElementById('wrap');
const azLabel = document.getElementById('az-label');

let manifest  = null;
let furMask   = null;
let azimuth   = 0;      // -90 ~ +90 degrees
let timeIdx   = 0;      // current time frame index
let lastTs    = 0;
let cache     = {{}};     // url → HTMLImageElement

// ── 1. Load manifest ──────────────────────────────────────────────────────
fetch(MANIFEST_URL)
  .then(r => r.json())
  .then(m => {{
    manifest = m;
    loading.textContent = '預載圖片中…';
    preloadNear(0);
    if (FUR_MASK_URL) fetch(FUR_MASK_URL).then(r=>r.json()).then(m=>{{furMask=m;}});
    wrap.style.display = '';
    loading.style.display = 'none';
    requestAnimationFrame(loop);
  }})
  .catch(() => {{ loading.textContent = '載入失敗，請重整'; }});

// ── 2. Animation loop (時間軸 12fps + 角度選取) ───────────────────────────
function loop(ts) {{
  requestAnimationFrame(loop);
  if (!manifest) return;

  const fps = manifest.fps || 12;
  if (ts - lastTs < 1000/fps) return;
  lastTs = ts;

  timeIdx = (timeIdx + 1) % manifest.n_time;
  draw();
}}

function draw() {{
  if (!manifest) return;

  // 將 azimuth (-90~+90) 映射到 azimuth index (0~35)
  const clamp = Math.max(-90, Math.min(90, azimuth));
  const az_idx = Math.round((clamp + 90) / 180 * (manifest.n_azimuth - 1));
  const col = manifest.grid[String(az_idx)] || [];
  const url = col[timeIdx % col.length] || '';

  azLabel.textContent = clamp.toFixed(0) + '°';

  if (!url) return;
  const img = getOrLoad(url);
  if (img?.complete && img.naturalWidth) {{
    ctx.drawImage(img, 0, 0, 512, 512);
    // 毛髮 motion blur 疊加（簡化版）
    if (furMask) applyFurBlur();
  }}
}}

function getOrLoad(url) {{
  if (!cache[url]) {{
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = url;
    cache[url] = img;
  }}
  return cache[url];
}

function preloadNear(az) {{
  if (!manifest) return;
  const center = Math.round((Math.max(-90,Math.min(90,az))+90)/180*(manifest.n_azimuth-1));
  for (let d=-3; d<=3; d++) {{
    const idx = (center+d+manifest.n_azimuth)%manifest.n_azimuth;
    const col = manifest.grid[String(idx)] || [];
    col.slice(0,6).forEach(getOrLoad);
  }}
}}

function applyFurBlur() {{
  // 簡化：在毛髮區域疊加低透明度模糊層，未來接真實 mask 資料
  ctx.save();
  ctx.globalAlpha = 0.08;
  ctx.filter = 'blur(2px)';
  ctx.drawImage(c, 0, 0);
  ctx.restore();
  ctx.filter = 'none';
}}

// ── 3. 控制：滑鼠拖曳 ────────────────────────────────────────────────────
let dragging=false, lastX=0;
c.addEventListener('pointerdown', e=>{{ dragging=true; lastX=e.clientX; c.setPointerCapture(e.pointerId); }});
c.addEventListener('pointerup',   ()=>dragging=false);
c.addEventListener('pointermove', e=>{{
  if (!dragging) return;
  const dx = e.clientX - lastX; lastX = e.clientX;
  azimuth = Math.max(-90, Math.min(90, azimuth + dx * 0.5));
  preloadNear(azimuth);
}});

// ── 4. 控制：手機陀螺儀 ──────────────────────────────────────────────────
function attachGyro() {{
  window.addEventListener('deviceorientation', e => {{
    azimuth = Math.max(-90, Math.min(90, e.gamma || 0));
    preloadNear(azimuth);
  }});
}}
if (window.DeviceOrientationEvent?.requestPermission) {{
  document.body.addEventListener('click', () => {{
    DeviceOrientationEvent.requestPermission()
      .then(s => {{ if (s === 'granted') attachGyro(); }})
      .catch(()=>{{}});
  }}, {{once: true}});
}} else {{
  attachGyro();
}}
</script>
</body></html>"""
