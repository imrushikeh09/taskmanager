from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Task
from .choices import TaskStatus, TaskPriority


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
        return task

    @classmethod
    @transaction.atomic
    def update_task_status(cls, *, task: Task, new_status: str):
        """
        Update the status of a task with domain validation.
        """
        if new_status not in TaskStatus.values:
            raise ValidationError({"status": f"Invalid status '{new_status}'. Allowed: {TaskStatus.values}"})

        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
        return task

    @classmethod
    @transaction.atomic
    def assign_task(cls, *, task: Task, assignee):
        """
        Assign or reassign a task to a user.
        """
        if assignee and not assignee.is_active:
            raise ValidationError({"assignee": "Cannot assign task to an inactive user account."})

        task.assignee = assignee
        task.save(update_fields=["assignee", "updated_at"])
        return task
