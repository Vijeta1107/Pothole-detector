"""
run_pipeline.py — Master orchestrator for the pothole detection system.
Member 4 owns this file.
Calls all modules in sequence and returns the complete report.
"""

import os
import traceback
from config import UPLOADS_DIR


def run_pipeline(image_path: str, latitude: float = None, longitude: float = None) -> dict:
    """
    Full pipeline: image → detection → severity → geocoding → VLM → report → DB → PDF

    Args:
        image_path: path to the uploaded road image
        latitude:   GPS latitude (optional)
        longitude:  GPS longitude (optional)

    Returns:
        Complete report dict with pdf_path, or error dict on failure
    """

    print("\n" + "=" * 60)
    print("🚀 PIPELINE STARTED")
    print("=" * 60)

    # ── Step 1: Validate image ──
    if not image_path or not os.path.exists(image_path):
        return {"error": f"Image not found: {image_path}"}

    print(f"📸 Image: {image_path}")
    print(f"📍 GPS:   {latitude}, {longitude}")

    try:
        # ── Step 2: Detection ──
        print("\n[1/6] Running damage detection...")
        from detector import detect
        detection_dict = detect(image_path)
        print(f"      → {detection_dict['damage_type']} | conf={detection_dict['confidence']:.2%} | "
              f"coverage={detection_dict['damage_coverage_pct']:.1f}%")

        # ── Step 3: Severity ──
        print("\n[2/6] Assessing severity...")
        from severity import assess_severity
        severity_dict = assess_severity(detection_dict)
        print(f"      → Severity={severity_dict['severity']} | Priority={severity_dict['priority']}")

        # ── Step 4: Geocoding ──
        print("\n[3/6] Reverse geocoding...")
        from geocoder import reverse_geocode
        location_dict = reverse_geocode(latitude, longitude)
        print(f"      → {location_dict.get('full_address', 'Location not available')}")

        # ── Step 5: VLM Description ──
        print("\n[4/6] Generating AI description...")
        from vlm import describe
        vlm_description = describe(
            image_path=detection_dict.get("annotated_image_path", image_path),
            damage_type=detection_dict["damage_type"],
            severity=severity_dict["severity"],
            coverage_pct=detection_dict["damage_coverage_pct"]
        )
        print(f"      → Description generated ({len(vlm_description)} chars)")

        # ── Step 6: Assemble report ──
        print("\n[5/6] Assembling report...")
        from report import generate_report
        report_dict = generate_report(
            detection_dict=detection_dict,
            severity_dict=severity_dict,
            location_dict=location_dict,
            vlm_description=vlm_description
        )
        print(f"      → Complaint ID: {report_dict['complaint_id']}")

        # ── Step 7: Generate PDF ──
        print("\n[6/6] Generating PDF report...")
        try:
            from pdf_generator import create_pdf
            pdf_path = create_pdf(report_dict)
            report_dict["pdf_path"] = pdf_path
            print(f"      → PDF: {pdf_path}")
        except Exception as e:
            print(f"      ⚠️  PDF generation failed: {e}")
            report_dict["pdf_path"] = ""

        # ── Step 8: Save to database ──
        try:
            from database import save_complaint
            saved = save_complaint(report_dict)
            print(f"\n💾 Database: {'✅ Saved' if saved else '❌ Save failed'}")
        except Exception as e:
            print(f"\n⚠️  Database save failed: {e}")

        print("\n" + "=" * 60)
        print(f"✅ PIPELINE COMPLETE — {report_dict['complaint_id']}")
        print("=" * 60)

        return report_dict

    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        print(f"\n❌ {error_msg}")
        traceback.print_exc()
        return {"error": error_msg}


# ──────────────────────────────────────────
# QUICK TEST — run: python run_pipeline.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PIL import Image as PILImage

    print("=" * 60)
    print("PIPELINE INTEGRATION TEST")
    print("=" * 60)

    # Create a test image if none provided
    test_img = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pipeline_test.jpg"
    if not os.path.exists(test_img):
        img = PILImage.new("RGB", (640, 480), color=(80, 80, 80))
        img.save(test_img)
        print(f"Created dummy image: {test_img}")

    result = run_pipeline(
        image_path=test_img,
        latitude=15.3647,
        longitude=75.1240
    )

    if "error" not in result:
        from report import format_report_for_display
        print("\n" + format_report_for_display(result))
    else:
        print(f"Error: {result['error']}")
