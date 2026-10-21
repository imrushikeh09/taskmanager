from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle

from projects.models import Project

User = get_user_model()


class AuthAndJWTTestCase(TestCase):
    """
    Integration tests for SimpleJWT Authentication & Rate Throttling:
    - Token generation (/api/v1/auth/token/)
    - Token refresh (/api/v1/auth/token/refresh/)
    - Bearer header authorization on protected resources
    - Rate throttling breach (429 Too Many Requests)
    """

    def setUp(self):
        self.client = APIClient()
        self.username = "jwt_tester"
        self.password = "strong_jwt_pass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="jwt_tester@example.com",
        )
        self.project = Project.objects.create(name="JWT Project", owner=self.user)

    def test_token_obtain_pair_success(self):
        """POST /api/v1/auth/token/ with valid credentials returns access and refresh tokens."""
        response = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertTrue(len(data["access"]) > 20)
        self.assertTrue(len(data["refresh"]) > 20)

    def test_token_obtain_pair_invalid_credentials(self):
        """POST /api/v1/auth/token/ with wrong password returns 401 Unauthorized."""
        response = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": "wrong_password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        """POST /api/v1/auth/token/refresh/ with valid refresh token returns fresh access token."""
        obtain_res = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        refresh_token = obtain_res.json()["refresh"]

        refresh_res = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        data = refresh_res.json()
        self.assertIn("access", data)

    def test_bearer_token_authorization_on_endpoints(self):
        """Requesting protected write endpoint with Bearer header authenticates user."""
        obtain_res = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        access_token = obtain_res.json()["access"]

        # Authenticate via HTTP Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            "/api/v1/tasks/",
            {
                "title": "JWT Authenticated Task",
                "project_id": self.project.id,
                "status": "TODO",
                "priority": "HIGH",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["creator_username"], self.username)

    def test_rate_throttling_breach_returns_429(self):
        """Rapid unauthenticated requests exceeding throttle limit return 429 Too Many Requests."""
        cache.clear()
        with patch.object(AnonRateThrottle, "get_rate", return_value="2/min"):
            unauth_client = APIClient()
            r1 = unauth_client.get("/api/v1/projects/")
            self.assertEqual(r1.status_code, status.HTTP_200_OK)

            r2 = unauth_client.get("/api/v1/projects/")
            self.assertEqual(r2.status_code, status.HTTP_200_OK)

            # 3rd request breaches the limit -> 429 Too Many Requests
            r3 = unauth_client.get("/api/v1/projects/")
            self.assertEqual(r3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertIn("detail", r3.json())
