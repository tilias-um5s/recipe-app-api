from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


class AdmineSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@email.com',
            password='TestSuperUserPass123'
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@email.com',
            password='Testpass123',
            username='testuser'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_customuser_changelist')
        response = self.client.get(url)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.admin_user.email)

    def test_user_change_page(self):
        """Test user change page"""
        url = reverse('admin:core_customuser_change', args=(self.user.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_creation_page(self):
        """Test if user is created successfully in the admin page"""
        url = reverse('admin:core_customuser_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
