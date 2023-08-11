"""

"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)
import tempfile
import os
from PIL import Image

RECIPE_URL = reverse("recipe:recipe-list")

def detail_url(recipe_id):
    """Return recipe details URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])

def image_upload_url(recipe_id):
    """Return recipe upload url"""
    return reverse('recipe:recipe-upload-image',args=[recipe_id])


def create_recipe(user, **params):
    """Create a recipe for the given user."""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description":"Sample Description",
        "link": "http://example.com/recipe.pdf"
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user,**defaults)
    return recipe

def create_user(**params):
    """Create and authenticate an user with email & password"""
    return get_user_model().objects.create_user(**params)

class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipes API access"""

    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email = "user@example.com", password="testpass123")
        # self.user = get_user_model().objects.create_user(
        #     "user@example.com",
        #     "testpass123"
        # )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user = self.user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code , status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test that only recips for logged in users are returned"""
        other_user = create_user(email="other@example.com", password="testpass123")
        # other_user = get_user_model().objects.create_user(
        #     "other@example.com",
        #     "testpass123",
        # )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test getting the details of an individual recipe"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe"""
        payload = {
            "title":"Sample Recipe",
             "time_minutes": 30,
             "price": Decimal("5.99"),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test updating a recipe with patch"""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user = self.user,
            title = "Sample Recipe Title",
            link = original_link,
        )
        payload = {"title":"New Sample Recipe"}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test updating a recipe with put"""
        recipe = create_recipe(
            title ="Sample recipe title",
            user = self.user,
            link = "https://example.com/recipe.pdf",
            description = "Sample recipe description",
            )
        payload = {
            "title": "new Recipe Title",
            "link": "https://example.com/new-recipe.pdf",
            "description": "New recipe description",
            "time_minutes": 10,
            "price":Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url,payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test that updateing the user field returns an error."""
        new_user = create_user(
            email="user2@example.com",
            password="testpass@123"
        )
        recipe = create_recipe(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe by id"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        # check if deleted successfully and not found anymore on get request
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_otehr_users_recipe_error(self):
        """Test trying to delete another users recipes return error code (404)"""
        new_user = create_user(email='user2@example.com', password='testpass123')
        recipe = create_recipe(user = new_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code , status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags"""
        payload = {
            "title": "Thai Prawn Curry",
            "time_minutes": 30,
            "price": Decimal("6"),
            "tags": [{"name":"Thai"}, {"name":"Dinner"}],
        }
        res = self.client.post(RECIPE_URL, payload, format="json" )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags"""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            'title' : 'Pongal',
            'time_minutes':5,
            'price':Decimal('8'),
            'tags': [{"name":"Indian"}, {"name":"Breakfast"}]
        }
        res = self.client.post(RECIPE_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """ Test updating an exisiting recipe with new tag"""
        # Create the initial recipe and add two tags to it
        recipe = create_recipe(user=self.user)
        payload = {"tags": [{"name":"Lunch"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user = self.user, name="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test updateing an existing recipe assignes tags"""
        tag_breakfast = Tag.objects.create(user = self.user, name="Breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {"tags": [{"name":"Lunch"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing all assigned tags from an existing recipe."""
        tag = Tag.objects.create(user=self.user, name="Dessert")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        payload={"tags":[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a new recipe with ingredients"""
        payload = {
            "title" : "Cauliflower Tacos",
            'time_minutes':15,
            'price':Decimal("3.99"),
            "ingredients": [{"name":"Cauliflower"}, {"name":"Salt"}]
        }
        res = self.client.post(RECIPE_URL,payload ,format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existsing_ingredient(self):
        """Test creating a new recipe with existsing ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")
        payload={
            "title":"Vietnemese Soup",
            "time_minutes":60,
            "price": Decimal('8'),
            "ingredients":[{"name":"Lemon"},{"name":"Fish Sauce"}]
            }
        res = self.client.post(RECIPE_URL,payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
                ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test updating an existing recipe's ingrediants"""
        recipe = create_recipe(user=self.user)

        payload = {"ingredients":[{"name":"Limes"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name="Limes")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredients(self):
        """Test updating an existing recipe assignes the given ingredients to it."""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name="Chili")
        payload={"ingredients":[{"name": "Chili"}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload ,format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test that clearing a new recipe with assigned ingredients works properly"""
        ingredient = Ingredient.objects.create(user=self.user, name="Garlic")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        payload={"ingredients": []}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags"""
        r1 = create_recipe(user=self.user, title="Thai Vegetable Curry")
        tag1 = Tag.objects.create(user=self.user, name="Vegan")
        r1.tags.add(tag1)
        r2 = create_recipe(user = self.user, title = "Aubergini with Tahini")
        tag2 = Tag.objects.create(user=self.user,name ="Vegetarian")
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title="Fish and Chips")

        params = {"tags": f"{tag1.id},{tag2.id}"}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def filter_by_ingredients(self):
        """ Filter by ingredients"""
        r1 = create_recipe(user = self.user, title="Posh Beans on Toast")
        r2 = create_recipe(user = self.user, title="Chicken Cacciatore")
        r3 = create_recipe(user = self.user, title="Red Lentil Daal")
        ingredient1 = Ingredient.objects.create(user=self.user, name="Feta Cheese")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Chicken")
        r1.ingredients.add(ingredient1)
        r2.ingredients.add(ingredient2)

        params = {'ingredients':f'{ingredient1.id}, {ingredient2.id}' }
        res = self.client.get(RECIPE_URL,params)

        serializer1 = RecipeSerializer(r1)
        serializer2 = RecipeSerializer(r2)
        serializer3 = RecipeSerializer(r3)
        self.assertIn(serializer1.data,res.data)
        self.assertIn(serializer2.data,res.data)
        self.assertNotIn(serializer3.data,res.data)


class ImageUploadTests(TestCase):
    """Testing image upload functionality of recipes app"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    #Runs after test completes
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image for a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image file fails"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
