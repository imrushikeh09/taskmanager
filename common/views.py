from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


class BaseAPIView(APIView):
    """
    Staff-level Base API View providing uniform response envelopes
    and centralized domain exception handling.
    All custom APIViews inherit from this base class.
    """

    def success_response(self, data=None, status_code=status.HTTP_200_OK, message="Success"):
        """Return standardized success envelope."""
        payload = {
            "success": True,
            "message": message,
            "data": data,
        }
        return Response(payload, status=status_code)

    def error_response(self, message: str, code: str = "ERROR", details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return standardized error envelope matching docs/api_contract.md."""
        payload = {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        }
        return Response(payload, status=status_code)

    def handle_exception(self, exc):
        """
        Catch domain ValidationErrors from the service layer
        and map them to standard 400 Bad Request JSON responses.
        """
        if isinstance(exc, DjangoValidationError):
            details = exc.message_dict if hasattr(exc, "message_dict") else {"non_field_errors": list(exc.messages)}
            return self.error_response(
                message="Validation failed.",
                code="VALIDATION_ERROR",
                details=details,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(exc, DRFValidationError):
            return self.error_response(
                message="Invalid request data.",
                code="VALIDATION_ERROR",
                details=exc.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return super().handle_exception(exc)
