from .models import KnowledgeSource

def get_disease_knowledge(disease):
    """Retrieve verified knowledge base records for a specific disease."""
    if not disease:
        return None
    try:
        return KnowledgeSource.objects.get(disease=disease)
    except KnowledgeSource.DoesNotExist:
        return None

def format_natural_explanation(crop_name, disease_name, answers, confidence_pct, is_low_confidence=False):
    """Generates simple, farmer-friendly explanation without exposing ML math."""
    if is_low_confidence:
        return (
            f"The image visual patterns and symptoms for your {crop_name} could not be matched with high certainty. "
            f"Symptoms like '{answers.get('visible_symptoms_text', 'observed issues')}' were noted, but clearer photo angles "
            f"or expert consultation are recommended for confirmation."
        )

    weather = answers.get('weather_condition', 'current weather')
    first_noticed = answers.get('first_noticed_text', 'recently')
    symptoms = answers.get('visible_symptoms_text', 'observed symptoms')

    explanation = (
        f"The visual leaf and plant patterns uploaded strongly resemble {disease_name} in {crop_name}. "
        f"Your inputs indicate symptoms ({symptoms}) were first noticed {first_noticed} under {weather} weather conditions, "
        f"which aligns with known field progression for this disease."
    )
    return explanation
