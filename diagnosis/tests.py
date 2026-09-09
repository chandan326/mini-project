import io
import json
import tempfile
from unittest.mock import patch, Mock
from PIL import Image
from django.test import TestCase, Client, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import InMemoryStorage
from django.contrib.auth.models import User
from crops.models import Crop
from diseases.models import Disease
from diagnosis.models import Diagnosis, Feedback, DiagnosisImage


def plant_image(name='plant.jpg', size=(400, 300), color='green'):
    buffer = io.BytesIO()
    Image.new('RGB', size, color=color).save(buffer, 'JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


def gemini_response(output, finish='STOP'):
    provider = Mock(status_code=200)
    provider.json.return_value = {'candidates': [{'finishReason': finish, 'content': {'parts': [{'text': json.dumps(output)}]}}]}
    return provider


@override_settings(DEMO_MODE=True, STORAGES={'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class DiagnosisFlowTest(TestCase):
    def setUp(self):
        cache.clear()
        self.crop = Crop.objects.create(name='Tomato', slug='tomato')
        self.disease = Disease.objects.create(name='Early Blight', crop=self.crop)

    def submit(self, count=1, **fields):
        return self.client.post('/api/diagnosis/create/', {'crop_id': self.crop.id, 'images': [plant_image(f'plant-{i}.jpg') for i in range(count)], **fields})

    def test_five_repeated_field_uploads_and_report(self):
        response = self.submit(5)
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(len(data['images']), 5)
        self.assertEqual(data['analysis_method'], 'demo')
        self.assertIsNone(data['predicted_disease'])
        self.assertEqual(data['confidence_score'], 0)
        self.assertEqual(self.client.get(data['result_url']).status_code, 200)
        self.assertEqual(self.client.get(f"/api/diagnosis/{data['id']}/").status_code, 200)
        photo = self.client.get(data['images'][0]['image'])
        self.assertEqual(photo.status_code, 200)
        self.assertGreater(len(b''.join(photo.streaming_content)), 100)
        report = self.client.get(f"/api/reports/{data['id']}/")
        self.assertEqual(report.status_code, 200, report.content[:200])
        self.assertTrue(report.content.startswith(b'%PDF-'))

    def test_api_rejects_zero_images_without_creating_record(self):
        self.assertEqual(self.submit(0).status_code, 400)
        self.assertFalse(Diagnosis.objects.exists())

    def test_api_rejects_six_images_without_truncating(self):
        self.assertEqual(self.submit(6).status_code, 400)
        self.assertFalse(Diagnosis.objects.exists())

    def test_corrupt_file_is_rejected_before_storage(self):
        response = self.submit(images=[SimpleUploadedFile('fake.jpg', b'not an image', 'image/jpeg')])
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Diagnosis.objects.exists())
        self.assertFalse(DiagnosisImage.objects.exists())

    def test_svg_is_rejected(self):
        response = self.submit(images=[SimpleUploadedFile('photo.svg', b'<svg/>', 'image/svg+xml')])
        self.assertEqual(response.status_code, 400)

    def test_small_image_is_rejected(self):
        self.assertEqual(self.submit(images=[plant_image(size=(100,100))]).status_code, 400)

    def test_large_combined_payload_is_rejected(self):
        with override_settings(MAX_UPLOAD_BYTES=100):
            self.assertEqual(self.submit().status_code, 400)

    def test_invalid_crop_ids_and_inactive_crop(self):
        for value in ['garbage', -1, '9999999999999999999999999']:
            self.assertEqual(self.submit(crop_id=value).status_code, 400)
        self.crop.is_active = False
        self.crop.save()
        self.assertEqual(self.submit().status_code, 400)

    def test_questionnaire_validation(self):
        for fields in [{'weather_condition': 'made up'}, {'is_spreading': 'maybe'}, {'treatment_details': 'x'*1001}, {'affected_parts': ['invalid']}]:
            self.assertEqual(self.submit(**fields).status_code, 400)

    def test_valid_questionnaire_is_saved(self):
        response = self.submit(affected_parts=['Leaves', 'Stem'], visible_symptoms=['yellowing', 'brown_spots'], treatment_applied='Yes', treatment_details='No chemical treatment')
        self.assertEqual(response.status_code, 201)
        answers = Diagnosis.objects.get().answers
        self.assertEqual(answers.visible_symptoms, ['yellowing', 'brown_spots'])
        self.assertEqual(answers.affected_parts, ['Leaves', 'Stem'])

    def test_html_form_and_ajax_share_validation(self):
        response = self.client.post('/diagnosis/', {'crop_id': self.crop.id, 'image_1': plant_image()}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Diagnosis.objects.get().status, 'COMPLETED')
        response = self.client.post('/diagnosis/', {'crop_id': self.crop.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_guest_result_images_pdf_and_feedback_are_private(self):
        data = self.submit().json()
        other = Client()
        for url in [data['result_url'], f"/api/diagnosis/{data['id']}/", f"/api/reports/{data['id']}/", data['images'][0]['image']]:
            self.assertEqual(other.get(url).status_code, 404)
        self.assertEqual(other.post('/api/diagnosis/feedback/', {'diagnosis': data['id'], 'is_helpful': True}).status_code, 404)

    def test_account_results_are_private(self):
        owner = User.objects.create_user('owner')
        other = User.objects.create_user('other')
        self.client.force_login(owner)
        data = self.submit().json()
        self.client.force_login(other)
        self.assertEqual(self.client.get(data['result_url']).status_code, 404)
        self.client.force_login(owner)
        self.assertEqual(self.client.get(data['result_url']).status_code, 200)

    def test_feedback_boolean_and_retry_update(self):
        data = self.submit().json()
        url = f"/diagnosis/feedback/{data['id']}/"
        self.assertEqual(self.client.post(url, {'is_helpful': 'true'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code, 200)
        self.assertTrue(Feedback.objects.get().is_helpful)
        self.client.post(url, {'is_helpful': 'false', 'comments': 'Please improve'})
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertFalse(Feedback.objects.get().is_helpful)
        self.assertEqual(self.client.post(url, {'comments': 'missing choice'}).status_code, 400)

    def test_feedback_api_and_validation(self):
        data = self.submit().json()
        payload = {'diagnosis': data['id'], 'is_helpful': True}
        self.assertEqual(self.client.post('/api/diagnosis/feedback/', payload).status_code, 201)
        self.assertEqual(self.client.post('/api/diagnosis/feedback/', payload).status_code, 200)
        self.assertEqual(self.client.post('/api/diagnosis/feedback/', {**payload, 'comments': 'x'*2001}).status_code, 400)
        self.assertEqual(self.client.post('/api/diagnosis/feedback/', {**payload, 'diagnosis': 'bad'}).status_code, 400)

    def test_anonymous_api_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/diagnosis/create/', {'crop_id': self.crop.id, 'images': [plant_image()]}).status_code, 403)
        client.get('/diagnosis/')
        csrf = client.cookies['csrftoken'].value
        response = client.post('/api/diagnosis/create/', {'crop_id': self.crop.id, 'images': [plant_image()]}, HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 201, response.content)

    def test_provider_failure_is_not_fake_success(self):
        with override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only'):
            with patch('ml_model.gemini.requests.post', side_effect=__import__('requests').Timeout):
                response = self.submit()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(Diagnosis.objects.get().status, 'FAILED')
        self.assertEqual(DiagnosisImage.objects.count(), 0)

    def test_missing_live_model_is_explicit(self):
        with override_settings(DEMO_MODE=False, GEMINI_API_KEY=''):
            self.assertContains(self.client.get('/diagnosis/'), 'Image analysis is currently unavailable')
            self.assertEqual(self.submit().status_code, 503)
        self.assertFalse(Diagnosis.objects.exists())
        self.assertFalse(DiagnosisImage.objects.exists())

    def test_gemini_single_request_includes_all_photos(self):
        output = {'disease_id': self.disease.id, 'confidence': .82, 'contains_plant': True, 'inconsistent': False, 'explanation': 'Visible spots require expert confirmation.'}
        provider = gemini_response(output)
        with override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only', GEMINI_MODEL='gemini-3.1-flash-lite', GEMINI_TIMEOUT_SECONDS=60):
            with patch('ml_model.gemini.requests.post', return_value=provider) as request:
                response = self.submit(5)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(request.call_args.args[0], 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent')
                parts = request.call_args.kwargs['json']['contents'][0]['parts']
                self.assertEqual(len(parts), 6)
                self.assertEqual(sum('inlineData' in part for part in parts), 5)
                self.assertEqual(request.call_args.kwargs['timeout'], (5,60))
                self.assertFalse(request.call_args.kwargs['allow_redirects'])
                self.assertFalse(request.call_args.kwargs['json']['store'])
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['analysis_method'], 'gemini')
        self.assertAlmostEqual(response.json()['confidence_score'], .82)

    def test_provider_invalid_or_non_plant_response(self):
        base = {'disease_id': self.disease.id, 'confidence': .82, 'contains_plant': True, 'inconsistent': False, 'explanation': 'Visible spots.'}
        for overrides, expected in [({'disease_id': 9999},503), ({'confidence': 3},503), ({'contains_plant': False},400), ({'confidence': '0.8'},503)]:
            provider = gemini_response({**base, **overrides})
            with override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only'):
                with patch('ml_model.gemini.requests.post', return_value=provider):
                    self.assertEqual(self.submit().status_code, expected)

    def test_disabled_unsupported_or_malformed_configuration_never_calls_provider(self):
        for config in [{'ENABLE_AI_GENERATION': False}, {'AI_PROVIDER': 'unsupported'}, {'GEMINI_MODEL': 'gemini-3/../../other'}]:
            with self.subTest(config=config), override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only', **config):
                with patch('ml_model.gemini.requests.post') as request:
                    self.assertEqual(self.submit().status_code, 503)
                    request.assert_not_called()
                    self.assertContains(self.client.get('/diagnosis/'), 'Image analysis is currently unavailable')
                    self.assertEqual(self.client.get('/api/health/').json()['analysis'], 'unavailable')
        self.assertFalse(Diagnosis.objects.exists())

    def test_provider_auth_quota_and_model_errors_are_actionable_and_private(self):
        for status, message in [(401, 'authenticate'), (403, 'authenticate'), (404, 'model is unavailable'), (429, 'request limit')]:
            provider = Mock(status_code=status)
            provider.json.return_value = {'error': {'message': 'Secret: never-return-this'}}
            with self.subTest(status=status), override_settings(DEMO_MODE=False, GEMINI_API_KEY='never-return-this'):
                with patch('ml_model.gemini.requests.post', return_value=provider):
                    response = self.submit()
            self.assertEqual(response.status_code, 503)
            self.assertIn(message, response.json()['detail'])
            self.assertNotIn('never-return-this', response.content.decode())
        self.assertFalse(DiagnosisImage.objects.exists())

    def test_incomplete_empty_or_malformed_provider_output_never_completes(self):
        valid = {'disease_id': self.disease.pk, 'confidence': .8, 'contains_plant': True, 'inconsistent': False, 'explanation': 'Visible spots.'}
        responses = [gemini_response(valid, finish='MAX_TOKENS'), gemini_response(valid, finish='SAFETY')]
        for body in [{'candidates': []}, {'promptFeedback': {'blockReason': 'SAFETY'}}, {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': 'not JSON'}]}}]}]:
            provider = Mock(status_code=200)
            provider.json.return_value = body
            responses.append(provider)
        with override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only'):
            for provider in responses:
                with patch('ml_model.gemini.requests.post', return_value=provider):
                    self.assertEqual(self.submit().status_code, 503)
        self.assertFalse(Diagnosis.objects.filter(status='COMPLETED').exists())
        self.assertFalse(DiagnosisImage.objects.exists())

    def test_unknown_assessment_has_no_forced_disease_or_treatment(self):
        provider = gemini_response({'disease_id': 0, 'confidence': .95, 'contains_plant': True, 'inconsistent': False, 'explanation': 'No identifiable disease.'})
        with override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only'):
            with patch('ml_model.gemini.requests.post', return_value=provider):
                response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()['predicted_disease'])
        self.assertEqual(response.json()['confidence_score'], 0)
        self.assertTrue(Diagnosis.objects.get().is_low_confidence)

    def test_configured_live_mode_removes_unavailable_banner(self):
        with override_settings(DEMO_MODE=False, GEMINI_API_KEY='test-only', ENABLE_AI_GENERATION=True, AI_PROVIDER='gemini', GEMINI_TIMEOUT_SECONDS=60):
            response = self.client.get('/diagnosis/')
            self.assertNotContains(response, 'Image analysis is currently unavailable')
            self.assertContains(response, 'data-request-timeout="150000"')
            self.assertEqual(self.client.get('/api/health/').json()['analysis'], 'gemini')

    def test_pdf_escapes_questionnaire_text_and_works_without_paths(self):
        data = self.submit(treatment_details='<img src="file:///does-not-exist"/> & text').json()
        # InMemoryStorage has no filesystem path, like Cloudinary.
        response = self.client.get(f"/api/reports/{data['id']}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'%PDF-', response.content)

    def test_image_orientation_and_metadata_are_normalized(self):
        original = io.BytesIO()
        image = Image.new('RGB', (400, 300), 'green')
        exif = Image.Exif(); exif[274] = 6; exif[315] = 'test author'
        image.save(original, 'JPEG', exif=exif)
        self.submit(images=[SimpleUploadedFile('rotate.jpg', original.getvalue(), 'image/jpeg')])
        with DiagnosisImage.objects.get().image.open('rb') as saved:
            normalized = Image.open(saved)
            self.assertEqual(normalized.size, (300, 400))
            self.assertFalse(normalized.getexif())

    def test_bounded_database_queries_on_home(self):
        for n in range(12):
            Crop.objects.create(name=f'Crop {n}')
        with self.assertNumQueries(2):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_malformed_filter_is_400_not_500(self):
        self.assertEqual(self.client.get('/api/diseases/?crop_id=invalid').status_code, 400)

    def test_health_does_not_expose_credentials(self):
        with override_settings(GEMINI_API_KEY='never-return-this'):
            response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['database']['connected'])
        self.assertNotContains(response, 'never-return-this')
