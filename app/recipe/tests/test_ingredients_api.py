from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.validators import ValidationError
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe
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

    def test_create_invalid_ingredients(self):
        """Test creating an invalid ingredient"""
        payload = {'name': ''}
        response = self.client.post(INGREDIENTS_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(ValidationError)

    def test_creating_ingredients_successful(self):
        """Test creating valid new ingredients"""
        payload = {'name': 'Eggs'}
        response = self.client.post(INGREDIENTS_LIST_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertTrue(exists)

    def test_retrive_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Eggs',
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Oats',
        )

        recipe = Recipe.objects.create(
            user=self.user,
            title='Omelette',
            time_minutes=10,
            price=1.00
        )
        recipe.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_LIST_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returnes unique items"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Eggs',
        )
        Ingredient.objects.create(
            user=self.user,
            name='Oats',
        )

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Omelette',
            time_minutes=10,
            price=1.00
        )
        recipe1.ingredients.add(ingredient1)

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Boiled eggs',
            time_minutes=15,
            price=1.00
        )
        recipe2.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_LIST_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)
