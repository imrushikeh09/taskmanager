from rest_framework import serializers
from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus, TaskPriority
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskReadSerializer(serializers.ModelSerializer):
    """
    Serializer for outgoing Task representations (Read operations).
    Uses eager-loaded relationships to avoid N+1 queries.
    """
    project_name = serializers.CharField(source="project.name", read_only=True)
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    assignee_username = serializers.CharField(source="assignee.username", read_only=True, default=None)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "project",
            "project_name",
            "creator",
            "creator_username",
            "assignee",
            "assignee_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskWriteSerializer(serializers.Serializer):
    """
    Serializer for incoming Task payloads (Create and Update operations).
    Performs field-level and object-level validation.
    """
    title = serializers.CharField(max_length=255, min_length=3, required=True)
    description = serializers.CharField(allow_blank=True, default="")
    project_id = serializers.IntegerField(required=True)
    assignee_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    status = serializers.ChoiceField(choices=TaskStatus.choices, default=TaskStatus.TODO)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    due_date = serializers.DateField(required=False, allow_null=True, default=None)

    def validate_title(self, value):
        """Field-level validator for task title."""
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Task title must be at least 3 characters long.")
        return cleaned

    def validate_project_id(self, value):
        """Field-level validator ensuring target project exists."""
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Project with ID {value} does not exist.")
        return value

    def validate_assignee_id(self, value):
        """Field-level validator ensuring assignee exists and is active."""
        if value is not None:
            user = User.objects.filter(id=value).first()
            if not user:
                raise serializers.ValidationError(f"User with ID {value} does not exist.")
            if not user.is_active:
                raise serializers.ValidationError("Cannot assign task to an inactive user account.")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for partial updates (PATCH) on tasks.
    All fields are optional.
    """
    assignee_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "due_date", "assignee_id"]
        extra_kwargs = {
            "title": {"required": False, "min_length": 3},
            "description": {"required": False},
            "status": {"required": False},
            "priority": {"required": False},
            "due_date": {"required": False},
        }

    def validate_assignee_id(self, value):
        if value is not None:
            user = User.objects.filter(id=value).first()
            if not user:
                raise serializers.ValidationError(f"User with ID {value} does not exist.")
            if not user.is_active:
                raise serializers.ValidationError("Cannot assign task to an inactive user.")
        return value

    def update(self, instance, validated_data):
        assignee_id = validated_data.pop("assignee_id", None)
        if assignee_id is not None:
            instance.assignee = User.objects.get(id=assignee_id)
        elif "assignee_id" in self.initial_data and assignee_id is None:
            instance.assignee = None

        return super().update(instance, validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for outgoing Notification representations.
    """
    task_title = serializers.CharField(source="task.title", read_only=True, default=None)

    class Meta:
        from tasks.models import Notification
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

