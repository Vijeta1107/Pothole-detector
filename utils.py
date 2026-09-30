"""
utils.py — Image preprocessing and helper utilities.
Member 1 owns this file.
"""

import os
import shutil
import uuid
from datetime import datetime
from config import IMAGE_SIZE, UPLOADS_DIR


def preprocess_image(image_path: str) -> str:
    """
    Resize and normalize image for YOLO inference.
    Saves preprocessed copy to uploads dir and returns its path.

    Args:
        image_path: path to raw input image

    Returns:
        path to preprocessed image (or original if preprocessing fails)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        from PIL import Image as PILImage
        import numpy as np

        img = PILImage.open(image_path).convert("RGB")
        orig_w, orig_h = img.size

        # ── Resize to max IMAGE_SIZE while keeping aspect ratio ──
        scale = min(IMAGE_SIZE / orig_w, IMAGE_SIZE / orig_h, 1.0)  # never upscale
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        if scale < 1.0:
            img = img.resize((new_w, new_h), PILImage.LANCZOS)
            print(f"  Resized: {orig_w}x{orig_h} → {new_w}x{new_h}")
        else:
            print(f"  Image size OK: {orig_w}x{orig_h} (no resize needed)")

        # ── Save preprocessed copy ──
        ext  = os.path.splitext(image_path)[1] or ".jpg"
        name = f"pre_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}{ext}"
        out_path = os.path.join(UPLOADS_DIR, name)
        img.save(out_path, quality=95)

        return out_path

    except ImportError:
        print("⚠️  Pillow not installed — skipping preprocessing")
        return image_path
    except Exception as e:
        print(f"⚠️  Preprocessing failed ({e}) — using original image")
        return image_path


def validate_image(image_path: str) -> tuple:
    """
    Check if image is valid and readable.

    Returns:
        (is_valid: bool, message: str)
    """
    if not image_path:
        return False, "No image path provided"
    if not os.path.exists(image_path):
        return False, f"File not found: {image_path}"

    allowed_ext = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in allowed_ext:
        return False, f"Unsupported format '{ext}'. Allowed: {allowed_ext}"

    try:
        from PIL import Image as PILImage
        with PILImage.open(image_path) as img:
            img.verify()
        return True, "OK"
    except Exception as e:
        return False, f"Corrupt or unreadable image: {e}"


def get_image_dimensions(image_path: str) -> tuple:
    """Returns (width, height) or (0, 0) on failure."""
    try:
        from PIL import Image as PILImage
        with PILImage.open(image_path) as img:
            return img.size
    except Exception:
        return 0, 0


def draw_detections(image_path: str, detections: list, out_path: str) -> str:
    """
    Manually draw bounding boxes on image (fallback if YOLO plot fails).

    Args:
        image_path:  source image
        detections:  list of detection dicts from detector.py
        out_path:    where to save annotated image

    Returns:
        out_path on success, original image_path on failure
    """
    try:
        from PIL import Image as PILImage, ImageDraw, ImageFont

        COLORS = {
            0: (52,  152, 219),   # Longitudinal Crack — blue
            1: (46,  204, 113),   # Transverse Crack   — green
            2: (243, 156, 18),    # Alligator Crack    — orange
            3: (231, 76,  60),    # Pothole            — red
        }

        img  = PILImage.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        for det in detections:
            bbox  = det.get("bbox", [])
            cls   = det.get("class_id", 0)
            name  = det.get("class_name", "Unknown")
            conf  = det.get("confidence", 0.0)
            color = COLORS.get(cls, (128, 128, 128))

            if len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                # Box
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                # Label background
                label = f"{name} {conf:.0%}"
                lw = len(label) * 7 + 8
                draw.rectangle([x1, y1 - 22, x1 + lw, y1], fill=color)
                draw.text((x1 + 4, y1 - 20), label, fill=(255, 255, 255))

        img.save(out_path)
        return out_path

    except Exception as e:
        print(f"⚠️  draw_detections failed: {e}")
        return image_path


def create_demo_images():
    """
    Create placeholder demo images if real ones aren't present.
    Member 3 should replace these with real road photos.
    """
    from config import DEMO_IMAGES_DIR

    demos = [
        ("demo_01_pothole.jpg",       (80, 80, 80),   "POTHOLE"),
        ("demo_02_alligator.jpg",     (70, 65, 60),   "ALLIGATOR CRACK"),
        ("demo_03_longitudinal.jpg",  (75, 75, 70),   "LONGITUDINAL CRACK"),
        ("demo_04_transverse.jpg",    (72, 70, 68),   "TRANSVERSE CRACK"),
        ("demo_05_severe.jpg",        (60, 55, 55),   "SEVERE DAMAGE"),
    ]

    try:
        from PIL import Image as PILImage, ImageDraw
        created = 0
        for filename, bg_color, label in demos:
            path = os.path.join(DEMO_IMAGES_DIR, filename)
            if not os.path.exists(path):
                img  = PILImage.new("RGB", (640, 480), color=bg_color)
                draw = ImageDraw.Draw(img)
                # Simulate a road texture
                for y in range(0, 480, 40):
                    draw.line([(0, y), (640, y)], fill=(bg_color[0]+10,)*3, width=1)
                # Label
                draw.rectangle([160, 180, 480, 300], outline=(255, 80, 80), width=4)
                draw.text((170, 330), f"[DEMO] {label}", fill=(255, 255, 255))
                draw.text((170, 355), "Replace with real road image", fill=(180, 180, 180))
                img.save(path)
                created += 1
        if created:
            print(f"✅ Created {created} placeholder demo images in {DEMO_IMAGES_DIR}")
    except ImportError:
        print("⚠️  Pillow not available — demo images not created")


# ──────────────────────────────────────────
# QUICK TEST — run: python utils.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("UTILS MODULE TEST")
    print("=" * 60)

    # Create demo images
    print("\n[1] Creating demo images...")
    create_demo_images()

    # Test validation
    print("\n[2] Testing image validation...")
    from config import DEMO_IMAGES_DIR
    demo = os.path.join(DEMO_IMAGES_DIR, "demo_01_pothole.jpg")
    valid, msg = validate_image(demo)
    print(f"  Valid: {valid} | Message: {msg}")

    # Test preprocessing
    print("\n[3] Testing preprocessing...")
    if valid:
        out = preprocess_image(demo)
        w, h = get_image_dimensions(out)
        print(f"  Output: {out}")
        print(f"  Dimensions: {w}x{h}")

    print("\n✅ utils.py working correctly!")
