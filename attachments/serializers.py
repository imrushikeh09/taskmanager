import os
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import serializers
from .models import TaskAttachment


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif",
    ".txt", ".csv", ".docx", ".xlsx", ".zip",
}


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading and retrieving task attachment files.
    Validates file sizes, mime extensions, and links to target tasks.
    """
    file = serializers.FileField(
        write_only=True,
        required=True,
        help_text="File payload to upload (Max size: 10MB)",
    )
    task_title = serializers.CharField(source="task.title", read_only=True)
    uploader_username = serializers.CharField(source="uploader.username", read_only=True)

    class Meta:
        model = TaskAttachment
        fields = [
            "id",
            "task",
            "task_title",
            "uploader",
            "uploader_username",
            "file",
            "file_name",
            "file_url",
            "file_size_bytes",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "task_title",
            "uploader",
            "uploader_username",
            "file_name",
            "file_url",
            "file_size_bytes",
            "uploaded_at",
        ]

    def validate_file(self, value):
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds the 10 MB limit ({value.size} bytes provided)."
            )
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed_str = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise serializers.ValidationError(
                f"Unsupported file extension '{ext}'. Allowed extensions: {allowed_str}"
            )
        return value

    def create(self, validated_data):
        uploaded_file = validated_data.pop("file")
        task = validated_data.get("task")
        user = self.context["request"].user

        # Save file to storage under attachments/task_<id>/<file>
        file_path = default_storage.save(f"attachments/task_{task.id}/{uploaded_file.name}", uploaded_file)
        file_url = f"{settings.MEDIA_URL}{file_path}"

        return TaskAttachment.objects.create(
            task=task,
            uploader=user,
            file_name=uploaded_file.name,
            file_url=file_url,
            file_size_bytes=uploaded_file.size,
        )
