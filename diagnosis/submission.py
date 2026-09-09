import logging
from django.conf import settings
from django.db import transaction
from ml_model.gemini import AnalysisUnavailable
from .access import remember_diagnosis
from .serializers import DiagnosisInputSerializer
from .uploads import collect_images, prepare_images
from .services import create_diagnosis_session, process_diagnosis_images, execute_diagnosis_pipeline

logger = logging.getLogger(__name__)


def submit_diagnosis(request, data, files):
    serializer = DiagnosisInputSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    cleaned = dict(serializer.validated_data)
    crop = cleaned.pop('crop_id')
    images = prepare_images(collect_images(files))
    if not settings.DEMO_MODE and not settings.GEMINI_API_KEY:
        raise AnalysisUnavailable('Live image analysis has not been configured yet.')
    diagnosis = create_diagnosis_session(crop, request.user)
    saved_images = []
    try:
        saved_images = process_diagnosis_images(diagnosis, images)
        execute_diagnosis_pipeline(diagnosis, cleaned, saved_images)
    except Exception:
        # File storage does not participate in a SQL rollback.
        for item in diagnosis.images.all():
            try:
                item.image.delete(save=False)
            except Exception:
                logger.warning('Could not clean up a failed assessment image.')
        with transaction.atomic():
            diagnosis.images.all().delete()
            diagnosis.status = 'FAILED'
            diagnosis.explanation = 'Assessment could not be completed. Please retry.'
            diagnosis.save(update_fields=['status', 'explanation', 'updated_at'])
        raise
    remember_diagnosis(request, diagnosis)
    return diagnosis
