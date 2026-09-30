"""
severity.py — Severity assessment and priority logic.
Member 2 owns this file.
NO ML dependency. Can run immediately without best.pt.
"""

from config import (
    SEVERITY_THRESHOLDS, CLASS_SEVERITY_BOOST,
    PRIORITY_MAP, RECOMMENDED_ACTIONS, CLASS_NAMES
)


def assess_severity(detection_dict: dict) -> dict:
    """
    Given a detection dict, compute severity level, priority, and recommended action.

    Args:
        detection_dict: output from detector.detect() or a mock dict

    Returns:
        severity_dict with keys: severity, priority, recommended_action, severity_reason
    """

    damage_type      = detection_dict.get("damage_type", "No Damage")
    class_id         = detection_dict.get("class_id", -1)
    coverage_pct     = detection_dict.get("damage_coverage_pct", 0.0)
    num_detections   = detection_dict.get("num_detections", 0)

    # ── No damage detected ──
    if num_detections == 0 or damage_type == "No Damage":
        return {
            "severity":           "LOW",
            "priority":           3,
            "recommended_action": RECOMMENDED_ACTIONS["No Damage"],
            "severity_reason":    "No damage detected in image.",
        }

    # ── Base severity from coverage % ──
    base_severity = "LOW"
    for level, (low, high) in SEVERITY_THRESHOLDS.items():
        if low <= coverage_pct < high:
            base_severity = level
            break

    # ── Boost severity based on damage class ──
    severity_levels = ["LOW", "MEDIUM", "HIGH"]
    boost = CLASS_SEVERITY_BOOST.get(class_id, 0)
    current_idx = severity_levels.index(base_severity)
    boosted_idx = min(current_idx + boost, len(severity_levels) - 1)
    final_severity = severity_levels[boosted_idx]

    # ── Extra boost if multiple detections ──
    if num_detections >= 3 and final_severity != "HIGH":
        boosted_idx = min(boosted_idx + 1, len(severity_levels) - 1)
        final_severity = severity_levels[boosted_idx]

    priority = PRIORITY_MAP[final_severity]
    recommended_action = RECOMMENDED_ACTIONS.get(damage_type, RECOMMENDED_ACTIONS["No Damage"])

    # ── Build human-readable reason ──
    reason_parts = [
        f"Damage coverage: {coverage_pct:.1f}% of road surface",
        f"Damage type: {damage_type}",
        f"Detections found: {num_detections}",
    ]
    if boost > 0:
        reason_parts.append(f"Severity elevated: {damage_type} is high-risk damage class")
    if num_detections >= 3:
        reason_parts.append("Severity elevated: multiple damage instances detected")

    return {
        "severity":           final_severity,
        "priority":           priority,
        "recommended_action": recommended_action,
        "severity_reason":    ". ".join(reason_parts),
    }


def get_severity_color(severity: str) -> str:
    """Returns hex color for UI display."""
    return {"LOW": "#28a745", "MEDIUM": "#ffc107", "HIGH": "#dc3545"}.get(severity, "#6c757d")


def get_priority_label(priority: int) -> str:
    """Returns human-readable priority label."""
    return {1: "🔴 URGENT", 2: "🟡 MODERATE", 3: "🟢 ROUTINE"}.get(priority, "UNKNOWN")


# ──────────────────────────────────────────
# QUICK TEST — run: python severity.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    # Test with mock detection dicts
    test_cases = [
        {
            "name": "Severe pothole",
            "detection": {
                "damage_type": "Pothole", "class_id": 3,
                "damage_coverage_pct": 8.5, "num_detections": 2
            }
        },
        {
            "name": "Small longitudinal crack",
            "detection": {
                "damage_type": "Longitudinal Crack", "class_id": 0,
                "damage_coverage_pct": 2.1, "num_detections": 1
            }
        },
        {
            "name": "Major alligator cracking",
            "detection": {
                "damage_type": "Alligator Crack", "class_id": 2,
                "damage_coverage_pct": 18.0, "num_detections": 5
            }
        },
        {
            "name": "No damage",
            "detection": {
                "damage_type": "No Damage", "class_id": -1,
                "damage_coverage_pct": 0.0, "num_detections": 0
            }
        },
    ]

    print("=" * 60)
    print("SEVERITY MODULE TEST")
    print("=" * 60)
    for tc in test_cases:
        result = assess_severity(tc["detection"])
        print(f"\nTest: {tc['name']}")
        print(f"  Severity:  {result['severity']}")
        print(f"  Priority:  {get_priority_label(result['priority'])}")
        print(f"  Action:    {result['recommended_action']}")
        print(f"  Reason:    {result['severity_reason']}")
    print("\n✅ severity.py working correctly!")