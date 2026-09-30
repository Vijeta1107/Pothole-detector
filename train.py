"""
train.py — YOLOv8 training script.
Member 1 owns this file.
Run: python train.py
Or on Colab/Kaggle with GPU.
"""

import os
from config import BASE_DIR, MODEL_PATH, IMAGE_SIZE

DATA_YAML   = os.path.join(BASE_DIR, "data.yaml")
RUNS_DIR    = os.path.join(BASE_DIR, "runs")
EPOCHS      = 50
BATCH_SIZE  = 16
BASE_MODEL  = "yolov8s.pt"    # start from pretrained small model


def train():
    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ ultralytics not installed. Run: pip install ultralytics")
        return

    if not os.path.exists(DATA_YAML):
        print(f"❌ data.yaml not found at {DATA_YAML}")
        print("   Make sure your dataset is set up in data/unified/")
        return

    print("=" * 60)
    print("🚀 STARTING YOLOV8 TRAINING")
    print("=" * 60)
    print(f"  Base model:  {BASE_MODEL}")
    print(f"  Data yaml:   {DATA_YAML}")
    print(f"  Epochs:      {EPOCHS}")
    print(f"  Batch size:  {BATCH_SIZE}")
    print(f"  Image size:  {IMAGE_SIZE}")
    print(f"  Output dir:  {RUNS_DIR}")

    model = YOLO(BASE_MODEL)

    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        project=RUNS_DIR,
        name="pothole_yolov8",
        patience=15,           # early stopping
        save=True,
        save_period=10,        # checkpoint every 10 epochs
        plots=True,
        verbose=True,
        device=0 if _gpu_available() else "cpu",
        augment=True,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
    )

    # ── Copy best.pt to models/ ──
    best_src = os.path.join(RUNS_DIR, "pothole_yolov8", "weights", "best.pt")
    if os.path.exists(best_src):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        import shutil
        shutil.copy2(best_src, MODEL_PATH)
        print(f"\n✅ Best model copied to: {MODEL_PATH}")
    else:
        print(f"\n⚠️  best.pt not found at expected path: {best_src}")
        print(f"   Check runs/ folder and copy manually to {MODEL_PATH}")

    return results


def _gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


if __name__ == "__main__":
    train()
