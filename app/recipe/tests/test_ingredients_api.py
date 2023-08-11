"""
Test for Ingredient API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

from core.models import (
    Recipe,
    Ingredient,
)

INGREDIENTS_URL = reverse("recipe:ingredient-list")

def detail_url(ingredient_id):
    """Return ingredient details URL"""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create a new user."""
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class PublicIngredientsApiTests(TestCase):
    """ Test unauthenticated API requests """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """ Test authenticated API requestss """
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieveing all ingredients"""
        Ingredient.objects.create(user=self.user,name="Kale")
        Ingredient.objects.create(user=self.user,name="Vanilla")

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only the users ingredients are returned"""
        other_user = create_user(email="user2@example.com")
        Ingredient.objects.create(user=other_user, name="Salt")
        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name="Cilantro")
        payload = {"name": "Coriander"}

        url = detail_url(ingredient.id)
        res = self.client.patch(url,payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting a ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name="Lettuce")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_asigned_to_recipes(self):
        """Test returning assigned ingredients to recipes"""
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Apple Crumble',
            time_minutes=5,
            price=300
        )
        ingredient1 = Ingredient.objects.create(user = self.user, name="Apples")
        ingredient2= Ingredient.objects.create(user = self.user, name="Turkey")
        recipe1.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only':1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data , res.data)
        self.assertNotIn(serializer2.data , res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient1 = Ingredient.objects.create(user = self.user, name="Eggs")
        ingredient2 = Ingredient.objects.create(user = self.user, name="Lentils")
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Eggs Benedict',
            time_minutes=5,
            price=300,
            )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title ='Herb Eggs',
            time_minutes=6,
            price=798,
            )
        # Add the same ingrediants in both recipes
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only':1})
        self.assertEqual(len(res.data), 1)