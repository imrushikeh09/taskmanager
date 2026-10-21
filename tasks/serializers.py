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


class TaskUpdateSerializer(serializers.Serializer):
    """
    Serializer for partial updates (PATCH) on tasks.
    All fields are optional.
    """
    title = serializers.CharField(max_length=255, min_length=3, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=TaskStatus.choices, required=False)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, required=False)
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)

    def validate_assignee_id(self, value):
        if value is not None:
            user = User.objects.filter(id=value).first()
            if not user:
                raise serializers.ValidationError(f"User with ID {value} does not exist.")
            if not user.is_active:
                raise serializers.ValidationError("Cannot assign task to an inactive user.")
        return value
