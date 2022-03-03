import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


def image_upload_url(recipe_id):
    """Return the recipe image upload url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


# /api/recipe/recipes
RECIPE_LIST_URL = reverse('recipe:recipe-list')


# /api/recipe/recipes/1/
def recipe_detail_URL(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test the publicly available recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that the recipe endpoint requires authenticated users"""
        response = self.client.get(RECIPE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the recipe endpoint with authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@email.com',
            password='testPASS678',
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving the list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPE_LIST_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that the recipes are limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='user2@email.com',
            password='testPASS321'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        response = self.client.get(RECIPE_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_detail_view(self):
        """Test viewing a recipe's details"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_detail_URL(recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_creating_basic_recipe(self):
        """Test creating a basic recipe"""
        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 10,
            'price': 5.00,
            'link': '',
        }

        response = self.client.post(RECIPE_LIST_URL, payload)
        recipe = Recipe.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_creating_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00,
        }

        response = self.client.post(RECIPE_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_creating_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Eggs')
        ingredient2 = sample_ingredient(user=self.user, name='Oats')

        payload = {
            'title': 'Pancake',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 5.00,
        }

        response = self.client.post(RECIPE_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_updating_recipe(self):
        """Test partial updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chiken tikka', 'tags': [new_tag.id]}
        url = recipe_detail_URL(recipe.id)
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertEqual(recipe.title, payload['title'])
        self.assertIn(new_tag, tags)

    def test_full_updating_recipe(self):
        """Test full updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        new_tag = sample_tag(user=self.user, name='Healthy')
        new_ingredient = sample_ingredient(user=self.user, name='Eggs')

        payload = {
            'title': 'Omelette',
            'tags': [new_tag.id],
            'ingredients': [new_ingredient.id],
            'time_minutes': 20,
            'price': 5.00,
            'link': '',
        }
        url = recipe_detail_URL(recipe.id)
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        tags = recipe.tags.all()
        ingredients = recipe.ingredients.all()

        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)
        self.assertEqual(ingredients.count(), 1)
        self.assertIn(new_ingredient, ingredients)
        self.assertEqual(recipe.title, payload['title'])


class RecipeImageUploadTests(TestCase):
    """Test uploading an image to a recipe"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@email.com',
            password='testPASS123'
        )
        self.client.force_authenticate(self.user)

        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """Makes sure that the file system kept clean
        by removing all the test files"""

        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, 'JPEG')
            ntf.seek(0)
            print(ntf.name)
            payload = {'image': ntf}
            response = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image_to_recipe(self):
        """Test uploading an invalid image to a recipe"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'noimage'}
        response = self.client.post(url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
