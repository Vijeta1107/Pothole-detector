"""
app.py — Gradio UI for the Pothole Detection Complaint System.
Member 4 owns this file.
Run: python app.py
"""

import os
import gradio as gr
import pandas as pd
from datetime import datetime
from config import DEMO_IMAGES_DIR, REPORTS_DIR, BASE_DIR


# ── Demo image presets (GPS coords for Hubballi area) ──
DEMO_PRESETS = {
    "Demo 1 — Pothole (PB Road, Hubballi)":        ("demo_01_pothole.jpg",      15.3647, 75.1240),
    "Demo 2 — Alligator Crack (Dharwad Road)":     ("demo_02_alligator.jpg",    15.4589, 75.0078),
    "Demo 3 — Longitudinal Crack (Vidyanagar)":    ("demo_03_longitudinal.jpg", 15.3560, 75.1350),
    "Demo 4 — Transverse Crack (Keshwapur)":       ("demo_04_transverse.jpg",   15.3720, 75.1100),
    "Demo 5 — Severe Damage (Old Hubli Road)":     ("demo_05_severe.jpg",       15.3480, 75.1580),
}

SEVERITY_COLORS = {
    "HIGH":   "#dc3545",
    "MEDIUM": "#fd7e14",
    "LOW":    "#28a745",
}


# ══════════════════════════════════════════════════════════════
# CORE PIPELINE WRAPPER
# ══════════════════════════════════════════════════════════════

def analyze_image(image_path, latitude, longitude, progress=gr.Progress()):
    """
    Main function called by Gradio.
    Returns: annotated_image, report_text, pdf_path, severity_badge
    """
    if image_path is None:
        return None, "❌ Please upload a road image first.", None, ""

    try:
        lat = float(latitude) if latitude and str(latitude).strip() else None
        lon = float(longitude) if longitude and str(longitude).strip() else None
    except ValueError:
        lat, lon = None, None

    progress(0.1, desc="Loading image...")
    from run_pipeline import run_pipeline

    progress(0.2, desc="Detecting damage...")
    report = run_pipeline(image_path, lat, lon)

    if "error" in report and not report.get("complaint_id"):
        return None, f"❌ Error: {report['error']}", None, ""

    progress(0.9, desc="Finalizing report...")

    # ── Format display ──
    from report import format_report_for_display
    report_text = format_report_for_display(report)

    # ── Annotated image ──
    annot_img = report.get("annotated_image_path", "")
    if not annot_img or not os.path.exists(annot_img):
        annot_img = image_path

    # ── PDF ──
    pdf_path = report.get("pdf_path", "")
    pdf_out  = pdf_path if pdf_path and os.path.exists(pdf_path) else None

    # ── Severity badge HTML ──
    sev   = report.get("severity", "LOW")
    color = SEVERITY_COLORS.get(sev, "#6c757d")
    pri   = {1: "URGENT", 2: "MODERATE", 3: "ROUTINE"}.get(report.get("priority", 3), "ROUTINE")
    badge = f"""
    <div style='text-align:center; padding:16px; border-radius:12px; background:{color}20; border:2px solid {color}'>
        <div style='font-size:2em; font-weight:bold; color:{color}'>{sev}</div>
        <div style='font-size:1em; color:#555; margin-top:4px'>Priority: {pri}</div>
        <div style='font-size:0.85em; color:#777; margin-top:8px'>🆔 {report.get("complaint_id","")}</div>
    </div>"""

    progress(1.0, desc="Done!")
    return annot_img, report_text, pdf_out, badge


def load_demo(demo_choice):
    """Load a demo image and pre-fill GPS coordinates."""
    if not demo_choice or demo_choice not in DEMO_PRESETS:
        return None, "", ""

    filename, lat, lon = DEMO_PRESETS[demo_choice]
    demo_path = os.path.join(DEMO_IMAGES_DIR, filename)

    if not os.path.exists(demo_path):
        # Create a placeholder image if demo images aren't present yet
        try:
            from PIL import Image as PILImage, ImageDraw
            img = PILImage.new("RGB", (640, 480), color=(90, 90, 90))
            draw = ImageDraw.Draw(img)
            draw.text((180, 200), f"Demo: {filename}", fill=(255, 255, 255))
            draw.text((160, 230), "(Replace with real road image)", fill=(200, 200, 200))
            img.save(demo_path)
        except Exception:
            return None, str(lat), str(lon)

    return demo_path, str(lat), str(lon)


def get_complaint_history():
    """Fetch complaints from DB and return as DataFrame."""
    try:
        from database import get_complaints_for_display
        rows = get_complaints_for_display()
        if not rows:
            return pd.DataFrame(columns=["Complaint ID", "Timestamp", "Damage Type",
                                          "Severity", "Priority", "Coverage %", "City", "Road", "Status"])
        return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})


def get_stats_html():
    """Return stats as HTML."""
    try:
        from database import get_stats
        s = get_stats()
        return f"""
        <div style='display:flex; gap:16px; flex-wrap:wrap; justify-content:center; padding:12px'>
            <div style='background:#1a3a5c; color:white; padding:16px 28px; border-radius:10px; text-align:center'>
                <div style='font-size:2em; font-weight:bold'>{s['total']}</div>
                <div>Total Complaints</div>
            </div>
            <div style='background:#dc3545; color:white; padding:16px 28px; border-radius:10px; text-align:center'>
                <div style='font-size:2em; font-weight:bold'>{s['high']}</div>
                <div>HIGH Severity</div>
            </div>
            <div style='background:#fd7e14; color:white; padding:16px 28px; border-radius:10px; text-align:center'>
                <div style='font-size:2em; font-weight:bold'>{s['medium']}</div>
                <div>MEDIUM Severity</div>
            </div>
            <div style='background:#28a745; color:white; padding:16px 28px; border-radius:10px; text-align:center'>
                <div style='font-size:2em; font-weight:bold'>{s['low']}</div>
                <div>LOW Severity</div>
            </div>
        </div>"""
    except Exception:
        return "<p>Stats unavailable</p>"


# ══════════════════════════════════════════════════════════════
# GRADIO UI
# ══════════════════════════════════════════════════════════════

CSS = """
#title { text-align: center; }
.tab-nav button { font-size: 15px !important; font-weight: 600 !important; }
.report-box textarea { font-family: monospace !important; font-size: 13px !important; }
footer { display: none !important; }
"""

with gr.Blocks(title="🛣️ Pothole Detection System", css=CSS, theme=gr.themes.Soft()) as app:

    # ── Header ──
    gr.HTML("""
    <div style='text-align:center; padding:20px 0 10px'>
        <h1 style='font-size:2em; color:#1a3a5c; margin:0'>
            🛣️ Smart City Pothole Detection System
        </h1>
        <p style='color:#666; margin:6px 0 0'>
            AI-powered road damage detection & automated complaint generation
        </p>
    </div>
    """)

    with gr.Tabs():

        # ════════════════════════════════════
        # TAB 1: Submit Complaint
        # ════════════════════════════════════
        with gr.Tab("📤 Submit Complaint"):
            gr.Markdown("Upload a road image and optionally provide GPS coordinates to generate a complaint report.")

            with gr.Row():
                # Left column — inputs
                with gr.Column(scale=1):
                    image_input = gr.Image(
                        label="📸 Road Image",
                        type="filepath",
                        height=300
                    )
                    with gr.Row():
                        lat_input = gr.Number(
                            label="📍 Latitude",
                            value=15.3647,
                            precision=6,
                            info="e.g. 15.3647"
                        )
                        lon_input = gr.Number(
                            label="📍 Longitude",
                            value=75.1240,
                            precision=6,
                            info="e.g. 75.1240"
                        )
                    analyze_btn = gr.Button(
                        "🔍 Analyze & Generate Report",
                        variant="primary",
                        size="lg"
                    )
                    severity_badge = gr.HTML(label="Severity")

                # Right column — outputs
                with gr.Column(scale=1):
                    annot_image = gr.Image(
                        label="🎯 Detected Damage",
                        type="filepath",
                        height=300,
                        interactive=False
                    )
                    report_text = gr.Textbox(
                        label="📋 Complaint Report",
                        lines=18,
                        interactive=False,
                        elem_classes=["report-box"]
                    )
                    pdf_output = gr.File(
                        label="📄 Download PDF Report",
                        file_types=[".pdf"]
                    )

            analyze_btn.click(
                fn=analyze_image,
                inputs=[image_input, lat_input, lon_input],
                outputs=[annot_image, report_text, pdf_output, severity_badge],
                show_progress=True
            )

        # ════════════════════════════════════
        # TAB 2: Demo
        # ════════════════════════════════════
        with gr.Tab("🎬 Demo"):
            gr.Markdown("Select a pre-loaded demo image to see the system in action.")

            with gr.Row():
                demo_dropdown = gr.Dropdown(
                    choices=list(DEMO_PRESETS.keys()),
                    label="📂 Select Demo Image",
                    value=list(DEMO_PRESETS.keys())[0]
                )
                load_demo_btn  = gr.Button("Load Demo", variant="secondary")
                run_demo_btn   = gr.Button("▶️ Run Demo Analysis", variant="primary")

            with gr.Row():
                demo_lat = gr.Number(label="Latitude",  precision=6)
                demo_lon = gr.Number(label="Longitude", precision=6)

            with gr.Row():
                with gr.Column():
                    demo_image_input = gr.Image(
                        label="Demo Image",
                        type="filepath",
                        height=280,
                        interactive=False
                    )
                    demo_severity_badge = gr.HTML()

                with gr.Column():
                    demo_annot_img = gr.Image(
                        label="Detection Result",
                        type="filepath",
                        height=280,
                        interactive=False
                    )
                    demo_report = gr.Textbox(
                        label="Report",
                        lines=12,
                        interactive=False,
                        elem_classes=["report-box"]
                    )
                    demo_pdf = gr.File(label="Download PDF", file_types=[".pdf"])

            load_demo_btn.click(
                fn=load_demo,
                inputs=[demo_dropdown],
                outputs=[demo_image_input, demo_lat, demo_lon]
            )
            run_demo_btn.click(
                fn=analyze_image,
                inputs=[demo_image_input, demo_lat, demo_lon],
                outputs=[demo_annot_img, demo_report, demo_pdf, demo_severity_badge]
            )
            # Auto-load first demo on startup
            app.load(
                fn=load_demo,
                inputs=[demo_dropdown],
                outputs=[demo_image_input, demo_lat, demo_lon]
            )

        # ════════════════════════════════════
        # TAB 3: Complaint History
        # ════════════════════════════════════
        with gr.Tab("📊 Complaint History"):
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh", variant="secondary")

            stats_html = gr.HTML(get_stats_html())

            history_table = gr.DataFrame(
                value=get_complaint_history(),
                label="All Complaints",
                interactive=False,
                wrap=True
            )

            refresh_btn.click(
                fn=lambda: (get_stats_html(), get_complaint_history()),
                outputs=[stats_html, history_table]
            )

        # ════════════════════════════════════
        # TAB 4: About
        # ════════════════════════════════════
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
## Smart City Pothole Detection System

**Problem Statement PS-SC1** — Domain 7: Smart Cities & Infrastructure

### System Overview
This system enables citizens to report road damage by uploading a photo and optionally providing GPS coordinates. The AI pipeline automatically:

1. **Detects** damage type using YOLOv8 (Pothole, Alligator Crack, Longitudinal Crack, Transverse Crack)
2. **Assesses severity** (LOW / MEDIUM / HIGH) based on coverage area and damage class
3. **Geocodes** the location using OpenStreetMap Nominatim API
4. **Generates a description** using Claude Vision API
5. **Produces a PDF** complaint report with unique complaint ID
6. **Stores** the complaint in a SQLite database

### Tech Stack
- **Detection:** YOLOv8 (Ultralytics) trained on RDD2022 + Pothole dataset
- **VLM:** Claude Vision API (Anthropic) with rule-based fallback
- **Geocoding:** Nominatim / OpenStreetMap (free, no API key)
- **UI:** Gradio
- **PDF:** ReportLab
- **Database:** SQLite

### Team
- Member 1: YOLOv8 training & detection
- Member 2: Severity, geocoding, report, database
- Member 3: VLM description & PDF generation
- Member 4: Config, pipeline & Gradio UI
            """)

    gr.HTML("""
    <div style='text-align:center; color:#aaa; font-size:12px; margin-top:10px; padding-bottom:10px'>
        Smart City Municipal Corporation · Pothole Detection System v1.0 · GenAI Hackathon 2026
    </div>
    """)


# ══════════════════════════════════════════════════════════════
# LAUNCH
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Pothole Detection System")
    print("=" * 60)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,       # Creates public URL — useful for Colab / judges
        show_error=True,
    )
