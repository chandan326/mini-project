import os
from io import BytesIO
from knowledge_base.services import get_disease_knowledge

def generate_diagnosis_pdf(diagnosis):
    """
    Generates structured PDF diagnostic report using ReportLab.
    Returns BytesIO buffer.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor('#1E5631')
    SECONDARY = colors.HexColor('#4C9A2A')
    DARK_TEXT = colors.HexColor('#212529')
    BG_LIGHT = colors.HexColor('#F4F7F4')
    BORDER_COLOR = colors.HexColor('#D1E2D1')

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#555555')
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=DARK_TEXT
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#666666')
    )

    # 1. Header Table
    header_data = [
        [
            Paragraph("<b>AGRI-HEALTH AI</b><br/><font size=9 color='#4C9A2A'>Plant Disease Assessment Report</font>", title_style),
            Paragraph(f"<b>Report ID:</b> {str(diagnosis.id)[:8]}<br/><b>Date:</b> {diagnosis.created_at.strftime('%B %d, %Y')}<br/><b>Status:</b> {diagnosis.status}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=4, spaceAfter=12))

    # 2. Key Assessment Summary Box
    disease = diagnosis.predicted_disease
    disease_name = disease.name if (disease and not diagnosis.is_low_confidence) else "Uncertain / Low Confidence Diagnosis"
    crop_name = diagnosis.crop.name

    status_label = "High Confidence Identification"
    status_bg = colors.HexColor('#D4EDDA')
    status_fg = colors.HexColor('#155724')

    if diagnosis.is_low_confidence or diagnosis.is_inconsistent:
        status_label = "Uncertain Result - Expert Verification Recommended"
        status_bg = colors.HexColor('#FFF3CD')
        status_fg = colors.HexColor('#856404')

    summary_content = [
        [Paragraph("<b>Crop Analyzed:</b>", bold_body_style), Paragraph(crop_name, body_style)],
        [Paragraph("<b>Assessed Disease:</b>", bold_body_style), Paragraph(f"<b>{disease_name}</b>", body_style)],
        [Paragraph("<b>Confidence Score:</b>", bold_body_style), Paragraph(f"{diagnosis.confidence_pct}%", body_style)],
        [Paragraph("<b>Assessment Status:</b>", bold_body_style), Paragraph(f"<font color='{status_fg.hexval()}'><b>{status_label}</b></font>", body_style)],
    ]

    summary_table = Table(summary_content, colWidths=[140, 400])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5EFE5')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # 3. Assessment Explanation
    story.append(Paragraph("Why This Assessment Was Reached", section_heading))
    story.append(Paragraph(diagnosis.explanation, body_style))
    story.append(Spacer(1, 10))

    # 4. Uploaded Images Thumbnails
    story.append(Paragraph("Uploaded Plant Photos", section_heading))
    img_cells = []
    for diag_img in diagnosis.images.all()[:5]:
        if diag_img.image and os.path.exists(diag_img.image.path):
            try:
                rl_img = RLImage(diag_img.image.path, width=80, height=80)
                caption = f"Slot {diag_img.slot_number}"
                if not diag_img.is_valid:
                    caption += " (Blur)"
                img_cells.append(Table([[rl_img], [Paragraph(caption, subtitle_style)]], colWidths=[85]))
            except Exception:
                pass

    if img_cells:
        img_table = Table([img_cells], colWidths=[100] * len(img_cells))
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 12))

    # 5. Questionnaire Answers
    story.append(Paragraph("Farmer Symptom Report", section_heading))
    answers = getattr(diagnosis, 'answers', None)
    if answers:
        symptoms_str = ", ".join(answers.visible_symptoms) if answers.visible_symptoms else "None specified"
        parts_str = ", ".join(answers.affected_parts) if answers.affected_parts else "Leaves"
        ans_data = [
            [Paragraph("<b>First Noticed:</b>", bold_body_style), Paragraph(answers.first_noticed, body_style)],
            [Paragraph("<b>Affected Parts:</b>", bold_body_style), Paragraph(parts_str, body_style)],
            [Paragraph("<b>Reported Symptoms:</b>", bold_body_style), Paragraph(symptoms_str, body_style)],
            [Paragraph("<b>Weather Condition:</b>", bold_body_style), Paragraph(answers.weather_condition, body_style)],
        ]
        ans_table = Table(ans_data, colWidths=[140, 400])
        ans_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F0F0F0')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(ans_table)
        story.append(Spacer(1, 12))

    # 6. Knowledge Base Guidance (Immediate Management & Prevention)
    knowledge = get_disease_knowledge(disease) if disease else None
    if knowledge:
        story.append(Paragraph("Recommended Management Steps", section_heading))
        story.append(Paragraph(f"<b>Immediate Field Actions:</b> {knowledge.treatment_immediate}", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Cultural & Crop Care:</b> {knowledge.treatment_management}", body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Preventive Guidance", section_heading))
        story.append(Paragraph(knowledge.prevention_methods, body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Monitoring & Expert Referral", section_heading))
        story.append(Paragraph(knowledge.monitoring_guidance, body_style))
        story.append(Spacer(1, 12))

    # 7. Official Agricultural Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CCCCCC'), spaceBefore=8, spaceAfter=8))
    disclaimer_text = (
        "<b>Important Notice & Disclaimer:</b> This report provides AI-assisted agricultural information generated from image "
        "pattern recognition and farmer-provided input. It does not replace professional agricultural expert inspection or "
        "laboratory analysis. Always verify recommendations with your local agricultural extension service or expert before "
        "applying chemical treatments."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
