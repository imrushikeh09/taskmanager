import logging
from django.core.cache import cache

logger = logging.getLogger("taskmanager")

PERFORMANCE_REPORT_CACHE_KEY_PREFIX = "perf_report:project"
PERFORMANCE_REPORT_TTL = 300  # 5 minutes in seconds (as defined in reference guide)


def get_performance_report_cache_key(project_id: int) -> str:
    """Generate deterministic Redis cache key for project performance report."""
    return f"{PERFORMANCE_REPORT_CACHE_KEY_PREFIX}:{project_id}"


def invalidate_performance_cache(project_id: int) -> bool:
    """
    Deletes the cached performance report for a specific project.
    Called when a task is created, updated, reassigned, or deleted.
    Ensures subsequent requests recalculate using fresh data (Reference PDF - Problem 2).
    """
    key = get_performance_report_cache_key(project_id)
    deleted = cache.delete(key)
    if deleted:
        logger.info(f"Invalidated cache key={key} for project={project_id}")
    return bool(deleted)
