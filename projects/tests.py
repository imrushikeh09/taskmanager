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
