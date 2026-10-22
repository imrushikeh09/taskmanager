from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import TaskAttachment
from .serializers import TaskAttachmentSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List task attachments",
        description="Retrieve all file attachments with optional filter by ?task=<id>.",
        tags=["Attachments"],
    ),
    create=extend_schema(
        summary="Upload file attachment",
        description="Upload a file attachment (multipart/form-data) linked to a task. Max size 10MB.",
        tags=["Attachments"],
    ),
    retrieve=extend_schema(
        summary="Get attachment metadata",
        description="Retrieve metadata for a specific task attachment.",
        tags=["Attachments"],
    ),
    destroy=extend_schema(
        summary="Delete attachment",
        description="Delete a task attachment record and reference.",
        tags=["Attachments"],
    ),
)
class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for uploading, listing, and managing task file attachments.
    Supports multipart/form-data payload uploads.
    """
    queryset = TaskAttachment.objects.select_related("task", "uploader").all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["task"]
    ordering_fields = ["uploaded_at", "file_size_bytes"]
    ordering = ["-uploaded_at"]
    http_method_names = ["get", "post", "delete", "head", "options"]
