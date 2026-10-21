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
        Calculates project task summary metrics using SQL aggregations.
        Avoids loading all task rows into Python memory.
        """
        project = Project.objects.filter(id=project_id).first()
        if not project:
            return None

        # Aggregate total tasks and breakdown by status in single optimized query
        tasks_qs = project.tasks.all()
        total_tasks = tasks_qs.count()

        # Count by status using conditional aggregation (FILTER in SQL)
        status_counts = tasks_qs.values("status").annotate(count=models.Count("id"))
        priority_counts = tasks_qs.values("priority").annotate(count=models.Count("id"))

        by_status = {item["status"]: item["count"] for item in status_counts}
        by_priority = {item["priority"]: item["count"] for item in priority_counts}

        return {
            "project_id": project.id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "by_status": by_status,
            "by_priority": by_priority,
        }
