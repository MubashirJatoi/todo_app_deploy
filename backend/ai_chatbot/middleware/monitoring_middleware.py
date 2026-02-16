"""
Monitoring middleware to track performance metrics for API endpoints
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware
from starlette.requests import Request as StarletteRequest
from starlette.types import ASGIApp, Receive, Scope, Send
from ai_chatbot.services.metrics_collector import performance_monitor, MetricType
import time
import asyncio


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor API performance and collect metrics
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = performance_monitor.start_timer()

        # Increment active requests
        performance_monitor.increment_active_requests()

        try:
            # Process the request
            response = await call_next(request)

            # Calculate response time
            response_time = performance_monitor.end_timer(start_time, MetricType.RESPONSE_TIME)

            # Record successful request
            performance_monitor.collector.increment_counter(MetricType.REQUEST_COUNT)

            # Log response details
            if hasattr(performance_monitor, 'logger'):
                performance_monitor.logger.info(
                    "API Request Completed",
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    client_ip=self._get_client_ip(request)
                )

            return response

        except Exception as e:
            # Calculate response time even for errors
            response_time = performance_monitor.end_timer(start_time, MetricType.RESPONSE_TIME)

            # Record error
            performance_monitor.collector.increment_counter(MetricType.ERROR_RATE)

            # Log error details
            if hasattr(performance_monitor, 'logger'):
                performance_monitor.logger.error(
                    "API Request Failed",
                    method=request.method,
                    url=str(request.url),
                    error=str(e),
                    response_time_ms=response_time,
                    client_ip=self._get_client_ip(request)
                )

            # Re-raise the exception
            raise
        finally:
            # Decrement active requests
            performance_monitor.decrement_active_requests()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"


# Function to add monitoring middleware to the app
def add_monitoring_middleware(app):
    """
    Add monitoring middleware to the FastAPI app
    """
    app.add_middleware(MonitoringMiddleware)
    return app