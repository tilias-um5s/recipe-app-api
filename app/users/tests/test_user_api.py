from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
CREATE_TOKEN_URL = reverse('users:auth-token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users Api (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload(credentials) is successful"""
        payload = {
            'email': 'ilias@email.com',
            'password': 'test123',
            'username': 'ilias'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_already_exists(self):
        """Test creating a duplicate user fails"""
        payload = {
            'email': 'ilias@email.com',
            'password': 'test123',
            'username': 'ilias'
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_is_short(self):
        """Test if the user's password is less than 5 characters"""
        payload = {
            'email': 'ilias@email.com',
            'password': 'pw',
            'username': 'ilias',
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'ilias@email.com',
            'password': 'test123',
            'username': 'ilias'
        }
        create_user(**payload)
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_for_invalid_user(self):
        """Test that a token is not created for an invalid user"""
        payload = {
            'email': 'ilias@email.com',
            'password': 'test123',
            'username': 'ilias'
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created with invalid credentials"""
        create_user(
            email='ilias@email.com',
            password='test123',
            username='ilias'
        )
        payload = {
            'email': 'ilias@email.com',
            'password': 'test1',
            'username': 'ilias'
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_token_with_missing_field(self):
        """Test that a token is not created if the password is missing"""
        payload = {
            'email': 'ilias@email.com',
            'password': '',
            'username': 'ilias'
        }
        create_user(**payload)
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
