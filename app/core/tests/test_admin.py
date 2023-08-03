"""
Test django admin modifications
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):
    """Testing the admin site for users."""
    def setUp(self):
        self.client = Client()
        # Create a user that is not staff or superuser and log in to client
        self.admin_user = get_user_model().objects.create_superuser(
            email = "superuser@example.com",
            password = "testpass123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = "user@example.com",
            password = "testpass123",
            name = "test User"
        )

    def test_users_list(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
