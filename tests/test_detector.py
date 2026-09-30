"""
tests/test_detector.py — Unit tests for detector.py
Run: python -m pytest tests/ -v
  or: python tests/test_detector.py
"""

import sys, os, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_test_image(path: str, w: int = 640, h: int = 480):
    """Create a simple grey test image."""
    try:
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (w, h), color=(100, 100, 100))
        img.save(path)
        return True
    except ImportError:
        # Fallback: create a minimal JPEG manually
        return False


# ── Tests ─────────────────────────────────────────────────────

def test_missing_image():
    from detector import detect
    result = detect("/nonexistent/path/image.jpg")
    assert result["error"] != ""
    assert result["num_detections"] == 0
    print("✅ test_missing_image passed")


def test_returns_required_keys():
    from detector import detect
    tmp = tempfile.mktemp(suffix=".jpg")
    _make_test_image(tmp)
    try:
        result = detect(tmp)
        required = ["damage_type", "class_id", "confidence", "damage_coverage_pct",
                    "num_detections", "all_detections", "annotated_image_path",
                    "original_image_path", "image_width", "image_height", "error"]
        for key in required:
            assert key in result, f"Missing key: {key}"
        print("✅ test_returns_required_keys passed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_confidence_range():
    from detector import detect
    tmp = tempfile.mktemp(suffix=".jpg")
    _make_test_image(tmp)
    try:
        result = detect(tmp)
        assert 0.0 <= result["confidence"] <= 1.0, f"Confidence out of range: {result['confidence']}"
        print("✅ test_confidence_range passed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_coverage_pct_range():
    from detector import detect
    tmp = tempfile.mktemp(suffix=".jpg")
    _make_test_image(tmp)
    try:
        result = detect(tmp)
        assert 0.0 <= result["damage_coverage_pct"] <= 100.0
        print("✅ test_coverage_pct_range passed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_annotated_image_created():
    from detector import detect
    tmp = tempfile.mktemp(suffix=".jpg")
    _make_test_image(tmp)
    try:
        result = detect(tmp)
        annot = result.get("annotated_image_path", "")
        if annot:  # might be empty on error
            assert os.path.exists(annot), f"Annotated image not found: {annot}"
        print("✅ test_annotated_image_created passed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_all_detections_is_list():
    from detector import detect
    tmp = tempfile.mktemp(suffix=".jpg")
    _make_test_image(tmp)
    try:
        result = detect(tmp)
        assert isinstance(result["all_detections"], list)
        print("✅ test_all_detections_is_list passed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_mock_detection_structure():
    """Test _mock_detection returns valid structure."""
    from detector import _mock_detection
    tmp = tempfile.mktemp(suffix=".jpg")
    _make_test_image(tmp)
    try:
        result = _mock_detection(tmp)
        assert result["damage_type"] == "Pothole"
        assert result["num_detections"] >= 1
        assert isinstance(result["all_detections"], list)
        print("✅ test_mock_detection_structure passed")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_error_result_structure():
    from detector import _error_result
    result = _error_result("test error")
    assert result["error"] == "test error"
    assert result["num_detections"] == 0
    assert result["damage_type"] == "Error"
    print("✅ test_error_result_structure passed")


# ── Run all ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("DETECTOR TESTS")
    print("=" * 50)
    test_missing_image()
    test_returns_required_keys()
    test_confidence_range()
    test_coverage_pct_range()
    test_annotated_image_created()
    test_all_detections_is_list()
    test_mock_detection_structure()
    test_error_result_structure()
    print("\n✅ ALL DETECTOR TESTS PASSED")
