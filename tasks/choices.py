from django.db import models


class TaskStatus(models.TextChoices):
    """
    Allowed execution statuses for a task.
    """
    TODO = "TODO", "To Do"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    BLOCKED = "BLOCKED", "Blocked"
    COMPLETED = "COMPLETED", "Completed"


class TaskPriority(models.TextChoices):
    """
    Priority classification for scheduling urgency.
    """
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    URGENT = "URGENT", "Urgent"
