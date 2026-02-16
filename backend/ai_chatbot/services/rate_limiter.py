"""
Rate limiting service to prevent abuse of chatbot services
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from datetime import datetime
from typing import Dict, Optional
import time


class RateLimiterService:
    """
    Service class to handle rate limiting for different types of chatbot operations
    """

    def __init__(self):
        # Initialize the limiter with a default key function
        self.limiter = Limiter(key_func=get_remote_address)

        # Define different rate limits for different operations
        self.rate_limits = {
            'chat_messages_per_minute': '10/minute',      # 10 chat messages per minute per IP
            'chat_messages_per_hour': '100/hour',         # 100 chat messages per hour per IP
            'conversations_per_day': '50/day',            # 50 new conversations per day per IP
            'bulk_operations_per_minute': '5/minute',     # 5 bulk operations per minute per IP
        }

        # Track user-specific limits (in a real implementation, this would use Redis or DB)
        self.user_limits: Dict[str, Dict[str, any]] = {}

    def init_app(self, app: FastAPI):
        """
        Initialize the rate limiter with the FastAPI app
        """
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    def limit_chat_requests(self):
        """
        Decorator to limit chat requests
        """
        return self.limiter.limit(self.rate_limits['chat_messages_per_minute'])

    def limit_bulk_operations(self):
        """
        Decorator to limit bulk operations (like deleting all tasks)
        """
        return self.limiter.limit(self.rate_limits['bulk_operations_per_minute'])

    def check_user_rate_limit(self, user_id: str, operation: str) -> bool:
        """
        Check if a user has exceeded rate limits for a specific operation

        Args:
            user_id: The ID of the user
            operation: The type of operation being performed

        Returns:
            True if allowed, False if rate limit exceeded
        """
        current_time = time.time()
        user_key = f"{user_id}:{operation}"

        if user_key not in self.user_limits:
            self.user_limits[user_key] = {
                'count': 0,
                'reset_time': current_time + self._get_reset_interval(operation)
            }

        user_limit = self.user_limits[user_key]

        # Reset counter if reset time has passed
        if current_time >= user_limit['reset_time']:
            user_limit['count'] = 0
            user_limit['reset_time'] = current_time + self._get_reset_interval(operation)

        # Check if limit exceeded
        if user_limit['count'] >= self._get_max_count(operation):
            return False

        # Increment counter
        user_limit['count'] += 1
        return True

    def _get_max_count(self, operation: str) -> int:
        """
        Get maximum allowed count for an operation
        """
        limits = {
            'chat_message': 50,        # Max 50 chat messages per interval
            'bulk_delete': 10,         # Max 10 bulk delete operations per interval
            'task_creation': 100,      # Max 100 task creations per interval
            'account_action': 5,       # Max 5 account-related actions per interval
        }
        return limits.get(operation, 50)

    def _get_reset_interval(self, operation: str) -> int:
        """
        Get reset interval in seconds for an operation
        """
        intervals = {
            'chat_message': 3600,      # 1 hour for chat messages
            'bulk_delete': 300,        # 5 minutes for bulk deletes
            'task_creation': 3600,     # 1 hour for task creation
            'account_action': 3600,    # 1 hour for account actions
        }
        return intervals.get(operation, 3600)

    def get_remaining_limits(self, user_id: str, operation: str) -> Dict[str, any]:
        """
        Get remaining limit information for a user and operation
        """
        current_time = time.time()
        user_key = f"{user_id}:{operation}"

        if user_key not in self.user_limits:
            max_count = self._get_max_count(operation)
            return {
                'remaining': max_count,
                'reset_time': current_time + self._get_reset_interval(operation),
                'max_count': max_count
            }

        user_limit = self.user_limits[user_key]
        remaining = max(0, self._get_max_count(operation) - user_limit['count'])
        reset_time = user_limit['reset_time']

        return {
            'remaining': remaining,
            'reset_time': reset_time,
            'max_count': self._get_max_count(operation)
        }


# Global instance for reuse
rate_limiter_service = RateLimiterService()