import logging
from django.http import HttpResponse, JsonResponse
from diagnosis.access import get_accessible_diagnosis
from .pdf_generator import generate_diagnosis_pdf

logger = logging.getLogger(__name__)


def download_report_pdf_view(request, pk):
    diagnosis = get_accessible_diagnosis(request, pk)
    if diagnosis.status != 'COMPLETED':
        return JsonResponse({'error': 'This assessment is not complete yet.'}, status=409)
    try:
        buffer = generate_diagnosis_pdf(diagnosis)
    except Exception:
        logger.exception('Report generation failed')
        return JsonResponse({'error': 'The report could not be generated. Please retry.'}, status=503)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="AgriHealth_Report_{str(diagnosis.id)[:8]}_{diagnosis.crop.slug}.pdf"'
    response['Cache-Control'] = 'private, no-store'
    return response
