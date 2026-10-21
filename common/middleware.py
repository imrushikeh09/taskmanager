import logging
import time
import uuid

logger = logging.getLogger("taskmanager.request")

# Slow request warning threshold in milliseconds (500ms)
SLOW_REQUEST_THRESHOLD_MS = 500.0


class CorrelationIdMiddleware:
    """
    Middleware that ensures every request has a unique correlation ID (X-Request-ID).
    If the client provides X-Request-ID, it is reused to support distributed tracing.
    Otherwise, a new UUID4 is generated.
    The correlation ID is attached to both the request object and the response headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Read from incoming HTTP header or generate fresh UUID
        correlation_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        request.correlation_id = correlation_id

        response = self.get_response(request)

        # Inject correlation ID into outgoing response header
        response["X-Request-ID"] = correlation_id
        return response


class RequestLoggingMiddleware:
    """
    Middleware that measures execution duration for every HTTP request
    and logs performance metrics, including warnings for slow requests (>500ms).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        correlation_id = getattr(request, "correlation_id", "no-id")
        user = getattr(request, "user", None)
        user_identifier = user.username if user and user.is_authenticated else "Anonymous"

        # Attach execution time header for client observability
        response["X-Response-Time-MS"] = f"{duration_ms:.2f}"

        # Standard request log
        log_message = (
            f"[{response.status_code}] {request.method} {request.path} "
            f"took {duration_ms:.2f}ms | user={user_identifier} | req_id={correlation_id}"
        )

        if duration_ms >= SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(f"SLOW REQUEST ALERT: {log_message}")
        else:
            logger.info(log_message)

        return response
