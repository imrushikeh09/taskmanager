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
