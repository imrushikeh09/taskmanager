import multiprocessing
import os

# Server Socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker Processes & Concurrency
# Formula: (2 x CPUs) + 1, with sensible defaults for containerized environments
cpu_cores = multiprocessing.cpu_count()
default_workers = max(2, min((cpu_cores * 2) + 1, 8))
workers = int(os.getenv("GUNICORN_WORKERS", default_workers))
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_class = "gthread"

# Worker Lifecycle & Memory Leak Mitigation
# Periodically recycles workers to prevent unbounded memory growth
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 60))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

# Observability & Logging
accesslog = "-"  # Stream to stdout for Docker logging drivers
errorlog = "-"   # Stream to stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (took %(M)sms)'

# Process Naming
proc_name = "taskmanager_gunicorn"
