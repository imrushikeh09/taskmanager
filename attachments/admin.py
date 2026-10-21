from django.contrib import admin
from .models import TaskAttachment


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "task", "uploader", "file_size_bytes", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("file_name", "task__title", "uploader__username")
    readonly_fields = ("uploaded_at",)
