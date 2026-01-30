#!/usr/bin/env python3
"""
Metrics Monitor - Complete Application Metrics Collection and Monitoring

Provides comprehensive metrics monitoring:
- Request rate tracking (RPM)
- Latency measurements (avg, p50, p95, p99)
- Error rate monitoring
- User activity tracking
- WebSocket connection counts
- System resource monitoring (CPU, Memory, Disk)
- Trading-specific metrics
- Historical data with configurable retention
- Export capabilities (JSON, CSV)

Author: Juan Carlos Garcia Arriero
Date: 30 Enero 2026
Version: 2.0.0
"""

import os
import json
import csv
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import threading
from collections import deque
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# Singleton instance
_monitor_instance = None


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"          # Duration measurements


@dataclass
class MetricsSnapshot:
    """Point-in-time metrics snapshot with comprehensive data"""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Request metrics
    request_rate_rpm: float = 0.0
    total_requests: int = 0
    requests_last_minute: int = 0
    requests_last_hour: int = 0
    
    # Error metrics
    error_rate_pct: float = 0.0
    total_errors: int = 0
    errors_last_minute: int = 0
    error_types: Dict[str, int] = field(default_factory=dict)
    
    # Latency metrics (milliseconds)
    avg_latency_ms: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    
    # User metrics
    active_users: int = 0
    total_sessions: int = 0
    
    # WebSocket metrics
    websocket_connections: int = 0
    websocket_messages_sent: int = 0
    websocket_messages_received: int = 0
    
    # System resource metrics
    memory_usage_pct: float = 0.0
    memory_usage_mb: float = 0.0
    memory_available_mb: float = 0.0
    cpu_usage_pct: float = 0.0
    disk_usage_pct: float = 0.0
    
    # Trading metrics (for bot)
    open_positions: int = 0
    total_trades_today: int = 0
    pnl_today: float = 0.0
    
    # Uptime
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with serializable values"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class RequestRecord:
    """Record of a single HTTP request"""
    timestamp: datetime
    path: str
    method: str
    status_code: int
    latency_ms: float
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class ErrorRecord:
    """Record of an error"""
    timestamp: datetime
    path: str
    error_type: str
    status_code: Optional[int] = None
    message: Optional[str] = None
    stack_trace: Optional[str] = None


class MetricsMonitor:
    """
    Comprehensive Application Metrics Monitor.
    
    Collects, aggregates, and provides access to:
    - HTTP request performance metrics
    - Error tracking and categorization
    - User activity monitoring
    - WebSocket connection statistics
    - System resource utilization
    - Trading-specific metrics
    - Historical data with export capabilities
    """
    
    VERSION = "2.0.0"
    
    def __init__(
        self,
        window_seconds: int = 300,
        history_retention_minutes: int = 60,
        snapshot_interval_seconds: int = 10
    ):
        """
        Initialize the metrics monitor.
        
        Args:
            window_seconds: Window for rate calculations (default: 5 minutes)
            history_retention_minutes: How long to keep history (default: 60 minutes)
            snapshot_interval_seconds: Interval for automatic snapshots
        """
        self.window_seconds = window_seconds
        self.history_retention_minutes = history_retention_minutes
        self.snapshot_interval_seconds = snapshot_interval_seconds
        
        # Start time for uptime calculation
        self._start_time = datetime.now()
        
        # Request tracking with larger buffer
        max_requests = 50000
        self._requests: deque = deque(maxlen=max_requests)
        self._errors: deque = deque(maxlen=5000)
        self._latencies: deque = deque(maxlen=max_requests)
        
        # User tracking
        self._active_users: Dict[str, datetime] = {}
        self._user_activity_timeout = timedelta(minutes=5)
        self._total_sessions = 0
        
        # WebSocket tracking
        self._websocket_connections = 0
        self._websocket_messages_sent = 0
        self._websocket_messages_received = 0
        
        # Counters
        self._total_requests = 0
        self._total_errors = 0
        self._error_types: Dict[str, int] = {}
        
        # Trading metrics
        self._open_positions = 0
        self._total_trades_today = 0
        self._pnl_today = 0.0
        self._last_trade_reset = datetime.now().date()
        
        # Historical snapshots for time-series
        max_snapshots = (history_retention_minutes * 60) // snapshot_interval_seconds
        self._history: deque = deque(maxlen=max(max_snapshots, 360))
        
        # Endpoint statistics
        self._endpoint_stats: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Background snapshot thread
        self._snapshot_thread = None
        self._running = False
        
        logger.info(
            f"MetricsMonitor v{self.VERSION} initialized "
            f"(window={window_seconds}s, retention={history_retention_minutes}min)"
        )
    
    def start_background_collection(self):
        """Start background metrics collection"""
        if self._running:
            return
        
        self._running = True
        self._snapshot_thread = threading.Thread(
            target=self._background_collector,
            daemon=True,
            name="MetricsCollector"
        )
        self._snapshot_thread.start()
        logger.info("Background metrics collection started")
    
    def stop_background_collection(self):
        """Stop background metrics collection"""
        self._running = False
        if self._snapshot_thread:
            self._snapshot_thread.join(timeout=5)
        logger.info("Background metrics collection stopped")
    
    def _background_collector(self):
        """Background thread for periodic snapshot collection"""
        while self._running:
            try:
                snapshot = self.get_current_snapshot()
                with self._lock:
                    self._history.append(snapshot)
                
                # Reset daily trading metrics if day changed
                self._check_daily_reset()
                
            except Exception as e:
                logger.error(f"Error in background collector: {e}")
            
            time.sleep(self.snapshot_interval_seconds)
    
    def _check_daily_reset(self):
        """Reset daily metrics if day changed"""
        today = datetime.now().date()
        if today != self._last_trade_reset:
            with self._lock:
                self._total_trades_today = 0
                self._pnl_today = 0.0
                self._last_trade_reset = today
                logger.info("Daily trading metrics reset")
    
    # ==================== REQUEST TRACKING ====================
    
    def record_request(
        self,
        path: str,
        method: str,
        status_code: int,
        latency_ms: float,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Record an HTTP request with full context"""
        now = datetime.now()
        
        record = RequestRecord(
            timestamp=now,
            path=path,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        with self._lock:
            self._requests.append(record)
            self._latencies.append((now, latency_ms))
            self._total_requests += 1
            
            # Update endpoint statistics
            endpoint_key = f"{method}:{path}"
            if endpoint_key not in self._endpoint_stats:
                self._endpoint_stats[endpoint_key] = {
                    'count': 0,
                    'total_latency': 0,
                    'errors': 0,
                    'min_latency': float('inf'),
                    'max_latency': 0
                }
            
            stats = self._endpoint_stats[endpoint_key]
            stats['count'] += 1
            stats['total_latency'] += latency_ms
            stats['min_latency'] = min(stats['min_latency'], latency_ms)
            stats['max_latency'] = max(stats['max_latency'], latency_ms)
            
            # Track errors (4xx and 5xx)
            if status_code >= 400:
                self._record_error_internal(
                    path=path,
                    error_type=f"HTTP_{status_code}",
                    status_code=status_code,
                    timestamp=now
                )
                stats['errors'] += 1
            
            # Track user activity
            if user_id:
                self._active_users[user_id] = now
    
    def record_error(
        self,
        path: str,
        error_type: str,
        message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        """Record an error with details"""
        with self._lock:
            self._record_error_internal(
                path=path,
                error_type=error_type,
                status_code=status_code,
                message=message,
                stack_trace=stack_trace
            )
    
    def _record_error_internal(
        self,
        path: str,
        error_type: str,
        timestamp: Optional[datetime] = None,
        status_code: Optional[int] = None,
        message: Optional[str] = None,
        stack_trace: Optional[str] = None
    ):
        """Internal error recording (must hold lock)"""
        if timestamp is None:
            timestamp = datetime.now()
        
        record = ErrorRecord(
            timestamp=timestamp,
            path=path,
            error_type=error_type,
            status_code=status_code,
            message=message,
            stack_trace=stack_trace
        )
        
        self._errors.append(record)
        self._total_errors += 1
        
        # Track error types
        self._error_types[error_type] = self._error_types.get(error_type, 0) + 1
    
    # ==================== USER TRACKING ====================
    
    def record_user_activity(self, user_id: str):
        """Record user activity"""
        with self._lock:
            if user_id not in self._active_users:
                self._total_sessions += 1
            self._active_users[user_id] = datetime.now()
    
    def record_user_logout(self, user_id: str):
        """Record user logout"""
        with self._lock:
            self._active_users.pop(user_id, None)
    
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
    
    def record_websocket_message(self, direction: str = 'sent'):
        """Record WebSocket message"""
        with self._lock:
            if direction == 'sent':
                self._websocket_messages_sent += 1
            else:
                self._websocket_messages_received += 1
    
    def get_websocket_connections(self) -> int:
        """Get current WebSocket connection count"""
        return self._websocket_connections
    
    # ==================== TRADING METRICS ====================
    
    def update_trading_metrics(
        self,
        open_positions: Optional[int] = None,
        trade_executed: bool = False,
        pnl_change: float = 0.0
    ):
        """Update trading-specific metrics"""
        with self._lock:
            if open_positions is not None:
                self._open_positions = open_positions
            
            if trade_executed:
                self._total_trades_today += 1
            
            self._pnl_today += pnl_change
    
    # ==================== SYSTEM METRICS ====================
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource metrics"""
        try:
            # Memory
            memory = psutil.virtual_memory()
            memory_usage_pct = memory.percent
            memory_usage_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # CPU
            cpu_usage_pct = psutil.cpu_percent(interval=0.1)
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_usage_pct = disk.percent
            
            return {
                'memory_usage_pct': round(memory_usage_pct, 1),
                'memory_usage_mb': round(memory_usage_mb, 1),
                'memory_available_mb': round(memory_available_mb, 1),
                'cpu_usage_pct': round(cpu_usage_pct, 1),
                'disk_usage_pct': round(disk_usage_pct, 1)
            }
        except Exception as e:
            logger.warning(f"Error getting system metrics: {e}")
            return {
                'memory_usage_pct': 0.0,
                'memory_usage_mb': 0.0,
                'memory_available_mb': 0.0,
                'cpu_usage_pct': 0.0,
                'disk_usage_pct': 0.0
            }
    
    # ==================== METRICS CALCULATION ====================
    
    def _calculate_percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile from sorted list"""
        if not sorted_values:
            return 0.0
        
        index = int(len(sorted_values) * percentile / 100)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def get_current_snapshot(self) -> MetricsSnapshot:
        """Get comprehensive current metrics snapshot"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_hour = now - timedelta(hours=1)
        
        with self._lock:
            # Filter requests by time windows
            recent_requests = [r for r in self._requests if r.timestamp > cutoff]
            requests_last_minute = len([r for r in self._requests if r.timestamp > cutoff_minute])
            requests_last_hour = len([r for r in self._requests if r.timestamp > cutoff_hour])
            
            # Filter errors
            recent_errors = [e for e in self._errors if e.timestamp > cutoff]
            errors_last_minute = len([e for e in self._errors if e.timestamp > cutoff_minute])
            
            # Get latencies for window
            recent_latencies = [lat for ts, lat in self._latencies if ts > cutoff]
            
            # Calculate request rate (requests per minute)
            request_count = len(recent_requests)
            window_minutes = self.window_seconds / 60
            request_rate = request_count / window_minutes if window_minutes > 0 else 0
            
            # Calculate error rate
            error_rate = (len(recent_errors) / request_count * 100) if request_count > 0 else 0
            
            # Calculate latency percentiles
            avg_latency = 0.0
            p50_latency = 0.0
            p95_latency = 0.0
            p99_latency = 0.0
            min_latency = 0.0
            max_latency = 0.0
            
            if recent_latencies:
                sorted_latencies = sorted(recent_latencies)
                avg_latency = sum(sorted_latencies) / len(sorted_latencies)
                p50_latency = self._calculate_percentile(sorted_latencies, 50)
                p95_latency = self._calculate_percentile(sorted_latencies, 95)
                p99_latency = self._calculate_percentile(sorted_latencies, 99)
                min_latency = sorted_latencies[0]
                max_latency = sorted_latencies[-1]
            
            # Get system metrics
            system_metrics = self._get_system_metrics()
            
            # Calculate uptime
            uptime = (now - self._start_time).total_seconds()
            
            return MetricsSnapshot(
                timestamp=now,
                # Request metrics
                request_rate_rpm=round(request_rate, 2),
                total_requests=self._total_requests,
                requests_last_minute=requests_last_minute,
                requests_last_hour=requests_last_hour,
                # Error metrics
                error_rate_pct=round(error_rate, 2),
                total_errors=self._total_errors,
                errors_last_minute=errors_last_minute,
                error_types=dict(self._error_types),
                # Latency metrics
                avg_latency_ms=round(avg_latency, 2),
                latency_p50_ms=round(p50_latency, 2),
                latency_p95_ms=round(p95_latency, 2),
                latency_p99_ms=round(p99_latency, 2),
                min_latency_ms=round(min_latency, 2),
                max_latency_ms=round(max_latency, 2),
                # User metrics
                active_users=self.get_active_user_count(),
                total_sessions=self._total_sessions,
                # WebSocket metrics
                websocket_connections=self._websocket_connections,
                websocket_messages_sent=self._websocket_messages_sent,
                websocket_messages_received=self._websocket_messages_received,
                # System metrics
                memory_usage_pct=system_metrics['memory_usage_pct'],
                memory_usage_mb=system_metrics['memory_usage_mb'],
                memory_available_mb=system_metrics['memory_available_mb'],
                cpu_usage_pct=system_metrics['cpu_usage_pct'],
                disk_usage_pct=system_metrics['disk_usage_pct'],
                # Trading metrics
                open_positions=self._open_positions,
                total_trades_today=self._total_trades_today,
                pnl_today=round(self._pnl_today, 2),
                # Uptime
                uptime_seconds=round(uptime, 0)
            )
    
    # ==================== HISTORICAL DATA ====================
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for the specified time period"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            history = [
                snapshot.to_dict()
                for snapshot in self._history
                if snapshot.timestamp > cutoff
            ]
        
        return history
    
    def get_request_history(self, limit: int = 100) -> List[Dict]:
        """Get recent request history"""
        with self._lock:
            history = list(self._requests)[-limit:]
            return [
                {
                    'timestamp': r.timestamp.isoformat(),
                    'path': r.path,
                    'method': r.method,
                    'status_code': r.status_code,
                    'latency_ms': r.latency_ms,
                    'user_id': r.user_id
                }
                for r in history
            ]
    
    def get_error_history(self, limit: int = 50) -> List[Dict]:
        """Get recent error history"""
        with self._lock:
            history = list(self._errors)[-limit:]
            return [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'path': e.path,
                    'error_type': e.error_type,
                    'status_code': e.status_code,
                    'message': e.message
                }
                for e in history
            ]
    
    def get_endpoint_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics per endpoint"""
        with self._lock:
            stats = {}
            for endpoint, data in self._endpoint_stats.items():
                if data['count'] > 0:
                    stats[endpoint] = {
                        'count': data['count'],
                        'avg_latency_ms': round(data['total_latency'] / data['count'], 2),
                        'min_latency_ms': round(data['min_latency'], 2) if data['min_latency'] != float('inf') else 0,
                        'max_latency_ms': round(data['max_latency'], 2),
                        'error_count': data['errors'],
                        'error_rate_pct': round(data['errors'] / data['count'] * 100, 2)
                    }
            return stats
    
    # ==================== STATISTICS & EXPORT ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics summary"""
        snapshot = self.get_current_snapshot()
        
        return {
            'current': snapshot.to_dict(),
            'totals': {
                'total_requests': self._total_requests,
                'total_errors': self._total_errors,
                'error_rate_pct': round(
                    self._total_errors / self._total_requests * 100
                    if self._total_requests > 0 else 0, 2
                ),
                'total_sessions': self._total_sessions
            },
            'error_breakdown': dict(self._error_types),
            'endpoints': self.get_endpoint_statistics(),
            'configuration': {
                'window_seconds': self.window_seconds,
                'history_retention_minutes': self.history_retention_minutes,
                'snapshot_interval_seconds': self.snapshot_interval_seconds
            },
            'version': self.VERSION
        }
    
    def reset_statistics(self):
        """Reset all statistics counters"""
        with self._lock:
            self._total_requests = 0
            self._total_errors = 0
            self._error_types.clear()
            self._endpoint_stats.clear()
            self._total_sessions = 0
            self._websocket_messages_sent = 0
            self._websocket_messages_received = 0
            self._total_trades_today = 0
            self._pnl_today = 0.0
            self._requests.clear()
            self._errors.clear()
            self._latencies.clear()
            self._history.clear()
            logger.info("Metrics statistics reset")
    
    def export_to_json(self, filepath: str):
        """Export all metrics to JSON file"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'history': self.get_metrics_history(minutes=self.history_retention_minutes),
            'recent_requests': self.get_request_history(limit=500),
            'recent_errors': self.get_error_history(limit=100)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {filepath}")
    
    def export_to_csv(self, filepath: str):
        """Export metrics history to CSV file"""
        history = self.get_metrics_history(minutes=self.history_retention_minutes)
        
        if not history:
            logger.warning("No history to export")
            return
        
        # Get all keys from first record
        fieldnames = list(history[0].keys())
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(history)
        
        logger.info(f"Metrics history exported to {filepath}")


class MetricsMiddleware:
    """Flask middleware for automatic request metrics collection"""
    
    def __init__(self, app, monitor: MetricsMonitor):
        self.app = app
        self.monitor = monitor
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        logger.info("MetricsMiddleware attached to Flask app")
    
    def _before_request(self):
        """Record request start time"""
        from flask import g, request, session
        g.request_start_time = time.time()
        
        # Track user activity if logged in
        user_id = session.get('user_id') or session.get('user')
        if user_id:
            self.monitor.record_user_activity(str(user_id))
    
    def _after_request(self, response):
        """Record request metrics"""
        from flask import g, request, session
        
        start_time = getattr(g, 'request_start_time', None)
        if start_time:
            latency_ms = (time.time() - start_time) * 1000
            
            user_id = session.get('user_id') or session.get('user')
            
            self.monitor.record_request(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                latency_ms=latency_ms,
                user_id=str(user_id) if user_id else None,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string if request.user_agent else None
            )
        
        return response


def get_metrics_monitor(
    window_seconds: int = 300,
    history_retention_minutes: int = 60,
    start_background: bool = True
) -> MetricsMonitor:
    """
    Get the singleton MetricsMonitor instance.
    
    Args:
        window_seconds: Metrics aggregation window (default: 5 minutes)
        history_retention_minutes: How long to keep history (default: 60 minutes)
        start_background: Start background collection thread
        
    Returns:
        MetricsMonitor singleton instance
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = MetricsMonitor(
            window_seconds=window_seconds,
            history_retention_minutes=history_retention_minutes
        )
        
        if start_background:
            _monitor_instance.start_background_collection()
    
    return _monitor_instance


def setup_metrics_for_app(app, window_seconds: int = 300) -> Tuple[MetricsMonitor, MetricsMiddleware]:
    """
    Convenience function to setup metrics for a Flask app.
    
    Args:
        app: Flask application instance
        window_seconds: Metrics window in seconds
        
    Returns:
        Tuple of (MetricsMonitor, MetricsMiddleware)
    """
    monitor = get_metrics_monitor(window_seconds=window_seconds)
    middleware = MetricsMiddleware(app, monitor)
    return monitor, middleware
