from django.db import models


class NotificationType(models.TextChoices):
    """
    Categorization of in-app notification events.
    Extensible across tasks, projects, comments, and system alerts.
    """
    TASK_ASSIGNED = "TASK_ASSIGNED", "Task Assigned"
    STATUS_CHANGED = "STATUS_CHANGED", "Status Changed"
    SYSTEM_ALERT = "SYSTEM_ALERT", "System Alert"
