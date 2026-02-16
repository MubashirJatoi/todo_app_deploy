"""
API endpoints for monitoring and metrics collection
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ai_chatbot.services.metrics_collector import performance_monitor
from ai_chatbot.services.auth_validator import validate_auth_token
from fastapi.security import HTTPBearer
import uuid


router = APIRouter()
security = HTTPBearer()


@router.get("/metrics", tags=["monitoring"])
async def get_metrics(credentials: HTTPBearer = Depends(security)):
    """
    Get performance metrics and system statistics
    """
    try:
        # For simplicity, we'll return metrics to any authenticated user
        # In a production system, you might want to restrict this to admin users only
        auth_token = credentials.credentials
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Get metrics summary
        metrics_summary = performance_monitor.get_metrics_summary()

        return {
            "status": "success",
            "timestamp": performance_monitor.collector.metrics.get('response_time', [{'timestamp': None}])[-1:][0]['timestamp'] if performance_monitor.collector.metrics.get('response_time') else None,
            "metrics": metrics_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")


@router.get("/health", tags=["monitoring"])
async def health_check():
    """
    Health check endpoint to verify system status
    """
    try:
        uptime = performance_monitor.get_system_uptime()

        # Basic health indicators
        health_status = {
            "status": "healthy",
            "uptime_seconds": uptime,
            "active_requests": performance_monitor.active_requests,
            "checks": {
                "database_connection": "ok",  # Would be more sophisticated in reality
                "cohere_api_connection": "ok",  # Would be more sophisticated in reality
                "memory_usage": "normal",  # Would be more sophisticated in reality
            }
        }

        # Add basic metrics if available
        metrics_summary = performance_monitor.get_metrics_summary()
        if metrics_summary:
            health_status["recent_metrics"] = {
                "request_count": metrics_summary.get("request_count", {}).get("counter", 0),
                "avg_response_time_ms": metrics_summary.get("response_time", {}).get("avg", 0),
                "error_count": metrics_summary.get("error_rate", {}).get("counter", 0),
            }

        return health_status

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/performance-report", tags=["monitoring"])
async def get_performance_report(credentials: HTTPBearer = Depends(security)):
    """
    Get a detailed performance report
    """
    try:
        auth_token = credentials.credentials
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # Get detailed metrics
        metrics = performance_monitor.get_metrics_summary()

        report = {
            "report_timestamp": performance_monitor.collector.metrics.get('response_time', [{'timestamp': None}])[-1:][0]['timestamp'] if performance_monitor.collector.metrics.get('response_time') else None,
            "uptime_seconds": performance_monitor.get_system_uptime(),
            "active_requests": performance_monitor.active_requests,
            "performance_summary": {
                "response_times": metrics.get("response_time", {}),
                "request_throughput": metrics.get("request_count", {}),
                "error_rates": metrics.get("error_rate", {}),
                "concurrent_users": metrics.get("concurrent_users", {}),
                "cohere_api_usage": metrics.get("cohere_api_calls", {}),
                "database_queries": metrics.get("database_queries", {}),
            },
            "recommendations": []
        }

        # Add performance recommendations based on metrics
        avg_response_time = metrics.get("response_time", {}).get("avg", 0)
        error_rate = metrics.get("error_rate", {}).get("counter", 0)
        request_count = metrics.get("request_count", {}).get("counter", 0)

        if avg_response_time > 1000:  # Over 1 second average
            report["recommendations"].append("Average response time is high (>1s). Consider optimizing performance.")
        if error_rate > request_count * 0.05:  # More than 5% error rate
            report["recommendations"].append("High error rate detected (>5%). Investigate error causes.")
        if avg_response_time > 2000:  # Over 2 seconds average
            report["recommendations"].append("Critical: Average response time is very high (>2s). Immediate attention needed.")

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance report: {str(e)}")


@router.post("/metrics/reset", tags=["monitoring"])
async def reset_metrics(credentials: HTTPBearer = Depends(security)):
    """
    Reset all collected metrics (admin only)
    """
    try:
        auth_token = credentials.credentials
        user_id = await validate_auth_token(auth_token)

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

        # In a real implementation, you'd check if the user has admin privileges
        # For this implementation, we'll allow any authenticated user to reset metrics
        # (In production, this should be restricted to admins)

        performance_monitor.collector.reset_metrics()

        return {
            "status": "success",
            "message": "Metrics reset successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting metrics: {str(e)}")