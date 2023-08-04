"""
Serializers for User API views
"""


from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """ Serializer to map the model instance into JSON format """

    class Meta:
        """Serializer Meta class"""
        model =  get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs={"password":{"write_only": True, "min_length":5}}

        def create(self, validated_data):
            """ create and return a suer with encrypted password."""
            return get_user_model().objects.create_user(**validated_data)