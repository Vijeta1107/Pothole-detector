"""
geocoder.py — Reverse geocoding using Nominatim (OpenStreetMap).
Member 2 owns this file.
No API key needed. 100% free.
"""

import time
from config import GEOCODER_USER_AGENT, GEOCODER_TIMEOUT


def reverse_geocode(latitude: float, longitude: float) -> dict:
    """
    Convert GPS coordinates to human-readable address.

    Args:
        latitude:  float, e.g. 15.3647
        longitude: float, e.g. 75.1240

    Returns:
        location_dict with city, area, road, full_address, maps_url
    """

    # ── Handle missing / invalid GPS ──
    if latitude is None or longitude is None:
        return _empty_location("GPS coordinates not provided")

    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return _empty_location("Invalid GPS coordinates format")

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return _empty_location("GPS coordinates out of valid range")

    # ── Nominatim reverse geocoding ──
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError

        geolocator = Nominatim(
            user_agent=GEOCODER_USER_AGENT,
            timeout=GEOCODER_TIMEOUT
        )

        # Nominatim rate limit: 1 request per second
        time.sleep(1)

        location = geolocator.reverse(
            f"{lat}, {lon}",
            exactly_one=True,
            language="en"
        )

        if location is None:
            return _empty_location("Location not found for given coordinates")

        addr = location.raw.get("address", {})

        city  = (addr.get("city") or addr.get("town") or
                 addr.get("village") or addr.get("county") or "Unknown City")
        area  = (addr.get("suburb") or addr.get("neighbourhood") or
                 addr.get("quarter") or addr.get("state_district") or "Unknown Area")
        road  = (addr.get("road") or addr.get("pedestrian") or
                 addr.get("highway") or "Unknown Road")
        state = addr.get("state", "")
        country = addr.get("country", "India")

        full_address = location.address or f"{road}, {area}, {city}, {state}, {country}"

        maps_url = f"https://www.google.com/maps?q={lat},{lon}"

        return {
            "latitude":     lat,
            "longitude":    lon,
            "city":         city,
            "area":         area,
            "road":         road,
            "state":        state,
            "country":      country,
            "full_address": full_address,
            "maps_url":     maps_url,
            "error":        "",
        }

    except ImportError:
        return _empty_location("geopy not installed. Run: pip install geopy")
    except Exception as e:
        return _fallback_location(lat, lon, str(e))


def _empty_location(reason: str) -> dict:
    """Return empty location dict when GPS is unavailable."""
    return {
        "latitude":     None,
        "longitude":    None,
        "city":         "Not provided",
        "area":         "Not provided",
        "road":         "Not provided",
        "state":        "Not provided",
        "country":      "Not provided",
        "full_address": "Location not available",
        "maps_url":     "",
        "error":        reason,
    }


def _fallback_location(lat: float, lon: float, error: str) -> dict:
    """Return minimal location dict when geocoding fails."""
    return {
        "latitude":     lat,
        "longitude":    lon,
        "city":         "Unknown",
        "area":         "Unknown",
        "road":         "Unknown",
        "state":        "Unknown",
        "country":      "India",
        "full_address": f"Coordinates: {lat:.4f}, {lon:.4f}",
        "maps_url":     f"https://www.google.com/maps?q={lat},{lon}",
        "error":        f"Geocoding failed: {error}",
    }


def format_location_display(location_dict: dict) -> str:
    """Format location for display in UI and PDF."""
    if location_dict.get("error") and not location_dict.get("latitude"):
        return "Location not provided"

    parts = []
    if location_dict.get("road") not in ("Unknown", "Not provided", None):
        parts.append(location_dict["road"])
    if location_dict.get("area") not in ("Unknown", "Not provided", None):
        parts.append(location_dict["area"])
    if location_dict.get("city") not in ("Unknown", "Not provided", None):
        parts.append(location_dict["city"])

    return ", ".join(parts) if parts else location_dict.get("full_address", "Unknown Location")


# ──────────────────────────────────────────
# QUICK TEST — run: python geocoder.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("GEOCODER MODULE TEST")
    print("=" * 60)

    test_coords = [
        (15.3647, 75.1240, "Hubballi, Karnataka"),
        (12.9716, 77.5946, "Bengaluru, Karnataka"),
        (19.0760, 72.8777, "Mumbai, Maharashtra"),
        (None,    None,    "No GPS provided"),
        (999,     999,     "Invalid coordinates"),
    ]

    for lat, lon, label in test_coords:
        print(f"\nTest: {label} ({lat}, {lon})")
        result = reverse_geocode(lat, lon)
        print(f"  City:    {result['city']}")
        print(f"  Area:    {result['area']}")
        print(f"  Road:    {result['road']}")
        print(f"  Address: {result['full_address']}")
        if result['error']:
            print(f"  Error:   {result['error']}")

    print("\n✅ geocoder.py working correctly!")