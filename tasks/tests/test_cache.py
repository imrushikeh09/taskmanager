from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status

from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus, TaskPriority
from tasks.services import TaskService
from tasks.cache import get_performance_report_cache_key

User = get_user_model()


class RedisCachingTestCase(TestCase):
    """
    Automated integration tests for Redis Caching:
    - Cache-Aside Pattern (miss -> calculate -> cache, hit -> 0 SQL queries)
    - Proactive cache invalidation on task write paths
    - Performance report HTTP endpoint caching
    """

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username="cache_tester", password="secure_pass123")
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(name="Cached Project", owner=self.user)
        self.task1 = TaskService.create_task(
            project=self.project,
            creator=self.user,
            title="Task Alpha",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
        )
        self.task2 = TaskService.create_task(
            project=self.project,
            creator=self.user,
            title="Task Beta",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
        )

    def tearDown(self):
        cache.clear()

    def test_cache_aside_miss_then_hit_zero_queries(self):
        """
        First call (Cache Miss): executes DB query and caches result in Redis.
        Second call (Cache Hit): executes strictly 0 SQL queries.
        """
        cache_key = get_performance_report_cache_key(self.project.id)
        self.assertIsNone(cache.get(cache_key))

        # 1st Call: Cache Miss
        report_1 = TaskService.get_heavy_performance_report(self.project.id)
        self.assertIsNotNone(report_1)
        self.assertEqual(report_1["total_tasks"], 2)
        self.assertEqual(report_1["completed_tasks"], 1)

        # Key should now exist in Redis
        self.assertIsNotNone(cache.get(cache_key))

        # 2nd Call: Cache Hit (Zero SQL queries!)
        with self.assertNumQueries(0):
            report_2 = TaskService.get_heavy_performance_report(self.project.id)
            self.assertEqual(report_2["total_tasks"], 2)
            self.assertEqual(report_2["completed_tasks"], 1)

    def test_cache_invalidation_on_task_create(self):
        """Creating a task invalidates the cached report."""
        TaskService.get_heavy_performance_report(self.project.id)
        cache_key = get_performance_report_cache_key(self.project.id)
        self.assertIsNotNone(cache.get(cache_key))

        # Create a new task
        TaskService.create_task(
            project=self.project,
            creator=self.user,
            title="Task Gamma",
            status=TaskStatus.TODO,
        )

        # Cache must be invalidated
        self.assertIsNone(cache.get(cache_key))

        # Subsequent call recalculates fresh data (3 tasks)
        fresh_report = TaskService.get_heavy_performance_report(self.project.id)
        self.assertEqual(fresh_report["total_tasks"], 3)

    def test_cache_invalidation_on_task_status_update(self):
        """Updating task status invalidates cached performance report."""
        TaskService.get_heavy_performance_report(self.project.id)
        cache_key = get_performance_report_cache_key(self.project.id)
        self.assertIsNotNone(cache.get(cache_key))

        # Mark Task Alpha as COMPLETED
        TaskService.update_task_status(task=self.task1, new_status=TaskStatus.COMPLETED)

        # Cache must be purged
        self.assertIsNone(cache.get(cache_key))

        # Recalculates: completed_tasks is now 2
        fresh_report = TaskService.get_heavy_performance_report(self.project.id)
        self.assertEqual(fresh_report["completed_tasks"], 2)

    def test_api_performance_report_endpoint_cache_hit(self):
        """GET /api/v1/projects/<id>/performance-report/ uses cache on repeated calls."""
        res1 = self.client.get(f"/api/v1/projects/{self.project.id}/performance-report/")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.json()["total_tasks"], 2)

        # Second request (Cache Hit: 0 database queries)
        with self.assertNumQueries(0):
            res2 = self.client.get(f"/api/v1/projects/{self.project.id}/performance-report/")
            self.assertEqual(res2.status_code, status.HTTP_200_OK)
            self.assertEqual(res2.json()["total_tasks"], 2)
