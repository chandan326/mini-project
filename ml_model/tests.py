import io
from PIL import Image
from django.test import TestCase
from crops.models import Crop
from diseases.models import Disease
from ml_model.preprocessing import validate_and_preprocess_image
from ml_model.model_loader import get_predictor

class MLModelPipelineTest(TestCase):
    def setUp(self):
        self.crop = Crop.objects.create(name="Tomato")
        self.disease = Disease.objects.create(name="Early Blight", crop=self.crop)
        self.predictor = get_predictor()

    def generate_test_image(self, width=200, height=200, color='green'):
        file_obj = io.BytesIO()
        img = Image.new('RGB', (width, height), color=color)
        img.save(file_obj, 'JPEG')
        file_obj.seek(0)
        return file_obj

    def test_image_preprocessing_valid(self):
        img_file = self.generate_test_image()
        res = validate_and_preprocess_image(img_file)
        self.assertTrue(res['is_valid'])

    def test_demo_predictor_inference(self):
        img_file = self.generate_test_image()
        res = self.predictor.predict_single(img_file, self.crop)
        self.assertTrue(res['is_valid'])
        self.assertIn('probabilities', res)

    def test_ensemble_aggregation(self):
        img_file = self.generate_test_image()
        pred_res = self.predictor.predict_single(img_file, self.crop)
        answers = {
            'visible_symptoms': ['Yellowing'],
            'weather_condition': 'Humid'
        }
        agg = self.predictor.aggregate_predictions([pred_res], self.crop, answers)
        self.assertIn('confidence', agg)
        self.assertIn('confidence_pct', agg)
