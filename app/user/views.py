"""
Views for user API
"""

from rest_framework import generics
from user.serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    """Creates a new user in the system."""
    serializer_class = UserSerializer
