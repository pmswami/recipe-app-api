"""
Serializer for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """Serializes a recipe object"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', "time_minutes", "price", "link"]
        read_only_fields = ["id"]
