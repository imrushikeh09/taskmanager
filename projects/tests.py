from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from projects.models import Project
from projects.services import ProjectService
from tasks.models import Task
from tasks.choices import TaskStatus, TaskPriority

User = get_user_model()


class ProjectServiceTestCase(TestCase):
    """
    Automated tests for ProjectService, SQL aggregation metrics, and constraints.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="project_lead", password="secure_pass123")

    def test_create_project_service(self):
        """Verify ProjectService creates a project cleanly."""
        project = ProjectService.create_project(
            owner=self.user,
            name="Cloud Migration",
            description="Migrating legacy services to containers",
        )
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.name, "Cloud Migration")

    def test_unique_project_owner_name_constraint(self):
        """Verify database enforces unique project names per owner."""
        Project.objects.create(owner=self.user, name="Duplicate Name")
        with self.assertRaises(IntegrityError):
            Project.objects.create(owner=self.user, name="Duplicate Name")

    def test_get_project_statistics_aggregation(self):
        """
        Verify SQL aggregation returns accurate task counts by status and priority
        without loading all task instances into Python memory.
        """
        project = Project.objects.create(owner=self.user, name="Metrics Project")

        # Create 3 tasks with different statuses
        Task.objects.create(project=project, creator=self.user, title="Task 1", status=TaskStatus.TODO, priority=TaskPriority.HIGH)
        Task.objects.create(project=project, creator=self.user, title="Task 2", status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)
        Task.objects.create(project=project, creator=self.user, title="Task 3", status=TaskStatus.COMPLETED, priority=TaskPriority.MEDIUM)

        stats = ProjectService.get_project_statistics(project.id)
        self.assertIsNotNone(stats)
        self.assertEqual(stats["total_tasks"], 3)
        self.assertEqual(stats["by_status"].get(TaskStatus.TODO), 1)
        self.assertEqual(stats["by_status"].get(TaskStatus.IN_PROGRESS), 1)
        self.assertEqual(stats["by_status"].get(TaskStatus.COMPLETED), 1)
        self.assertEqual(stats["by_priority"].get(TaskPriority.HIGH), 2)
        self.assertEqual(stats["by_priority"].get(TaskPriority.MEDIUM), 1)


from rest_framework.test import APIClient
from rest_framework import status


class ProjectViewSetTestCase(TestCase):
    """
    Integration tests for ProjectViewSet endpoints and /projects/{id}/stats/ action.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="lead_dev", password="secure_pass123")
        self.project = Project.objects.create(owner=self.user, name="Infrastructure Setup")
        Task.objects.create(project=self.project, creator=self.user, title="Task A", status=TaskStatus.TODO)
        Task.objects.create(project=self.project, creator=self.user, title="Task B", status=TaskStatus.COMPLETED)

    def test_list_projects(self):
        """GET /api/v1/projects/ returns paginated project list."""
        response = self.client.get("/api/v1/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "Infrastructure Setup")

    def test_project_stats_custom_action(self):
        """GET /api/v1/projects/<id>/stats/ returns calculated task metrics."""
        response = self.client.get(f"/api/v1/projects/{self.project.id}/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["project_id"], self.project.id)
        self.assertEqual(data["total_tasks"], 2)
        self.assertEqual(data["by_status"].get(TaskStatus.TODO), 1)
        self.assertEqual(data["by_status"].get(TaskStatus.COMPLETED), 1)

    def test_create_project_unauthenticated_fails(self):
        """POST /api/v1/projects/ without auth returns 401 Unauthorized."""
        payload = {"name": "Unauthorized Project", "description": "Should fail"}
        response = self.client.post("/api/v1/projects/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_authenticated(self):
        """POST /api/v1/projects/ with authenticated user assigns owner automatically."""
        self.client.force_authenticate(user=self.user)
        payload = {"name": "New Microservice", "description": "Auth test project"}
        response = self.client.post("/api/v1/projects/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner_username"], self.user.username)

    def test_update_project_non_owner_forbidden(self):
        """PATCH /api/v1/projects/<id>/ by non-owner returns 403 Forbidden."""
        other_user = User.objects.create_user(username="intruder", password="password123")
        self.client.force_authenticate(user=other_user)
        payload = {"name": "Hijacked Project"}
        response = self.client.patch(f"/api/v1/projects/{self.project.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_owner_success(self):
        """PATCH /api/v1/projects/<id>/ by owner succeeds with 200 OK."""
        self.client.force_authenticate(user=self.user)
        payload = {"name": "Updated Setup"}
        response = self.client.patch(f"/api/v1/projects/{self.project.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Updated Setup")

    def test_list_projects_query_count_is_constant(self):
        """
        Verify that GET /api/v1/projects/ executes strictly 2 queries (COUNT and eager-loaded page)
        regardless of whether there are 1 or 15 projects in the database.
        Guarantees O(1) query complexity and prevents N+1 regression on owner lookup.
        """
        for i in range(14):
            u = User.objects.create_user(username=f"owner_{i}", password="password123")
            Project.objects.create(owner=u, name=f"Project {i}")

        self.client.force_authenticate(user=self.user)
        with self.assertNumQueries(2):
            response = self.client.get("/api/v1/projects/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 15)

    def test_project_stats_query_count_is_constant(self):
        """
        Verify that GET /api/v1/projects/<id>/stats/ executes exactly 2 queries:
        1 query for Project lookup and 1 single-pass conditional aggregation across 50 tasks.
        Guarantees O(1) query complexity.
        """
        tasks = [
            Task(
                project=self.project,
                creator=self.user,
                title=f"Bulk Task {i}",
                status=TaskStatus.TODO if i % 2 == 0 else TaskStatus.COMPLETED,
                priority=TaskPriority.HIGH if i % 3 == 0 else TaskPriority.MEDIUM,
            )
            for i in range(50)
        ]
        Task.objects.bulk_create(tasks)

        self.client.force_authenticate(user=self.user)
        with self.assertNumQueries(2):
            response = self.client.get(f"/api/v1/projects/{self.project.id}/stats/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["total_tasks"], 52)  # 2 from setUp + 50 bulk

