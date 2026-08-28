"""Road AI Monitor — FastAPI backend"""

#python server.py

import io
import os
import json
import base64
import logging
from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ── Model ──────────────────────────────────────────────────────────────────
MODEL_PATH = Path(os.getenv("MODEL_PATH", "best.pt"))
model = None

try:
    from ultralytics import YOLO
    if MODEL_PATH.exists():
        log.info(f"Loading model: {MODEL_PATH} ...")
        model = YOLO(str(MODEL_PATH))
        log.info("Model loaded OK.")
    else:
        log.warning(f"'{MODEL_PATH}' not found — running in MOCK mode.")
except ImportError:
    log.warning("ultralytics not installed — running in MOCK mode.")

# ── Detection DB (shared across devices) ───────────────────────────────────
DB_PATH = Path("db.json")

def load_db() -> list:
    try:
        return json.loads(DB_PATH.read_text(encoding="utf-8")) if DB_PATH.exists() else []
    except Exception:
        return []

def save_db(items: list) -> None:
    DB_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Road AI Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Severity thresholds ────────────────────────────────────────────────────
# Bounding-box area relative to the full image (%).
# Adjust after real camera calibration.
SEV_AREA_VUA  = 5.0   # >= vua threshold → severe
SEV_AREA_NHE  = 1.5   # >= nhe threshold → moderate; < nhe → minor

SEV_COLORS = {
    "nhe":  (244, 196,  48),   # yellow
    "vua":  (255, 140,  66),   # orange
    "nang": (255,  59,  59),   # red
}


def classify_severity(area_pct: float) -> str:
    if area_pct >= SEV_AREA_VUA:
        return "nang"
    if area_pct >= SEV_AREA_NHE:
        return "vua"
    return "nhe"


def annotate(img: Image.Image, detections: list) -> Image.Image:
    """Draw bounding boxes on the image by severity."""
    draw = ImageDraw.Draw(img)
    for d in detections:
        x1, y1, x2, y2 = [int(v) for v in d["box"]]
        color = SEV_COLORS[d["severity"]]
        for off in range(3):
            draw.rectangle([x1 - off, y1 - off, x2 + off, y2 + off], outline=color)
        label = f"{d['severity'].upper()}  {d['conf']:.0%}"
        draw.text((x1 + 4, y1 + 4), label, fill=color)
    return img


def to_base64(img: Image.Image, max_w=800, max_h=600, quality=82) -> str:
    out = img.copy()
    out.thumbnail((max_w, max_h), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ── Routes ─────────────────────────────────────────────────────────────────
@app.get("/")
def index():
    html = Path("road_ai_monitor.html")
    if html.exists():
        return FileResponse("road_ai_monitor.html", media_type="text/html")
    return JSONResponse({"msg": "Place road_ai_monitor.html in the same directory as server.py"})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_path": str(MODEL_PATH),
        "model_loaded": model is not None,
        "mode": "real" if model else "mock",
    }


@app.get("/db")
def db_get():
    return load_db()

@app.put("/db")
async def db_put(items: List[Any] = Body(...)):
    save_db(items)
    return {"saved": len(items)}

@app.delete("/db")
def db_clear():
    save_db([])
    return {"cleared": True}


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Unable to open image")

    img_w, img_h = img.size

    # ── MOCK mode (best.pt not yet available) ────────────────────────────
    if model is None:
        import random
        if random.random() < 0.12:
            return {"detected": False, "mock": True}
        sev   = random.choices(["nhe", "vua", "nang"], weights=[3, 4, 3])[0]
        size  = {"nhe": 15, "vua": 42, "nang": 70}[sev]
        conf  = round(random.uniform(0.72, 0.96), 3)

        # Draw a fake box on the image so the frontend has an annotated image
        margin = int(min(img_w, img_h) * 0.15)
        fake_box = [margin, margin, img_w - margin, img_h - margin]
        ann = annotate(img.copy(), [{"box": fake_box, "severity": sev, "conf": conf}])
        return {
            "detected":       True,
            "severity":       sev,
            "sizeCm":         size,
            "depthCm":        max(3, int(size * 0.32)),
            "conf":           conf,
            "areaPct":        round(random.uniform(1, 20), 1),
            "totalBoxes":     1,
            "annotatedImage": to_base64(ann),
            "mock":           True,
        }

    # ── REAL inference ────────────────────────────────────────────────────
    results = model(img, verbose=False)[0]

    if len(results.boxes) == 0:
        return {"detected": False, "mock": False}

    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf     = float(box.conf[0])
        area_pct = (x2 - x1) * (y2 - y1) / (img_w * img_h) * 100
        sev      = classify_severity(area_pct)
        detections.append({"box": [x1, y1, x2, y2], "conf": conf,
                            "area_pct": area_pct, "severity": sev})

    detections.sort(key=lambda d: d["conf"], reverse=True)
    best     = detections[0]
    severity = best["severity"]
    area_pct = best["area_pct"]
    conf     = best["conf"]

    # Estimate size (cm) — real calibration required
    size_cm  = max(10, int(area_pct * 5.5))
    depth_cm = max(3,  int(size_cm * 0.28 + conf * 5))

    ann_img   = annotate(img.copy(), detections)
    ann_b64   = to_base64(ann_img)

    return {
        "detected":       True,
        "severity":       severity,
        "sizeCm":         size_cm,
        "depthCm":        depth_cm,
        "conf":           round(conf, 3),
        "areaPct":        round(area_pct, 1),
        "totalBoxes":     len(detections),
        "annotatedImage": ann_b64,
        "mock":           False,
    }


@app.post("/auto")
async def auto_detect(folder: str = "pic1"):
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(404, f"Folder '{folder}' does not exist next to server.py")

    IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    results = []

    for f in sorted(folder_path.iterdir()):
        if f.suffix.lower() not in IMAGE_EXT:
            continue
        entry = {"filename": f.name, "detected": False, "mock": model is None}
        try:
            img = Image.open(f).convert("RGB")
            img_w, img_h = img.size

            if model is None:
                import random
                if random.random() >= 0.12:
                    sev  = random.choices(["nhe","vua","nang"], weights=[3,4,3])[0]
                    size = {"nhe":15,"vua":42,"nang":70}[sev]
                    conf = round(random.uniform(0.72, 0.96), 3)
                    margin = int(min(img_w, img_h) * 0.15)
                    ann = annotate(img.copy(),
                        [{"box":[margin,margin,img_w-margin,img_h-margin],"severity":sev,"conf":conf}])
                    entry.update({"detected":True,"severity":sev,"sizeCm":size,
                        "depthCm":max(3,int(size*0.32)),"conf":conf,
                        "areaPct":round(random.uniform(1,20),1),"totalBoxes":1,
                        "annotatedImage":to_base64(ann)})
            else:
                res = model(img, verbose=False)[0]
                if len(res.boxes) > 0:
                    detections = []
                    for box in res.boxes:
                        x1,y1,x2,y2 = box.xyxy[0].tolist()
                        conf = float(box.conf[0])
                        area_pct = (x2-x1)*(y2-y1)/(img_w*img_h)*100
                        detections.append({"box":[x1,y1,x2,y2],"conf":conf,
"area_pct":area_pct,"severity":classify_severity(area_pct)})
                    detections.sort(key=lambda d: d["conf"], reverse=True)
                    best = detections[0]
                    size_cm  = max(10, int(best["area_pct"] * 5.5))
                    depth_cm = max(3,  int(size_cm * 0.28 + best["conf"] * 5))
                    ann = annotate(img.copy(), detections)
                    entry.update({"detected":True,"severity":best["severity"],
                        "sizeCm":size_cm,"depthCm":depth_cm,"conf":round(best["conf"],3),
                        "areaPct":round(best["area_pct"],1),"totalBoxes":len(detections),
                        "annotatedImage":to_base64(ann)})
        except Exception as e:
            entry["error"] = str(e)
            log.warning(f"Auto detect error on {f.name}: {e}")
        results.append(entry)
        log.info(f"AUTO {f.name}: {'detected '+results[-1].get('severity','') if results[-1]['detected'] else 'no detect'}")

    return {"folder": folder, "total": len(results), "results": results}


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    module = Path(__file__).stem  # auto-detect module name (server / api_server / ...)
    uvicorn.run(f"{module}:app", host="0.0.0.0", port=8000, reload=True) 