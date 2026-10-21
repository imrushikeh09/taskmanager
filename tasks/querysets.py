from django.db import models
from django.utils import timezone
from .choices import TaskStatus


class TaskQuerySet(models.QuerySet):
    """
    Custom QuerySet for Task providing domain-level query methods.
    Encapsulates reusable filters and eager loading logic.
    """

    def with_related(self):
        """
        Eager loads single-valued foreign key relationships.
        Prevents N+1 queries when accessing project or user metadata.
        """
        return self.select_related("project", "creator", "assignee")

    def for_user(self, user):
        """
        Returns tasks accessible to a specific user:
        - Tasks assigned to the user
        - Tasks created by the user
        - Tasks belonging to projects owned by the user
        """
        return self.filter(
            models.Q(assignee=user)
            | models.Q(creator=user)
            | models.Q(project__owner=user)
        ).distinct()

    def in_progress(self):
        """Filter tasks currently in progress."""
        return self.filter(status=TaskStatus.IN_PROGRESS)

    def completed(self):
        """Filter tasks that have been completed."""
        return self.filter(status=TaskStatus.COMPLETED)

    def pending(self):
        """Filter active tasks that are not yet completed."""
        return self.exclude(status=TaskStatus.COMPLETED)

    def overdue(self):
        """
        Filter tasks whose due date has passed and are not completed.
        """
        return self.filter(
            due_date__lt=timezone.now().date()
        ).exclude(status=TaskStatus.COMPLETED)
