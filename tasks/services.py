from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.utils import timezone
from .models import Task
from .choices import TaskStatus, TaskPriority
from .cache import (
    get_performance_report_cache_key,
    invalidate_performance_cache,
    PERFORMANCE_REPORT_TTL,
)


class TaskService:
    """
    Encapsulates all domain business logic for Tasks.
    Ensures views and API controllers remain thin and decoupled from business rules.
    """

    @staticmethod
    def validate_due_date(due_date):
        """Ensure due date is not in the past."""
        if due_date and due_date < timezone.now().date():
            raise ValidationError({"due_date": "Due date cannot be set in the past."})

    @classmethod
    @transaction.atomic
    def create_task(cls, *, project, creator, title, description="", status=TaskStatus.TODO, priority=TaskPriority.MEDIUM, due_date=None, assignee=None):
        """
        Create a new task within a project after verifying domain rules.
        Invalidates cached performance reports for the project.
        """
        cls.validate_due_date(due_date)

        if assignee and not assignee.is_active:
            raise ValidationError({"assignee": "Cannot assign task to an inactive user account."})

        task = Task.objects.create(
            project=project,
            creator=creator,
            assignee=assignee,
            title=title.strip(),
            description=description.strip(),
            status=status,
            priority=priority,
            due_date=due_date,
        )

        # Invalidate cached report for this project on write
        invalidate_performance_cache(project.id)
        return task

    @classmethod
    @transaction.atomic
    def update_task_status(cls, *, task: Task, new_status: str):
        """
        Update the status of a task with domain validation.
        Invalidates cached performance reports for the project.
        """
        if new_status not in TaskStatus.values:
            raise ValidationError({"status": f"Invalid status '{new_status}'. Allowed: {TaskStatus.values}"})

        task.status = new_status
        task.save(update_fields=["status", "updated_at"])

        # Invalidate cached report for this project on status change
        invalidate_performance_cache(task.project_id)
        return task

    @classmethod
    @transaction.atomic
    def assign_task(cls, *, task: Task, assignee):
        """
        Assign or reassign a task to a user.
        Invalidates cached performance reports for the project.
        """
        if assignee and not assignee.is_active:
            raise ValidationError({"assignee": "Cannot assign task to an inactive user account."})

        task.assignee = assignee
        task.save(update_fields=["assignee", "updated_at"])

        # Invalidate cached report for this project on assignment change
        invalidate_performance_cache(task.project_id)
        return task

    @classmethod
    def get_heavy_performance_report(cls, project_id: int):
        """
        Calculates heavy statistical performance report for a project.
        Implements the Redis Cache-Aside Pattern (Reference PDF - Scenario 1, Problem 1):
          1. Checks Redis for a cached report using deterministic key.
          2. Cache Hit -> Returns cached report immediately (0 SQL queries).
          3. Cache Miss -> Executes single-pass DB aggregation, populates Redis (TTL 300s), and returns result.
        """
        cache_key = get_performance_report_cache_key(project_id)
        cached_report = cache.get(cache_key)
        if cached_report is not None:
            return cached_report

        from projects.models import Project

        project = Project.objects.filter(id=project_id).first()
        if not project:
            return None

        tasks_qs = project.tasks.all()
        counts = tasks_qs.aggregate(
            total_tasks=models.Count("id"),
            todo_count=models.Count("id", filter=models.Q(status=TaskStatus.TODO)),
            in_progress_count=models.Count("id", filter=models.Q(status=TaskStatus.IN_PROGRESS)),
            blocked_count=models.Count("id", filter=models.Q(status=TaskStatus.BLOCKED)),
            completed_count=models.Count("id", filter=models.Q(status=TaskStatus.COMPLETED)),
            urgent_count=models.Count("id", filter=models.Q(priority=TaskPriority.URGENT)),
            high_count=models.Count("id", filter=models.Q(priority=TaskPriority.HIGH)),
        )

        overdue_count = tasks_qs.filter(
            due_date__lt=timezone.now().date(),
            status__in=[TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED],
        ).count()

        total = counts["total_tasks"]
        completion_rate = round((counts["completed_count"] / total * 100), 2) if total > 0 else 0.0

        report_data = {
            "project_id": project.id,
            "project_name": project.name,
            "total_tasks": total,
            "completed_tasks": counts["completed_count"],
            "completion_rate_pct": completion_rate,
            "overdue_tasks": overdue_count,
            "status_breakdown": {
                TaskStatus.TODO: counts["todo_count"],
                TaskStatus.IN_PROGRESS: counts["in_progress_count"],
                TaskStatus.BLOCKED: counts["blocked_count"],
                TaskStatus.COMPLETED: counts["completed_count"],
            },
            "priority_breakdown": {
                TaskPriority.URGENT: counts["urgent_count"],
                TaskPriority.HIGH: counts["high_count"],
            },
        }

        # Store in Redis cache for 300 seconds (5-minute TTL)
        cache.set(cache_key, report_data, timeout=PERFORMANCE_REPORT_TTL)
        return report_data

