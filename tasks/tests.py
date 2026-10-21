from datetime import timedelta
from django.conf import settings
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


class AuthAndJWTTestCase(TestCase):
    """
    Integration tests for SimpleJWT Authentication:
    - Token generation (/api/v1/auth/token/)
    - Token refresh (/api/v1/auth/token/refresh/)
    - Bearer header authorization on protected resources
    """

    def setUp(self):
        self.client = APIClient()
        self.username = "jwt_tester"
        self.password = "strong_jwt_pass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="jwt_tester@example.com",
        )
        self.project = Project.objects.create(name="JWT Project", owner=self.user)

    def test_token_obtain_pair_success(self):
        """POST /api/v1/auth/token/ with valid credentials returns access and refresh tokens."""
        response = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertTrue(len(data["access"]) > 20)
        self.assertTrue(len(data["refresh"]) > 20)

    def test_token_obtain_pair_invalid_credentials(self):
        """POST /api/v1/auth/token/ with wrong password returns 401 Unauthorized."""
        response = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": "wrong_password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        """POST /api/v1/auth/token/refresh/ with valid refresh token returns fresh access token."""
        obtain_res = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        refresh_token = obtain_res.json()["refresh"]

        refresh_res = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        data = refresh_res.json()
        self.assertIn("access", data)

    def test_bearer_token_authorization_on_endpoints(self):
        """Requesting protected write endpoint with Bearer header authenticates user."""
        obtain_res = self.client.post(
            "/api/v1/auth/token/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        access_token = obtain_res.json()["access"]

        # Authenticate via HTTP Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            "/api/v1/tasks/",
            {
                "title": "JWT Authenticated Task",
                "project_id": self.project.id,
                "status": "TODO",
                "priority": "HIGH",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["creator_username"], self.username)

    def test_rate_throttling_breach_returns_429(self):
        """Rapid unauthenticated requests exceeding throttle limit return 429 Too Many Requests."""
        from unittest.mock import patch
        from rest_framework.throttling import AnonRateThrottle
        from django.core.cache import cache

        cache.clear()
        with patch.object(AnonRateThrottle, "get_rate", return_value="2/min"):
            unauth_client = APIClient()
            r1 = unauth_client.get("/api/v1/projects/")
            self.assertEqual(r1.status_code, status.HTTP_200_OK)

            r2 = unauth_client.get("/api/v1/projects/")
            self.assertEqual(r2.status_code, status.HTTP_200_OK)

            # 3rd request breaches the limit -> 429 Too Many Requests
            r3 = unauth_client.get("/api/v1/projects/")
            self.assertEqual(r3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertIn("detail", r3.json())



from django.core.cache import cache
from tasks.cache import get_performance_report_cache_key, invalidate_performance_cache


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


from django.contrib.auth.models import Group
from common.roles import UserRole


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


class CeleryNotificationTaskTests(TestCase):
    """
    Automated verification of Celery asynchronous background tasks (Day 18):
    - Background task execution and DB notification creation
    - Redis Cache atomic SETNX idempotency fence
    - Exponential backoff retry logic on transient exceptions
    - Safe handling for missing or unassigned records
    """

    def setUp(self):
        self.creator = User.objects.create_user(username="celery_creator", password="password123")
        self.assignee = User.objects.create_user(username="celery_assignee", password="password123")
        self.project = Project.objects.create(name="Celery Project", owner=self.creator)
        self.task = Task.objects.create(
            project=self.project,
            creator=self.creator,
            assignee=self.assignee,
            title="Async worker task",
            status=TaskStatus.TODO,
        )

    def tearDown(self):
        from django.core.cache import cache
        cache.clear()

    def test_send_task_assigned_notification_creates_db_record(self):
        """Task assignment async job creates an in-app notification in PostgreSQL."""
        from tasks.tasks import send_task_assigned_notification
        from tasks.models import Notification
        from tasks.choices import NotificationType

        result = send_task_assigned_notification(self.task.id)
        self.assertIsNotNone(result)

        notif = Notification.objects.filter(recipient=self.assignee, task=self.task).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.notification_type, NotificationType.TASK_ASSIGNED)
        self.assertIn("You have been assigned to task", notif.message)
        self.assertFalse(notif.is_read)

    def test_send_task_assigned_notification_idempotency_fence(self):
        """Executing the assignment task multiple times produces only 1 notification (idempotent)."""
        from tasks.tasks import send_task_assigned_notification
        from tasks.models import Notification

        # First run: should create notification
        first_result = send_task_assigned_notification(self.task.id)
        self.assertIsInstance(first_result, int)

        # Second run: should hit atomic Redis idempotency lock and return skipped_duplicate
        second_result = send_task_assigned_notification(self.task.id)
        self.assertEqual(second_result, "skipped_duplicate")

        # Database must still have only 1 notification
        count = Notification.objects.filter(recipient=self.assignee, task=self.task).count()
        self.assertEqual(count, 1)

    def test_send_task_assigned_notification_missing_task_graceful_exit(self):
        """Non-existent task ID logs an error and returns None without raising an unhandled exception."""
        from tasks.tasks import send_task_assigned_notification
        result = send_task_assigned_notification(999999)
        self.assertIsNone(result)

    def test_send_task_assigned_notification_unassigned_task_skipped(self):
        """Task without assignee gracefully skips notification creation."""
        from tasks.tasks import send_task_assigned_notification
        unassigned_task = Task.objects.create(
            project=self.project,
            creator=self.creator,
            assignee=None,
            title="Unassigned Task",
        )
        result = send_task_assigned_notification(unassigned_task.id)
        self.assertIsNone(result)

    def test_send_task_status_changed_notification_creates_db_record(self):
        """Status change async job notifies creator when status progresses."""
        from tasks.tasks import send_task_status_changed_notification
        from tasks.models import Notification
        from tasks.choices import NotificationType

        result = send_task_status_changed_notification(self.task.id, "TODO", "COMPLETED")
        self.assertIsNotNone(result)

        notif = Notification.objects.filter(recipient=self.creator, task=self.task).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.notification_type, NotificationType.STATUS_CHANGED)
        self.assertIn("status changed from TODO to COMPLETED", notif.message)

    def test_send_task_status_changed_idempotency(self):
        """Submitting the exact same status transition twice triggers idempotency skip."""
        from tasks.tasks import send_task_status_changed_notification
        from tasks.models import Notification

        first_res = send_task_status_changed_notification(self.task.id, "TODO", "IN_PROGRESS")
        self.assertIsInstance(first_res, int)

        second_res = send_task_status_changed_notification(self.task.id, "TODO", "IN_PROGRESS")
        self.assertEqual(second_res, "skipped_duplicate")

        count = Notification.objects.filter(recipient=self.creator, task=self.task).count()
        self.assertEqual(count, 1)

    def test_task_exponential_backoff_retry_on_transient_error(self):
        """Verify exponential backoff retry mechanism is called on transient exceptions."""
        from unittest.mock import patch
        from tasks.tasks import send_task_assigned_notification

        with patch.object(send_task_assigned_notification, "retry", side_effect=RuntimeError("Retry triggered")) as mock_retry:
            with patch("tasks.models.Task.objects.select_related") as mock_qs:
                mock_qs.return_value.get.side_effect = Exception("DB Connection Lost")
                with self.assertRaises(RuntimeError):
                    send_task_assigned_notification(self.task.id)

                mock_retry.assert_called_once()
                _, kwargs = mock_retry.call_args
                # default request.retries is 0 -> 2 ** 0 = 1
                self.assertEqual(kwargs.get("countdown"), 1)



class NotificationAPITests(TestCase):
    """
    Automated integration tests for In-App Notification REST Endpoints:
    - User tenant isolation (users only see their own notifications)
    - Filtering by ?is_read status (leveraging composite index)
    - Read state management (PATCH single, POST bulk read-all)
    - Query efficiency guardrails
    """

    def setUp(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(username="notif_user_a", password="password123")
        self.user_b = User.objects.create_user(username="notif_user_b", password="password123")
        self.project = Project.objects.create(name="Notification Project", owner=self.user_a)
        self.task = Task.objects.create(
            project=self.project,
            creator=self.user_a,
            assignee=self.user_a,
            title="Notification Task",
        )

        from tasks.models import Notification
        from tasks.choices import NotificationType

        # Create notifications for user A (1 unread, 1 read)
        self.notif_a_unread = Notification.objects.create(
            recipient=self.user_a,
            task=self.task,
            notification_type=NotificationType.TASK_ASSIGNED,
            message="Alert 1 for user A",
            is_read=False,
        )
        self.notif_a_read = Notification.objects.create(
            recipient=self.user_a,
            task=self.task,
            notification_type=NotificationType.STATUS_CHANGED,
            message="Alert 2 for user A",
            is_read=True,
        )
        # Create notification for user B
        self.notif_b = Notification.objects.create(
            recipient=self.user_b,
            task=self.task,
            notification_type=NotificationType.TASK_ASSIGNED,
            message="Alert for user B",
            is_read=False,
        )

    def test_unauthenticated_request_rejected(self):
        """Unauthenticated requests to notifications endpoint return 401 Unauthorized."""
        response = self.client.get("/api/v1/notifications/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_list_their_own_notifications(self):
        """Authenticated user only receives notifications addressed to them."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/v1/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 2)
        notif_ids = [item["id"] for item in results]
        self.assertIn(self.notif_a_unread.id, notif_ids)
        self.assertIn(self.notif_a_read.id, notif_ids)
        self.assertNotIn(self.notif_b.id, notif_ids)

    def test_filter_notifications_by_is_read(self):
        """Query param ?is_read=false returns only unread notifications."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/v1/notifications/?is_read=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.notif_a_unread.id)
        self.assertFalse(results[0]["is_read"])

    def test_mark_single_notification_as_read(self):
        """PATCH /api/v1/notifications/{id}/read/ updates is_read to true."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch(f"/api/v1/notifications/{self.notif_a_unread.id}/read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["is_read"])

        self.notif_a_unread.refresh_from_db()
        self.assertTrue(self.notif_a_unread.is_read)

    def test_cannot_read_other_user_notification(self):
        """User cannot access or mark another user's notification as read (404 Not Found)."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.patch(f"/api/v1/notifications/{self.notif_b.id}/read/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_all_notifications_as_read(self):
        """POST /api/v1/notifications/read-all/ marks all unread notifications as read."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post("/api/v1/notifications/read-all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["updated_count"], 1)

        self.notif_a_unread.refresh_from_db()
        self.assertTrue(self.notif_a_unread.is_read)

    def test_notification_list_query_efficiency(self):
        """Notification list query has eager loading and does not produce N+1 queries."""
        self.client.force_authenticate(user=self.user_a)
        with self.assertNumQueries(2):  # 1 count query + 1 select query with select_related
            response = self.client.get("/api/v1/notifications/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)




