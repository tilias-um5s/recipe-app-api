from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

from unittest.mock import patch


def sample_user(email='test@email.com', password='testPass123'):
    """Create a sample user for tests"""
    return get_user_model().objects.create_user(email, password)


class TestModel(TestCase):

    def test_create_user_with_email_success(self):
        """Tests if a user is created succesfuly with an email"""
        email = 'test@email.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self):
        """Tests if the user's email is normalized"""
        email = 'test@EMAIL.COM'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='Testpass123')

    def test_create_superuser_success(self):
        """Test creating a superuser"""
        superuser = get_user_model().objects.create_superuser(
            email='testsuperuser@email.com',
            password='TestSuperUserPass123',
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Breakfast',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the Ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the Recipe string representation"""
        recipe = models.Recipe.objects.create(
            # Required fields only
            user=sample_user(),
            title='Omlette',
            time_minutes=5,
            price=1.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        expc_path = f'uploads/recipe/recipe_image_{uuid}.jpg'

        self.assertEqual(file_path, expc_path)
