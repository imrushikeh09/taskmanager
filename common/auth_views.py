from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


class DecoratedTokenObtainPairView(TokenObtainPairView):
    """
    Takes user credentials (username and password) and returns an access and refresh
    JSON web token pair to prove authentication.
    """

    @extend_schema(
        tags=["Authentication"],
        summary="Obtain JWT token pair",
        description="Authenticates user credentials and returns an access token (60 min validity) and refresh token (7 days validity).",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenRefreshView(TokenRefreshView):
    """
    Takes a refresh type JSON web token and returns a fresh access token
    if the refresh token is valid and not expired.
    """

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh JWT access token",
        description="Submits a valid refresh token to obtain a fresh access token without re-entering user credentials.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


from django.contrib.auth import get_user_model
from rest_framework import serializers, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from common.roles import get_user_role

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Serializer representing the profile, permissions, and active RBAC role of the authenticated user.
    """
    role = serializers.SerializerMethodField(help_text="Active RBAC Role (ADMIN, CONTRIBUTOR, VIEWER)")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_superuser",
            "is_staff",
        ]
        read_only_fields = fields

    def get_role(self, obj) -> str:
        return get_user_role(obj)


class CurrentUserView(APIView):
    """
    Returns the authenticated user's profile and active RBAC role.
    Consumed by frontend applications on initialization and state hydration.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Get current user profile",
        description="Retrieve profile details, email, and active RBAC role for the currently authenticated session.",
        responses={200: CurrentUserSerializer},
    )
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

