#!/usr/bin/env python3
"""
Metrics Monitor - Application metrics collection and monitoring

Provides:
- Request rate tracking
- Latency measurements
- Error rate monitoring
- User activity tracking
- WebSocket connection counts
"""

import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Singleton instance
_monitor_instance = None


@dataclass
class MetricsSnapshot:
    """Point-in-time metrics snapshot"""
    timestamp: datetime = field(default_factory=datetime.now)
    request_rate_rpm: float = 0.0
    error_rate_pct: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    active_users: int = 0
    websocket_connections: int = 0
    total_requests: int = 0
    total_errors: int = 0


class MetricsMonitor:
    """
    Application metrics monitor.
    
    Collects and aggregates metrics for:
    - HTTP request performance
    - Error tracking
    - User activity
    - WebSocket connections
    """
    
    def __init__(self, window_seconds: int = 300):
        self.window_seconds = window_seconds
        
        # Request tracking
        self._requests: deque = deque(maxlen=10000)
        self._errors: deque = deque(maxlen=1000)
        self._latencies: deque = deque(maxlen=10000)
        
        # User tracking
        self._active_users: Dict[str, datetime] = {}
        self._user_activity_timeout = timedelta(minutes=5)
        
        # WebSocket tracking
        self._websocket_connections = 0
        
        # Counters
        self._total_requests = 0
        self._total_errors = 0
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        logger.info(f"MetricsMonitor initialized (window={window_seconds}s)")
    
    # ==================== REQUEST TRACKING ====================
    
    def record_request(self, path: str, method: str, status_code: int, latency_ms: float):
        """Record an HTTP request"""
        now = datetime.now()
        
        with self._lock:
            self._requests.append({
                'timestamp': now,
                'path': path,
                'method': method,
                'status_code': status_code,
                'latency_ms': latency_ms
            })
            
            self._latencies.append((now, latency_ms))
            self._total_requests += 1
            
            # Track errors (4xx and 5xx)
            if status_code >= 400:
                self._errors.append({
                    'timestamp': now,
                    'path': path,
                    'status_code': status_code
                })
                self._total_errors += 1
    
    def record_error(self, path: str, error_type: str):
        """Record an error"""
        now = datetime.now()
        
        with self._lock:
            self._errors.append({
                'timestamp': now,
                'path': path,
                'error_type': error_type
            })
            self._total_errors += 1
    
    # ==================== USER TRACKING ====================
    
    def record_user_activity(self, user_id: str):
        """Record user activity"""
        with self._lock:
            self._active_users[user_id] = datetime.now()
    
    def get_active_user_count(self) -> int:
        """Get count of recently active users"""
        cutoff = datetime.now() - self._user_activity_timeout
        
        with self._lock:
            # Clean up old entries
            self._active_users = {
                uid: ts for uid, ts in self._active_users.items()
                if ts > cutoff
            }
            return len(self._active_users)
    
    # ==================== WEBSOCKET TRACKING ====================
    
    def increment_websocket_connections(self):
        """Increment WebSocket connection count"""
        with self._lock:
            self._websocket_connections += 1
    
    def decrement_websocket_connections(self):
        """Decrement WebSocket connection count"""
        with self._lock:
            self._websocket_connections = max(0, self._websocket_connections - 1)
    
    def get_websocket_connections(self) -> int:
        """Get current WebSocket connection count"""
        return self._websocket_connections
    
    # ==================== METRICS CALCULATION ====================
    
    def get_current_snapshot(self) -> MetricsSnapshot:
        """Get current metrics snapshot"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        with self._lock:
            # Filter to window
            recent_requests = [r for r in self._requests if r['timestamp'] > cutoff]
            recent_errors = [e for e in self._errors if e['timestamp'] > cutoff]
            recent_latencies = [lat for ts, lat in self._latencies if ts > cutoff]
            
            # Calculate request rate (requests per minute)
            request_count = len(recent_requests)
            window_minutes = self.window_seconds / 60
            request_rate = request_count / window_minutes if window_minutes > 0 else 0
            
            # Calculate error rate
            error_rate = (len(recent_errors) / request_count * 100) if request_count > 0 else 0
            
            # Calculate latency percentiles
            avg_latency = 0
            p95_latency = 0
            p99_latency = 0
            
            if recent_latencies:
                sorted_latencies = sorted(recent_latencies)
                avg_latency = sum(sorted_latencies) / len(sorted_latencies)
                p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
                p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
            
            return MetricsSnapshot(
                timestamp=now,
                request_rate_rpm=round(request_rate, 2),
                error_rate_pct=round(error_rate, 2),
                avg_latency_ms=round(avg_latency, 2),
                p95_latency_ms=round(p95_latency, 2),
                p99_latency_ms=round(p99_latency, 2),
                active_users=self.get_active_user_count(),
                websocket_connections=self._websocket_connections,
                total_requests=self._total_requests,
                total_errors=self._total_errors
            )
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        snapshot = self.get_current_snapshot()
        return {
            'timestamp': snapshot.timestamp.isoformat(),
            'request_rate_rpm': snapshot.request_rate_rpm,
            'error_rate_pct': snapshot.error_rate_pct,
            'avg_latency_ms': snapshot.avg_latency_ms,
            'p95_latency_ms': snapshot.p95_latency_ms,
            'p99_latency_ms': snapshot.p99_latency_ms,
            'active_users': snapshot.active_users,
            'websocket_connections': snapshot.websocket_connections,
            'total_requests': snapshot.total_requests,
            'total_errors': snapshot.total_errors
        }
    
    # ==================== HISTORICAL DATA ====================
    
    def get_request_history(self, limit: int = 100) -> List[Dict]:
        """Get recent request history"""
        with self._lock:
            history = list(self._requests)[-limit:]
            return [
                {
                    'timestamp': r['timestamp'].isoformat(),
                    'path': r['path'],
                    'method': r['method'],
                    'status_code': r['status_code'],
                    'latency_ms': r['latency_ms']
                }
                for r in history
            ]
    
    def get_error_history(self, limit: int = 50) -> List[Dict]:
        """Get recent error history"""
        with self._lock:
            history = list(self._errors)[-limit:]
            return [
                {
                    'timestamp': e['timestamp'].isoformat(),
                    'path': e['path'],
                    'status_code': e.get('status_code'),
                    'error_type': e.get('error_type')
                }
                for e in history
            ]


class MetricsMiddleware:
    """Flask middleware for automatic request metrics collection"""
    
    def __init__(self, app, monitor: MetricsMonitor):
        self.app = app
        self.monitor = monitor
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _before_request(self):
        """Record request start time"""
        from flask import g, request
        g.request_start_time = time.time()
    
    def _after_request(self, response):
        """Record request metrics"""
        from flask import g, request
        
        start_time = getattr(g, 'request_start_time', None)
        if start_time:
            latency_ms = (time.time() - start_time) * 1000
            self.monitor.record_request(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                latency_ms=latency_ms
            )
        
        return response


def get_metrics_monitor(window_seconds: int = 300) -> MetricsMonitor:
    """
    Get the singleton MetricsMonitor instance.
    
    Args:
        window_seconds: Metrics aggregation window
        
    Returns:
        MetricsMonitor instance
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = MetricsMonitor(window_seconds)
    
    return _monitor_instance
