from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from diagnosis.models import Diagnosis
from .pdf_generator import generate_diagnosis_pdf

def download_report_pdf_view(request, pk):
    """Generates and serves downloadable PDF report for a given diagnosis UUID."""
    diagnosis = get_object_or_404(Diagnosis, pk=pk)
    try:
        pdf_buffer = generate_diagnosis_pdf(diagnosis)
        filename = f"AgriHealth_Report_{str(diagnosis.id)[:8]}_{diagnosis.crop.slug}.pdf"
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        raise Http404(f"Error generating report: {e}")
