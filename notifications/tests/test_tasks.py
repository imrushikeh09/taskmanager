from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus
from notifications.models import Notification
from notifications.choices import NotificationType
from notifications.tasks import (
    send_task_assigned_notification,
    send_task_status_changed_notification,
)

User = get_user_model()


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
        cache.clear()

    def test_send_task_assigned_notification_creates_db_record(self):
        """Task assignment async job creates an in-app notification in PostgreSQL."""
        result = send_task_assigned_notification(self.task.id)
        self.assertIsNotNone(result)

        notif = Notification.objects.filter(recipient=self.assignee, task=self.task).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.notification_type, NotificationType.TASK_ASSIGNED)
        self.assertIn("You have been assigned to task", notif.message)
        self.assertFalse(notif.is_read)

    def test_send_task_assigned_notification_idempotency_fence(self):
        """Executing the assignment task multiple times produces only 1 notification (idempotent)."""
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
        result = send_task_assigned_notification(999999)
        self.assertIsNone(result)

    def test_send_task_assigned_notification_unassigned_task_skipped(self):
        """Task without assignee gracefully skips notification creation."""
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
        result = send_task_status_changed_notification(self.task.id, "TODO", "COMPLETED")
        self.assertIsNotNone(result)

        notif = Notification.objects.filter(recipient=self.creator, task=self.task).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.notification_type, NotificationType.STATUS_CHANGED)
        self.assertIn("status changed from TODO to COMPLETED", notif.message)

    def test_send_task_status_changed_idempotency(self):
        """Submitting the exact same status transition twice triggers idempotency skip."""
        first_res = send_task_status_changed_notification(self.task.id, "TODO", "IN_PROGRESS")
        self.assertIsInstance(first_res, int)

        second_res = send_task_status_changed_notification(self.task.id, "TODO", "IN_PROGRESS")
        self.assertEqual(second_res, "skipped_duplicate")

        count = Notification.objects.filter(recipient=self.creator, task=self.task).count()
        self.assertEqual(count, 1)

    def test_task_exponential_backoff_retry_on_transient_error(self):
        """Verify exponential backoff retry mechanism is called on transient exceptions."""
        with patch.object(send_task_assigned_notification, "retry", side_effect=RuntimeError("Retry triggered")) as mock_retry:
            with patch("tasks.models.Task.objects.select_related") as mock_qs:
                mock_qs.return_value.get.side_effect = Exception("DB Connection Lost")
                with self.assertRaises(RuntimeError):
                    send_task_assigned_notification(self.task.id)

                mock_retry.assert_called_once()
                _, kwargs = mock_retry.call_args
                # default request.retries is 0 -> 2 ** 0 = 1
                self.assertEqual(kwargs.get("countdown"), 1)
