import uuid
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from common.middleware import CorrelationIdMiddleware, RequestLoggingMiddleware


class MiddlewareTestCase(TestCase):
    """
    Automated tests verifying cross-cutting middleware:
    Correlation ID extraction/generation, response header injection, and request timing.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_correlation_id_generated_when_absent(self):
        """When client sends no X-Request-ID, middleware generates a valid UUID4."""
        request = self.factory.get("/api/v1/projects/")
        get_response = lambda req: HttpResponse("OK")
        middleware = CorrelationIdMiddleware(get_response)

        response = middleware(request)

        self.assertTrue(hasattr(request, "correlation_id"))
        self.assertIn("X-Request-ID", response)
        # Verify it is a valid UUID
        parsed_uuid = uuid.UUID(response["X-Request-ID"])
        self.assertEqual(str(parsed_uuid), response["X-Request-ID"])

    def test_correlation_id_preserved_when_provided(self):
        """When client sends an X-Request-ID header, middleware preserves it."""
        custom_id = "trace-client-abc-12345"
        request = self.factory.get("/api/v1/projects/", HTTP_X_REQUEST_ID=custom_id)
        get_response = lambda req: HttpResponse("OK")
        middleware = CorrelationIdMiddleware(get_response)

        response = middleware(request)

        self.assertEqual(request.correlation_id, custom_id)
        self.assertEqual(response["X-Request-ID"], custom_id)

    def test_request_logging_middleware_attaches_timing_header(self):
        """Verify RequestLoggingMiddleware attaches execution time header in milliseconds."""
        request = self.factory.get("/api/v1/projects/")
        request.correlation_id = "test-req-id"
        get_response = lambda req: HttpResponse("OK")
        middleware = RequestLoggingMiddleware(get_response)

        response = middleware(request)

        self.assertIn("X-Response-Time-MS", response)
        duration = float(response["X-Response-Time-MS"])
        self.assertGreaterEqual(duration, 0.0)

    @patch("common.middleware.logger.warning")
    def test_slow_request_alert_triggered(self, mock_warning):
        """Verify that requests taking >= 500ms trigger a SLOW REQUEST warning."""
        request = self.factory.get("/api/v1/projects/")
        request.correlation_id = "slow-req-123"

        # Simulate slow response by mocking time.perf_counter
        with patch("time.perf_counter", side_effect=[0.0, 0.650]):  # 650ms duration
            get_response = lambda req: HttpResponse("OK")
            middleware = RequestLoggingMiddleware(get_response)
            middleware(request)

        mock_warning.assert_called_once()
        warning_msg = mock_warning.call_args[0][0]
        self.assertIn("SLOW REQUEST ALERT", warning_msg)
        self.assertIn("slow-req-123", warning_msg)
