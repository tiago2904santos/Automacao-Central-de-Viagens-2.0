from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, f"{reverse('core:login')}?next={reverse('core:dashboard')}")

    def test_dashboard_redirects_to_central_documentos_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('eventos:documentos-hub'))
        response = self.client.get(reverse('core:dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Central global de documentos')
        self.assertContains(response, reverse('eventos:oficios-global'))
