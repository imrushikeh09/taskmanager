from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from projects.models import Project
from projects.serializers import ProjectSerializer
from projects.services import ProjectService
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet providing complete CRUD for Projects,
    plus sub-resource aggregation statistics (/projects/{id}/stats/).
    """
    queryset = Project.objects.select_related("owner").all()
    serializer_class = ProjectSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Assign project owner automatically."""
        owner = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(owner=owner)

    @extend_schema(
        summary="Get project task metrics",
        description="Calculates task breakdown by status and priority using efficient SQL aggregation.",
        responses={200: OpenApiResponse(description="Project statistics object")},
    )
    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        """Return aggregated project statistics."""
        statistics = ProjectService.get_project_statistics(project_id=pk)
        if not statistics:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": f"Project {pk} not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(statistics, status=status.HTTP_200_OK)
