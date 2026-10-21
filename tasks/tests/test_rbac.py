from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status

from common.roles import UserRole
from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus
from tasks.services import TaskService

User = get_user_model()


class RBACTestCase(TestCase):
    """
    Automated integration tests for 3-Tier Role-Based Access Control (RBAC):
    - Viewer: Read-only access across all resources; write operations return 403 Forbidden.
    - Contributor: Can create tasks/projects and modify only own resources.
    - Admin: Superuser / Staff with full override permissions across all resources.
    """

    def setUp(self):
        self.client = APIClient()

        # Create Django Groups for RBAC
        self.viewer_group = Group.objects.create(name=UserRole.VIEWER)
        self.admin_group = Group.objects.create(name=UserRole.ADMIN)

        # Users
        self.viewer_user = User.objects.create_user(username="viewer_user", password="secure_pass123")
        self.viewer_user.groups.add(self.viewer_group)

        self.contributor_user = User.objects.create_user(username="contributor_user", password="secure_pass123")
        self.other_contributor = User.objects.create_user(username="other_contributor", password="secure_pass123")

        self.admin_user = User.objects.create_user(username="admin_user", password="secure_pass123", is_staff=True)

        # Contributor creates a Project and Task
        self.project = Project.objects.create(name="Contributor Project", owner=self.contributor_user)
        self.task = TaskService.create_task(
            project=self.project,
            creator=self.contributor_user,
            title="Contributor Task",
            status=TaskStatus.TODO,
        )

    def test_viewer_can_read_projects_and_tasks(self):
        """Viewer role can perform GET operations (200 OK)."""
        self.client.force_authenticate(user=self.viewer_user)
        res_projects = self.client.get("/api/v1/projects/")
        self.assertEqual(res_projects.status_code, status.HTTP_200_OK)

        res_tasks = self.client.get("/api/v1/tasks/")
        self.assertEqual(res_tasks.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create_project_or_task(self):
        """Viewer role is blocked from POST operations with 403 Forbidden."""
        self.client.force_authenticate(user=self.viewer_user)

        res_proj = self.client.post("/api/v1/projects/", {"name": "Viewer Proj"}, format="json")
        self.assertEqual(res_proj.status_code, status.HTTP_403_FORBIDDEN)

        res_task = self.client.post(
            "/api/v1/tasks/",
            {"title": "Viewer Task", "project_id": self.project.id},
            format="json",
        )
        self.assertEqual(res_task.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_update_or_delete_task(self):
        """Viewer role is blocked from PATCH/DELETE operations with 403 Forbidden."""
        self.client.force_authenticate(user=self.viewer_user)

        res_patch = self.client.patch(f"/api/v1/tasks/{self.task.id}/", {"title": "Hacked"}, format="json")
        self.assertEqual(res_patch.status_code, status.HTTP_403_FORBIDDEN)

        res_del = self.client.delete(f"/api/v1/tasks/{self.task.id}/")
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

    def test_contributor_can_update_own_task(self):
        """Contributor can modify their own task (200 OK)."""
        self.client.force_authenticate(user=self.contributor_user)
        response = self.client.patch(f"/api/v1/tasks/{self.task.id}/", {"title": "Updated by Owner"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Updated by Owner")

    def test_contributor_cannot_update_other_user_task(self):
        """Contributor cannot modify another user's task (403 Forbidden)."""
        self.client.force_authenticate(user=self.other_contributor)
        response = self.client.patch(f"/api/v1/tasks/{self.task.id}/", {"title": "Unauthorized"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_user_task(self):
        """Admin has master override to update any user's task (200 OK)."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/api/v1/tasks/{self.task.id}/",
            {"title": "Updated by Admin Superuser"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Updated by Admin Superuser")

    def test_admin_can_delete_any_user_project(self):
        """Admin has master override to delete any user's project (204 No Content)."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/api/v1/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())
