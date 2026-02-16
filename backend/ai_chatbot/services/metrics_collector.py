"""
Performance monitoring and metrics collection for the AI chatbot
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
import time
import threading
from collections import defaultdict, deque
import statistics


class MetricType(Enum):
    """Types of metrics that can be collected"""
    RESPONSE_TIME = "response_time"
    REQUEST_COUNT = "request_count"
    ERROR_RATE = "error_rate"
    CONCURRENT_USERS = "concurrent_users"
    COHERE_API_CALLS = "cohere_api_calls"
    DATABASE_QUERIES = "database_queries"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"


class MetricsCollector:
    """Collects and stores various performance metrics"""

    def __init__(self):
        self.metrics: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=1000))  # Store last 1000 values
        self.counters: Dict[MetricType, int] = defaultdict(int)
        self.gauges: Dict[MetricType, float] = defaultdict(float)
        self.lock = threading.Lock()  # Thread-safe operations

    def record_timing(self, metric_type: MetricType, duration_ms: float):
        """Record a timing measurement (e.g., response time)"""
        with self.lock:
            self.metrics[metric_type].append({
                'value': duration_ms,
                'timestamp': datetime.now(timezone.utc)
            })

    def increment_counter(self, metric_type: MetricType, amount: int = 1):
        """Increment a counter (e.g., request count)"""
        with self.lock:
            self.counters[metric_type] += amount

    def set_gauge(self, metric_type: MetricType, value: float):
        """Set a gauge value (e.g., current concurrent users)"""
        with self.lock:
            self.gauges[metric_type] = value

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics"""
        with self.lock:
            summary = {}

            # Calculate statistics for timing metrics
            for metric_type, values in self.metrics.items():
                if values:
                    value_list = [v['value'] for v in values]
                    summary[metric_type.value] = {
                        'count': len(value_list),
                        'avg': statistics.mean(value_list),
                        'min': min(value_list),
                        'max': max(value_list),
                        'p95': self._percentile(value_list, 95),
                        'p99': self._percentile(value_list, 99),
                        'last_10_samples': [v['value'] for v in list(values)[-10:]]
                    }
                else:
                    summary[metric_type.value] = {
                        'count': 0,
                        'avg': 0,
                        'min': 0,
                        'max': 0,
                        'p95': 0,
                        'p99': 0,
                        'last_10_samples': []
                    }

            # Add counter values
            for metric_type, count in self.counters.items():
                if metric_type.value not in summary:
                    summary[metric_type.value] = {}
                summary[metric_type.value]['counter'] = count

            # Add gauge values
            for metric_type, value in self.gauges.items():
                if metric_type.value not in summary:
                    summary[metric_type.value] = {}
                summary[metric_type.value]['gauge'] = value

            return summary

    def _percentile(self, data: list, percentile: float) -> float:
        """Calculate percentile of a data list"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            if upper_index >= len(sorted_data):
                return sorted_data[lower_index]
            # Interpolate between the two values
            fraction = index - lower_index
            return sorted_data[lower_index] + fraction * (sorted_data[upper_index] - sorted_data[lower_index])

    def reset_metrics(self):
        """Reset all collected metrics"""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()


class PerformanceMonitor:
    """Monitors performance and collects metrics"""

    def __init__(self):
        self.collector = MetricsCollector()
        self.active_requests = 0
        self.start_time = datetime.now(timezone.utc)

    def start_timer(self) -> float:
        """Start a timer and return the start time"""
        return time.time()

    def end_timer(self, start_time: float, metric_type: MetricType = MetricType.RESPONSE_TIME) -> float:
        """End a timer and record the duration"""
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        self.collector.record_timing(metric_type, duration_ms)
        return duration_ms

    def track_request(self, func):
        """Decorator to track request performance"""
        def wrapper(*args, **kwargs):
            # Increment active requests
            self.increment_active_requests()

            start_time = self.start_timer()
            try:
                result = func(*args, **kwargs)
                # Record success metrics
                self.collector.increment_counter(MetricType.REQUEST_COUNT)
                return result
            except Exception as e:
                # Record error metrics
                self.collector.increment_counter(MetricType.ERROR_RATE)
                raise
            finally:
                # Record response time
                self.end_timer(start_time)
                # Decrement active requests
                self.decrement_active_requests()
        return wrapper

    def increment_active_requests(self):
        """Increment the count of active requests"""
        self.active_requests += 1
        self.collector.set_gauge(MetricType.CONCURRENT_USERS, self.active_requests)

    def decrement_active_requests(self):
        """Decrement the count of active requests"""
        self.active_requests = max(0, self.active_requests - 1)
        self.collector.set_gauge(MetricType.CONCURRENT_USERS, self.active_requests)

    def record_cohere_api_call(self, duration_ms: Optional[float] = None):
        """Record a Cohere API call"""
        self.collector.increment_counter(MetricType.COHERE_API_CALLS)
        if duration_ms:
            self.collector.record_timing(MetricType.COHERE_API_CALLS, duration_ms)

    def record_database_query(self, duration_ms: Optional[float] = None):
        """Record a database query"""
        self.collector.increment_counter(MetricType.DATABASE_QUERIES)
        if duration_ms:
            self.collector.record_timing(MetricType.DATABASE_QUERIES, duration_ms)

    def get_system_uptime(self) -> float:
        """Get the system uptime in seconds"""
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics"""
        summary = self.collector.get_metrics_summary()
        summary['system_uptime_seconds'] = self.get_system_uptime()
        summary['active_requests'] = self.active_requests
        return summary


# Global instance for reuse
performance_monitor = PerformanceMonitor()