from django.contrib import admin
from .models import Task
from attachments.models import TaskAttachment


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ("uploaded_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "status", "priority", "assignee", "due_date", "created_at")
    list_filter = ("status", "priority", "project", "due_date")
    search_fields = ("title", "description", "project__name", "assignee__username", "creator__username")
    autocomplete_fields = ("project", "creator", "assignee")
    readonly_fields = ("created_at", "updated_at")
    inlines = [TaskAttachmentInline]
