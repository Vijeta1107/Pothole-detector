"""
config.py — Central configuration.
FIXED: CONF_THRESHOLD 0.40→0.15, IOU_THRESHOLD 0.70→0.45
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH     = os.path.join(BASE_DIR, "models", "best.pt")
FALLBACK_MODEL = "yolov8s.pt"

# ── Model trained with these exact lowercase names ──
# {0:'longitudinal_crack', 1:'transverse_crack', 2:'alligator_crack', 3:'pothole'}
# We map them to display names here:
CLASS_NAMES = {
    0: "Longitudinal Crack",
    1: "Transverse Crack",
    2: "Alligator Crack",
    3: "Pothole",
}

# Model's actual internal names (must match training data.yaml exactly)
MODEL_CLASS_NAMES = {
    0: "longitudinal_crack",
    1: "transverse_crack",
    2: "alligator_crack",
    3: "pothole",
}

SEVERITY_THRESHOLDS = {
    "LOW":    (0.0,  5.0),
    "MEDIUM": (5.0,  15.0),
    "HIGH":   (15.0, 100.0),
}

CLASS_SEVERITY_BOOST = {
    0: 0,   # Longitudinal Crack
    1: 0,   # Transverse Crack
    2: 1,   # Alligator Crack  → +1 level
    3: 2,   # Pothole          → +2 levels
}

PRIORITY_MAP = {
    "LOW":    3,
    "MEDIUM": 2,
    "HIGH":   1,
}

RECOMMENDED_ACTIONS = {
    "Pothole":            "Immediate pothole patching required. High risk to vehicles.",
    "Alligator Crack":    "Structural resurfacing needed. Schedule within 2 weeks.",
    "Longitudinal Crack": "Seal crack to prevent water ingress. Schedule within 1 month.",
    "Transverse Crack":   "Monitor and seal. Schedule within 1 month.",
    "No Damage":          "No immediate action required. Routine monitoring advised.",
}

# ── FIXED THRESHOLDS ──────────────────────────────────────────────
# OLD: CONF=0.40, IOU=0.70 → model never detected cracks (max crack conf ~0.05)
# NEW: CONF=0.15, IOU=0.45 → standard values, allows crack detection
CONF_THRESHOLD = 0.15   # was 0.40 — too high, blocked all crack detections
IOU_THRESHOLD  = 0.45   # was 0.70 — too high for NMS, suppressed valid boxes
IMAGE_SIZE     = 640

# ── Output paths ──
OUTPUTS_DIR     = os.path.join(BASE_DIR, "outputs")
ANNOTATED_DIR   = os.path.join(OUTPUTS_DIR, "annotated")
REPORTS_DIR     = os.path.join(OUTPUTS_DIR, "reports")
DATABASE_DIR    = os.path.join(OUTPUTS_DIR, "database")
DATABASE_PATH   = os.path.join(DATABASE_DIR, "complaints.db")
DEMO_IMAGES_DIR = os.path.join(BASE_DIR, "demo_images")
UPLOADS_DIR     = os.path.join(OUTPUTS_DIR, "uploads")

for folder in [OUTPUTS_DIR, ANNOTATED_DIR, REPORTS_DIR, DATABASE_DIR, DEMO_IMAGES_DIR, UPLOADS_DIR]:
    os.makedirs(folder, exist_ok=True)

# ── API keys — load from .env file ──
def _load_env_file():
    env_paths = [
        os.path.join(BASE_DIR, ".env"),
        os.path.join(os.path.dirname(BASE_DIR), ".env"),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip(); v = v.strip().strip('"').strip("'")
                        if k and v and k not in os.environ:
                            os.environ[k] = v

_load_env_file()

VLM_PROVIDER   = os.environ.get("VLM_PROVIDER", "gemini")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "").strip()

ENABLE_GROQ_FALLBACK       = True
ENABLE_RULE_BASED_FALLBACK = True

GEOCODER_USER_AGENT = "pothole_detector_hackathon_2026"
GEOCODER_TIMEOUT    = 10

PDF_ORG_NAME    = "Smart City Municipal Corporation"
PDF_SYSTEM_NAME = "Pothole Detection System v1.0"
PDF_LOGO_PATH   = os.path.join(BASE_DIR, "assets", "logo.png")

if __name__ == "__main__":
    print(f"CONF_THRESHOLD: {CONF_THRESHOLD}  (was 0.40)")
    print(f"IOU_THRESHOLD:  {IOU_THRESHOLD}  (was 0.70)")
    print(f"Gemini key set: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"Groq key set:   {'✅' if GROQ_API_KEY else '❌'}")