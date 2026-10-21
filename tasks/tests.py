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


from rest_framework.test import APIClient
from rest_framework import status


class TaskAPIViewTestCase(TestCase):
    """
    Integration tests for TaskListCreateAPIView and TaskDetailAPIView.
    Validates HTTP status codes, standard JSON envelopes, and error handling.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_user", password="secure_pass123")
        self.project = Project.objects.create(name="API Project", owner=self.user)
        self.task = TaskService.create_task(
            project=self.project,
            creator=self.user,
            assignee=self.user,
            title="Initial API Task",
            description="Testing endpoint flow",
        )

    def test_get_task_list(self):
        """GET /api/v1/tasks/ returns 200 with standard envelope."""
        response = self.client.get("/api/v1/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["title"], "Initial API Task")
        self.assertEqual(data["data"][0]["project_name"], "API Project")

    def test_post_task_success(self):
        """POST /api/v1/tasks/ creates a task and returns 201 Created."""
        payload = {
            "title": "Created via APIView",
            "description": "Explicit request handling test",
            "project_id": self.project.id,
            "status": "TODO",
            "priority": "HIGH",
        }
        response = self.client.post("/api/v1/tasks/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["title"], "Created via APIView")
        self.assertEqual(data["data"]["priority"], "HIGH")

    def test_post_task_validation_failure(self):
        """POST /api/v1/tasks/ with invalid data returns 400 with standard error envelope."""
        payload = {
            "title": "ab",  # Too short (min_length=3)
            "project_id": 999999,  # Non-existent project
        }
        response = self.client.post("/api/v1/tasks/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("title", data["error"]["details"])
        self.assertIn("project_id", data["error"]["details"])

    def test_get_task_detail_success(self):
        """GET /api/v1/tasks/<id>/ returns 200 OK."""
        response = self.client.get(f"/api/v1/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["data"]["id"], self.task.id)

    def test_get_task_detail_not_found(self):
        """GET /api/v1/tasks/99999/ returns 404 Not Found."""
        response = self.client.get("/api/v1/tasks/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_patch_task_partial_update(self):
        """PATCH /api/v1/tasks/<id>/ partially updates status and returns 200 OK."""
        payload = {"status": "IN_PROGRESS"}
        response = self.client.patch(f"/api/v1/tasks/{self.task.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["data"]["status"], "IN_PROGRESS")

    def test_delete_task_success(self):
        """DELETE /api/v1/tasks/<id>/ returns 204 No Content."""
        response = self.client.delete(f"/api/v1/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

