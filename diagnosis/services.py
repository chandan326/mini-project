from django.conf import settings
from .models import Diagnosis, DiagnosisImage, DiagnosisAnswer
from ml_model.model_loader import get_predictor
from ml_model.gemini import analyze_images


def create_diagnosis_session(crop, user=None):
    return Diagnosis.objects.create(
        crop=crop, user=user if user and user.is_authenticated else None,
        status='PROCESSING', image_retention_status='STORED_WITH_USER_PERMISSION',
    )


def process_diagnosis_images(diagnosis, image_files):
    predictor = get_predictor()
    saved = []
    for index, file_obj in enumerate(image_files, 1):
        validation = predictor.preprocess(file_obj)
        file_obj.seek(0)
        item = DiagnosisImage(diagnosis=diagnosis, slot_number=index,
                              is_valid=validation['is_valid'], quality_warning=validation.get('warning'))
        try:
            item.image.save(file_obj.name, file_obj, save=False)
            item.save()
        except Exception:
            if item.image.name:
                try:
                    item.image.delete(save=False)
                except Exception:
                    pass
            raise
        # Reuse normalized upload bytes instead of downloading every image again.
        file_obj.seek(0)
        item._source_file = file_obj
        saved.append(item)
    return saved


def execute_diagnosis_pipeline(diagnosis, answers_data, saved_images=None):
    items = saved_images if saved_images is not None else list(diagnosis.images.all())
    inputs = [getattr(item, '_source_file', item.image) for item in items]
    if settings.DEMO_MODE:
        result = get_predictor().aggregate_predictions([], diagnosis.crop, answers_data)
    else:
        result = analyze_images(inputs, diagnosis.crop, answers_data)
    DiagnosisAnswer.objects.update_or_create(diagnosis=diagnosis, defaults=answers_data)
    diagnosis.predicted_disease = result['predicted_disease']
    diagnosis.confidence_score = result['confidence']
    diagnosis.is_low_confidence = result['is_low_confidence']
    diagnosis.is_inconsistent = result['is_inconsistent']
    diagnosis.explanation = result['explanation']
    diagnosis.status = 'COMPLETED'
    diagnosis.save()
    return diagnosis
