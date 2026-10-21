from rest_framework import serializers
from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project resource representation.
    Avoids N+1 query bottleneck by consuming annotated 'task_count' from QuerySet.
    """
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "owner_username",
            "task_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_task_count(self, obj) -> int:
        """
        Returns task count without triggering N+1 queries.
        Prefers the SQL-annotated attribute; falls back to ORM count for unsaved/unannotated instances.
        """
        if hasattr(obj, "task_count"):
            return obj.task_count
        return obj.tasks.count()

