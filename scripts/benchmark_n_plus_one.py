"""
Benchmark script demonstrating the N+1 Query Problem vs. Eager Loading (select_related).
Simulates loading 500 tasks across multiple projects and measures:
1. Total SQL query count sent to PostgreSQL.
2. Total execution time (latency).
3. The exact SQL queries produced by Django ORM.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to sys.path so config can be imported
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection, reset_queries
from django.contrib.auth import get_user_model
from django.conf import settings
from projects.models import Project
from tasks.models import Task
from tasks.choices import TaskStatus, TaskPriority

# Ensure query logging is active
settings.DEBUG = True

User = get_user_model()


def seed_data(task_count=500):
    """Seed sample projects and tasks for benchmarking."""
    print(f"\n--- 1. Seeding {task_count} Benchmark Tasks ---")
    user, _ = User.objects.get_or_create(username="benchmark_user", defaults={"email": "bench@local"})

    # Create 5 projects
    projects = []
    for i in range(1, 6):
        p, _ = Project.objects.get_or_create(
            name=f"Benchmark Project {i}",
            owner=user,
            defaults={"description": f"Testing performance for project {i}"},
        )
        projects.append(p)

    existing_count = Task.objects.filter(title__startswith="Benchmark Task").count()
    if existing_count < task_count:
        needed = task_count - existing_count
        tasks_to_create = []
        for i in range(existing_count + 1, existing_count + needed + 1):
            project = projects[i % len(projects)]
            tasks_to_create.append(
                Task(
                    project=project,
                    creator=user,
                    assignee=user,
                    title=f"Benchmark Task {i:04d}",
                    description="Performance test task",
                    status=TaskStatus.IN_PROGRESS if i % 2 == 0 else TaskStatus.TODO,
                    priority=TaskPriority.HIGH if i % 3 == 0 else TaskPriority.MEDIUM,
                )
            )
        Task.objects.bulk_create(tasks_to_create)
        print(f"Created {len(tasks_to_create)} new tasks.")
    else:
        print(f"Already found {existing_count} tasks ready for benchmarking.")


def run_unoptimized_query(limit=500):
    """
    Simulates a junior engineer's unoptimized loop.
    Triggers the classic N+1 query problem.
    """
    reset_queries()
    start_time = time.perf_counter()

    # 1 query to fetch tasks
    tasks = list(Task.objects.filter(title__startswith="Benchmark Task")[:limit])

    # Incurring N queries for project and N queries for assignee:
    rendered = []
    for task in tasks:
        # Accessing foreign key without select_related fires a new SQL SELECT!
        rendered.append({
            "id": task.id,
            "title": task.title,
            "project_name": task.project.name,      # Query!
            "assignee_name": task.assignee.username,  # Query!
        })

    duration_ms = (time.perf_counter() - start_time) * 1000
    query_count = len(connection.queries)
    return query_count, duration_ms, connection.queries[:3]


def run_optimized_query(limit=500):
    """
    Simulates a staff engineer's optimized query using with_related() / select_related().
    Fetches all data in ONE single SQL query via SQL JOINs.
    """
    reset_queries()
    start_time = time.perf_counter()

    # Eager loading project and assignee via SQL JOINs
    tasks = list(
        Task.objects.filter(title__startswith="Benchmark Task")
        .with_related()[:limit]
    )

    rendered = []
    for task in tasks:
        # All related fields are already cached in Python memory - ZERO queries fired!
        rendered.append({
            "id": task.id,
            "title": task.title,
            "project_name": task.project.name,
            "assignee_name": task.assignee.username,
        })

    duration_ms = (time.perf_counter() - start_time) * 1000
    query_count = len(connection.queries)
    return query_count, duration_ms, connection.queries[:1]


def cleanup_data():
    """Clean up benchmark data."""
    print("\n--- Cleaning up benchmark records ---")
    deleted_tasks = Task.objects.filter(title__startswith="Benchmark Task").delete()[0]
    deleted_projects = Project.objects.filter(name__startswith="Benchmark Project").delete()[0]
    print(f"Deleted {deleted_tasks} tasks and {deleted_projects} projects.")


if __name__ == "__main__":
    seed_data(500)

    print("\n--- 2. Running Unoptimized Query (N+1 Anti-Pattern) ---")
    bad_queries, bad_time, sample_bad_sql = run_unoptimized_query(500)
    print(f"Queries Executed : {bad_queries} queries")
    print(f"Time Taken       : {bad_time:.2f} ms")

    print("\n--- 3. Running Optimized Query (select_related / with_related) ---")
    good_queries, good_time, sample_good_sql = run_optimized_query(500)
    print(f"Queries Executed : {good_queries} query")
    print(f"Time Taken       : {good_time:.2f} ms")

    print("\n==================================================================")
    print("                      BENCHMARK COMPARISON                        ")
    print("==================================================================")
    print(f"{'Metric':<25} | {'Unoptimized (N+1)':<20} | {'Optimized (JOIN)':<15}")
    print("-" * 66)
    print(f"{'SQL Query Count':<25} | {bad_queries:<20} | {good_queries:<15}")
    print(f"{'Execution Time':<25} | {bad_time:.2f} ms{'':<13} | {good_time:.2f} ms")
    query_reduction = ((bad_queries - good_queries) / bad_queries) * 100
    time_reduction = ((bad_time - good_time) / bad_time) * 100
    print(f"{'Query Reduction':<25} | {'-':<20} | {query_reduction:.1f}% fewer queries")
    print(f"{'Latency Improvement':<25} | {'-':<20} | {time_reduction:.1f}% faster")
    print("==================================================================")

    print("\nSample SQL from Unoptimized (Repeated N times for each row):")
    for q in sample_bad_sql:
        print(f"  SQL: {q['sql'][:100]}... (Time: {q['time']}s)")

    print("\nSample SQL from Optimized (Single JOIN query):")
    for q in sample_good_sql:
        print(f"  SQL: {q['sql'][:120]}... (Time: {q['time']}s)")

    cleanup_data()
