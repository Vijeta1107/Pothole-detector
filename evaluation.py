"""
evaluation.py — Model evaluation: mAP, precision, recall, per-class metrics.
Member 1 owns this file.
Run: python evaluation.py
"""

import os
import sys
from config import MODEL_PATH, BASE_DIR, IMAGE_SIZE, CLASS_NAMES

DATA_YAML = os.path.join(BASE_DIR, "data.yaml")


def evaluate(model_path: str = None, split: str = "val") -> dict:
    model_path = model_path or MODEL_PATH

    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ ultralytics not installed. Run: pip install ultralytics")
        return {}

    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print(f"   Place best.pt at: {model_path}")
        return {}

    if not os.path.exists(DATA_YAML):
        print(f"❌ data.yaml not found: {DATA_YAML}")
        return {}

    print("=" * 60)
    print(f"📊 EVALUATING MODEL: {model_path}")
    print(f"   Split: {split}")
    print("=" * 60)

    model   = YOLO(model_path)
    metrics = model.val(
        data=DATA_YAML,
        split=split,
        imgsz=IMAGE_SIZE,
        verbose=True,
        plots=True,
    )

    results = {
        "mAP50":     round(float(metrics.box.map50), 4),
        "mAP50_95":  round(float(metrics.box.map),   4),
        "precision": round(float(metrics.box.mp),     4),
        "recall":    round(float(metrics.box.mr),     4),
    }

    if hasattr(metrics.box, "ap_class_index"):
        for idx, cls_id in enumerate(metrics.box.ap_class_index):
            cls_name = CLASS_NAMES.get(int(cls_id), f"class_{cls_id}")
            results[f"AP50_{cls_name}"] = round(float(metrics.box.ap50[idx]), 4)

    print("\n📈 RESULTS:")
    print(f"  mAP@0.5:      {results['mAP50']:.4f}  ({results['mAP50']*100:.1f}%)")
    print(f"  mAP@0.5:0.95: {results['mAP50_95']:.4f}  ({results['mAP50_95']*100:.1f}%)")
    print(f"  Precision:    {results['precision']:.4f}")
    print(f"  Recall:       {results['recall']:.4f}")
    print("\n  Per-class AP@0.5:")
    for k, v in results.items():
        if k.startswith("AP50_"):
            print(f"    {k[5:]:25s}: {v:.4f}  ({v*100:.1f}%)")

    return results


def quick_inference_test(image_path: str):
    from detector import detect
    result = detect(image_path)
    print(f"\nInference test on: {image_path}")
    print(f"  Damage:     {result['damage_type']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Coverage:   {result['damage_coverage_pct']:.1f}%")
    print(f"  Detections: {result['num_detections']}")
    return result


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else MODEL_PATH
    split = sys.argv[2] if len(sys.argv) > 2 else "val"
    evaluate(model, split)
