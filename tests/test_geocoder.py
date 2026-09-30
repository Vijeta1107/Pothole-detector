"""
tests/test_geocoder.py — Unit tests for geocoder.py
Run: python -m pytest tests/ -v
  or: python tests/test_geocoder.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geocoder import reverse_geocode, format_location_display, _empty_location, _fallback_location


# ── Tests ─────────────────────────────────────────────────────

def test_none_coordinates():
    result = reverse_geocode(None, None)
    assert result["error"] != ""
    assert result["latitude"] is None
    assert result["longitude"] is None
    print("✅ test_none_coordinates passed")


def test_invalid_coordinates():
    result = reverse_geocode(999, 999)
    assert result["error"] != ""
    print("✅ test_invalid_coordinates passed")


def test_string_invalid():
    result = reverse_geocode("abc", "xyz")
    assert result["error"] != ""
    print("✅ test_string_invalid passed")


def test_valid_coordinate_structure():
    """Test that valid coords return the expected dict structure."""
    result = reverse_geocode(15.3647, 75.1240)
    required_keys = ["latitude", "longitude", "city", "area", "road",
                     "full_address", "maps_url", "error"]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"
    assert result["latitude"]  == 15.3647
    assert result["longitude"] == 75.1240
    assert "maps.google.com" in result["maps_url"] or "google.com/maps" in result["maps_url"]
    print("✅ test_valid_coordinate_structure passed")


def test_maps_url_format():
    result = reverse_geocode(12.9716, 77.5946)
    if result["maps_url"]:
        assert "12.9716" in result["maps_url"] or "maps" in result["maps_url"]
    print("✅ test_maps_url_format passed")


def test_empty_location_helper():
    result = _empty_location("Test reason")
    assert result["latitude"]  is None
    assert result["longitude"] is None
    assert result["error"]     == "Test reason"
    print("✅ test_empty_location_helper passed")


def test_fallback_location_helper():
    result = _fallback_location(15.0, 75.0, "Network error")
    assert result["latitude"]  == 15.0
    assert result["longitude"] == 75.0
    assert "15.0" in result["full_address"] or "Coordinates" in result["full_address"]
    print("✅ test_fallback_location_helper passed")


def test_format_location_display_no_gps():
    loc = _empty_location("No GPS")
    display = format_location_display(loc)
    assert isinstance(display, str)
    assert len(display) > 0
    print("✅ test_format_location_display_no_gps passed")


def test_format_location_display_with_data():
    loc = {
        "latitude": 15.3647, "longitude": 75.1240,
        "city": "Hubballi", "area": "Deshpande Nagar",
        "road": "PB Road", "full_address": "PB Road, Hubballi",
        "maps_url": "", "error": "",
    }
    display = format_location_display(loc)
    assert "PB Road" in display or "Hubballi" in display
    print("✅ test_format_location_display_with_data passed")


# ── Run all ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("GEOCODER TESTS")
    print("=" * 50)
    test_none_coordinates()
    test_invalid_coordinates()
    test_string_invalid()
    test_valid_coordinate_structure()
    test_maps_url_format()
    test_empty_location_helper()
    test_fallback_location_helper()
    test_format_location_display_no_gps()
    test_format_location_display_with_data()
    print("\n✅ ALL GEOCODER TESTS PASSED")
    print("(Note: live geocoding tests depend on internet access)")
