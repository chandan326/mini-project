import io
from unittest.mock import patch

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from crops.catalog import INDIA_MAJOR_CROPS
from crops.models import Crop
from diseases.models import Disease
from knowledge_base.models import KnowledgeSource
from diagnosis.models import DiagnosisImage
from diagnosis.tests import plant_image, gemini_response


@override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only', STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class ResultRegressionTests(TestCase):
    def setUp(self):
        cache.clear()
        self.crop = Crop.objects.create(name='Tomato')

    def submit(self, crop=None, count=1, **output):
        result = {'confidence': .85, 'contains_plant': True, 'inconsistent': False,
                  'explanation': 'Photo-specific evidence requires field confirmation.', **output}
        with patch('ml_model.gemini.requests.post', return_value=gemini_response(result)):
            return self.client.post('/api/diagnosis/create/', {
                'crop_id': (crop or self.crop).pk,
                'images': [plant_image(f'photo-{i}.jpg', color=(30+i*20, 120, 35)) for i in range(count)],
            })

    def test_all_30_crops_render_reports_and_every_uploaded_photo(self):
        for index, crop_data in enumerate(INDIA_MAJOR_CROPS):
            # Each crop is an independent user scenario, not a burst-rate test.
            cache.clear()
            crop, _ = Crop.objects.get_or_create(name=crop_data['name'])
            count = index % 5 + 1
            with self.subTest(crop=crop.name, photos=count):
                response = self.submit(crop=crop, count=count, condition_name='Possible environmental stress', category='environmental')
                self.assertEqual(response.status_code, 201, response.content)
                data = response.json()
                self.assertEqual(len(data['images']), count)
                page = self.client.get(data['result_url'])
                self.assertContains(page, 'Possible environmental stress')
                self.assertContains(page, 'data-result-photo', count=count)
                for photo in data['images']:
                    fetched = self.client.get(photo['image'])
                    self.assertEqual(fetched.status_code, 200)
                    with Image.open(io.BytesIO(b''.join(fetched.streaming_content))) as saved:
                        self.assertEqual(saved.size, (400, 300))
                pdf = self.client.get(f"/api/reports/{data['id']}/")
                self.assertEqual(pdf.status_code, 200)
                self.assertTrue(pdf.content.startswith(b'%PDF-'))

    def test_live_findings_override_catalog_boilerplate_in_html_and_pdf(self):
        disease = Disease.objects.create(crop=self.crop, name='Catalog blight')
        KnowledgeSource.objects.create(disease=disease, title='Test guide',
            symptoms_summary='CATALOG_ONLY_SYMPTOMS', treatment_immediate='CATALOG_ONLY_CARE')
        data = self.submit(catalog_disease_id=disease.pk, condition_name='Possible early blight',
                           observed_signs=['PHOTO_SPECIFIC_SIGN'], immediate_steps=['PHOTO_SPECIFIC_CARE']).json()
        page = self.client.get(data['result_url'])
        for value in ['Possible early blight', 'PHOTO_SPECIFIC_SIGN', 'PHOTO_SPECIFIC_CARE']:
            self.assertContains(page, value)
        for value in ['CATALOG_ONLY_SYMPTOMS', 'CATALOG_ONLY_CARE', 'Brown spots with concentric rings']:
            self.assertNotContains(page, value)
        from pypdf import PdfReader
        pdf = self.client.get(f"/api/reports/{data['id']}/")
        text = '\n'.join(page.extract_text() for page in PdfReader(io.BytesIO(pdf.content)).pages)
        self.assertIn('PHOTO_SPECIFIC_CARE', text)
        self.assertIn('PHOTO_SPECIFIC_SIGN', text)
        self.assertNotIn('CATALOG_ONLY_CARE', text)

    def test_category_labels_and_conflicting_catalog_match(self):
        disease = Disease.objects.create(crop=self.crop, name='Unrelated catalog disease')
        labels = {'healthy': 'No obvious disease visible', 'pest': 'Possible pest damage',
                  'nutrient': 'Possible nutrient issue', 'environmental': 'Possible environmental stress',
                  'unknown': 'Unable to determine with certainty'}
        for category, label in labels.items():
            with self.subTest(category=category):
                data = self.submit(catalog_disease_id=disease.pk, category=category, condition_name=label).json()
                self.assertIsNone(data['predicted_disease'])
                page = self.client.get(data['result_url'])
                self.assertContains(page, label)
                self.assertNotContains(page, disease.name)
                if category == 'unknown':
                    self.assertNotContains(page, 'is below our reliable threshold')

    def test_missing_storage_file_keeps_text_pdf_and_exposes_retry(self):
        data = self.submit(count=5).json()
        image = DiagnosisImage.objects.filter(diagnosis_id=data['id']).first()
        image.image.storage.delete(image.image.name)
        failed = self.client.get(data['images'][0]['image'])
        self.assertEqual(failed.status_code, 503)
        self.assertEqual(failed['Cache-Control'], 'private, no-store')
        self.assertContains(self.client.get(data['result_url']), 'data-retry-photo', count=5)
        self.assertEqual(self.client.get(f"/api/reports/{data['id']}/").status_code, 200)
        for photo in data['images'][1:]:
            fetched = self.client.get(photo['image'])
            self.assertEqual(fetched.status_code, 200)
            fetched.close()

    def test_unavailable_report_has_private_recovery_page(self):
        import uuid
        page = self.client.get(f'/diagnosis/result/{uuid.uuid4()}/')
        self.assertContains(page, 'This report is unavailable in this session', status_code=404)
        self.assertContains(page, 'Start a new assessment', status_code=404)

    def test_png_and_webp_are_normalized_and_included_in_provider_request(self):
        images = []
        for kind in ['PNG', 'WEBP', 'JPEG']:
            buffer = io.BytesIO()
            Image.new('RGB', (400, 300), 'green').save(buffer, kind)
            images.append(SimpleUploadedFile('photo.' + kind.lower(), buffer.getvalue(), 'image/' + kind.lower()))
        with patch('ml_model.gemini.requests.post', return_value=gemini_response({
            'confidence': .8, 'contains_plant': True, 'inconsistent': False, 'explanation': 'Visible leaves.'
        })) as provider:
            response = self.client.post('/api/diagnosis/create/', {'crop_id': self.crop.pk, 'images': images})
        self.assertEqual(response.status_code, 201)
        inputs = provider.call_args.kwargs['json']['contents'][0]['parts'][1:]
        self.assertEqual(len(inputs), 3)
        self.assertTrue(all(part['inlineData']['mimeType'] == 'image/jpeg' for part in inputs))
