"""
report.py — Complaint report assembler.
Member 2 owns this file.
Combines detection + severity + location + VLM into final report dict.
"""

import uuid
from datetime import datetime
from config import PDF_ORG_NAME, PDF_SYSTEM_NAME


def generate_complaint_id() -> str:
    """Generate a unique complaint ID like CMP-20260530-A3F2."""
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = str(uuid.uuid4()).upper()[:4]
    return f"CMP-{date_part}-{unique_part}"


def generate_report(
    detection_dict: dict,
    severity_dict: dict,
    location_dict: dict,
    vlm_description: str = "",
    pdf_path: str = ""
) -> dict:
    """
    Assemble all module outputs into a single report dict.

    Args:
        detection_dict:  from detector.detect()
        severity_dict:   from severity.assess_severity()
        location_dict:   from geocoder.reverse_geocode()
        vlm_description: string from vlm.describe()
        pdf_path:        path to generated PDF (filled after pdf_generator runs)

    Returns:
        Complete report dict ready for database + PDF + UI display
    """

    complaint_id = generate_complaint_id()
    timestamp    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    damage_type  = detection_dict.get("damage_type", "Unknown")
    confidence   = detection_dict.get("confidence", 0.0)
    coverage_pct = detection_dict.get("damage_coverage_pct", 0.0)
    num_det      = detection_dict.get("num_detections", 0)
    orig_img     = detection_dict.get("original_image_path", "")
    annot_img    = detection_dict.get("annotated_image_path", "")

    severity     = severity_dict.get("severity", "LOW")
    priority     = severity_dict.get("priority", 3)
    action       = severity_dict.get("recommended_action", "")
    sev_reason   = severity_dict.get("severity_reason", "")

    # ── Build VLM description fallback ──
    if not vlm_description or vlm_description.strip() == "":
        vlm_description = _generate_rule_based_description(
            damage_type, severity, coverage_pct, location_dict
        )

    # ── Format location string ──
    city    = location_dict.get("city", "Unknown")
    area    = location_dict.get("area", "Unknown")
    road    = location_dict.get("road", "Unknown")
    lat     = location_dict.get("latitude")
    lon     = location_dict.get("longitude")
    maps_url = location_dict.get("maps_url", "")

    gps_string = f"{lat:.4f}°N, {lon:.4f}°E" if lat and lon else "Not provided"

    report = {
        # Identification
        "complaint_id":          complaint_id,
        "timestamp":             timestamp,
        "generated_by":          PDF_SYSTEM_NAME,
        "organization":          PDF_ORG_NAME,

        # Damage info
        "damage_type":           damage_type,
        "confidence":            round(confidence * 100, 1),   # as percentage
        "damage_coverage_pct":   round(coverage_pct, 2),
        "num_detections":        num_det,
        "all_detections":        detection_dict.get("all_detections", []),

        # Severity
        "severity":              severity,
        "priority":              priority,
        "recommended_action":    action,
        "severity_reason":       sev_reason,

        # Location
        "latitude":              lat,
        "longitude":             lon,
        "gps_string":            gps_string,
        "city":                  city,
        "area":                  area,
        "road":                  road,
        "full_address":          location_dict.get("full_address", "Not provided"),
        "maps_url":              maps_url,

        # VLM
        "vlm_description":       vlm_description,

        # Images
        "original_image_path":   orig_img,
        "annotated_image_path":  annot_img,

        # PDF
        "pdf_path":              pdf_path,

        # Status
        "status":                "SUBMITTED",
    }

    return report


def _generate_rule_based_description(
    damage_type: str,
    severity: str,
    coverage_pct: float,
    location_dict: dict
) -> str:
    """
    Fallback description when VLM API is unavailable.
    Produces a professional complaint-style paragraph.
    """
    location_str = location_dict.get("full_address", "the reported location")
    sev_word = {"LOW": "minor", "MEDIUM": "moderate", "HIGH": "severe"}.get(severity, "notable")

    templates = {
        "Pothole": (
            f"A {sev_word} pothole has been detected on the road surface at {location_str}. "
            f"The damaged area covers approximately {coverage_pct:.1f}% of the road surface in the image. "
            f"This pothole poses a significant risk to vehicle safety and requires prompt municipal attention."
        ),
        "Alligator Crack": (
            f"Extensive {sev_word} alligator cracking (fatigue cracking) has been observed at {location_str}. "
            f"The cracked area covers approximately {coverage_pct:.1f}% of the visible road surface. "
            f"This pattern indicates structural pavement failure and requires resurfacing."
        ),
        "Longitudinal Crack": (
            f"A {sev_word} longitudinal crack running parallel to the road direction has been detected at "
            f"{location_str}, covering {coverage_pct:.1f}% of the road surface. "
            f"Sealing is recommended to prevent water infiltration and further structural damage."
        ),
        "Transverse Crack": (
            f"A {sev_word} transverse crack perpendicular to the road direction has been detected at "
            f"{location_str}, covering {coverage_pct:.1f}% of the road surface. "
            f"Prompt sealing is recommended to prevent deterioration."
        ),
    }

    return templates.get(
        damage_type,
        f"Road damage of type '{damage_type}' ({sev_word} severity) has been detected at "
        f"{location_str}, covering approximately {coverage_pct:.1f}% of the visible road surface."
    )


def format_report_for_display(report: dict) -> str:
    """Format report dict as readable text for Gradio UI display."""
    lines = [
        f"🆔 COMPLAINT ID:      {report['complaint_id']}",
        f"📅 TIMESTAMP:         {report['timestamp']}",
        "─" * 50,
        f"⚠️  DAMAGE TYPE:       {report['damage_type']}",
        f"📊 CONFIDENCE:        {report['confidence']}%",
        f"📐 COVERAGE:          {report['damage_coverage_pct']}% of road surface",
        f"🔢 DETECTIONS:        {report['num_detections']} instance(s) found",
        "─" * 50,
        f"🚨 SEVERITY:          {report['severity']}",
        f"🔺 PRIORITY:          {'URGENT' if report['priority']==1 else 'MODERATE' if report['priority']==2 else 'ROUTINE'}",
        f"🔧 RECOMMENDED ACTION: {report['recommended_action']}",
        "─" * 50,
        f"📍 LOCATION:          {report['full_address']}",
        f"🗺️  GPS:               {report['gps_string']}",
    ]
    if report.get("maps_url"):
        lines.append(f"🔗 MAPS LINK:         {report['maps_url']}")
    lines += [
        "─" * 50,
        f"📝 DESCRIPTION:",
        f"   {report['vlm_description']}",
        "─" * 50,
        f"✅ STATUS:            {report['status']}",
    ]
    return "\n".join(lines)


# ──────────────────────────────────────────
# QUICK TEST — run: python report.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    # Mock data — no ML needed to test this
    mock_detection = {
        "damage_type": "Pothole", "class_id": 3,
        "confidence": 0.87, "damage_coverage_pct": 12.4,
        "num_detections": 2, "all_detections": [],
        "annotated_image_path": "/tmp/annot.jpg",
        "original_image_path": "/tmp/orig.jpg",
    }
    mock_severity = {
        "severity": "HIGH", "priority": 1,
        "recommended_action": "Immediate pothole patching required.",
        "severity_reason": "Pothole class + 12.4% coverage = HIGH",
    }
    mock_location = {
        "latitude": 15.3647, "longitude": 75.1240,
        "city": "Hubballi", "area": "Deshpande Nagar",
        "road": "PB Road", "full_address": "PB Road, Deshpande Nagar, Hubballi, Karnataka",
        "maps_url": "https://www.google.com/maps?q=15.3647,75.1240",
        "error": "",
    }

    report = generate_report(mock_detection, mock_severity, mock_location)

    print("=" * 60)
    print("REPORT MODULE TEST")
    print("=" * 60)
    print(format_report_for_display(report))
    print("\n✅ report.py working correctly!")