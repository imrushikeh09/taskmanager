from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from projects.models import Project
from tasks.models import Task
from attachments.models import TaskAttachment

User = get_user_model()


class TaskAttachmentAPITests(APITestCase):
    """
    Integration tests for Task Attachments API:
    Upload, file validation, filtering, and deletion.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="uploader_user", password="password123")
        self.project = Project.objects.create(name="Attachment Project", owner=self.user)
        self.task = Task.objects.create(title="Task with Attachments", project=self.project, creator=self.user)
        self.url = reverse("attachment-list")

    def test_upload_attachment_success(self):
        """User can upload a valid file attachment linked to a task."""
        self.client.force_authenticate(user=self.user)
        file_payload = SimpleUploadedFile(
            "requirements_spec.pdf",
            b"Dummy PDF binary content for testing.",
            content_type="application/pdf",
        )
        response = self.client.post(
            self.url,
            {"task": self.task.id, "file": file_payload},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["file_name"], "requirements_spec.pdf")
        self.assertEqual(response.data["task"], self.task.id)
        self.assertEqual(response.data["uploader"], self.user.id)
        self.assertTrue(TaskAttachment.objects.filter(id=response.data["id"]).exists())

    def test_upload_disallowed_extension_fails(self):
        """Uploading dangerous file formats (.exe) is rejected with 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        bad_file = SimpleUploadedFile("malware.exe", b"malicious payload", content_type="application/octet-stream")
        response = self.client.post(
            self.url,
            {"task": self.task.id, "file": bad_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_list_and_filter_attachments_by_task(self):
        """Client can query attachments filtered by ?task=<id>."""
        self.client.force_authenticate(user=self.user)
        att = TaskAttachment.objects.create(
            task=self.task,
            uploader=self.user,
            file_name="screenshot.png",
            file_url="/media/attachments/screenshot.png",
            file_size_bytes=1024,
        )
        response = self.client.get(f"{self.url}?task={self.task.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], att.id)

    def test_delete_attachment(self):
        """User can delete an existing task attachment."""
        self.client.force_authenticate(user=self.user)
        att = TaskAttachment.objects.create(
            task=self.task,
            uploader=self.user,
            file_name="delete_me.txt",
            file_url="/media/attachments/delete_me.txt",
            file_size_bytes=50,
        )
        detail_url = reverse("attachment-detail", kwargs={"pk": att.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaskAttachment.objects.filter(id=att.id).exists())

    def test_unauthenticated_upload_blocked(self):
        """Anonymous client cannot upload attachments."""
        file_payload = SimpleUploadedFile("doc.pdf", b"content", content_type="application/pdf")
        response = self.client.post(self.url, {"task": self.task.id, "file": file_payload}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
