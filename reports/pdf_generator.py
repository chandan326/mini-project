from io import BytesIO
from xml.sax.saxutils import escape
from PIL import Image as PillowImage
from knowledge_base.services import get_disease_knowledge


def generate_diagnosis_pdf(diagnosis):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportBody', fontSize=10, leading=15, spaceAfter=8))
    styles['Title'].textColor = colors.HexColor('#1e5631')
    styles['Heading2'].textColor = colors.HexColor('#1e5631')
    def paragraph(text, style='ReportBody'):
        return Paragraph(escape(str(text or '')).replace('\n', '<br/>'), styles[style])
    story = [paragraph('AgriHealth AI', 'Title'), paragraph('Plant Health Assessment Report', 'Heading2'),
             paragraph(f'Report: {diagnosis.id}\nDate: {diagnosis.created_at:%d %B %Y}'),
             HRFlowable(width='100%', color=colors.HexColor('#1e5631')), Spacer(1, 12)]
    confirmed = not diagnosis.is_demo and not diagnosis.is_low_confidence and diagnosis.predicted_disease
    disease = diagnosis.predicted_disease if confirmed else None
    summary = [
        ['Crop', diagnosis.crop.name],
        ['Analysis', 'Demo workflow - no disease prediction' if diagnosis.is_demo else 'AI-assisted image assessment'],
        ['Assessed condition', disease.name if disease else 'Unconfirmed - expert assessment recommended'],
        ['Model confidence', 'Not applicable in demo mode' if diagnosis.is_demo else f'{diagnosis.confidence_pct}% (not measured accuracy)'],
    ]
    table = Table([[paragraph(label), paragraph(value)] for label, value in summary], colWidths=[125, doc.width - 125])
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f7f2')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 10)]))
    story.extend([table, Spacer(1,12), paragraph('Assessment notes', 'Heading2'), paragraph(diagnosis.explanation)])
    story.append(paragraph('Submitted photos', 'Heading2'))
    cells = []
    missing = 0
    for item in diagnosis.images.all():
        try:
            # Storage.open works for both Cloudinary and disk; .path does not.
            with item.image.open('rb') as stored:
                with PillowImage.open(stored) as photo:
                    photo.thumbnail((220, 180))
                    normalized = BytesIO()
                    photo.convert('RGB').save(normalized, 'JPEG', quality=85)
                    width, height = photo.size
            normalized.seek(0)
            scale = min(86 / width, 75 / height)
            thumbnail = Image(normalized, width=width*scale, height=height*scale)
            cells.append([thumbnail, paragraph(f'Photo {item.slot_number}')])
        except (OSError, ValueError, NotImplementedError):
            missing += 1
        except Exception:
            # A temporarily unavailable media provider must not break the text report.
            missing += 1
    if cells:
        thumbs = Table([cells], colWidths=[doc.width / 5] * len(cells))
        thumbs.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        story.append(thumbs)
    if missing:
        story.append(paragraph(f'{missing} photo thumbnail(s) could not be loaded. Your text assessment is included.'))
    answers = getattr(diagnosis, 'answers', None)
    if answers:
        story.extend([paragraph('Reported conditions', 'Heading2'), paragraph(
            f'First noticed: {answers.first_noticed}\nAffected parts: {", ".join(answers.affected_parts)}\n'
            f'Symptoms: {", ".join(answers.visible_symptoms)}\nWeather: {answers.weather_condition}\n'
            f'Spreading: {answers.is_spreading}\nTreatment applied: {answers.treatment_applied}\n'
            f'Treatment details: {answers.treatment_details}')])
    knowledge = get_disease_knowledge(disease)
    if knowledge:
        for title, text in [('Immediate field care', knowledge.treatment_immediate), ('Crop management', knowledge.treatment_management), ('Prevention', knowledge.prevention_methods), ('Monitoring', knowledge.monitoring_guidance)]:
            story.extend([paragraph(title, 'Heading2'), paragraph(text)])
    else:
        story.extend([paragraph('Next steps', 'Heading2'), paragraph('Monitor changes, take clear plant photos in natural light, and contact a local agricultural extension expert if symptoms spread or the plant deteriorates. A demo or uncertain result cannot identify a disease.')])
    story.extend([Spacer(1, 12), HRFlowable(width='100%', color=colors.lightgrey), paragraph('AI-assisted information is not a confirmed plant diagnosis. Verify findings with an agricultural expert before choosing treatment.')])
    def footer(canvas, document):
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0] - 36, 20, f'AgriHealth AI | Page {document.page}')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    return buffer
