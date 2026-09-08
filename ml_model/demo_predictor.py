from .predictor import PlantDiseasePredictor


class DemoPredictor(PlantDiseasePredictor):
    """Exercises the workflow without pretending that an image model is installed."""
    def __init__(self):
        self.load_model()

    def load_model(self):
        self.model_loaded = False

    def predict_single(self, image_file, crop):
        validation = self.preprocess(image_file)
        return {'is_valid': validation['is_valid'], 'warning': validation.get('warning'), 'probabilities': {}}

    def aggregate_predictions(self, image_predictions, crop, answers):
        return {
            'predicted_disease': None, 'confidence': 0.0, 'confidence_pct': 0,
            'is_low_confidence': True, 'is_inconsistent': False, 'top_matches': [],
            'explanation': 'Demo assessment: Photos and questionnaire were processed successfully. '
                           'No live image-analysis model is enabled, so no disease or confidence score is predicted. '
                           'Use this result to review the workflow, not to decide plant treatment.'
        }
