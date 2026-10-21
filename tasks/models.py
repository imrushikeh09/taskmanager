from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from .choices import TaskStatus, TaskPriority, NotificationType
from .querysets import TaskQuerySet


class Task(TimeStampedModel):
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

    # Attach custom domain queryset as default manager
    objects = TaskQuerySet.as_manager()

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


class Notification(TimeStampedModel):
    """
    In-app alert delivered to users for critical task events.
    Indexed on (recipient, is_read) for instant lookup of unread notifications.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Recipient of the in-app notification",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Associated task reference",
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        help_text="Classification of notification event",
    )
    message = models.TextField(help_text="Human-readable notification text")
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates if recipient has acknowledged/read the notification",
    )

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"], name="idx_notif_recipient_read"),
        ]

    def __str__(self):
        return f"Notification to user={self.recipient_id} [{self.notification_type}] (read={self.is_read})"

