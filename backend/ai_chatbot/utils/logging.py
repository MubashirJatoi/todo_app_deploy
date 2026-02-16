import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json
import os


class AIChatbotLogger:
    """
    Logging utilities for the AI chatbot service
    """

    def __init__(self, name: str = "ai_chatbot", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Prevent adding multiple handlers if logger already exists
        if not self.logger.handlers:
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)

            # Create file handler if LOG_FILE environment variable is set
            log_file = os.getenv("LOG_FILE")
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)

                # Add file handler to logger
                self.logger.addHandler(file_handler)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)

            # Add console handler to logger
            self.logger.addHandler(console_handler)

    def _format_log_data(self, message: str, **kwargs) -> str:
        """
        Format log message with additional data
        """
        log_dict = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            **kwargs
        }
        return json.dumps(log_dict)

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log info message
        """
        if kwargs:
            formatted_message = self._format_log_data(message, **kwargs)
        else:
            formatted_message = message
        self.logger.info(formatted_message)

    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug message
        """
        if kwargs:
            formatted_message = self._format_log_data(message, **kwargs)
        else:
            formatted_message = message
        self.logger.debug(formatted_message)

    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log warning message
        """
        if kwargs:
            formatted_message = self._format_log_data(message, **kwargs)
        else:
            formatted_message = message
        self.logger.warning(formatted_message)

    def error(self, message: str, **kwargs: Any) -> None:
        """
        Log error message
        """
        if kwargs:
            formatted_message = self._format_log_data(message, **kwargs)
        else:
            formatted_message = message
        self.logger.error(formatted_message)

    def critical(self, message: str, **kwargs: Any) -> None:
        """
        Log critical message
        """
        if kwargs:
            formatted_message = self._format_log_data(message, **kwargs)
        else:
            formatted_message = message
        self.logger.critical(formatted_message)

    def log_interaction(self, user_id: str, conversation_id: str, input_text: str, output_text: str,
                      intent: str = None, entities: Dict = None) -> None:
        """
        Log chatbot interaction
        """
        self.info(
            "Chatbot interaction",
            user_id=user_id,
            conversation_id=conversation_id,
            input=input_text,
            output=output_text,
            intent=intent,
            entities=entities
        )

    def log_task_operation(self, user_id: str, operation: str, success: bool, details: Dict = None) -> None:
        """
        Log task operation
        """
        self.info(
            "Task operation",
            user_id=user_id,
            operation=operation,
            success=success,
            details=details
        )

    def log_api_call(self, service: str, endpoint: str, success: bool, duration_ms: float = None) -> None:
        """
        Log external API call
        """
        self.info(
            "External API call",
            service=service,
            endpoint=endpoint,
            success=success,
            duration_ms=duration_ms
        )

    def log_error(self, error_type: str, error_message: str, traceback_info: str = None, **kwargs) -> None:
        """
        Log error with additional context
        """
        self.error(
            "Error occurred",
            error_type=error_type,
            error_message=error_message,
            traceback=traceback_info,
            **kwargs
        )


# Global logger instance
logger = AIChatbotLogger()