from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .models import Notification
from .serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List user notifications",
        description="Retrieve a paginated list of in-app notifications for the authenticated user. Use query param ?is_read=true or ?is_read=false.",
        tags=["Notifications"],
    ),
    retrieve=extend_schema(
        summary="Retrieve notification detail",
        description="Get specific in-app notification details.",
        tags=["Notifications"],
    ),
    mark_as_read=extend_schema(
        summary="Mark notification as read",
        description="Acknowledge and mark a single notification as read.",
        responses={200: NotificationSerializer},
        tags=["Notifications"],
    ),
    mark_all_as_read=extend_schema(
        summary="Mark all notifications as read",
        description="Acknowledge and mark all unread notifications as read for current user.",
        responses={200: OpenApiResponse(description="All notifications marked as read")},
        tags=["Notifications"],
    ),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing and managing in-app notifications for the authenticated user.
    Leverages the composite index (recipient, is_read) for instant response times.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Notification.objects.none()
        qs = Notification.objects.filter(recipient=self.request.user).select_related("task")
        is_read_param = self.request.query_params.get("is_read")
        if is_read_param is not None:
            is_read = is_read_param.lower() in ["true", "1", "yes"]
            qs = qs.filter(is_read=is_read)
        return qs.order_by("-created_at")

    @action(detail=True, methods=["patch", "post"], url_path="read")
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read", "updated_at"])
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_as_read(self, request):
        updated_count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response(
            {"message": "All unread notifications marked as read.", "updated_count": updated_count},
            status=status.HTTP_200_OK,
        )
