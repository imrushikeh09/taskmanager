from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskListCreateAPIView, TaskDetailAPIView, TaskViewSet

# Register ModelViewSet with DRF DefaultRouter
router = DefaultRouter()
router.register(r"", TaskViewSet, basename="task")

urlpatterns = [
    # Explicit APIView endpoints (Milestone 2.1)
    path("apiview/", TaskListCreateAPIView.as_view(), name="task-list-create-apiview"),
    path("apiview/<int:pk>/", TaskDetailAPIView.as_view(), name="task-detail-apiview"),

    # ModelViewSet endpoints with pagination, filtering, search, and ordering (Milestone 2.2)
    path("", include(router.urls)),
]
