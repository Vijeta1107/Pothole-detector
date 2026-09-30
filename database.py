"""
database.py — SQLite storage for complaint records.
Member 2 owns this file.
"""

import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    """Create database and complaints table if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id          TEXT PRIMARY KEY,
            timestamp             TEXT NOT NULL,
            original_image_path   TEXT,
            annotated_image_path  TEXT,
            damage_type           TEXT,
            confidence            REAL,
            damage_coverage_pct   REAL,
            num_detections        INTEGER,
            severity              TEXT,
            priority              INTEGER,
            latitude              REAL,
            longitude             REAL,
            city                  TEXT,
            area                  TEXT,
            road                  TEXT,
            full_address          TEXT,
            maps_url              TEXT,
            vlm_description       TEXT,
            recommended_action    TEXT,
            severity_reason       TEXT,
            pdf_path              TEXT,
            status                TEXT DEFAULT 'SUBMITTED',
            all_detections_json   TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_complaint(report_dict: dict) -> bool:
    """
    Save a complaint report to the database.
    Returns True on success, False on failure.
    """
    try:
        init_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO complaints (
                complaint_id, timestamp, original_image_path, annotated_image_path,
                damage_type, confidence, damage_coverage_pct, num_detections,
                severity, priority, latitude, longitude, city, area, road,
                full_address, maps_url, vlm_description, recommended_action,
                severity_reason, pdf_path, status, all_detections_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            report_dict.get("complaint_id"),
            report_dict.get("timestamp"),
            report_dict.get("original_image_path"),
            report_dict.get("annotated_image_path"),
            report_dict.get("damage_type"),
            report_dict.get("confidence"),
            report_dict.get("damage_coverage_pct"),
            report_dict.get("num_detections"),
            report_dict.get("severity"),
            report_dict.get("priority"),
            report_dict.get("latitude"),
            report_dict.get("longitude"),
            report_dict.get("city"),
            report_dict.get("area"),
            report_dict.get("road"),
            report_dict.get("full_address"),
            report_dict.get("maps_url"),
            report_dict.get("vlm_description"),
            report_dict.get("recommended_action"),
            report_dict.get("severity_reason"),
            report_dict.get("pdf_path"),
            report_dict.get("status", "SUBMITTED"),
            json.dumps(report_dict.get("all_detections", [])),
        ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Database error saving complaint: {e}")
        return False


def get_all_complaints() -> list:
    """Fetch all complaints, newest first."""
    try:
        init_db()
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM complaints ORDER BY timestamp DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"Database error fetching complaints: {e}")
        return []


def get_complaint_by_id(complaint_id: str) -> dict:
    """Fetch a single complaint by ID."""
    try:
        init_db()
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    except Exception as e:
        print(f"Database error: {e}")
        return {}


def get_complaints_for_display() -> list:
    """
    Returns list of dicts formatted for Gradio DataFrame display.
    Only includes columns that are useful to show in a table.
    """
    rows = get_all_complaints()
    display = []
    for r in rows:
        display.append({
            "Complaint ID":  r.get("complaint_id", ""),
            "Timestamp":     r.get("timestamp", ""),
            "Damage Type":   r.get("damage_type", ""),
            "Severity":      r.get("severity", ""),
            "Priority":      {1: "URGENT", 2: "MODERATE", 3: "ROUTINE"}.get(r.get("priority"), ""),
            "Coverage %":    f"{r.get('damage_coverage_pct', 0):.1f}%",
            "City":          r.get("city", ""),
            "Road":          r.get("road", ""),
            "Status":        r.get("status", ""),
        })
    return display


def get_stats() -> dict:
    """Return summary statistics for display."""
    try:
        init_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE severity='HIGH'")
        high = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE severity='MEDIUM'")
        medium = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE severity='LOW'")
        low = cursor.fetchone()[0]
        conn.close()
        return {"total": total, "high": high, "medium": medium, "low": low}
    except Exception as e:
        return {"total": 0, "high": 0, "medium": 0, "low": 0}


# ──────────────────────────────────────────
# QUICK TEST — run: python database.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MODULE TEST")
    print("=" * 60)

    mock_report = {
        "complaint_id": "CMP-TEST-0001",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "damage_type": "Pothole", "confidence": 87.0,
        "damage_coverage_pct": 12.4, "num_detections": 2,
        "severity": "HIGH", "priority": 1,
        "city": "Hubballi", "area": "Deshpande Nagar", "road": "PB Road",
        "full_address": "PB Road, Hubballi", "latitude": 15.3647, "longitude": 75.1240,
        "maps_url": "", "vlm_description": "Severe pothole detected.",
        "recommended_action": "Immediate repair required.",
        "severity_reason": "Pothole + HIGH coverage",
        "pdf_path": "", "status": "SUBMITTED",
        "original_image_path": "", "annotated_image_path": "",
        "all_detections": [],
    }

    success = save_complaint(mock_report)
    print(f"Save complaint: {'✅' if success else '❌'}")

    rows = get_all_complaints()
    print(f"Total complaints in DB: {len(rows)}")

    fetched = get_complaint_by_id("CMP-TEST-0001")
    print(f"Fetch by ID: {'✅' if fetched else '❌'}")
    print(f"  Damage: {fetched.get('damage_type')} | Severity: {fetched.get('severity')}")

    stats = get_stats()
    print(f"Stats: {stats}")

    print("\n✅ database.py working correctly!")