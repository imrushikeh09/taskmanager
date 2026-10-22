"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from common.auth_views import (
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    CurrentUserView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI 3.0 Schema and Interactive Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication Endpoints (SimpleJWT & Profile Hydration)
    path('api/v1/auth/token/', DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/me/', CurrentUserView.as_view(), name='current_user'),

    # v1 Domain Endpoints
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/tasks/', include('tasks.urls')),
    path('api/v1/attachments/', include('attachments.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
]

# Media file serving in development and Docker local environments
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



