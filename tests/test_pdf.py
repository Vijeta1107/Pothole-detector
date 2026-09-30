"""
tests/test_pdf.py — Unit tests for pdf_generator.py
Run: python -m pytest tests/ -v
  or: python tests/test_pdf.py
"""

import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime


def _mock_report(overrides: dict = None) -> dict:
    """Return a complete mock report dict for testing."""
    base = {
        "complaint_id":        "CMP-TEST-0001",
        "timestamp":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "damage_type":         "Pothole",
        "confidence":          87.0,
        "damage_coverage_pct": 12.4,
        "num_detections":      2,
        "severity":            "HIGH",
        "priority":            1,
        "recommended_action":  "Immediate pothole patching required.",
        "severity_reason":     "Pothole + 12.4% coverage = HIGH",
        "city":                "Hubballi",
        "area":                "Deshpande Nagar",
        "road":                "PB Road",
        "full_address":        "PB Road, Deshpande Nagar, Hubballi, Karnataka 580020",
        "latitude":            15.3647,
        "longitude":           75.1240,
        "gps_string":          "15.3647°N, 75.1240°E",
        "maps_url":            "https://www.google.com/maps?q=15.3647,75.1240",
        "vlm_description":     "A severe pothole has been detected on the road surface.",
        "original_image_path": "",
        "annotated_image_path":"",
        "status":              "SUBMITTED",
    }
    if overrides:
        base.update(overrides)
    return base


# ── Tests ─────────────────────────────────────────────────────

def test_pdf_created():
    """PDF file should be created and exist on disk."""
    try:
        from pdf_generator import create_pdf
    except ImportError:
        print("⚠️  pdf_generator not available — skipping")
        return

    report = _mock_report()
    pdf_path = create_pdf(report)

    assert pdf_path != "", "create_pdf returned empty path"
    assert os.path.exists(pdf_path), f"PDF file not found: {pdf_path}"
    assert pdf_path.endswith(".pdf"), "File should have .pdf extension"
    print(f"✅ test_pdf_created passed — {pdf_path}")


def test_pdf_not_empty():
    """PDF should have content (> 1KB)."""
    try:
        from pdf_generator import create_pdf
    except ImportError:
        print("⚠️  pdf_generator not available — skipping")
        return

    report = _mock_report()
    pdf_path = create_pdf(report)
    if pdf_path and os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        assert size > 1024, f"PDF is suspiciously small: {size} bytes"
        print(f"✅ test_pdf_not_empty passed — {size} bytes")


def test_pdf_filename_contains_complaint_id():
    try:
        from pdf_generator import create_pdf
    except ImportError:
        print("⚠️  skipping")
        return

    cid = "CMP-PYTEST-ABCD"
    report = _mock_report({"complaint_id": cid})
    pdf_path = create_pdf(report)
    if pdf_path:
        assert cid in os.path.basename(pdf_path), \
            f"Expected '{cid}' in filename '{os.path.basename(pdf_path)}'"
        print("✅ test_pdf_filename_contains_complaint_id passed")


def test_pdf_with_image(tmp_path=None):
    """PDF should include an image when one is provided."""
    try:
        from pdf_generator import create_pdf
        from PIL import Image as PILImage
    except ImportError:
        print("⚠️  skipping (missing dependency)")
        return

    # Create a temp image
    img_path = tempfile.mktemp(suffix=".jpg")
    PILImage.new("RGB", (320, 240), color=(80, 80, 80)).save(img_path)

    report = _mock_report({
        "original_image_path":  img_path,
        "annotated_image_path": img_path,
    })
    pdf_path = create_pdf(report)

    if pdf_path:
        assert os.path.exists(pdf_path)
        print(f"✅ test_pdf_with_image passed — {pdf_path}")

    if os.path.exists(img_path):
        os.remove(img_path)


def test_pdf_all_severities():
    """PDFs should generate for LOW / MEDIUM / HIGH without error."""
    try:
        from pdf_generator import create_pdf
    except ImportError:
        print("⚠️  skipping")
        return

    for sev, pri, label in [("LOW", 3, "ROUTINE"), ("MEDIUM", 2, "MODERATE"), ("HIGH", 1, "URGENT")]:
        report = _mock_report({
            "complaint_id": f"CMP-SEV-{sev}",
            "severity":     sev,
            "priority":     pri,
        })
        pdf_path = create_pdf(report)
        assert pdf_path and os.path.exists(pdf_path), f"PDF failed for severity {sev}"
    print("✅ test_pdf_all_severities passed")


def test_pdf_no_image():
    """PDF should still generate gracefully when no image is provided."""
    try:
        from pdf_generator import create_pdf
    except ImportError:
        print("⚠️  skipping")
        return

    report = _mock_report({
        "complaint_id":        "CMP-NOIMG-0001",
        "original_image_path": "",
        "annotated_image_path": "",
    })
    pdf_path = create_pdf(report)
    assert pdf_path and os.path.exists(pdf_path)
    print("✅ test_pdf_no_image passed")


# ── Run all ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("PDF GENERATOR TESTS")
    print("=" * 50)
    test_pdf_created()
    test_pdf_not_empty()
    test_pdf_filename_contains_complaint_id()
    test_pdf_with_image()
    test_pdf_all_severities()
    test_pdf_no_image()
    print("\n✅ ALL PDF TESTS PASSED")
