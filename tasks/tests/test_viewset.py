from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus, TaskPriority
from tasks.services import TaskService

User = get_user_model()


class TaskViewSetTestCase(TestCase):
    """
    Integration tests for TaskViewSet:
    Verifies ModelViewSet with Pagination, Filtering, Search, and Ordering.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="viewset_user", password="secure_pass123")
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(name="ViewSet Project", owner=self.user)
        self.task1 = TaskService.create_task(
            project=self.project,
            creator=self.user,
            assignee=self.user,
            title="Alpha Task",
            description="First task description",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
        )
        self.task2 = TaskService.create_task(
            project=self.project,
            creator=self.user,
            assignee=self.user,
            title="Beta Task",
            description="Second task description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
        )

    def test_viewset_list_pagination(self):
        """GET /api/v1/tasks/ returns paginated response with count and results."""
        response = self.client.get("/api/v1/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 2)

    def test_viewset_filter_by_status(self):
        """GET /api/v1/tasks/?status=IN_PROGRESS filters accurately."""
        response = self.client.get("/api/v1/tasks/?status=IN_PROGRESS")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.task2.id)

    def test_viewset_filter_by_priority(self):
        """GET /api/v1/tasks/?priority=HIGH filters accurately."""
        response = self.client.get("/api/v1/tasks/?priority=HIGH")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["priority"], "HIGH")

    def test_viewset_search(self):
        """GET /api/v1/tasks/?search=Alpha matches title."""
        response = self.client.get("/api/v1/tasks/?search=Alpha")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "Alpha Task")

    def test_viewset_create(self):
        """POST /api/v1/tasks/ creates task through ModelViewSet."""
        payload = {
            "title": "Created via ViewSet",
            "description": "ViewSet test",
            "project_id": self.project.id,
            "status": "TODO",
            "priority": "MEDIUM",
        }
        response = self.client.post("/api/v1/tasks/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], "Created via ViewSet")

    def test_viewset_partial_update(self):
        """PATCH /api/v1/tasks/<id>/ updates task via ModelViewSet."""
        payload = {"status": "COMPLETED"}
        response = self.client.patch(f"/api/v1/tasks/{self.task1.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "COMPLETED")

    def test_viewset_destroy(self):
        """DELETE /api/v1/tasks/<id>/ deletes task via ModelViewSet."""
        response = self.client.delete(f"/api/v1/tasks/{self.task1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_viewset_create_unauthenticated_fails(self):
        """POST /api/v1/tasks/ without auth returns 401 Unauthorized."""
        self.client.force_authenticate(user=None)
        payload = {
            "title": "Unauth Task",
            "project_id": self.project.id,
        }
        response = self.client.post("/api/v1/tasks/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewset_modify_non_owner_forbidden(self):
        """PATCH /api/v1/tasks/<id>/ by non-owner returns 403 Forbidden."""
        other_user = User.objects.create_user(username="random_dev", password="password123")
        self.client.force_authenticate(user=other_user)
        payload = {"title": "Attempted Hack"}
        response = self.client.patch(f"/api/v1/tasks/{self.task1.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewset_list_tasks_query_count_is_constant(self):
        """
        Verify that GET /api/v1/tasks/ executes strictly 2 queries (1 count, 1 eager-loaded page)
        regardless of whether there are 2 or 20 tasks in the database.
        Prevents N+1 regression on project, creator, and assignee lookups.
        """
        extra_tasks = [
            Task(
                project=self.project,
                creator=self.user,
                assignee=self.user,
                title=f"Scalability Task {i}",
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
            )
            for i in range(18)
        ]
        Task.objects.bulk_create(extra_tasks)

        self.client.force_authenticate(user=self.user)
        # Exactly 2 queries: 1 for pagination COUNT, 1 for paginated page with eager JOINs
        with self.assertNumQueries(2):
            response = self.client.get("/api/v1/tasks/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 20)

    def test_viewset_retrieve_task_query_count_is_constant(self):
        """
        Verify that GET /api/v1/tasks/<id>/ executes strictly 1 query
        with eager loading for project, creator, and assignee.
        """
        self.client.force_authenticate(user=self.user)
        with self.assertNumQueries(1):
            response = self.client.get(f"/api/v1/tasks/{self.task1.id}/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["id"], self.task1.id)
