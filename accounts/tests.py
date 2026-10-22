from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from common.roles import UserRole

User = get_user_model()


class CurrentUserViewTests(APITestCase):
    """
    Integration tests for GET /api/v1/auth/me/ endpoint.
    Verifies user profile hydration and RBAC role computation.
    """

    def setUp(self):
        self.url = reverse("current_user")
        self.admin_user = User.objects.create_superuser(
            username="admin_hero",
            email="admin@hero.com",
            password="password123",
            first_name="Admin",
            last_name="Hero",
        )
        self.contributor_user = User.objects.create_user(
            username="dev_member",
            email="dev@member.com",
            password="password123",
            first_name="Dev",
            last_name="Member",
        )
        self.viewer_user = User.objects.create_user(
            username="guest_viewer",
            email="guest@viewer.com",
            password="password123",
        )
        viewer_group = Group.objects.create(name=UserRole.VIEWER)
        self.viewer_user.groups.add(viewer_group)

    def test_unauthenticated_request_fails(self):
        """Unauthenticated client cannot access /me/ endpoint."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_profile_and_role(self):
        """Admin user receives ADMIN role and superuser flags."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "admin_hero")
        self.assertEqual(response.data["email"], "admin@hero.com")
        self.assertEqual(response.data["role"], UserRole.ADMIN)
        self.assertTrue(response.data["is_superuser"])

    def test_contributor_profile_and_role(self):
        """Standard authenticated member receives CONTRIBUTOR role."""
        self.client.force_authenticate(user=self.contributor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "dev_member")
        self.assertEqual(response.data["role"], UserRole.CONTRIBUTOR)
        self.assertFalse(response.data["is_superuser"])

    def test_viewer_profile_and_role(self):
        """Viewer group member receives VIEWER role."""
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "guest_viewer")
        self.assertEqual(response.data["role"], UserRole.VIEWER)
