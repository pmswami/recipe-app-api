"""
Serializer for recipe APIs
"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
)

class TagSerializer(serializers.ModelSerializer):
    """Serailizer for tag objects"""

    class Meta:
        model=Tag
        fields=["id", "name"]
        read_only_field=['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializes a recipe object"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Get or Create Tags"""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create and return new recipe"""
        tags = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        # auth_user = self.context["request"].user
        # for tag in tags:
        #     tag_obj, created = Tag.objects.get_or_create(
        #         user=auth_user,
        #         **tag,
        #     )
        #     recipe.tags.add(tag_obj)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update an existing recipe"""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']



