#!/usr/bin/env python3
"""
Metrics Monitor - System and application metrics collection

Provides monitoring for:
- Request rates and latencies
- Error tracking
- Resource usage (CPU, Memory)
- WebSocket connections
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
from collections import deque

logger = logging.getLogger(__name__)

# Singleton instance
_monitor_instance = None


@dataclass
class MetricsSnapshot:
    """Point-in-time metrics snapshot"""
    timestamp: str
    request_rate_rpm: float = 0.0
    error_rate_pct: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    active_users: int = 0
    memory_usage_pct: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_pct: float = 0.0
    websocket_connections: int = 0
    total_requests: int = 0
    total_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetricsMonitor:
    """
    Monitors system and application metrics.
    
    Collects and aggregates metrics for dashboard display.
    In demo mode, generates simulated metrics.
    """
    
    def __init__(self, history_minutes: int = 60):
        self.history_minutes = history_minutes
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Metrics storage
        self._history: deque = deque(maxlen=history_minutes * 60)  # Per-second resolution
        self._request_times: deque = deque(maxlen=10000)  # Recent request latencies
        self._lock = threading.Lock()
        
        # Counters
        self._total_requests = 0
        self._total_errors = 0
        self._start_time = datetime.now()
        
        # Active tracking
        self._active_users: set = set()
        self._websocket_connections = 0
        
        logger.info(f"MetricsMonitor initialized (demo={self.demo_mode})")
    
    def record_request(self, latency_ms: float, is_error: bool = False, user_id: Optional[str] = None):
        """
        Record a request.
        
        Args:
            latency_ms: Request latency in milliseconds
            is_error: Whether the request resulted in an error
            user_id: Optional user identifier for active user tracking
        """
        with self._lock:
            self._total_requests += 1
            if is_error:
                self._total_errors += 1
            
            self._request_times.append({
                'timestamp': datetime.now(),
                'latency_ms': latency_ms,
                'is_error': is_error
            })
            
            if user_id:
                self._active_users.add(user_id)
    
    def update_websocket_count(self, count: int):
        """Update active WebSocket connection count"""
        with self._lock:
            self._websocket_connections = count
    
    def get_current_snapshot(self) -> MetricsSnapshot:
        """
        Get current metrics snapshot.
        
        Returns:
            MetricsSnapshot with current metrics
        """
        if self.demo_mode:
            return self._generate_demo_snapshot()
        
        with self._lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            # Filter recent requests
            recent_requests = [
                r for r in self._request_times
                if r['timestamp'] > one_minute_ago
            ]
            
            # Calculate request rate
            request_rate = len(recent_requests)
            
            # Calculate error rate
            recent_errors = sum(1 for r in recent_requests if r['is_error'])
            error_rate = (recent_errors / request_rate * 100) if request_rate > 0 else 0
            
            # Calculate latencies
            latencies = sorted([r['latency_ms'] for r in recent_requests]) if recent_requests else [0]
            p50 = self._percentile(latencies, 50)
            p95 = self._percentile(latencies, 95)
            p99 = self._percentile(latencies, 99)
            
            # Get resource usage
            memory_usage = self._get_memory_usage()
            cpu_usage = self._get_cpu_usage()
            
            return MetricsSnapshot(
                timestamp=now.isoformat(),
                request_rate_rpm=request_rate,
                error_rate_pct=error_rate,
                latency_p50_ms=p50,
                latency_p95_ms=p95,
                latency_p99_ms=p99,
                active_users=len(self._active_users),
                memory_usage_pct=memory_usage['percent'],
                memory_usage_mb=memory_usage['mb'],
                cpu_usage_pct=cpu_usage,
                websocket_connections=self._websocket_connections,
                total_requests=self._total_requests,
                total_errors=self._total_errors
            )
    
    def _generate_demo_snapshot(self) -> MetricsSnapshot:
        """Generate demo metrics for testing"""
        import random
        
        now = datetime.now()
        
        # Generate realistic demo values with some variance
        base_rpm = 100 + random.randint(-20, 30)
        
        return MetricsSnapshot(
            timestamp=now.isoformat(),
            request_rate_rpm=base_rpm,
            error_rate_pct=round(random.uniform(0.1, 2.0), 2),
            latency_p50_ms=round(random.uniform(15, 50), 1),
            latency_p95_ms=round(random.uniform(80, 200), 1),
            latency_p99_ms=round(random.uniform(150, 400), 1),
            active_users=random.randint(3, 15),
            memory_usage_pct=round(random.uniform(35, 65), 1),
            memory_usage_mb=round(random.uniform(200, 500), 1),
            cpu_usage_pct=round(random.uniform(10, 45), 1),
            websocket_connections=random.randint(1, 8),
            total_requests=10000 + random.randint(0, 1000),
            total_errors=random.randint(10, 100)
        )
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict]:
        """
        Get metrics history.
        
        Args:
            minutes: Number of minutes of history to return
        
        Returns:
            List of metrics snapshots
        """
        if self.demo_mode:
            # Generate demo history
            history = []
            now = datetime.now()
            for i in range(minutes):
                snapshot = self._generate_demo_snapshot()
                snapshot.timestamp = (now - timedelta(minutes=minutes-i)).isoformat()
                history.append(snapshot.to_dict())
            return history
        
        with self._lock:
            # Return recent history
            history_list = list(self._history)
            return history_list[-minutes:] if len(history_list) > minutes else history_list
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.
        
        Returns:
            Dict with current, totals, and configuration
        """
        snapshot = self.get_current_snapshot()
        
        error_rate = (self._total_errors / self._total_requests * 100) if self._total_requests > 0 else 0
        
        return {
            'current': snapshot.to_dict(),
            'totals': {
                'requests': self._total_requests,
                'errors': self._total_errors,
                'error_rate_pct': round(error_rate, 2),
                'uptime_seconds': (datetime.now() - self._start_time).total_seconds()
            },
            'configuration': {
                'history_minutes': self.history_minutes,
                'demo_mode': self.demo_mode
            }
        }
    
    def reset_statistics(self):
        """Reset all statistics"""
        with self._lock:
            self._total_requests = 0
            self._total_errors = 0
            self._request_times.clear()
            self._history.clear()
            self._active_users.clear()
            self._start_time = datetime.now()
            
            logger.info("Metrics statistics reset")
    
    def export_to_json(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'history': self.get_metrics_history()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_to_csv(self, filepath: str):
        """Export metrics history to CSV file"""
        history = self.get_metrics_history()
        
        if not history:
            return
        
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data"""
        if not data:
            return 0.0
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = f + 1 if f + 1 < len(data) else f
        return data[f] + (data[c] - data[f]) * (k - f)
    
    @staticmethod
    def _get_memory_usage() -> Dict[str, float]:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_percent = process.memory_percent()
            return {
                'percent': round(mem_percent, 1),
                'mb': round(mem_info.rss / 1024 / 1024, 1)
            }
        except ImportError:
            return {'percent': 0.0, 'mb': 0.0}
    
    @staticmethod
    def _get_cpu_usage() -> float:
        """Get current CPU usage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0


def get_metrics_monitor() -> MetricsMonitor:
    """
    Get the singleton MetricsMonitor instance.
    
    Returns:
        MetricsMonitor instance
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = MetricsMonitor()
    
    return _monitor_instance
