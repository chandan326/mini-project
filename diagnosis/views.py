import logging
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework.exceptions import APIException
from crops.models import Crop
from diseases.models import Symptom
from .models import Feedback
from .access import get_accessible_diagnosis
from .serializers import DiagnosisSerializer, FeedbackInputSerializer
from .submission import submit_diagnosis
from knowledge_base.services import get_disease_knowledge
from ml_model.configuration import analysis_mode

logger = logging.getLogger(__name__)


def wizard_view(request):
    context = {
        'crops': Crop.objects.filter(is_active=True),
        'symptoms': Symptom.objects.all(),
        'analysis_available': analysis_mode() != 'unavailable',
        'request_timeout_ms': (settings.GEMINI_TIMEOUT_SECONDS + 90) * 1000,
    }
    if request.method == 'POST':
        ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            diagnosis = submit_diagnosis(request, request.POST, request.FILES)
        except APIException as exc:
            if ajax:
                return JsonResponse({'errors': exc.detail}, status=exc.status_code)
            context['submission_error'] = exc.detail
            return render(request, 'diagnosis/wizard.html', context, status=exc.status_code)
        except Exception:
            logger.exception('Assessment submission failed')
            message = 'We could not complete the assessment. Please retry in a moment.'
            if ajax:
                return JsonResponse({'error': message}, status=503)
            context['submission_error'] = message
            return render(request, 'diagnosis/wizard.html', context, status=503)
        if ajax:
            return JsonResponse(DiagnosisSerializer(diagnosis, context={'request': request}).data, status=201)
        return redirect('diagnosis_result', pk=diagnosis.id)
    return render(request, 'diagnosis/wizard.html', context)


def result_view(request, pk):
    try:
        diagnosis = get_accessible_diagnosis(request, pk)
    except Http404:
        # Keep ownership private while giving expired/missing reports a usable UI.
        return render(request, 'diagnosis/result_unavailable.html', status=404)
    # Demo and uncertain predictions must not present disease-specific care as a diagnosis.
    disease = diagnosis.predicted_disease if not diagnosis.is_demo and not diagnosis.is_low_confidence else None
    return render(request, 'diagnosis/result.html', {
        'diagnosis': diagnosis,
        'disease': disease,
        'knowledge': get_disease_knowledge(disease),
        'has_feedback': diagnosis.feedbacks.exists(),
    })


@require_POST
def feedback_view(request, pk):
    diagnosis = get_accessible_diagnosis(request, pk)
    serializer = FeedbackInputSerializer(data=request.POST)
    if not serializer.is_valid():
        return JsonResponse({'errors': serializer.errors}, status=400)
    Feedback.objects.update_or_create(diagnosis=diagnosis, defaults=serializer.validated_data)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
    messages.success(request, 'Thank you for your feedback!')
    return redirect('diagnosis_result', pk=diagnosis.id)


def image_view(request, pk, image_id):
    diagnosis = get_accessible_diagnosis(request, pk)
    image = get_object_or_404(diagnosis.images, pk=image_id)
    try:
        response = FileResponse(image.image.open('rb'), content_type='image/jpeg')
        response['Cache-Control'] = 'private, max-age=300'
        return response
    except Exception:
        logger.warning('Saved assessment image unavailable: diagnosis_id=%s image_id=%s', diagnosis.pk, image.pk)
        response = JsonResponse({'error': 'This saved photo could not be retrieved. Please retry.'}, status=503)
        response['Cache-Control'] = 'private, no-store'
        return response
