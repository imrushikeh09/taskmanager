from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from projects.models import Project
from projects.serializers import ProjectSerializer
from projects.services import ProjectService
from common.permissions import IsOwnerOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary="List all projects", description="Retrieve paginated list of projects with search and ordering.", tags=["Projects"]),
    create=extend_schema(summary="Create a new project", description="Create a workspace project owned by the current user.", tags=["Projects"]),
    retrieve=extend_schema(summary="Retrieve project details", description="Get full project metadata by ID.", tags=["Projects"]),
    update=extend_schema(summary="Update project", description="Replace all project fields.", tags=["Projects"]),
    partial_update=extend_schema(summary="Partially update project", description="Modify specific project fields.", tags=["Projects"]),
    destroy=extend_schema(summary="Delete a project", description="Remove a project and its associated tasks.", tags=["Projects"]),
)
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet providing complete CRUD for Projects,
    plus sub-resource aggregation statistics (/projects/{id}/stats/).
    Secured by IsOwnerOrReadOnly: anyone can view, but only project owners can modify/delete.
    """
    queryset = Project.objects.select_related("owner").all()
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Assign project owner automatically to authenticated user."""
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Get project task metrics",
        description="Calculates task breakdown by status and priority using efficient SQL aggregation.",
        tags=["Projects"],
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
