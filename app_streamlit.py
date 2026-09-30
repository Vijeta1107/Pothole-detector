"""
app_streamlit.py — Streamlit UI for Pothole Detection System
Run: streamlit run app_streamlit.py
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# ── Page config (MUST be first Streamlit call) ──
st.set_page_config(
    page_title="Smart City Road Damage Detector",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Language support ──
LANGUAGES = {
    "English": {
        "title": "Smart City Road Damage Detector",
        "subtitle": "AI-powered detection • Automated complaint generation • Municipal dashboard",
        "nav_submit": "🛣️ Submit Complaint",
        "nav_demo": "🎬 Live Demo",
        "nav_history": "📊 Complaint History",
        "nav_map": "🗺️ Damage Map",
        "nav_about": "ℹ️ About",
        "upload_label": "Upload Road Image",
        "upload_hint": "JPG, PNG, WEBP — max 10MB",
        "lat_label": "Latitude",
        "lon_label": "Longitude",
        "analyze_btn": "🔍 Analyze & Generate Report",
        "analyzing": "Analyzing road damage with AI...",
        "step_detect": "🔍 Detecting damage...",
        "step_severity": "⚖️ Assessing severity...",
        "step_geo": "📍 Geocoding location...",
        "step_vlm": "🤖 Generating AI description...",
        "step_pdf": "📄 Creating PDF report...",
        "step_db": "💾 Saving to database...",
        "result_title": "Detection Results",
        "download_pdf": "📥 Download PDF Report",
        "severity_high": "HIGH SEVERITY",
        "severity_medium": "MEDIUM SEVERITY",
        "severity_low": "LOW SEVERITY",
        "no_image": "Please upload an image first",
        "complaint_id": "Complaint ID",
        "damage_type": "Damage Type",
        "confidence": "Confidence",
        "coverage": "Road Coverage",
        "instances": "Instances Found",
        "severity": "Severity",
        "priority": "Priority",
        "action": "Recommended Action",
        "location": "Location",
        "gps": "GPS Coordinates",
        "description": "AI Description",
        "history_title": "All Complaints",
        "total": "Total Complaints",
        "urgent": "URGENT",
        "moderate": "MODERATE",
        "routine": "ROUTINE",
        "refresh": "🔄 Refresh",
        "demo_select": "Select Demo Scene",
        "demo_run": "▶️ Run Analysis",
        "filter_sev": "Filter by Severity",
        "filter_all": "All",
        "no_history": "No complaints yet. Submit one to get started!",
        "map_title": "Damage Locations Map",
        "about_tech": "Tech Stack",
        "about_team": "Team Members",
    },
    "ಕನ್ನಡ (Kannada)": {
        "title": "ಸ್ಮಾರ್ಟ್ ಸಿಟಿ ರಸ್ತೆ ಹಾನಿ ಪತ್ತೆ ವ್ಯವಸ್ಥೆ",
        "subtitle": "AI ಆಧಾರಿತ ಪತ್ತೆ • ಸ್ವಯಂ ದೂರು ಉತ್ಪಾದನೆ • ಪಟ್ಟಣ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "nav_submit": "🛣️ ದೂರು ಸಲ್ಲಿಸಿ",
        "nav_demo": "🎬 ಡೆಮೊ",
        "nav_history": "📊 ದೂರು ಇತಿಹಾಸ",
        "nav_map": "🗺️ ನಕ್ಷೆ",
        "nav_about": "ℹ️ ಬಗ್ಗೆ",
        "upload_label": "ರಸ್ತೆ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "upload_hint": "JPG, PNG, WEBP — ಗರಿಷ್ಠ 10MB",
        "lat_label": "ಅಕ್ಷಾಂಶ",
        "lon_label": "ರೇಖಾಂಶ",
        "analyze_btn": "🔍 ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ವರದಿ ರಚಿಸಿ",
        "analyzing": "AI ಮೂಲಕ ರಸ್ತೆ ಹಾನಿ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        "step_detect": "🔍 ಹಾನಿ ಪತ್ತೆ ಮಾಡಲಾಗುತ್ತಿದೆ...",
        "step_severity": "⚖️ ತೀವ್ರತೆ ಮೌಲ್ಯಮಾಪನ...",
        "step_geo": "📍 ಸ್ಥಳ ಗುರುತಿಸಲಾಗುತ್ತಿದೆ...",
        "step_vlm": "🤖 AI ವಿವರಣೆ ರಚಿಸಲಾಗುತ್ತಿದೆ...",
        "step_pdf": "📄 PDF ರಚಿಸಲಾಗುತ್ತಿದೆ...",
        "step_db": "💾 ಡೇಟಾಬೇಸ್‌ಗೆ ಉಳಿಸಲಾಗುತ್ತಿದೆ...",
        "result_title": "ಪತ್ತೆ ಫಲಿತಾಂಶಗಳು",
        "download_pdf": "📥 PDF ವರದಿ ಡೌನ್‌ಲೋಡ್",
        "severity_high": "ಅತಿ ತೀವ್ರ",
        "severity_medium": "ಮಧ್ಯಮ ತೀವ್ರ",
        "severity_low": "ಕಡಿಮೆ ತೀವ್ರ",
        "no_image": "ದಯವಿಟ್ಟು ಮೊದಲು ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "complaint_id": "ದೂರು ID",
        "damage_type": "ಹಾನಿ ವಿಧ",
        "confidence": "ನಂಬಿಕೆ",
        "coverage": "ರಸ್ತೆ ವ್ಯಾಪ್ತಿ",
        "instances": "ಪ್ರಕರಣಗಳ ಸಂಖ್ಯೆ",
        "severity": "ತೀವ್ರತೆ",
        "priority": "ಆದ್ಯತೆ",
        "action": "ಶಿಫಾರಸು ಕ್ರಮ",
        "location": "ಸ್ಥಳ",
        "gps": "GPS ನಿರ್ದೇಶಾಂಕ",
        "description": "AI ವಿವರಣೆ",
        "history_title": "ಎಲ್ಲ ದೂರುಗಳು",
        "total": "ಒಟ್ಟು ದೂರುಗಳು",
        "urgent": "ತುರ್ತು",
        "moderate": "ಮಧ್ಯಮ",
        "routine": "ಸಾಮಾನ್ಯ",
        "refresh": "🔄 ರಿಫ್ರೆಶ್",
        "demo_select": "ಡೆಮೊ ದೃಶ್ಯ ಆರಿಸಿ",
        "demo_run": "▶️ ವಿಶ್ಲೇಷಣೆ ಚಲಾಯಿಸಿ",
        "filter_sev": "ತೀವ್ರತೆಯಿಂದ ಫಿಲ್ಟರ್",
        "filter_all": "ಎಲ್ಲ",
        "no_history": "ಇನ್ನೂ ದೂರುಗಳಿಲ್ಲ. ಮೊದಲ ದೂರು ಸಲ್ಲಿಸಿ!",
        "map_title": "ಹಾನಿ ಸ್ಥಳಗಳ ನಕ್ಷೆ",
        "about_tech": "ತಂತ್ರಜ್ಞಾನ",
        "about_team": "ತಂಡದ ಸದಸ್ಯರು",
    },
    "हिंदी (Hindi)": {
        "title": "स्मार्ट सिटी सड़क क्षति डिटेक्टर",
        "subtitle": "AI आधारित पहचान • स्वचालित शिकायत • नगर पालिका डैशबोर्ड",
        "nav_submit": "🛣️ शिकायत दर्ज करें",
        "nav_demo": "🎬 डेमो",
        "nav_history": "📊 शिकायत इतिहास",
        "nav_map": "🗺️ नक्शा",
        "nav_about": "ℹ️ के बारे में",
        "upload_label": "सड़क की तस्वीर अपलोड करें",
        "upload_hint": "JPG, PNG, WEBP — अधिकतम 10MB",
        "lat_label": "अक्षांश",
        "lon_label": "देशांतर",
        "analyze_btn": "🔍 विश्लेषण करें और रिपोर्ट बनाएं",
        "analyzing": "AI से सड़क क्षति का विश्लेषण हो रहा है...",
        "step_detect": "🔍 क्षति पहचान हो रही है...",
        "step_severity": "⚖️ गंभीरता का आकलन...",
        "step_geo": "📍 स्थान पहचान हो रही है...",
        "step_vlm": "🤖 AI विवरण तैयार हो रहा है...",
        "step_pdf": "📄 PDF रिपोर्ट बन रही है...",
        "step_db": "💾 डेटाबेस में सहेजा जा रहा है...",
        "result_title": "पहचान परिणाम",
        "download_pdf": "📥 PDF रिपोर्ट डाउनलोड करें",
        "severity_high": "अत्यधिक गंभीर",
        "severity_medium": "मध्यम गंभीर",
        "severity_low": "कम गंभीर",
        "no_image": "कृपया पहले तस्वीर अपलोड करें",
        "complaint_id": "शिकायत ID",
        "damage_type": "क्षति का प्रकार",
        "confidence": "विश्वास",
        "coverage": "सड़क कवरेज",
        "instances": "मिले मामले",
        "severity": "गंभीरता",
        "priority": "प्राथमिकता",
        "action": "अनुशंसित कार्रवाई",
        "location": "स्थान",
        "gps": "GPS निर्देशांक",
        "description": "AI विवरण",
        "history_title": "सभी शिकायतें",
        "total": "कुल शिकायतें",
        "urgent": "तत्काल",
        "moderate": "मध्यम",
        "routine": "सामान्य",
        "refresh": "🔄 रिफ्रेश",
        "demo_select": "डेमो दृश्य चुनें",
        "demo_run": "▶️ विश्लेषण चलाएं",
        "filter_sev": "गंभीरता से फ़िल्टर करें",
        "filter_all": "सभी",
        "no_history": "अभी तक कोई शिकायत नहीं। पहली शिकायत दर्ज करें!",
        "map_title": "क्षति स्थानों का नक्शा",
        "about_tech": "तकनीकी स्टैक",
        "about_team": "टीम सदस्य",
    },
}

DEMO_PRESETS = {
    "🕳️ Pothole — PB Road, Hubballi":         ("demo_01_pothole.jpg",      15.3647, 75.1240),
    "🕸️ Alligator Crack — Dharwad Road":       ("demo_02_alligator.jpg",    15.4589, 75.0078),
    "↔️ Longitudinal Crack — Vidyanagar":      ("demo_03_longitudinal.jpg", 15.3560, 75.1350),
    "↕️ Transverse Crack — Keshwapur":         ("demo_04_transverse.jpg",   15.3720, 75.1100),
    "⚠️ Severe Damage — Old Hubli Road":       ("demo_05_severe.jpg",       15.3480, 75.1580),
}

SEV_COLORS = {"HIGH": "#dc3545", "MEDIUM": "#fd7e14", "LOW": "#28a745"}
SEV_BG     = {"HIGH": "#dc354520", "MEDIUM": "#fd7e1420", "LOW": "#28a74520"}

# ──────────────────────────────────────────
# CSS — Dark industrial smart-city theme
# ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Global dark background ── */
.stApp { background: #0d1117; color: #e6edf3; }
section[data-testid="stSidebar"] { background: #161b22 !important; border-right: 1px solid #30363d; }

/* ── Header ── */
.hero-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #0d2137 50%, #051428 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        90deg, transparent, transparent 40px,
        rgba(45,106,159,0.05) 40px, rgba(45,106,159,0.05) 41px
    );
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4em; font-weight: 700;
    color: #58a6ff; margin: 0; letter-spacing: 1px;
}
.hero-sub { color: #8b949e; font-size: 0.95em; margin-top: 4px; }

/* ── Cards ── */
.card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 20px;
    margin-bottom: 16px;
}
.card-accent-red   { border-left: 4px solid #dc3545; }
.card-accent-orange{ border-left: 4px solid #fd7e14; }
.card-accent-green { border-left: 4px solid #28a745; }
.card-accent-blue  { border-left: 4px solid #58a6ff; }

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 130px;
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 16px;
    text-align: center;
}
.metric-value { font-family: 'Rajdhani', sans-serif; font-size: 2.2em; font-weight: 700; }
.metric-label { color: #8b949e; font-size: 0.8em; margin-top: 2px; }

/* ── Severity badge ── */
.sev-badge {
    display: inline-block; padding: 6px 16px;
    border-radius: 20px; font-family: 'Rajdhani', sans-serif;
    font-size: 1.1em; font-weight: 700; letter-spacing: 1px;
}
.sev-HIGH   { background: #dc354525; color: #ff6b7a; border: 1.5px solid #dc3545; }
.sev-MEDIUM { background: #fd7e1425; color: #ffb347; border: 1.5px solid #fd7e14; }
.sev-LOW    { background: #28a74525; color: #51d88a; border: 1.5px solid #28a745; }

/* ── Detection result panel ── */
.result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.result-item { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 12px; }
.result-label { color: #8b949e; font-size: 0.78em; text-transform: uppercase; letter-spacing: 1px; }
.result-value { font-size: 1.05em; font-weight: 500; color: #e6edf3; margin-top: 3px; }

/* ── Progress steps ── */
.step-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; }
.step-dot { width: 10px; height: 10px; border-radius: 50%; background: #58a6ff; }
.step-dot.done { background: #28a745; }
.step-text { color: #8b949e; font-size: 0.9em; }
.step-text.done { color: #51d88a; }

/* ── Table ── */
.stDataFrame { border: 1px solid #30363d !important; border-radius: 8px; overflow: hidden; }
thead th { background: #1a3a5c !important; color: #58a6ff !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1a3a5c, #2d6a9f) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important; letter-spacing: 0.5px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(88,166,255,0.3) !important; }

/* ── Primary button ── */
div[data-testid="stButton"]:first-child > button {
    background: linear-gradient(135deg, #dc3545, #a71d2a) !important;
}

/* ── Inputs ── */
.stNumberInput input, .stTextInput input {
    background: #161b22 !important; border: 1px solid #30363d !important;
    color: #e6edf3 !important; border-radius: 8px !important;
}
.stSelectbox > div { background: #161b22 !important; border-color: #30363d !important; }

/* ── File uploader ── */
.stFileUploader { border: 2px dashed #30363d !important; border-radius: 12px !important; background: #161b22 !important; }

/* ── Description box ── */
.desc-box {
    background: #0d1117; border: 1px solid #30363d; border-left: 4px solid #58a6ff;
    border-radius: 8px; padding: 16px; font-size: 0.95em;
    line-height: 1.7; color: #c9d1d9; font-style: italic;
}

/* ── Sidebar nav ── */
.nav-item {
    display: block; padding: 10px 16px; border-radius: 8px;
    color: #8b949e; text-decoration: none; margin-bottom: 4px;
    cursor: pointer; transition: all 0.15s;
}
.nav-item:hover, .nav-item.active {
    background: #1a3a5c; color: #58a6ff;
}

/* ── Language selector ── */
.lang-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    background: #1a3a5c; color: #58a6ff; font-size: 0.78em; margin: 2px;
}

/* ── Map container ── */
.map-container { border-radius: 12px; overflow: hidden; border: 1px solid #30363d; }

/* ── Instance list ── */
.instance-item {
    background: #0d1117; border: 1px solid #30363d; border-radius: 6px;
    padding: 8px 12px; margin-bottom: 6px;
    display: flex; justify-content: space-between; align-items: center;
}

/* Hide Streamlit default elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "page" not in st.session_state:
    st.session_state.page = "submit"
if "last_report" not in st.session_state:
    st.session_state.last_report = None


def T(key):
    """Translate key to current language."""
    lang = st.session_state.lang
    return LANGUAGES.get(lang, LANGUAGES["English"]).get(key, key)


# ──────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 8px'>
        <div style='font-family:Rajdhani; font-size:1.5em; font-weight:700; color:#58a6ff'>🛣️ SMART CITY</div>
        <div style='color:#8b949e; font-size:0.8em'>Road Damage Detector v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Language selector
    st.markdown("<div style='color:#8b949e; font-size:0.78em; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px'>🌐 Language / ಭಾಷೆ / भाषा</div>", unsafe_allow_html=True)
    lang_choice = st.selectbox(
        "Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.lang),
        label_visibility="collapsed"
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    st.markdown("---")

    # Navigation
    pages = [
        ("submit",  T("nav_submit")),
        ("demo",    T("nav_demo")),
        ("history", T("nav_history")),
        ("map",     T("nav_map")),
        ("about",   T("nav_about")),
    ]
    for page_id, page_label in pages:
        is_active = st.session_state.page == page_id
        style = "background:#1a3a5c; color:#58a6ff;" if is_active else "color:#8b949e;"
        if st.button(
            page_label,
            key=f"nav_{page_id}",
            use_container_width=True,
        ):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("---")

    # Stats sidebar widget
    try:
        from database import get_stats
        s = get_stats()
        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #30363d; border-radius:10px; padding:14px'>
            <div style='color:#8b949e; font-size:0.75em; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px'>{T("total")}</div>
            <div style='font-family:Rajdhani; font-size:2em; font-weight:700; color:#58a6ff'>{s['total']}</div>
            <div style='margin-top:10px; display:flex; gap:8px; flex-wrap:wrap'>
                <span style='background:#dc354525; color:#ff6b7a; padding:3px 10px; border-radius:12px; font-size:0.8em'>🔴 HIGH: {s['high']}</span>
                <span style='background:#fd7e1425; color:#ffb347; padding:3px 10px; border-radius:12px; font-size:0.8em'>🟡 MED: {s['medium']}</span>
                <span style='background:#28a74525; color:#51d88a; padding:3px 10px; border-radius:12px; font-size:0.8em'>🟢 LOW: {s['low']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass


# ──────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────
st.markdown(f"""
<div class='hero-header'>
    <div class='hero-title'>🛣️ {T("title")}</div>
    <div class='hero-sub'>{T("subtitle")}</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DISPLAY RESULTS FUNCTION  (defined here — before all pages use it)
# ══════════════════════════════════════════════════════════════
def _display_results(report, _col=None):
    sev   = report.get("severity", "LOW")
    color = SEV_COLORS.get(sev, "#58a6ff")
    pri   = {1: T("urgent"), 2: T("moderate"), 3: T("routine")}.get(report.get("priority", 3), "ROUTINE")

    # Severity banner
    st.markdown(f"""
    <div style='background:{SEV_BG.get(sev,"#58a6ff20")}; border:2px solid {color};
         border-radius:12px; padding:16px; text-align:center; margin-bottom:16px'>
        <div style='font-family:Rajdhani; font-size:2em; font-weight:700; color:{color}'>{T(f"severity_{sev.lower()}")}</div>
        <div style='color:#8b949e; margin-top:4px'>Priority: <b style="color:{color}">{pri}</b></div>
        <div style='color:#30363d; font-size:0.82em; margin-top:6px'>🆔 {report.get("complaint_id","")}</div>
    </div>
    """, unsafe_allow_html=True)

    # Annotated image
    annot = report.get("annotated_image_path", "")
    orig  = report.get("original_image_path", "")
    img_to_show = annot if annot and os.path.exists(annot) else orig
    if img_to_show and os.path.exists(img_to_show):
        st.image(img_to_show, caption="🎯 Detected Damage", use_container_width=True)

    # Detection metrics grid
    st.markdown(f"""
    <div class='result-grid'>
        <div class='result-item'>
            <div class='result-label'>{T("damage_type")}</div>
            <div class='result-value' style='color:{color}'>{report.get("damage_type","—")}</div>
        </div>
        <div class='result-item'>
            <div class='result-label'>{T("confidence")}</div>
            <div class='result-value'>{report.get("confidence",0):.1f}%</div>
        </div>
        <div class='result-item'>
            <div class='result-label'>{T("coverage")}</div>
            <div class='result-value'>{report.get("damage_coverage_pct",0):.1f}%</div>
        </div>
        <div class='result-item'>
            <div class='result-label'>{T("instances")}</div>
            <div class='result-value'>{report.get("num_detections",0)}</div>
        </div>
        <div class='result-item'>
            <div class='result-label'>{T("location")}</div>
            <div class='result-value' style='font-size:0.9em'>{report.get("city","—")}, {report.get("area","—")}</div>
        </div>
        <div class='result-item'>
            <div class='result-label'>{T("gps")}</div>
            <div class='result-value' style='font-size:0.85em'>{report.get("gps_string","—")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recommended action
    st.markdown(f"""
    <div class='card card-accent-{"red" if sev=="HIGH" else "orange" if sev=="MEDIUM" else "green"}' style='margin-top:12px'>
        <div class='result-label'>🔧 {T("action")}</div>
        <div style='color:#e6edf3; margin-top:4px'>{report.get("recommended_action","—")}</div>
    </div>
    """, unsafe_allow_html=True)

    # AI Description
    if report.get("vlm_description"):
        st.markdown(f"""
        <div style='margin-top:12px'>
            <div class='result-label' style='margin-bottom:6px'>🤖 {T("description")}</div>
            <div class='desc-box'>{report["vlm_description"]}</div>
        </div>
        """, unsafe_allow_html=True)

    # All detection instances
    instances = report.get("all_detections", [])
    if instances and len(instances) > 1:
        st.markdown(f"<div class='result-label' style='margin-top:12px; margin-bottom:6px'>📦 {len(instances)} Detected Instances</div>", unsafe_allow_html=True)
        for i, det in enumerate(instances):
            c = SEV_COLORS.get(sev, "#58a6ff")
            st.markdown(f"""
            <div class='instance-item'>
                <span style='color:{c}'>#{i+1} {det.get("class_name","")}</span>
                <span style='color:#8b949e; font-size:0.85em'>conf: {det.get("confidence",0):.0%}</span>
            </div>
            """, unsafe_allow_html=True)

    # Maps link
    if report.get("maps_url"):
        st.markdown(f"<a href='{report['maps_url']}' target='_blank' style='color:#58a6ff; font-size:0.9em'>🗺️ View on Google Maps</a>", unsafe_allow_html=True)

    # PDF download
    pdf_path = report.get("pdf_path", "")
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label=T("download_pdf"),
                data=f.read(),
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                use_container_width=True,
            )


# ══════════════════════════════════════════════════════════════
# PAGE: SUBMIT COMPLAINT
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "submit":

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown(f"<div class='card card-accent-blue'><b style='color:#58a6ff'>📸 {T('upload_label')}</b><br><small style='color:#8b949e'>{T('upload_hint')}</small></div>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            T("upload_label"),
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            st.image(uploaded_file, use_container_width=True, caption="Uploaded image")

        st.markdown("---")
        st.markdown(f"<div style='color:#8b949e; font-size:0.85em; margin-bottom:8px'>📍 GPS Coordinates (optional)</div>", unsafe_allow_html=True)

        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat = st.number_input(T("lat_label"), value=15.3647, format="%.6f", step=0.0001)
        with col_lon:
            lon = st.number_input(T("lon_label"), value=75.1240, format="%.6f", step=0.0001)

        analyze_clicked = st.button(T("analyze_btn"), use_container_width=True, type="primary")

    with col_right:
        if analyze_clicked:
            if uploaded_file is None:
                st.error(T("no_image"))
            else:
                # Save uploaded file
                import tempfile
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                # Progress display
                progress_placeholder = st.empty()
                steps = [
                    T("step_detect"), T("step_severity"), T("step_geo"),
                    T("step_vlm"), T("step_pdf"), T("step_db")
                ]

                with progress_placeholder.container():
                    st.markdown(f"<div class='card'><b style='color:#58a6ff'>{T('analyzing')}</b></div>", unsafe_allow_html=True)
                    progress_bar = st.progress(0)
                    status_text  = st.empty()

                    def update_progress(i, text):
                        progress_bar.progress((i + 1) / len(steps))
                        status_text.markdown(f"<div style='color:#8b949e; font-size:0.9em'>{text}</div>", unsafe_allow_html=True)

                    update_progress(0, steps[0])

                try:
                    from run_pipeline import run_pipeline
                    report = run_pipeline(tmp_path, lat, lon)
                    progress_placeholder.empty()

                    if "error" in report and not report.get("complaint_id"):
                        st.error(f"❌ {report['error']}")
                    else:
                        st.session_state.last_report = report
                        _display_results(report, col_right)

                except Exception as e:
                    progress_placeholder.empty()
                    st.error(f"❌ Error: {e}")
                finally:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

        elif st.session_state.last_report:
            _display_results(st.session_state.last_report, col_right)
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px 20px'>
                <div style='font-size:4em'>🛣️</div>
                <div style='color:#8b949e; margin-top:12px'>Upload a road image and click Analyze</div>
                <div style='color:#30363d; font-size:0.85em; margin-top:8px'>Supports JPG · PNG · WEBP</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: DEMO
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "demo":
    st.markdown(f"<div class='card card-accent-blue'><b style='color:#58a6ff'>{T('nav_demo')}</b> — Select a pre-loaded scene to see the AI in action</div>", unsafe_allow_html=True)

    demo_choice = st.selectbox(T("demo_select"), list(DEMO_PRESETS.keys()))
    filename, demo_lat, demo_lon = DEMO_PRESETS[demo_choice]

    from config import DEMO_IMAGES_DIR
    demo_path = os.path.join(DEMO_IMAGES_DIR, filename)

    # Create placeholder demo if not exists
    if not os.path.exists(demo_path):
        try:
            from PIL import Image as PILImage, ImageDraw
            img = PILImage.new("RGB", (640, 480), color=(70, 70, 75))
            draw = ImageDraw.Draw(img)
            draw.rectangle([80, 120, 560, 360], outline=(200, 80, 80), width=3)
            draw.text((200, 220), f"[DEMO] {filename}", fill=(255, 255, 255))
            draw.text((180, 250), "Replace with real road photo", fill=(180, 180, 180))
            img.save(demo_path)
        except Exception:
            pass

    col_d1, col_d2 = st.columns(2, gap="large")
    with col_d1:
        if os.path.exists(demo_path):
            st.image(demo_path, caption=demo_choice, use_container_width=True)
        st.markdown(f"**GPS:** {demo_lat:.4f}°N, {demo_lon:.4f}°E")

        if st.button(T("demo_run"), use_container_width=True):
            with st.spinner(T("analyzing")):
                try:
                    from run_pipeline import run_pipeline
                    demo_report = run_pipeline(demo_path, demo_lat, demo_lon)
                    st.session_state[f"demo_result_{demo_choice}"] = demo_report
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_d2:
        key = f"demo_result_{demo_choice}"
        if key in st.session_state and st.session_state[key]:
            _display_results(st.session_state[key])
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px 20px'>
                <div style='font-size:3em'>▶️</div>
                <div style='color:#8b949e; margin-top:10px'>Click "Run Analysis" to see results</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: COMPLAINT HISTORY
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "history":
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"<div style='font-family:Rajdhani; font-size:1.6em; font-weight:700; color:#58a6ff'>{T('history_title')}</div>", unsafe_allow_html=True)
    with col_h2:
        if st.button(T("refresh"), use_container_width=True):
            st.rerun()

    try:
        from database import get_all_complaints, get_stats
        stats = get_stats()
        rows  = get_all_complaints()

        # Stats metrics
        st.markdown(f"""
        <div class='metric-row'>
            <div class='metric-card'>
                <div class='metric-value' style='color:#58a6ff'>{stats['total']}</div>
                <div class='metric-label'>{T("total")}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-value' style='color:#ff6b7a'>{stats['high']}</div>
                <div class='metric-label'>HIGH</div>
            </div>
            <div class='metric-card'>
                <div class='metric-value' style='color:#ffb347'>{stats['medium']}</div>
                <div class='metric-label'>MEDIUM</div>
            </div>
            <div class='metric-card'>
                <div class='metric-value' style='color:#51d88a'>{stats['low']}</div>
                <div class='metric-label'>LOW</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Charts
        if rows:
            import json

            # Parse data for charts
            df_raw = pd.DataFrame(rows)

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown("<div class='card'><b style='color:#58a6ff'>📊 Severity Distribution</b></div>", unsafe_allow_html=True)
                sev_counts = df_raw["severity"].value_counts().reset_index()
                sev_counts.columns = ["Severity", "Count"]
                sev_counts["Color"] = sev_counts["Severity"].map(SEV_COLORS)
                st.bar_chart(sev_counts.set_index("Severity")["Count"])

            with chart_col2:
                st.markdown("<div class='card'><b style='color:#58a6ff'>🗺️ Damage Types</b></div>", unsafe_allow_html=True)
                dmg_counts = df_raw["damage_type"].value_counts().reset_index()
                dmg_counts.columns = ["Type", "Count"]
                st.bar_chart(dmg_counts.set_index("Type")["Count"])

            # Filter
            sev_filter = st.selectbox(
                T("filter_sev"),
                [T("filter_all"), "HIGH", "MEDIUM", "LOW"],
            )

            # Build display dataframe
            display_rows = []
            for r in rows:
                if sev_filter != T("filter_all") and r.get("severity") != sev_filter:
                    continue
                pri_label = {1: "🔴 URGENT", 2: "🟡 MODERATE", 3: "🟢 ROUTINE"}.get(r.get("priority"), "")
                display_rows.append({
                    T("complaint_id"):  r.get("complaint_id", ""),
                    "Timestamp":        r.get("timestamp", ""),
                    T("damage_type"):   r.get("damage_type", ""),
                    T("severity"):      r.get("severity", ""),
                    T("priority"):      pri_label,
                    T("coverage"):      f"{r.get('damage_coverage_pct', 0):.1f}%",
                    "City":             r.get("city", ""),
                    "Road":             r.get("road", ""),
                    "Status":           r.get("status", ""),
                })

            if display_rows:
                st.dataframe(
                    pd.DataFrame(display_rows),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(T("no_history"))
        else:
            st.info(T("no_history"))

    except Exception as e:
        st.error(f"Database error: {e}")


# ══════════════════════════════════════════════════════════════
# PAGE: MAP VIEW
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "map":
    st.markdown(f"<div style='font-family:Rajdhani; font-size:1.6em; font-weight:700; color:#58a6ff'>{T('map_title')}</div>", unsafe_allow_html=True)

    try:
        from database import get_all_complaints
        rows = get_all_complaints()

        map_data = []
        for r in rows:
            lat_v = r.get("latitude")
            lon_v = r.get("longitude")
            if lat_v and lon_v:
                try:
                    map_data.append({
                        "lat": float(lat_v),
                        "lon": float(lon_v),
                        "damage": r.get("damage_type", "Unknown"),
                        "severity": r.get("severity", "LOW"),
                        "id": r.get("complaint_id", ""),
                    })
                except Exception:
                    pass

        if map_data:
            df_map = pd.DataFrame(map_data)
            st.map(df_map[["lat", "lon"]], zoom=11, use_container_width=True)

            # Legend
            st.markdown("""
            <div class='card' style='margin-top:12px'>
                <b style='color:#58a6ff'>Complaint Locations</b>
                <div style='margin-top:8px; display:flex; gap:16px; flex-wrap:wrap'>
                    <span style='color:#ff6b7a'>🔴 HIGH severity</span>
                    <span style='color:#ffb347'>🟡 MEDIUM severity</span>
                    <span style='color:#51d88a'>🟢 LOW severity</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Table below map
            st.markdown("---")
            st.dataframe(
                df_map.rename(columns={"lat": "Latitude", "lon": "Longitude",
                                        "damage": "Damage Type", "severity": "Severity", "id": "ID"}),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.markdown("""
            <div class='card' style='text-align:center; padding:60px'>
                <div style='font-size:3em'>🗺️</div>
                <div style='color:#8b949e; margin-top:10px'>No GPS data yet. Submit complaints with coordinates to see the map.</div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Map error: {e}")


# ══════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "about":
    col_a1, col_a2 = st.columns([3, 2], gap="large")

    with col_a1:
        st.markdown(f"""
        <div class='card card-accent-blue'>
            <div style='font-family:Rajdhani; font-size:1.3em; font-weight:700; color:#58a6ff; margin-bottom:12px'>{T("about_tech")}</div>
            <table style='width:100%; border-collapse:collapse; color:#e6edf3'>
                <tr><td style='padding:8px; color:#8b949e'>Detection</td><td style='padding:8px'>YOLOv8 + Gemini Vision API</td></tr>
                <tr style='background:#0d1117'><td style='padding:8px; color:#8b949e'>VLM</td><td style='padding:8px'>Google Gemini 1.5 Flash + Groq LLaMA3</td></tr>
                <tr><td style='padding:8px; color:#8b949e'>Geocoding</td><td style='padding:8px'>OpenStreetMap Nominatim (free)</td></tr>
                <tr style='background:#0d1117'><td style='padding:8px; color:#8b949e'>UI</td><td style='padding:8px'>Streamlit (upgraded from Gradio)</td></tr>
                <tr><td style='padding:8px; color:#8b949e'>PDF</td><td style='padding:8px'>ReportLab</td></tr>
                <tr style='background:#0d1117'><td style='padding:8px; color:#8b949e'>Database</td><td style='padding:8px'>SQLite</td></tr>
                <tr><td style='padding:8px; color:#8b949e'>Languages</td><td style='padding:8px'>English · ಕನ್ನಡ · हिंदी</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='card' style='margin-top:16px'>
            <div style='font-family:Rajdhani; font-size:1.3em; font-weight:700; color:#58a6ff; margin-bottom:12px'>📊 Pipeline</div>
            <div style='color:#8b949e; font-size:0.9em; line-height:2'>
                📸 Image Upload<br>
                ↓ 🔍 YOLOv8 / Gemini Vision Detection<br>
                ↓ ⚖️ Severity Assessment (coverage + class boost)<br>
                ↓ 📍 Reverse Geocoding (OpenStreetMap)<br>
                ↓ 🤖 AI Description (Gemini 1.5 Flash / Groq LLaMA3)<br>
                ↓ 📄 PDF Report (ReportLab)<br>
                ↓ 💾 SQLite Database<br>
                ↓ ✅ Complaint ID Generated
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a2:
        st.markdown(f"""
        <div class='card card-accent-blue'>
            <div style='font-family:Rajdhani; font-size:1.3em; font-weight:700; color:#58a6ff; margin-bottom:12px'>{T("about_team")}</div>
            <div style='display:flex; flex-direction:column; gap:10px'>
                <div style='background:#0d1117; border-radius:8px; padding:12px'>
                    <div style='color:#58a6ff; font-weight:600'>Member 1</div>
                    <div style='color:#8b949e; font-size:0.85em'>YOLOv8 training · detector.py · utils.py · evaluation.py</div>
                </div>
                <div style='background:#0d1117; border-radius:8px; padding:12px'>
                    <div style='color:#58a6ff; font-weight:600'>Member 2</div>
                    <div style='color:#8b949e; font-size:0.85em'>severity.py · geocoder.py · report.py · database.py</div>
                </div>
                <div style='background:#0d1117; border-radius:8px; padding:12px'>
                    <div style='color:#58a6ff; font-weight:600'>Member 3</div>
                    <div style='color:#8b949e; font-size:0.85em'>vlm.py · pdf_generator.py · demo_images/</div>
                </div>
                <div style='background:#0d1117; border-radius:8px; padding:12px'>
                    <div style='color:#58a6ff; font-weight:600'>Member 4</div>
                    <div style='color:#8b949e; font-size:0.85em'>config.py · app_streamlit.py · run_pipeline.py</div>
                </div>
            </div>
        </div>

        <div class='card' style='margin-top:16px'>
            <div style='font-family:Rajdhani; font-size:1.1em; font-weight:700; color:#58a6ff; margin-bottom:10px'>🏆 PS-SC1 Deliverables</div>
            <div style='color:#8b949e; font-size:0.85em; line-height:2'>
                ✅ Image classification with VLM<br>
                ✅ Auto-generated structured complaint<br>
                ✅ GPS tag input support<br>
                ✅ 5 demo road images<br>
                ✅ PDF report download<br>
                ✅ SQLite complaint database<br>
                ✅ Multilingual UI (EN/KN/HI)<br>
                ✅ Interactive damage map<br>
                ✅ Severity charts & analytics
            </div>
        </div>
        """, unsafe_allow_html=True)


# Footer
st.markdown("""
<div style='text-align:center; color:#30363d; font-size:0.8em; padding:20px 0 10px; margin-top:40px; border-top:1px solid #21262d'>
    Smart City Municipal Corporation · Road Damage Detection System v2.0 · GenAI Hackathon 2026
</div>
""", unsafe_allow_html=True)