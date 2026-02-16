from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ai_chatbot.models.responses import ErrorResponse
import traceback
import logging


class AIChatbotErrorHandler:
    """
    Error handling utilities for the AI chatbot service
    """

    @staticmethod
    def handle_validation_error(exc: Exception) -> ErrorResponse:
        """
        Handle validation errors
        """
        return ErrorResponse(
            message="Invalid input data",
            error_code="VALIDATION_ERROR",
            details={
                "error": str(exc),
                "traceback": traceback.format_exc() if hasattr(exc, '__traceback__') else None
            }
        )

    @staticmethod
    def handle_authentication_error(exc: Exception) -> ErrorResponse:
        """
        Handle authentication errors
        """
        return ErrorResponse(
            message="Authentication failed",
            error_code="AUTHENTICATION_ERROR",
            details={
                "error": str(exc)
            }
        )

    @staticmethod
    def handle_authorization_error(exc: Exception) -> ErrorResponse:
        """
        Handle authorization errors
        """
        return ErrorResponse(
            message="Insufficient permissions",
            error_code="AUTHORIZATION_ERROR",
            details={
                "error": str(exc)
            }
        )

    @staticmethod
    def handle_external_api_error(service_name: str, exc: Exception) -> ErrorResponse:
        """
        Handle errors from external APIs (Cohere, Phase 2 API, etc.)
        """
        return ErrorResponse(
            message=f"Error communicating with {service_name}",
            error_code="EXTERNAL_API_ERROR",
            details={
                "service": service_name,
                "error": str(exc),
                "traceback": traceback.format_exc() if hasattr(exc, '__traceback__') else None
            }
        )

    @staticmethod
    def handle_internal_error(exc: Exception) -> ErrorResponse:
        """
        Handle internal server errors
        """
        logging.error(f"Internal error: {exc}")
        logging.error(traceback.format_exc())

        return ErrorResponse(
            message="An internal error occurred",
            error_code="INTERNAL_ERROR",
            details={
                "error": str(exc),
                "traceback": traceback.format_exc() if hasattr(exc, '__traceback__') else None
            }
        )

    @staticmethod
    def handle_business_logic_error(exc: Exception) -> ErrorResponse:
        """
        Handle business logic errors
        """
        return ErrorResponse(
            message="Business rule violation",
            error_code="BUSINESS_LOGIC_ERROR",
            details={
                "error": str(exc)
            }
        )


# Custom exception classes for the AI chatbot
class ChatbotException(Exception):
    """Base exception for chatbot-related errors"""
    def __init__(self, message: str, error_code: str = "CHATBOT_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class IntentClassificationError(ChatbotException):
    """Raised when intent classification fails"""
    def __init__(self, message: str = "Failed to classify user intent"):
        super().__init__(message, "INTENT_CLASSIFICATION_ERROR")


class EntityExtractionError(ChatbotException):
    """Raised when entity extraction fails"""
    def __init__(self, message: str = "Failed to extract entities from user input"):
        super().__init__(message, "ENTITY_EXTRACTION_ERROR")


class TaskOperationError(ChatbotException):
    """Raised when task operations fail"""
    def __init__(self, message: str = "Task operation failed"):
        super().__init__(message, "TASK_OPERATION_ERROR")


class ExternalServiceError(ChatbotException):
    """Raised when external services fail"""
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(f"{service_name}: {message}", "EXTERNAL_SERVICE_ERROR")


# Global error handler instance
error_handler = AIChatbotErrorHandler()


# Exception handlers for FastAPI
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            error_code="HTTP_ERROR"
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation exceptions"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_handler.handle_validation_error(exc).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_handler.handle_internal_error(exc).model_dump()
    )