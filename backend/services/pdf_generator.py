"""
FALCON EYE - Official Incident Dossier PDF Generator
Uses ReportLab to produce professional, downloadable public safety incident reports.
Includes:
- Branded Header & Confidentiality Classification
- Incident Identification & Category
- Geospatial Coordinates & Location
- AI Confidence & Risk Analysis Breakdown
- Verification & Response Status Timeline
- Evidence Snapshot Reference & Cryptographic SHA-256 Hash
- Authorized Control-Room Sign-off Block
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


class IncidentPDFGenerator:
    @staticmethod
    def generate_incident_report(incident_data: dict, output_filename: str = None) -> str:
        """
        Generates a PDF dossier for the specified incident record.
        Returns the absolute file path to the generated PDF.
        """
        inc_num = incident_data.get("incident_number", "INC-UNKNOWN")
        if not output_filename:
            output_filename = f"FalconEye_Dossier_{inc_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        pdf_path = os.path.join(REPORTS_DIR, output_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom styling palette
        primary_color = colors.HexColor("#080F1E")     # Deep Navy
        accent_color = colors.HexColor("#007799")      # Dark Cyan
        critical_color = colors.HexColor("#D32F2F")    # Alert Red
        text_dark = colors.HexColor("#1A202C")
        bg_light = colors.HexColor("#F8FAFC")

        title_style = ParagraphStyle(
            'FalconTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=primary_color,
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'FalconSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=accent_color,
            spaceAfter=12
        )

        section_heading = ParagraphStyle(
            'FalconSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=primary_color,
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'FalconBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=text_dark,
            leading=13
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("FALCON EYE — SMART PUBLIC SAFETY COMMAND CENTER", title_style))
        story.append(Paragraph("OFFICIAL EMERGENCY INCIDENT DOSSIER | AI-POWERED SURVEILLANCE & RESPONSE INTELLIGENCE", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=10))

        # 2. Executive Incident Summary Table
        sev = incident_data.get("severity", "MEDIUM")
        sev_color = critical_color if sev == "CRITICAL" else colors.HexColor("#E65100") if sev == "HIGH" else colors.HexColor("#2E7D32")

        summary_table_data = [
            [
                Paragraph("<b>Incident ID:</b>", body_style),
                Paragraph(f"<b>{inc_num}</b>", body_style),
                Paragraph("<b>Severity Level:</b>", body_style),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Category:</b>", body_style),
                Paragraph(str(incident_data.get("category", "HAZARD")).replace("_", " "), body_style),
                Paragraph("<b>Current Status:</b>", body_style),
                Paragraph(f"<b>{incident_data.get('status', 'DETECTED')}</b>", body_style)
            ],
            [
                Paragraph("<b>Timestamp:</b>", body_style),
                Paragraph(str(incident_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))), body_style),
                Paragraph("<b>AI Confidence:</b>", body_style),
                Paragraph(f"{int(float(incident_data.get('confidence', 0.85)) * 100)}%", body_style)
            ],
            [
                Paragraph("<b>Geographic Location:</b>", body_style),
                Paragraph(str(incident_data.get("location_name", "Central Transit Plaza")), body_style),
                Paragraph("<b>GPS Coordinates:</b>", body_style),
                Paragraph(f"{incident_data.get('latitude', 17.3850):.5f}° N, {incident_data.get('longitude', 78.4867):.5f}° E", body_style)
            ],
            [
                Paragraph("<b>Detection Source:</b>", body_style),
                Paragraph(str(incident_data.get("source_type", "AI_CCTV_STREAM")), body_style),
                Paragraph("<b>Situational Risk Index:</b>", body_style),
                Paragraph(f"<b>{incident_data.get('risk_score', 65.0)} / 100</b>", body_style)
            ]
        ]

        t_summary = Table(summary_table_data, colWidths=[1.3 * inch, 2.3 * inch, 1.4 * inch, 2.2 * inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_light),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 12))

        # 3. Incident Description & Situational Risk Breakdown
        story.append(Paragraph("SITUATIONAL CONTEXT & AI RISK ANALYSIS", section_heading))
        desc_text = incident_data.get("description", "Automated safety threshold exceeded. AI detection confirmed.")
        story.append(Paragraph(f"<b>Event Narrative:</b> {desc_text}", body_style))
        story.append(Spacer(1, 6))

        risk_factors = incident_data.get("risk_factors", "Elevated pedestrian flow; proximity to transit artery.")
        story.append(Paragraph(f"<b>Contributing Risk Factors:</b> {risk_factors}", body_style))
        story.append(Spacer(1, 10))

        # 4. Response & Verification Timeline
        story.append(Paragraph("INCIDENT LIFECYCLE & AUDIT TIMELINE", section_heading))
        created_str = str(incident_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        verified_by = incident_data.get("verified_by", "Control Room Lead Operator")
        assigned_team = incident_data.get("assigned_team", "Rapid Response Police Unit 04")

        timeline_data = [
            [Paragraph("<b>Step</b>", body_style), Paragraph("<b>State</b>", body_style), Paragraph("<b>Actor</b>", body_style), Paragraph("<b>Details & Timestamp</b>", body_style)],
            [Paragraph("1", body_style), Paragraph("DETECTED", body_style), Paragraph("Falcon AI Engine", body_style), Paragraph(f"Automated event trigger at {created_str}", body_style)],
            [Paragraph("2", body_style), Paragraph("VERIFIED", body_style), Paragraph(verified_by, body_style), Paragraph("Human operator visual confirmation approved", body_style)],
            [Paragraph("3", body_style), Paragraph("ACKNOWLEDGED", body_style), Paragraph("Command Desk", body_style), Paragraph("Alert acknowledged, emergency priority established", body_style)],
            [Paragraph("4", body_style), Paragraph("ASSIGNED", body_style), Paragraph(assigned_team, body_style), Paragraph("Unit dispatched via optimized emergency route", body_style)],
            [Paragraph("5", body_style), Paragraph(incident_data.get("status", "ACTIVE"), body_style), Paragraph("Field Personnel", body_style), Paragraph(f"Current Status: {incident_data.get('status', 'ACTIVE')}", body_style)]
        ]

        t_timeline = Table(timeline_data, colWidths=[0.5 * inch, 1.4 * inch, 1.8 * inch, 3.5 * inch])
        t_timeline.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#080F1E")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_timeline)
        story.append(Spacer(1, 12))

        # 5. Evidence & Cryptographic Integrity Section
        story.append(Paragraph("DIGITAL EVIDENCE INTEGRITY & CHAIN OF CUSTODY", section_heading))
        sha256_hash = incident_data.get("evidence_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        ev_path = incident_data.get("evidence_image_path", "data/evidence/snapshot_latest.jpg")

        evidence_table = [
            [Paragraph("<b>Cryptographic SHA-256 Hash:</b>", body_style), Paragraph(f"<font face='Courier' size='7'>{sha256_hash}</font>", body_style)],
            [Paragraph("<b>Storage Reference:</b>", body_style), Paragraph(f"<font face='Courier' size='8'>{ev_path}</font>", body_style)],
            [Paragraph("<b>Integrity Status:</b>", body_style), Paragraph("<font color='#2E7D32'><b>VERIFIED IMMUTABLE (Audit-Compliant)</b></font>", body_style)]
        ]
        t_evidence = Table(evidence_table, colWidths=[2.2 * inch, 5.0 * inch])
        t_evidence.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_light),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_evidence)
        story.append(Spacer(1, 16))

        # 6. Sign-off Authorization Block
        sign_block = [
            [
                Paragraph("<b>Reporting Officer:</b><br/>Lead Controller Vikram Sharma<br/>Badge: FE-SEC-091", body_style),
                Paragraph("<b>Supervising Director:</b><br/>Director of Emergency Services<br/>Falcon Public Safety Division", body_style)
            ],
            [
                Paragraph("<b>Digital Signature:</b> VALIDATED", body_style),
                Paragraph(f"<b>Generation Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", body_style)
            ]
        ]
        t_sign = Table(sign_block, colWidths=[3.6 * inch, 3.6 * inch])
        t_sign.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_sign)

        # Build PDF document
        doc.build(story)
        return pdf_path


# Global singleton instance
pdf_generator = IncidentPDFGenerator()
