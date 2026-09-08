from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import FarmerProfile


class AccountFlowTest(TestCase):
    def test_weak_password_is_rejected(self):
        response = self.client.post('/accounts/register/', {'username': 'farmer', 'password': '123', 'confirm_password': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_register_login_dashboard_and_post_logout(self):
        response = self.client.post('/accounts/register/', {'username': 'farmer', 'password': 'test-long-74!garden', 'confirm_password': 'test-long-74!garden'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FarmerProfile.objects.count(), 1)
        self.assertEqual(self.client.get('/accounts/logout/').status_code, 405)
        self.assertEqual(self.client.post('/accounts/logout/').status_code, 302)
        self.assertEqual(self.client.get('/accounts/dashboard/').status_code, 302)
        response = self.client.post('/accounts/login/?next=https://example.org', {'username':'farmer', 'password':'test-long-74!garden'})
        self.assertRedirects(response, '/accounts/dashboard/')

    def test_duplicate_username_and_mismatch_do_not_create_accounts(self):
        User.objects.create_user('farmer')
        response = self.client.post('/accounts/register/', {'username':'farmer', 'password':'test-long-74!garden','confirm_password':'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
