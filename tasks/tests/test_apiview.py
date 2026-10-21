from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from projects.models import Project
from tasks.models import Task
from tasks.services import TaskService

User = get_user_model()


class TaskAPIViewTestCase(TestCase):
    """
    Integration tests for TaskListCreateAPIView and TaskDetailAPIView.
    Validates HTTP status codes, standard JSON envelopes, and error handling.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_user", password="secure_pass123")
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(name="API Project", owner=self.user)
        self.task = TaskService.create_task(
            project=self.project,
            creator=self.user,
            assignee=self.user,
            title="Initial API Task",
            description="Testing endpoint flow",
        )

    def test_post_task_unauthenticated_fails(self):
        """POST /api/v1/tasks/apiview/ without auth returns 401 Unauthorized."""
        self.client.force_authenticate(user=None)
        payload = {"title": "Unauth Task", "project_id": self.project.id}
        response = self.client.post("/api/v1/tasks/apiview/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_task_list(self):
        """GET /api/v1/tasks/apiview/ returns 200 with standard envelope."""
        response = self.client.get("/api/v1/tasks/apiview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["title"], "Initial API Task")
        self.assertEqual(data["data"][0]["project_name"], "API Project")

    def test_post_task_success(self):
        """POST /api/v1/tasks/apiview/ creates a task and returns 201 Created."""
        payload = {
            "title": "Created via APIView",
            "description": "Explicit request handling test",
            "project_id": self.project.id,
            "status": "TODO",
            "priority": "HIGH",
        }
        response = self.client.post("/api/v1/tasks/apiview/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["title"], "Created via APIView")
        self.assertEqual(data["data"]["priority"], "HIGH")

    def test_post_task_validation_failure(self):
        """POST /api/v1/tasks/apiview/ with invalid data returns 400 with standard error envelope."""
        payload = {
            "title": "ab",  # Too short (min_length=3)
            "project_id": 999999,  # Non-existent project
        }
        response = self.client.post("/api/v1/tasks/apiview/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("title", data["error"]["details"])
        self.assertIn("project_id", data["error"]["details"])

    def test_get_task_detail_success(self):
        """GET /api/v1/tasks/apiview/<id>/ returns 200 OK."""
        response = self.client.get(f"/api/v1/tasks/apiview/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["data"]["id"], self.task.id)

    def test_get_task_detail_not_found(self):
        """GET /api/v1/tasks/apiview/99999/ returns 404 Not Found."""
        response = self.client.get("/api/v1/tasks/apiview/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data["error"]["code"], "NOT_FOUND")

    def test_patch_task_partial_update(self):
        """PATCH /api/v1/tasks/apiview/<id>/ partially updates status and returns 200 OK."""
        payload = {"status": "IN_PROGRESS"}
        response = self.client.patch(f"/api/v1/tasks/apiview/{self.task.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["data"]["status"], "IN_PROGRESS")

    def test_delete_task_success(self):
        """DELETE /api/v1/tasks/apiview/<id>/ returns 204 No Content."""
        response = self.client.delete(f"/api/v1/tasks/apiview/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
