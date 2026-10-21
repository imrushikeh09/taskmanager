from rest_framework import status, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from common.views import BaseAPIView
from projects.models import Project
from tasks.models import Task
from tasks.filters import TaskFilter
from tasks.serializers import TaskReadSerializer, TaskWriteSerializer, TaskUpdateSerializer
from tasks.services import TaskService
from django.contrib.auth import get_user_model

User = get_user_model()


@extend_schema(exclude=True)
class TaskListCreateAPIView(BaseAPIView):
    """
    APIView for listing and creating tasks.
    Demonstrates explicit DRF request processing and service delegation.
    """

    @extend_schema(
        summary="List all tasks",
        description="Retrieve tasks using optimized eager loading to avoid N+1 queries.",
        responses={200: TaskReadSerializer(many=True)},
    )
    def get(self, request):
        """List tasks with eager loaded foreign keys."""
        # Using custom QuerySet method to prevent N+1 queries
        tasks = Task.objects.with_related()
        serializer = TaskReadSerializer(tasks, many=True)
        return self.success_response(
            data=serializer.data,
            message="Tasks retrieved successfully.",
        )

    @extend_schema(
        summary="Create a new task",
        description="Validate client payload and delegate task creation to the TaskService layer.",
        request=TaskWriteSerializer,
        responses={
            201: TaskReadSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        """Create a task through the service layer."""
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # Resolve creator (default to first active user or request.user if authenticated)
        creator = request.user if request.user.is_authenticated else User.objects.first()
        project = Project.objects.get(id=validated["project_id"])
        assignee = User.objects.filter(id=validated.get("assignee_id")).first() if validated.get("assignee_id") else None

        # Invoke Domain Service Layer
        task = TaskService.create_task(
            project=project,
            creator=creator,
            assignee=assignee,
            title=validated["title"],
            description=validated.get("description", ""),
            status=validated.get("status"),
            priority=validated.get("priority"),
            due_date=validated.get("due_date"),
        )

        read_serializer = TaskReadSerializer(task)
        return self.success_response(
            data=read_serializer.data,
            status_code=status.HTTP_201_CREATED,
            message="Task created successfully.",
        )


@extend_schema(exclude=True)
class TaskDetailAPIView(BaseAPIView):
    """
    APIView for retrieving, updating, and deleting an individual task.
    """

    def get_object(self, pk):
        """Helper to fetch task with eager loaded relationships or None."""
        return Task.objects.with_related().filter(pk=pk).first()

    @extend_schema(
        summary="Retrieve task details",
        responses={200: TaskReadSerializer, 404: OpenApiResponse(description="Task not found")},
    )
    def get(self, request, pk):
        """Retrieve single task by ID."""
        task = self.get_object(pk)
        if not task:
            return self.error_response(
                message=f"Task with ID {pk} not found.",
                code="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskReadSerializer(task)
        return self.success_response(data=serializer.data)

    @extend_schema(
        summary="Partially update a task",
        request=TaskUpdateSerializer,
        responses={200: TaskReadSerializer, 400: OpenApiResponse(description="Validation error"), 404: OpenApiResponse(description="Task not found")},
    )
    def patch(self, request, pk):
        """Partially modify specified task fields."""
        task = self.get_object(pk)
        if not task:
            return self.error_response(
                message=f"Task with ID {pk} not found.",
                code="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # Update attributes through service or model fields
        if "status" in validated:
            TaskService.update_task_status(task=task, new_status=validated["status"])

        if "assignee_id" in validated:
            assignee = User.objects.filter(id=validated["assignee_id"]).first() if validated["assignee_id"] else None
            TaskService.assign_task(task=task, assignee=assignee)

        if "title" in validated:
            task.title = validated["title"]
        if "description" in validated:
            task.description = validated["description"]
        if "priority" in validated:
            task.priority = validated["priority"]
        if "due_date" in validated:
            TaskService.validate_due_date(validated["due_date"])
            task.due_date = validated["due_date"]

        task.save()
        refreshed_task = self.get_object(pk)
        return self.success_response(
            data=TaskReadSerializer(refreshed_task).data,
            message="Task updated successfully.",
        )

    @extend_schema(
        summary="Delete a task",
        responses={204: OpenApiResponse(description="Task deleted successfully"), 404: OpenApiResponse(description="Task not found")},
    )
    def delete(self, request, pk):
        """Idempotently delete a task."""
        task = self.get_object(pk)
        if not task:
            return self.error_response(
                message=f"Task with ID {pk} not found.",
                code="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        task.delete()
        return self.success_response(
            data=None,
            status_code=status.HTTP_204_NO_CONTENT,
            message="Task deleted successfully.",
        )


@extend_schema_view(
    list=extend_schema(
        summary="List all tasks",
        description="Retrieve a paginated list of tasks with filtering (status, priority, project, dates), full-text search, and ordering.",
        tags=["Tasks"],
    ),
    create=extend_schema(
        summary="Create a new task",
        description="Create a task linked to a project and assignee.",
        tags=["Tasks"],
    ),
    retrieve=extend_schema(
        summary="Retrieve task details",
        description="Get full task details with eager-loaded project and user metadata.",
        tags=["Tasks"],
    ),
    update=extend_schema(
        summary="Update task",
        description="Replace all fields of a task.",
        tags=["Tasks"],
    ),
    partial_update=extend_schema(
        summary="Partially update a task",
        description="Update specific fields of a task (e.g. status, priority, due date).",
        tags=["Tasks"],
    ),
    destroy=extend_schema(
        summary="Delete a task",
        description="Remove a task idempotently.",
        tags=["Tasks"],
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    Production-grade ModelViewSet providing complete CRUD for Tasks with:
    - Pagination (PageNumberPagination)
    - Filtering by project, status, priority, and date ranges (TaskFilter)
    - Full-text search on title and description
    - Ordering by due date, priority, and creation time
    - Eager loading (with_related) to prevent N+1 queries
    """
    queryset = Task.objects.with_related().all()
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return TaskWriteSerializer
        if self.action in ["update", "partial_update"]:
            return TaskUpdateSerializer
        return TaskReadSerializer

    def perform_create(self, serializer):
        validated = serializer.validated_data
        creator = self.request.user if self.request.user.is_authenticated else User.objects.first()
        project = Project.objects.get(id=validated["project_id"])
        assignee = User.objects.filter(id=validated.get("assignee_id")).first() if validated.get("assignee_id") else None

        task = TaskService.create_task(
            project=project,
            creator=creator,
            assignee=assignee,
            title=validated["title"],
            description=validated.get("description", ""),
            status=validated.get("status"),
            priority=validated.get("priority"),
            due_date=validated.get("due_date"),
        )
        serializer.instance = task

