from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_LIST_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITests(TestCase):
    """Testing the publicly available Ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that the Ingredient endpoints requires authentication"""
        response = self.client.get(INGREDIENTS_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test the private available Ingredient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@email.com',
            password='testPASS123',
        )

        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients list by an authenticated user"""
        Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Oats')

        response = self.client.get(INGREDIENTS_LIST_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_users(self):
        """Test listing ingredients created by the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='user2@email.com',
            password='user2Pass456',
        )
        Ingredient.objects.create(user=user2, name='Oats')
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')

        response = self.client.get(INGREDIENTS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)
