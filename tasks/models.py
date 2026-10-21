from django.conf import settings
from django.db import models


class TaskStatus(models.TextChoices):
    TODO = "TODO", "To Do"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    BLOCKED = "BLOCKED", "Blocked"
    COMPLETED = "COMPLETED", "Completed"


class TaskPriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    URGENT = "URGENT", "Urgent"


class Task(models.Model):
    """
    Represents an actionable unit of work within a project.
    Tracks assignment, progress status, priority, and due dates.
    """
    title = models.CharField(max_length=255, help_text="Summary of the task")
    description = models.TextField(blank=True, default="", help_text="Full task requirements and details")
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        help_text="Current execution status",
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        help_text="Priority level",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target completion date",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Parent project this task belongs to",
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tasks",
        help_text="User who created the task (protected from deletion)",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="User assigned to perform the task",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "status"], name="idx_task_project_status"),
            models.Index(fields=["assignee"], name="idx_task_assignee"),
            models.Index(fields=["due_date"], name="idx_task_due_date"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "title"],
                name="unique_task_project_title",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"
