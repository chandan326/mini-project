import io
from PIL import Image
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from crops.models import Crop
from diseases.models import Disease
from diagnosis.models import Diagnosis, Feedback

class DiagnosisFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.crop = Crop.objects.create(name="Tomato", slug="tomato")
        self.disease = Disease.objects.create(name="Early Blight", crop=self.crop)

    def create_dummy_image(self):
        file_obj = io.BytesIO()
        img = Image.new('RGB', (200, 200), color='green')
        img.save(file_obj, 'JPEG')
        file_obj.seek(0)
        return SimpleUploadedFile("test_plant.jpg", file_obj.read(), content_type="image/jpeg")

    def test_diagnosis_wizard_submission(self):
        img = self.create_dummy_image()
        response = self.client.post('/diagnosis/', {
            'crop_id': self.crop.id,
            'image_1': img,
            'first_noticed': '2-3 days ago',
            'affected_parts': ['Leaves'],
            'visible_symptoms': ['Yellowing'],
            'weather_condition': 'Humid'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Diagnosis.objects.exists())
        diag = Diagnosis.objects.first()
        self.assertEqual(diag.crop, self.crop)
        self.assertEqual(diag.status, 'COMPLETED')

    def test_feedback_submission(self):
        diag = Diagnosis.objects.create(crop=self.crop, status='COMPLETED')
        response = self.client.post(f'/diagnosis/feedback/{diag.id}/', {
            'is_helpful': 'true',
            'reason': '',
            'comments': 'Great report!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.filter(diagnosis=diag).count(), 1)
