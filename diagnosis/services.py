from django.conf import settings
from .models import Diagnosis, DiagnosisImage, DiagnosisAnswer
from ml_model.model_loader import get_predictor
from knowledge_base.services import get_disease_knowledge, format_natural_explanation

def create_diagnosis_session(crop, user=None):
    """Initializes a new diagnosis session."""
    diagnosis = Diagnosis.objects.create(
        crop=crop,
        user=user if user and user.is_authenticated else None,
        status='PROCESSING'
    )
    return diagnosis

def process_diagnosis_images(diagnosis, image_files):
    """
    Saves uploaded images (up to 5) and runs preprocessing quality checks.
    """
    predictor = get_predictor()
    saved_images = []

    for index, file_obj in enumerate(image_files[:getattr(settings, 'MAX_DIAGNOSIS_IMAGES', 5)], start=1):
        # Preprocess & inspect image
        val_res = predictor.preprocess(file_obj)
        
        diag_img = DiagnosisImage.objects.create(
            diagnosis=diagnosis,
            slot_number=index,
            image=file_obj,
            is_valid=val_res['is_valid'],
            quality_warning=val_res.get('warning')
        )
        saved_images.append(diag_img)
    return saved_images

def execute_diagnosis_pipeline(diagnosis, answers_data):
    """
    Executes full AI inference pipeline:
    1. Single image ML predictions.
    2. Ensemble aggregation.
    3. Questionnaire correlation.
    4. Verified Knowledge Base retrieval.
    5. Natural explanation generation.
    """
    predictor = get_predictor()
    diag_images = diagnosis.images.all()

    # Step 1: Run ML prediction per image
    image_results = []
    for diag_img in diag_images:
        if not diag_img.is_valid:
            image_results.append({'is_valid': False, 'warning': diag_img.quality_warning, 'probabilities': {}})
            continue

        res = predictor.predict_single(diag_img.image, diagnosis.crop)
        diag_img.prediction_prob = res.get('probabilities', {})
        if res.get('warning'):
            diag_img.quality_warning = res.get('warning')
        diag_img.save()
        image_results.append(res)

    # Save answers data
    vis_symptoms = answers_data.get('visible_symptoms', [])
    aff_parts = answers_data.get('affected_parts', [])

    DiagnosisAnswer.objects.update_or_create(
        diagnosis=diagnosis,
        defaults={
            'first_noticed': answers_data.get('first_noticed', 'Today'),
            'affected_parts': aff_parts,
            'visible_symptoms': vis_symptoms,
            'is_spreading': answers_data.get('is_spreading', 'Not sure'),
            'weather_condition': answers_data.get('weather_condition', 'Humid'),
            'treatment_applied': answers_data.get('treatment_applied', 'No'),
            'treatment_details': answers_data.get('treatment_details', ''),
        }
    )

    formatted_answers = {
        'first_noticed_text': answers_data.get('first_noticed', 'recently'),
        'visible_symptoms_text': ', '.join(vis_symptoms) if vis_symptoms else 'observed abnormalities',
        'weather_condition': answers_data.get('weather_condition', 'humid weather'),
    }

    # Step 2: Ensemble Aggregation
    agg_res = predictor.aggregate_predictions(image_results, diagnosis.crop, answers_data)

    predicted_disease = agg_res['predicted_disease']
    confidence = agg_res['confidence']
    is_low_confidence = agg_res['is_low_confidence']
    is_inconsistent = agg_res['is_inconsistent']

    # Step 3: Format Explanation
    explanation = format_natural_explanation(
        crop_name=diagnosis.crop.name,
        disease_name=predicted_disease.name if predicted_disease else 'Unknown Issue',
        answers=formatted_answers,
        confidence_pct=int(confidence * 100),
        is_low_confidence=is_low_confidence
    )

    # Step 4: Finalize Diagnosis Record
    diagnosis.predicted_disease = predicted_disease
    diagnosis.confidence_score = confidence
    diagnosis.is_low_confidence = is_low_confidence
    diagnosis.is_inconsistent = is_inconsistent
    diagnosis.explanation = explanation
    diagnosis.status = 'COMPLETED'
    diagnosis.save()

    return diagnosis
