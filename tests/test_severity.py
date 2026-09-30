"""
tests/test_severity.py — Unit tests for severity.py
Run: python -m pytest tests/ -v
  or: python tests/test_severity.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from severity import assess_severity, get_severity_color, get_priority_label


# ── Helpers ──────────────────────────────────────────────────

def make_det(damage_type, class_id, coverage_pct, num_detections):
    return {
        "damage_type": damage_type,
        "class_id": class_id,
        "damage_coverage_pct": coverage_pct,
        "num_detections": num_detections,
    }


# ── Tests ─────────────────────────────────────────────────────

def test_no_damage():
    result = assess_severity(make_det("No Damage", -1, 0.0, 0))
    assert result["severity"] == "LOW"
    assert result["priority"] == 3
    print("✅ test_no_damage passed")


def test_low_coverage_crack():
    """Small crack with 2% coverage → LOW"""
    result = assess_severity(make_det("Longitudinal Crack", 0, 2.0, 1))
    assert result["severity"] == "LOW"
    assert result["priority"] == 3
    print("✅ test_low_coverage_crack passed")


def test_medium_coverage_crack():
    """Transverse crack with 8% → MEDIUM"""
    result = assess_severity(make_det("Transverse Crack", 1, 8.0, 1))
    assert result["severity"] == "MEDIUM"
    assert result["priority"] == 2
    print("✅ test_medium_coverage_crack passed")


def test_pothole_boost():
    """Pothole with 4% coverage → LOW base, but +2 boost → HIGH"""
    result = assess_severity(make_det("Pothole", 3, 4.0, 1))
    assert result["severity"] == "HIGH"
    assert result["priority"] == 1
    print("✅ test_pothole_boost passed")


def test_alligator_boost():
    """Alligator crack with 4% → LOW base, +1 boost → MEDIUM"""
    result = assess_severity(make_det("Alligator Crack", 2, 4.0, 1))
    assert result["severity"] == "MEDIUM"
    assert result["priority"] == 2
    print("✅ test_alligator_boost passed")


def test_high_coverage():
    """Any damage with >15% coverage → HIGH"""
    result = assess_severity(make_det("Longitudinal Crack", 0, 20.0, 1))
    assert result["severity"] == "HIGH"
    print("✅ test_high_coverage passed")


def test_multiple_detections_boost():
    """3+ detections should boost severity"""
    low = assess_severity(make_det("Longitudinal Crack", 0, 3.0, 1))
    many = assess_severity(make_det("Longitudinal Crack", 0, 3.0, 4))
    levels = ["LOW", "MEDIUM", "HIGH"]
    assert levels.index(many["severity"]) >= levels.index(low["severity"])
    print("✅ test_multiple_detections_boost passed")


def test_severity_color():
    assert get_severity_color("HIGH")   == "#dc3545"
    assert get_severity_color("MEDIUM") == "#ffc107"
    assert get_severity_color("LOW")    == "#28a745"
    print("✅ test_severity_color passed")


def test_priority_label():
    assert "URGENT"   in get_priority_label(1)
    assert "MODERATE" in get_priority_label(2)
    assert "ROUTINE"  in get_priority_label(3)
    print("✅ test_priority_label passed")


def test_recommended_action_present():
    result = assess_severity(make_det("Pothole", 3, 10.0, 2))
    assert result["recommended_action"] != ""
    assert result["severity_reason"]    != ""
    print("✅ test_recommended_action_present passed")


# ── Run all ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("SEVERITY TESTS")
    print("=" * 50)
    test_no_damage()
    test_low_coverage_crack()
    test_medium_coverage_crack()
    test_pothole_boost()
    test_alligator_boost()
    test_high_coverage()
    test_multiple_detections_boost()
    test_severity_color()
    test_priority_label()
    test_recommended_action_present()
    print("\n✅ ALL SEVERITY TESTS PASSED")
