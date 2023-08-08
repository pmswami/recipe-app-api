"""
Serializer for recipe APIs
"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
)

class RecipeSerializer(serializers.ModelSerializer):
    """Serializes a recipe object"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', "time_minutes", "price", "link"]
        read_only_fields = ["id"]

class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serailizer for tag objects"""
    class Meta:
        model=Tag
        fields=["id", "name"]
        read_only_field=['id']
