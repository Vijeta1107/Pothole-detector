import os
from datetime import datetime
from config import REPORTS_DIR, PDF_ORG_NAME, PDF_SYSTEM_NAME


def create_pdf(report_dict: dict) -> str:
    """
    Generate a professional PDF complaint report.

    Args:
        report_dict: complete report dict from report.generate_report()

    Returns:
        Path to the generated PDF file
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, Image, HRFlowable)
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    except ImportError:
        print("❌ ReportLab not installed. Run: pip install reportlab")
        return ""

    # ── File path ──
    complaint_id = report_dict.get("complaint_id", "UNKNOWN")
    pdf_filename = f"{complaint_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

    # ── Colors ──
    DARK_BLUE    = colors.HexColor("#1a3a5c")
    MED_BLUE     = colors.HexColor("#2d6a9f")
    LIGHT_BLUE   = colors.HexColor("#e8f4fd")
    SEV_HIGH     = colors.HexColor("#dc3545")
    SEV_MEDIUM   = colors.HexColor("#fd7e14")
    SEV_LOW      = colors.HexColor("#28a745")
    GREY_LINE    = colors.HexColor("#dee2e6")
    LIGHT_GREY   = colors.HexColor("#f8f9fa")
    WHITE        = colors.white
    BLACK        = colors.black

    severity_colors = {"HIGH": SEV_HIGH, "MEDIUM": SEV_MEDIUM, "LOW": SEV_LOW}
    sev_color = severity_colors.get(report_dict.get("severity", "LOW"), SEV_LOW)

    # ── Document ──
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Helper styles ──
    def style(name, **kwargs):
        return ParagraphStyle(name, parent=styles["Normal"], **kwargs)

    title_style     = style("title",  fontSize=18, textColor=WHITE,   fontName="Helvetica-Bold",  alignment=TA_CENTER, spaceAfter=4)
    subtitle_style  = style("sub",    fontSize=10, textColor=WHITE,   fontName="Helvetica",        alignment=TA_CENTER)
    section_style   = style("sec",    fontSize=11, textColor=WHITE,   fontName="Helvetica-Bold",   alignment=TA_LEFT,  leftIndent=6)
    label_style     = style("lbl",    fontSize=9,  textColor=colors.HexColor("#6c757d"), fontName="Helvetica-Bold")
    value_style     = style("val",    fontSize=10, textColor=BLACK,   fontName="Helvetica")
    desc_style      = style("desc",   fontSize=10, textColor=BLACK,   fontName="Helvetica",        leading=14, spaceAfter=6)
    footer_style    = style("footer", fontSize=7,  textColor=colors.grey, alignment=TA_CENTER)
    id_style        = style("cid",    fontSize=12, textColor=MED_BLUE, fontName="Helvetica-Bold",  alignment=TA_RIGHT)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HEADER BLOCK
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    header_data = [[
        Paragraph(f"{PDF_ORG_NAME}", title_style),
    ]]
    header_table = Table(header_data, colWidths=[18*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*cm))

    # Sub-header row: system name + complaint ID
    sub_data = [[
        Paragraph(f"🛣️ {PDF_SYSTEM_NAME}", subtitle_style),
        Paragraph(f"ID: {complaint_id}", id_style),
    ]]
    sub_table = Table(sub_data, colWidths=[12*cm, 6*cm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 0.4*cm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SEVERITY BANNER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sev = report_dict.get("severity", "LOW")
    pri = report_dict.get("priority", 3)
    pri_label = {1: "URGENT", 2: "MODERATE", 3: "ROUTINE"}.get(pri, "ROUTINE")

    sev_banner_data = [[
        Paragraph(f"SEVERITY: {sev}", ParagraphStyle("sb", fontSize=14,
                  textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph(f"PRIORITY: {pri_label}", ParagraphStyle("pb", fontSize=14,
                  textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]]
    sev_table = Table(sev_banner_data, colWidths=[9*cm, 9*cm])
    sev_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), sev_color),
        ("BACKGROUND", (1,0), (1,0), DARK_BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(sev_table)
    story.append(Spacer(1, 0.4*cm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TWO-COLUMN LAYOUT: Image + Damage Info
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    img_col = []
    annot_img = report_dict.get("annotated_image_path", "")
    orig_img  = report_dict.get("original_image_path", "")
    img_to_show = annot_img if (annot_img and os.path.exists(annot_img)) else orig_img

    if img_to_show and os.path.exists(img_to_show):
        try:
            from PIL import Image as PILImage
            pil_img = PILImage.open(img_to_show)
            img_w, img_h = pil_img.size
            aspect = img_h / img_w
            display_w = 8.5 * cm
            display_h = min(display_w * aspect, 7 * cm)
            rl_img = Image(img_to_show, width=display_w, height=display_h)
            img_col.append(rl_img)
            img_col.append(Spacer(1, 0.2*cm))
            img_col.append(Paragraph("Road image with damage detection overlay",
                                     style("cap", fontSize=7, textColor=colors.grey, alignment=TA_CENTER)))
        except Exception as e:
            img_col.append(Paragraph(f"[Image could not be loaded]", label_style))
    else:
        img_col.append(Paragraph("[No image available]", label_style))

    # Damage details column
    details = [
        ("Damage Type",   report_dict.get("damage_type", "Unknown")),
        ("Confidence",    f"{report_dict.get('confidence', 0):.1f}%"),
        ("Coverage",      f"{report_dict.get('damage_coverage_pct', 0):.1f}% of road surface"),
        ("Detections",    f"{report_dict.get('num_detections', 0)} instance(s)"),
        ("Timestamp",     report_dict.get("timestamp", "")),
    ]
    detail_rows = []
    for lbl, val in details:
        detail_rows.append([
            Paragraph(lbl, label_style),
            Paragraph(str(val), value_style),
        ])

    detail_table = Table(detail_rows, colWidths=[3.5*cm, 5*cm])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [WHITE, LIGHT_GREY]),
        ("GRID", (0,0), (-1,-1), 0.5, GREY_LINE),
    ]))

    # Place image and details side by side
    two_col = Table([[img_col, detail_table]], colWidths=[9*cm, 9*cm])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 0.4*cm))

    def section_header(text):
        t = Table([[Paragraph(text, section_style)]], colWidths=[18*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), MED_BLUE),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        return t

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LOCATION SECTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(section_header("📍 LOCATION INFORMATION"))
    story.append(Spacer(1, 0.2*cm))

    loc_rows = [
        ("Address",     report_dict.get("full_address", "Not provided")),
        ("City",        report_dict.get("city", "Not provided")),
        ("Area",        report_dict.get("area", "Not provided")),
        ("Road",        report_dict.get("road", "Not provided")),
        ("GPS",         report_dict.get("gps_string", "Not provided")),
    ]
    loc_table_data = [[Paragraph(l, label_style), Paragraph(str(v), value_style)] for l, v in loc_rows]
    loc_table = Table(loc_table_data, colWidths=[4*cm, 14*cm])
    loc_table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [WHITE, LIGHT_GREY]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("GRID", (0,0), (-1,-1), 0.5, GREY_LINE),
    ]))
    story.append(loc_table)
    story.append(Spacer(1, 0.4*cm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AI DESCRIPTION SECTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(section_header("🤖 AI DAMAGE ASSESSMENT"))
    story.append(Spacer(1, 0.2*cm))
    desc_box_data = [[Paragraph(report_dict.get("vlm_description", "No description available."), desc_style)]]
    desc_box = Table(desc_box_data, colWidths=[18*cm])
    desc_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("BOX", (0,0), (-1,-1), 1, GREY_LINE),
    ]))
    story.append(desc_box)
    story.append(Spacer(1, 0.4*cm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RECOMMENDED ACTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(section_header("🔧 RECOMMENDED ACTION"))
    story.append(Spacer(1, 0.2*cm))
    action_style = ParagraphStyle("act", fontSize=11, fontName="Helvetica-Bold",
                                   textColor=sev_color, leftIndent=10, spaceBefore=4, spaceAfter=4)
    story.append(Paragraph(report_dict.get("recommended_action", ""), action_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"Reason: {report_dict.get('severity_reason', '')}", desc_style))
    story.append(Spacer(1, 0.4*cm))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FOOTER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY_LINE))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Generated by {PDF_SYSTEM_NAME} | {report_dict.get('timestamp', '')} | "
        f"This report was auto-generated using AI-based road damage detection.",
        footer_style
    ))

    # ── Build PDF ──
    doc.build(story)
    print(f"✅ PDF generated: {pdf_path}")
    return pdf_path


# ──────────────────────────────────────────
# QUICK TEST — run: python pdf_generator.py
# ──────────────────────────────────────────
if __name__ == "__main__":
    mock_report = {
        "complaint_id": "CMP-20260530-TEST",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "damage_type": "Pothole", "confidence": 87.0,
        "damage_coverage_pct": 12.4, "num_detections": 2,
        "severity": "HIGH", "priority": 1,
        "recommended_action": "Immediate pothole patching required. High risk to vehicles.",
        "severity_reason": "Pothole class + 12.4% coverage + multiple detections = HIGH",
        "city": "Hubballi", "area": "Deshpande Nagar", "road": "PB Road",
        "full_address": "PB Road, Deshpande Nagar, Hubballi, Karnataka - 580020",
        "latitude": 15.3647, "longitude": 75.1240, "gps_string": "15.3647°N, 75.1240°E",
        "maps_url": "https://www.google.com/maps?q=15.3647,75.1240",
        "vlm_description": (
            "A severe pothole with ragged edges has been identified on the road surface, "
            "posing immediate risk to vehicle tyres and suspension systems. "
            "The damaged area requires urgent municipal repair to prevent accidents and further deterioration."
        ),
        "original_image_path": "",
        "annotated_image_path": "",
        "status": "SUBMITTED",
    }

    print("Generating test PDF...")
    pdf_path = create_pdf(mock_report)
    if pdf_path:
        print(f"✅ PDF created at: {pdf_path}")
    else:
        print("❌ PDF generation failed — check ReportLab installation")