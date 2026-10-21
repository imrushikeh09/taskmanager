from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus, TaskPriority
from tasks.services import TaskService

User = get_user_model()


class TaskArchitectureTestCase(TestCase):
    """
    Automated tests verifying the Senior Backend Architecture:
    Services, QuerySets, Choices, and Domain Validation.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="secure_pass123")
        self.other_user = User.objects.create_user(username="bob", password="secure_pass123")
        self.project = Project.objects.create(
            name="Architecture Testing",
            description="Testing enterprise patterns",
            owner=self.user,
        )

    def test_service_create_task_success(self):
        """Verify TaskService creates a task successfully with default status."""
        task = TaskService.create_task(
            project=self.project,
            creator=self.user,
            assignee=self.user,
            title="Write clean service layer",
            due_date=timezone.now().date() + timedelta(days=3),
        )
        self.assertEqual(task.status, TaskStatus.TODO)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.creator, self.user)

    def test_service_create_task_rejects_past_due_date(self):
        """Verify domain rule: due date cannot be set in the past."""
        past_date = timezone.now().date() - timedelta(days=1)
        with self.assertRaises(ValidationError) as ctx:
            TaskService.create_task(
                project=self.project,
                creator=self.user,
                title="Invalid task",
                due_date=past_date,
            )
        self.assertIn("due_date", ctx.exception.message_dict)

    def test_service_update_task_status_validation(self):
        """Verify TaskService enforces valid status transitions."""
        task = TaskService.create_task(
            project=self.project,
            creator=self.user,
            title="Status test",
        )
        # Success update
        updated = TaskService.update_task_status(task=task, new_status=TaskStatus.IN_PROGRESS)
        self.assertEqual(updated.status, TaskStatus.IN_PROGRESS)

        # Invalid status rejected
        with self.assertRaises(ValidationError):
            TaskService.update_task_status(task=task, new_status="NON_EXISTENT_STATUS")

    def test_queryset_for_user(self):
        """Verify TaskQuerySet.for_user scopes tasks accurately."""
        task1 = TaskService.create_task(project=self.project, creator=self.user, assignee=self.user, title="Task 1")
        task2 = TaskService.create_task(project=self.project, creator=self.user, assignee=self.other_user, title="Task 2")

        # Project belongs to self.user, so for_user returns both
        user_tasks = Task.objects.for_user(self.user)
        self.assertEqual(user_tasks.count(), 2)

        # Bob is only assignee on task2
        bob_tasks = Task.objects.for_user(self.other_user)
        self.assertEqual(bob_tasks.count(), 1)
        self.assertEqual(bob_tasks.first().id, task2.id)

    def test_queryset_overdue(self):
        """Verify TaskQuerySet.overdue catches only uncompleted overdue tasks."""
        # Task with future due date (not overdue)
        Task.objects.create(
            project=self.project,
            creator=self.user,
            title="Future task",
            due_date=timezone.now().date() + timedelta(days=2),
        )
        # Task with past due date but completed (not overdue)
        Task.objects.create(
            project=self.project,
            creator=self.user,
            title="Completed past task",
            status=TaskStatus.COMPLETED,
            due_date=timezone.now().date() - timedelta(days=2),
        )
        # Task with past due date and in progress (OVERDUE)
        overdue_task = Task.objects.create(
            project=self.project,
            creator=self.user,
            title="Real overdue task",
            status=TaskStatus.IN_PROGRESS,
            due_date=timezone.now().date() - timedelta(days=2),
        )

        overdue_qs = Task.objects.overdue()
        self.assertEqual(overdue_qs.count(), 1)
        self.assertEqual(overdue_qs.first().id, overdue_task.id)

    def test_queryset_with_related_prevents_n_plus_one(self):
        """
        Verify that with_related() executes exactly ONE SQL query
        instead of multiple queries for project, creator, and assignee.
        """
        TaskService.create_task(project=self.project, creator=self.user, assignee=self.user, title="Query test 1")
        TaskService.create_task(project=self.project, creator=self.user, assignee=self.other_user, title="Query test 2")

        # Using with_related(): 1 single SQL query with JOINs
        with self.assertNumQueries(1):
            tasks = list(Task.objects.with_related())
            for task in tasks:
                # Accessing related objects does NOT trigger additional DB queries!
                _ = task.project.name
                _ = task.creator.username
                _ = task.assignee.username if task.assignee else None
