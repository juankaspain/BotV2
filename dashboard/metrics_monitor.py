#!/usr/bin/env python3
"""Professional Metrics Monitoring System v1.0

Real-time monitoring of:
- Request rate (RPM)
- Error rate (%)
- P50, P95, P99 latency
- Active users
- Memory usage
- CPU usage  
- WebSocket connections

Author: Juan Carlos Garcia Arriero
Date: 25 Enero 2026
Version: 1.0.0
"""

import logging
import threading
import time
import psutil
import numpy as np
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: str
    request_rate_rpm: float
    error_rate_pct: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    active_users: int
    memory_usage_pct: float
    memory_usage_mb: float
    cpu_usage_pct: float
    websocket_connections: int
    total_requests: int
    total_errors: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MetricsMonitor:
    """Professional metrics monitoring with rolling windows"""
    
    def __init__(self, window_seconds: int = 300):
        """
        Initialize metrics monitor.
        
        Args:
            window_seconds: Rolling window size in seconds (default 5 minutes)
        """
        self.window_seconds = window_seconds
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Request tracking (timestamp, latency_ms, is_error)
        self._requests = deque(maxlen=10000)
        
        # Active users tracking (user_id -> last_seen_timestamp)
        self._active_users = {}
        self._user_timeout = 300  # 5 minutes
        
        # WebSocket connections
        self._websocket_connections = 0
        
        # Process for resource monitoring
        self._process = psutil.Process()
        
        # Metrics history (last 1 hour, 1 snapshot per minute)
        self._metrics_history = deque(maxlen=60)
        
        # Statistics
        self._total_requests = 0
        self._total_errors = 0
        
        # Start background cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        
        logger.info("[+] MetricsMonitor initialized (window: %ds)", window_seconds)
    
    # ==================== REQUEST TRACKING ====================
    
    def record_request(self, latency_ms: float, is_error: bool = False, user_id: Optional[str] = None):
        """
        Record a request with latency and error status.
        
        Args:
            latency_ms: Request latency in milliseconds
            is_error: Whether the request resulted in an error
            user_id: Optional user identifier
        """
        with self._lock:
            timestamp = time.time()
            self._requests.append((timestamp, latency_ms, is_error))
            self._total_requests += 1
            
            if is_error:
                self._total_errors += 1
            
            # Track active user
            if user_id:
                self._active_users[user_id] = timestamp
    
    def get_request_rate_rpm(self) -> float:
        """
        Calculate requests per minute (RPM) over the rolling window.
        
        Returns:
            Requests per minute
        """
        with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            # Count requests in window
            recent_requests = sum(1 for ts, _, _ in self._requests if ts >= cutoff)
            
            # Convert to RPM
            rpm = (recent_requests / self.window_seconds) * 60
            return round(rpm, 2)
    
    def get_error_rate_pct(self) -> float:
        """
        Calculate error rate percentage over the rolling window.
        
        Returns:
            Error rate as percentage (0-100)
        """
        with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            # Count requests and errors in window
            recent_requests = [(ts, is_err) for ts, _, is_err in self._requests if ts >= cutoff]
            
            if not recent_requests:
                return 0.0
            
            total = len(recent_requests)
            errors = sum(1 for _, is_err in recent_requests if is_err)
            
            return round((errors / total) * 100, 2)
    
    def get_latency_percentiles(self) -> Tuple[float, float, float]:
        """
        Calculate latency percentiles (P50, P95, P99) over the rolling window.
        
        Returns:
            Tuple of (p50, p95, p99) in milliseconds
        """
        with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            # Collect latencies in window
            latencies = [lat for ts, lat, _ in self._requests if ts >= cutoff]
            
            if not latencies:
                return (0.0, 0.0, 0.0)
            
            # Calculate percentiles
            p50 = round(np.percentile(latencies, 50), 2)
            p95 = round(np.percentile(latencies, 95), 2)
            p99 = round(np.percentile(latencies, 99), 2)
            
            return (p50, p95, p99)
    
    # ==================== USER TRACKING ====================
    
    def record_user_activity(self, user_id: str):
        """
        Record user activity.
        
        Args:
            user_id: User identifier
        """
        with self._lock:
            self._active_users[user_id] = time.time()
    
    def get_active_users(self) -> int:
        """
        Get count of active users (activity within timeout period).
        
        Returns:
            Number of active users
        """
        with self._lock:
            now = time.time()
            cutoff = now - self._user_timeout
            
            # Count users active within timeout
            active = sum(1 for last_seen in self._active_users.values() if last_seen >= cutoff)
            return active
    
    def get_active_user_ids(self) -> List[str]:
        """
        Get list of active user IDs.
        
        Returns:
            List of active user identifiers
        """
        with self._lock:
            now = time.time()
            cutoff = now - self._user_timeout
            
            return [uid for uid, last_seen in self._active_users.items() if last_seen >= cutoff]
    
    # ==================== WEBSOCKET TRACKING ====================
    
    def increment_websocket_connections(self):
        """Increment WebSocket connection count"""
        with self._lock:
            self._websocket_connections += 1
            logger.debug("WebSocket connections: %d", self._websocket_connections)
    
    def decrement_websocket_connections(self):
        """Decrement WebSocket connection count"""
        with self._lock:
            if self._websocket_connections > 0:
                self._websocket_connections -= 1
            logger.debug("WebSocket connections: %d", self._websocket_connections)
    
    def get_websocket_connections(self) -> int:
        """
        Get current WebSocket connection count.
        
        Returns:
            Number of active WebSocket connections
        """
        with self._lock:
            return self._websocket_connections
    
    # ==================== SYSTEM RESOURCES ====================
    
    def get_memory_usage(self) -> Tuple[float, float]:
        """
        Get memory usage of current process.
        
        Returns:
            Tuple of (usage_pct, usage_mb)
        """
        try:
            mem_info = self._process.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)  # Convert bytes to MB
            
            # Get system memory for percentage
            system_mem = psutil.virtual_memory()
            mem_pct = (mem_info.rss / system_mem.total) * 100
            
            return (round(mem_pct, 2), round(mem_mb, 2))
        except Exception as e:
            logger.error("Failed to get memory usage: %s", e)
            return (0.0, 0.0)
    
    def get_cpu_usage(self) -> float:
        """
        Get CPU usage of current process.
        
        Returns:
            CPU usage percentage (0-100)
        """
        try:
            # Get CPU percentage over 0.1 second interval
            cpu_pct = self._process.cpu_percent(interval=0.1)
            return round(cpu_pct, 2)
        except Exception as e:
            logger.error("Failed to get CPU usage: %s", e)
            return 0.0
    
    # ==================== SNAPSHOT & HISTORY ====================
    
    def get_current_snapshot(self) -> MetricsSnapshot:
        """
        Get current metrics snapshot.
        
        Returns:
            MetricsSnapshot object with all current metrics
        """
        with self._lock:
            # Get all metrics
            request_rate = self.get_request_rate_rpm()
            error_rate = self.get_error_rate_pct()
            p50, p95, p99 = self.get_latency_percentiles()
            active_users = self.get_active_users()
            mem_pct, mem_mb = self.get_memory_usage()
            cpu_pct = self.get_cpu_usage()
            ws_conns = self.get_websocket_connections()
            
            snapshot = MetricsSnapshot(
                timestamp=datetime.now().isoformat(),
                request_rate_rpm=request_rate,
                error_rate_pct=error_rate,
                latency_p50_ms=p50,
                latency_p95_ms=p95,
                latency_p99_ms=p99,
                active_users=active_users,
                memory_usage_pct=mem_pct,
                memory_usage_mb=mem_mb,
                cpu_usage_pct=cpu_pct,
                websocket_connections=ws_conns,
                total_requests=self._total_requests,
                total_errors=self._total_errors
            )
            
            return snapshot
    
    def save_snapshot_to_history(self):
        """Save current snapshot to history"""
        snapshot = self.get_current_snapshot()
        with self._lock:
            self._metrics_history.append(snapshot)
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict]:
        """
        Get metrics history.
        
        Args:
            minutes: Number of minutes of history to return (max 60)
        
        Returns:
            List of metric snapshots as dictionaries
        """
        with self._lock:
            # Limit to available history
            count = min(minutes, len(self._metrics_history))
            recent = list(self._metrics_history)[-count:] if count > 0 else []
            return [s.to_dict() for s in recent]
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics.
        
        Returns:
            Dictionary with all statistics
        """
        snapshot = self.get_current_snapshot()
        
        with self._lock:
            stats = {
                'current': snapshot.to_dict(),
                'totals': {
                    'total_requests': self._total_requests,
                    'total_errors': self._total_errors,
                    'total_error_rate_pct': round(
                        (self._total_errors / self._total_requests * 100) if self._total_requests > 0 else 0,
                        2
                    )
                },
                'configuration': {
                    'window_seconds': self.window_seconds,
                    'user_timeout_seconds': self._user_timeout,
                    'max_history_minutes': 60
                }
            }
            
            return stats
    
    def reset_statistics(self):
        """Reset all statistics"""
        with self._lock:
            self._total_requests = 0
            self._total_errors = 0
            self._requests.clear()
            self._metrics_history.clear()
            logger.info("[+] Statistics reset")
    
    # ==================== EXPORT ====================
    
    def export_to_json(self, filepath: str):
        """
        Export current statistics to JSON file.
        
        Args:
            filepath: Path to output JSON file
        """
        stats = self.get_statistics()
        stats['history'] = self.get_metrics_history()
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info("[+] Metrics exported to %s", filepath)
    
    def export_to_csv(self, filepath: str):
        """
        Export metrics history to CSV file.
        
        Args:
            filepath: Path to output CSV file
        """
        import csv
        
        history = self.get_metrics_history()
        if not history:
            logger.warning("No metrics history to export")
            return
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)
        
        logger.info("[+] Metrics history exported to %s", filepath)
    
    # ==================== CLEANUP ====================
    
    def _cleanup_loop(self):
        """Background thread for cleanup and snapshot saving"""
        while True:
            try:
                # Sleep for 1 minute
                time.sleep(60)
                
                with self._lock:
                    # Clean up old user data
                    now = time.time()
                    cutoff = now - (self._user_timeout * 2)  # Double timeout for cleanup
                    
                    expired_users = [uid for uid, last_seen in self._active_users.items() 
                                    if last_seen < cutoff]
                    
                    for uid in expired_users:
                        del self._active_users[uid]
                    
                    if expired_users:
                        logger.debug("Cleaned up %d expired users", len(expired_users))
                
                # Save snapshot to history
                self.save_snapshot_to_history()
                
            except Exception as e:
                logger.error("Error in cleanup loop: %s", e)


# ==================== SINGLETON ====================

_metrics_monitor_instance = None
_metrics_monitor_lock = threading.Lock()


def get_metrics_monitor(window_seconds: int = 300) -> MetricsMonitor:
    """
    Get singleton MetricsMonitor instance.
    
    Args:
        window_seconds: Rolling window size (only used on first call)
    
    Returns:
        MetricsMonitor instance
    """
    global _metrics_monitor_instance
    
    if _metrics_monitor_instance is None:
        with _metrics_monitor_lock:
            if _metrics_monitor_instance is None:
                _metrics_monitor_instance = MetricsMonitor(window_seconds=window_seconds)
    
    return _metrics_monitor_instance


# ==================== FLASK MIDDLEWARE ====================

class MetricsMiddleware:
    """Flask middleware for automatic request tracking"""
    
    def __init__(self, app, metrics_monitor: Optional[MetricsMonitor] = None):
        """
        Initialize middleware.
        
        Args:
            app: Flask application
            metrics_monitor: MetricsMonitor instance (creates new if None)
        """
        self.app = app
        self.metrics = metrics_monitor or get_metrics_monitor()
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        logger.info("[+] MetricsMiddleware registered")
    
    def _before_request(self):
        """Record request start time"""
        from flask import g
        g.request_start_time = time.time()
    
    def _after_request(self, response):
        """Record request completion and metrics"""
        from flask import g, request, session
        
        # Calculate latency
        if hasattr(g, 'request_start_time'):
            latency_ms = (time.time() - g.request_start_time) * 1000
        else:
            latency_ms = 0
        
        # Determine if error
        is_error = response.status_code >= 400
        
        # Get user ID from session
        user_id = session.get('user')
        
        # Record metrics
        self.metrics.record_request(
            latency_ms=latency_ms,
            is_error=is_error,
            user_id=user_id
        )
        
        return response
