import random
from django.conf import settings
from .predictor import PlantDiseasePredictor
from diseases.models import Disease

class DemoPredictor(PlantDiseasePredictor):
    """
    Demo/College-Presentation Predictor implementation.
    Simulates ML inference based on crop context, image quality parameters, and questionnaire weights.
    """

    def __init__(self):
        self.load_model()

    def load_model(self):
        """Mock model initialization."""
        self.model_loaded = True

    def predict_single(self, image_file, crop):
        """Generates realistic disease probability distribution for a single image."""
        val_res = self.preprocess(image_file)
        if not val_res['is_valid']:
            return {
                'is_valid': False,
                'warning': val_res['warning'],
                'probabilities': {}
            }

        diseases = list(Disease.objects.filter(crop=crop, active=True))
        if not diseases:
            return {
                'is_valid': True,
                'warning': 'No registered diseases for this crop.',
                'probabilities': {}
            }

        # Base mock probabilities across crop's known diseases
        probs = {}
        total = 0.0
        for d in diseases:
            weight = random.uniform(0.1, 0.9)
            probs[d.id] = weight
            total += weight

        # Normalize
        for k in probs:
            probs[k] = round(probs[k] / total, 4)

        return {
            'is_valid': True,
            'warning': val_res.get('warning'),
            'probabilities': probs
        }

    def aggregate_predictions(self, image_results, crop, answers):
        """
        Ensemble aggregation across 1 to 5 images + farmer questionnaire symptom matching.
        """
        diseases = list(Disease.objects.filter(crop=crop, active=True))
        if not diseases:
            return {
                'predicted_disease': None,
                'confidence': 0.0,
                'is_low_confidence': True,
                'is_inconsistent': False,
                'top_matches': [],
                'explanation': 'No disease entries found for this crop in the system.'
            }

        valid_predictions = [res for res in image_results if res.get('is_valid')]
        if not valid_predictions:
            return {
                'predicted_disease': None,
                'confidence': 0.0,
                'is_low_confidence': True,
                'is_inconsistent': False,
                'top_matches': [],
                'explanation': 'No valid clear images were available for analysis.'
            }

        # 1. Image Ensemble Probability
        disease_scores = {d.id: 0.0 for d in diseases}
        for res in valid_predictions:
            probs = res.get('probabilities', {})
            for d_id, prob in probs.items():
                if d_id in disease_scores:
                    disease_scores[d_id] += prob

        num_valid = len(valid_predictions)
        for d_id in disease_scores:
            disease_scores[d_id] /= num_valid

        # 2. Symptom & Questionnaire Matching
        symptoms_reported = answers.get('visible_symptoms', [])
        weather = answers.get('weather_condition', '').lower()
        is_spreading = answers.get('is_spreading', '')

        # Apply heuristic weights based on reporting symptoms
        for d in diseases:
            d_symptom_codes = [s.code.lower() for s in d.symptoms.all()]
            match_count = sum(1 for sym in symptoms_reported if sym.lower() in d_symptom_codes or sym.lower() in d.name.lower())
            
            # Boost score if reported symptoms match disease symptoms
            boost = match_count * 0.20
            if 'humid' in weather or 'rainy' in weather:
                if 'blight' in d.name.lower() or 'spot' in d.name.lower() or 'rot' in d.name.lower():
                    boost += 0.10
            
            disease_scores[d.id] += boost

        # Re-normalize combined scores
        total_score = sum(disease_scores.values()) or 1.0
        sorted_diseases = sorted(
            [{'disease': d, 'score': round(disease_scores[d.id] / total_score, 4)} for d in diseases],
            key=lambda x: x['score'],
            reverse=True
        )

        top_match = sorted_diseases[0]
        top_disease = top_match['disease']
        raw_confidence = top_match['score']

        # Adjust final confidence bound between 45% and 94% for realistic AI representation
        confidence = min(max(raw_confidence, 0.45), 0.94)

        # 3. Check Consistency Across Images
        highest_prob_count = 0
        for res in valid_predictions:
            p_probs = res.get('probabilities', {})
            if p_probs:
                best_img_d_id = max(p_probs, key=p_probs.get)
                if best_img_d_id == top_disease.id:
                    highest_prob_count += 1

        agreement_ratio = highest_prob_count / float(num_valid)
        is_inconsistent = num_valid > 1 and agreement_ratio < getattr(settings, 'CONSISTENCY_THRESHOLD', 0.50)

        # 4. Check Low Confidence Threshold
        confidence_threshold = getattr(settings, 'CONFIDENCE_THRESHOLD', 0.60)
        is_low_confidence = (confidence < confidence_threshold) or is_inconsistent

        top_matches_list = [
            {
                'disease_id': item['disease'].id,
                'name': item['disease'].name,
                'name_hi': item['disease'].name_hi,
                'score_pct': int(item['score'] * 100)
            }
            for item in sorted_diseases[:3]
        ]

        return {
            'predicted_disease': top_disease if not is_low_confidence else sorted_diseases[0]['disease'],
            'confidence': round(confidence, 2),
            'confidence_pct': int(confidence * 100),
            'is_low_confidence': is_low_confidence,
            'is_inconsistent': is_inconsistent,
            'agreement_ratio': round(agreement_ratio, 2),
            'top_matches': top_matches_list,
            'valid_images_count': num_valid
        }
