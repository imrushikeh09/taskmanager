from django.db import transaction, models
from .models import Project


class ProjectService:
    """
    Encapsulates all domain business logic for Projects.
    """

    @classmethod
    @transaction.atomic
    def create_project(cls, *, owner, name: str, description: str = ""):
        """
        Create a new project workspace.
        """
        project = Project.objects.create(
            owner=owner,
            name=name.strip(),
            description=description.strip(),
        )
        return project

    @staticmethod
    def get_project_statistics(project_id: int):
        """
        Calculates project task summary metrics using single-pass SQL conditional aggregation.
        Uses PostgreSQL 'COUNT(id) FILTER (WHERE ...)' to avoid multiple DB roundtrips and in-memory row processing.
        """
        from tasks.choices import TaskStatus, TaskPriority

        project = Project.objects.filter(id=project_id).first()
        if not project:
            return None

        # Execute single-pass conditional aggregation across all statuses and priorities
        metrics = project.tasks.aggregate(
            total_tasks=models.Count("id"),
            # Status conditional aggregations
            todo_count=models.Count("id", filter=models.Q(status=TaskStatus.TODO)),
            in_progress_count=models.Count("id", filter=models.Q(status=TaskStatus.IN_PROGRESS)),
            blocked_count=models.Count("id", filter=models.Q(status=TaskStatus.BLOCKED)),
            completed_count=models.Count("id", filter=models.Q(status=TaskStatus.COMPLETED)),
            # Priority conditional aggregations
            low_count=models.Count("id", filter=models.Q(priority=TaskPriority.LOW)),
            medium_count=models.Count("id", filter=models.Q(priority=TaskPriority.MEDIUM)),
            high_count=models.Count("id", filter=models.Q(priority=TaskPriority.HIGH)),
            urgent_count=models.Count("id", filter=models.Q(priority=TaskPriority.URGENT)),
        )

        return {
            "project_id": project.id,
            "project_name": project.name,
            "total_tasks": metrics["total_tasks"],
            "by_status": {
                TaskStatus.TODO: metrics["todo_count"],
                TaskStatus.IN_PROGRESS: metrics["in_progress_count"],
                TaskStatus.BLOCKED: metrics["blocked_count"],
                TaskStatus.COMPLETED: metrics["completed_count"],
            },
            "by_priority": {
                TaskPriority.LOW: metrics["low_count"],
                TaskPriority.MEDIUM: metrics["medium_count"],
                TaskPriority.HIGH: metrics["high_count"],
                TaskPriority.URGENT: metrics["urgent_count"],
            },
        }
