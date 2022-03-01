from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.validators import ValidationError

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_LIST_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that the Tags endpoint requires authenticated users"""
        response = self.client.get(TAGS_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test retrieving tags by authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@email.com',
            password='testPASS123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        response = self.client.get(TAGS_LIST_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_users(self):
        """Test that the returned tags are returned for authenticated users"""
        user2 = get_user_model().objects.create_user(
            email='user2@email.com',
            password='TestPass456',
        )

        Tag.objects.create(user=user2, name='Launch')
        tag = Tag.objects.create(user=self.user, name='Fruity')

        response = self.client.get(TAGS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_creating_invalid_tags(self):
        """Test creating invalid tags"""
        payload = {'name': ''}

        response = self.client.post(TAGS_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(ValidationError)

    def test_create_tags_successful(self):
        """Test creating tags successfully"""
        payload = {'name': 'test tag'}

        self.client.post(TAGS_LIST_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertTrue(exists)
