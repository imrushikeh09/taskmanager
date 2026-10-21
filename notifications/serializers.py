from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for outgoing Notification representations.
    """
    task_title = serializers.CharField(source="task.title", read_only=True, default=None)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "task",
            "task_title",
            "notification_type",
            "message",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recipient",
            "task",
            "task_title",
            "notification_type",
            "message",
            "created_at",
            "updated_at",
        ]
