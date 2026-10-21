import logging
from celery import shared_task
from django.core.cache import cache
from .models import Task, Notification
from .choices import NotificationType

logger = logging.getLogger("taskmanager")


@shared_task(bind=True, max_retries=3)
def send_task_assigned_notification(self, task_id: int):
    """
    Asynchronously creates an in-app notification when a task is assigned to a user.

    Features:
    - Redis Cache-backed idempotency check to avoid duplicate notifications.
    - Exponential backoff retry on transient failures (1s, 2s, 4s).
    - Structured error logging.
    """
    try:
        task = Task.objects.select_related("assignee", "creator", "project").get(id=task_id)
    except Task.DoesNotExist:
        logger.error(
            "Task id=%s does not exist; cannot dispatch task assignment notification",
            task_id,
        )
        return None
    except Exception as exc:
        delay = 2 ** self.request.retries
        logger.warning(
            "Transient error processing assignment notification for task %s: %s. Retrying in %ds (attempt %d/3)...",
            task_id,
            exc,
            delay,
            self.request.retries + 1,
        )
        raise self.retry(exc=exc, countdown=delay)

    if not task.assignee:
        logger.info("Task id=%s has no assignee; skipping notification creation", task_id)
        return None

    # Idempotency fence: atomic SETNX via cache.add
    idempotency_key = f"notif:task_assigned:{task_id}:{task.assignee_id}"
    if not cache.add(idempotency_key, "1", timeout=86400):
        logger.info(
            "Idempotency hit: assignment notification for task=%s assignee=%s already sent. Skipping duplicate.",
            task_id,
            task.assignee_id,
        )
        return "skipped_duplicate"

    notification = Notification.objects.create(
        recipient=task.assignee,
        task=task,
        notification_type=NotificationType.TASK_ASSIGNED,
        message=f"You have been assigned to task '{task.title}' in project '{task.project.name}'.",
    )
    logger.info(
        "Created in-app notification id=%s for assignee user=%s on task=%s",
        notification.id,
        task.assignee_id,
        task.id,
    )
    return notification.id


@shared_task(bind=True, max_retries=3)
def send_task_status_changed_notification(self, task_id: int, old_status: str, new_status: str):
    """
    Asynchronously creates an in-app notification when a task's status changes.

    Features:
    - Redis Cache-backed idempotency check scoped by transition state.
    - Exponential backoff retry on transient errors.
    - Notifies the task creator about milestone progress.
    """
    try:
        task = Task.objects.select_related("creator", "assignee", "project").get(id=task_id)
    except Task.DoesNotExist:
        logger.error(
            "Task id=%s does not exist; cannot dispatch status notification",
            task_id,
        )
        return None
    except Exception as exc:
        delay = 2 ** self.request.retries
        logger.warning(
            "Transient error processing status notification for task %s: %s. Retrying in %ds (attempt %d/3)...",
            task_id,
            exc,
            delay,
            self.request.retries + 1,
        )
        raise self.retry(exc=exc, countdown=delay)

    # Idempotency fence
    idempotency_key = f"notif:task_status:{task_id}:{old_status}:{new_status}"
    if not cache.add(idempotency_key, "1", timeout=86400):
        logger.info(
            "Idempotency hit: status notification for key '%s' already sent. Skipping duplicate.",
            idempotency_key,
        )
        return "skipped_duplicate"

    recipient = task.creator
    if not recipient:
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        task=task,
        notification_type=NotificationType.STATUS_CHANGED,
        message=f"Task '{task.title}' status changed from {old_status} to {new_status}.",
    )
    logger.info(
        "Created in-app status notification id=%s for creator user=%s on task=%s",
        notification.id,
        recipient.id,
        task.id,
    )
    return notification.id
