import django_filters
from django.utils import timezone
from .models import Task
from .choices import TaskStatus, TaskPriority


class TaskFilter(django_filters.FilterSet):
    """
    Declarative FilterSet for Task filtering.
    Supports exact matching, date ranges, and custom business filters.
    """
    status = django_filters.ChoiceFilter(choices=TaskStatus.choices)
    priority = django_filters.ChoiceFilter(choices=TaskPriority.choices)
    project = django_filters.NumberFilter(field_name="project_id")
    assignee = django_filters.NumberFilter(field_name="assignee_id")
    due_date_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_date_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    is_overdue = django_filters.BooleanFilter(method="filter_is_overdue")

    class Meta:
        model = Task
        fields = ["status", "priority", "project", "assignee", "due_date_before", "due_date_after"]

    def filter_is_overdue(self, queryset, name, value):
        """Custom filter to find active tasks past their due date."""
        today = timezone.now().date()
        if value is True:
            return queryset.filter(due_date__lt=today).exclude(status=TaskStatus.COMPLETED)
        elif value is False:
            return queryset.exclude(due_date__lt=today, status__ne=TaskStatus.COMPLETED)
        return queryset
