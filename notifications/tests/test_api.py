from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from projects.models import Project
from tasks.models import Task
from notifications.models import Notification
from notifications.choices import NotificationType

User = get_user_model()


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
