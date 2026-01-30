#!/usr/bin/env python3
"""Metrics API Routes v2.0

Comprehensive REST API endpoints for application metrics monitoring.
Integrates with MetricsMonitor for real-time and historical metrics.

Author: Juan Carlos Garcia Arriero
Date: 30 Enero 2026
Version: 2.0.0
"""

import logging
from flask import Blueprint, jsonify, request, session, send_file
from functools import wraps
from datetime import datetime
import tempfile
import os

from .metrics_monitor import get_metrics_monitor, setup_metrics_for_app

logger = logging.getLogger(__name__)

# Create blueprint
metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')


# ==================== DECORATORS ====================

def login_required(f):
    """Require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow bypass in demo mode
        demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        if not demo_mode and 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require admin role for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        if demo_mode:
            return f(*args, **kwargs)
        
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_role = session.get('role', 'user')
        if user_role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== CORE METRICS ENDPOINTS ====================

@metrics_bp.route('/current', methods=['GET'])
@login_required
def get_current_metrics():
    """
    Get current metrics snapshot.
    
    Returns comprehensive real-time metrics including:
    - Request rate (RPM)
    - Error rate and breakdown
    - Latency percentiles (p50, p95, p99)
    - Active users and sessions
    - WebSocket statistics
    - System resources (CPU, memory, disk)
    - Trading metrics (positions, P&L)
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        return jsonify({
            'success': True,
            'metrics': snapshot.to_dict(),
            'timestamp': datetime.now().isoformat(),
            'version': monitor.VERSION
        })
    
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/history', methods=['GET'])
@login_required
def get_metrics_history():
    """
    Get metrics history for time-series visualization.
    
    Query params:
    - minutes: Number of minutes of history (default: 60, max: 60)
    
    Returns array of MetricsSnapshot objects for charting.
    """
    try:
        monitor = get_metrics_monitor()
        
        # Parse query parameters
        minutes = min(int(request.args.get('minutes', 60)), 60)
        
        # Get history
        history = monitor.get_metrics_history(minutes=minutes)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'minutes': minutes,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/statistics', methods=['GET'])
@login_required
def get_metrics_statistics():
    """
    Get comprehensive metrics statistics.
    
    Returns:
    - current: Current snapshot
    - totals: Cumulative totals since start
    - error_breakdown: Errors by type
    - endpoints: Per-endpoint statistics
    - configuration: Monitor configuration
    """
    try:
        monitor = get_metrics_monitor()
        stats = monitor.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== DETAILED METRICS ENDPOINTS ====================

@metrics_bp.route('/requests', methods=['GET'])
@login_required
def get_request_history():
    """
    Get recent request history.
    
    Query params:
    - limit: Maximum number of requests (default: 100, max: 500)
    
    Returns detailed request records with path, method, status, latency.
    """
    try:
        monitor = get_metrics_monitor()
        limit = min(int(request.args.get('limit', 100)), 500)
        
        history = monitor.get_request_history(limit=limit)
        
        return jsonify({
            'success': True,
            'requests': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting request history: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/errors', methods=['GET'])
@login_required
def get_error_history():
    """
    Get recent error history.
    
    Query params:
    - limit: Maximum number of errors (default: 50, max: 200)
    
    Returns detailed error records with type, message, stack trace.
    """
    try:
        monitor = get_metrics_monitor()
        limit = min(int(request.args.get('limit', 50)), 200)
        
        history = monitor.get_error_history(limit=limit)
        
        return jsonify({
            'success': True,
            'errors': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting error history: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/endpoints', methods=['GET'])
@login_required
def get_endpoint_statistics():
    """
    Get per-endpoint statistics.
    
    Returns statistics for each API endpoint:
    - Request count
    - Average/min/max latency
    - Error count and rate
    """
    try:
        monitor = get_metrics_monitor()
        stats = monitor.get_endpoint_statistics()
        
        # Sort by request count descending
        sorted_stats = dict(
            sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)
        )
        
        return jsonify({
            'success': True,
            'endpoints': sorted_stats,
            'count': len(sorted_stats),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting endpoint statistics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/latency', methods=['GET'])
@login_required
def get_latency_metrics():
    """
    Get detailed latency metrics.
    
    Returns latency statistics for performance monitoring:
    - Average, min, max latency
    - Percentiles (p50, p95, p99)
    - Latency by endpoint
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        endpoint_stats = monitor.get_endpoint_statistics()
        
        # Extract latency data per endpoint
        endpoint_latency = {
            endpoint: {
                'avg_ms': stats['avg_latency_ms'],
                'min_ms': stats['min_latency_ms'],
                'max_ms': stats['max_latency_ms']
            }
            for endpoint, stats in endpoint_stats.items()
        }
        
        return jsonify({
            'success': True,
            'latency': {
                'current': {
                    'avg_ms': snapshot.avg_latency_ms,
                    'p50_ms': snapshot.latency_p50_ms,
                    'p95_ms': snapshot.latency_p95_ms,
                    'p99_ms': snapshot.latency_p99_ms,
                    'min_ms': snapshot.min_latency_ms,
                    'max_ms': snapshot.max_latency_ms
                },
                'by_endpoint': endpoint_latency
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting latency metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/system', methods=['GET'])
@login_required
def get_system_metrics():
    """
    Get system resource metrics.
    
    Returns current resource utilization:
    - CPU usage percentage
    - Memory usage (percent, MB, available)
    - Disk usage percentage
    - Uptime
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        return jsonify({
            'success': True,
            'system': {
                'cpu_usage_pct': snapshot.cpu_usage_pct,
                'memory': {
                    'usage_pct': snapshot.memory_usage_pct,
                    'usage_mb': snapshot.memory_usage_mb,
                    'available_mb': snapshot.memory_available_mb
                },
                'disk_usage_pct': snapshot.disk_usage_pct,
                'uptime_seconds': snapshot.uptime_seconds,
                'uptime_formatted': _format_uptime(snapshot.uptime_seconds)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/trading', methods=['GET'])
@login_required
def get_trading_metrics():
    """
    Get trading-specific metrics.
    
    Returns:
    - Open positions count
    - Total trades today
    - P&L today
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        return jsonify({
            'success': True,
            'trading': {
                'open_positions': snapshot.open_positions,
                'total_trades_today': snapshot.total_trades_today,
                'pnl_today': snapshot.pnl_today,
                'pnl_formatted': f"${snapshot.pnl_today:,.2f}"
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting trading metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/websockets', methods=['GET'])
@login_required
def get_websocket_metrics():
    """
    Get WebSocket metrics.
    
    Returns:
    - Active connections
    - Messages sent/received
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        return jsonify({
            'success': True,
            'websockets': {
                'connections': snapshot.websocket_connections,
                'messages_sent': snapshot.websocket_messages_sent,
                'messages_received': snapshot.websocket_messages_received,
                'total_messages': snapshot.websocket_messages_sent + snapshot.websocket_messages_received
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting WebSocket metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== ADMIN ENDPOINTS ====================

@metrics_bp.route('/reset', methods=['POST'])
@admin_required
def reset_metrics():
    """
    Reset all metrics statistics.
    Requires admin privileges.
    """
    try:
        monitor = get_metrics_monitor()
        monitor.reset_statistics()
        
        logger.info(f"Metrics reset by user: {session.get('user', 'unknown')}")
        
        return jsonify({
            'success': True,
            'message': 'Metrics statistics reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/trading/update', methods=['POST'])
@login_required
def update_trading_metrics():
    """
    Update trading metrics.
    
    Request body:
    - open_positions: int (optional)
    - trade_executed: bool (optional)
    - pnl_change: float (optional)
    """
    try:
        monitor = get_metrics_monitor()
        data = request.get_json() or {}
        
        monitor.update_trading_metrics(
            open_positions=data.get('open_positions'),
            trade_executed=data.get('trade_executed', False),
            pnl_change=data.get('pnl_change', 0.0)
        )
        
        return jsonify({
            'success': True,
            'message': 'Trading metrics updated',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error updating trading metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== EXPORT ENDPOINTS ====================

@metrics_bp.route('/export/json', methods=['GET'])
@login_required
def export_metrics_json():
    """
    Export all metrics to JSON file.
    """
    try:
        monitor = get_metrics_monitor()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        # Export to temp file
        monitor.export_to_json(temp_path)
        
        # Send file
        return send_file(
            temp_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    
    except Exception as e:
        logger.error(f"Error exporting metrics to JSON: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temp file
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass


@metrics_bp.route('/export/csv', methods=['GET'])
@login_required
def export_metrics_csv():
    """
    Export metrics history to CSV file.
    """
    try:
        monitor = get_metrics_monitor()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        # Export to temp file
        monitor.export_to_csv(temp_path)
        
        # Send file
        return send_file(
            temp_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'metrics_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        logger.error(f"Error exporting metrics to CSV: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temp file
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass


# ==================== HEALTH CHECK ====================

@metrics_bp.route('/health', methods=['GET'])
def metrics_health():
    """
    Health check endpoint for metrics system.
    No authentication required.
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        # Determine health status based on metrics
        status = 'healthy'
        issues = []
        
        if snapshot.error_rate_pct > 10:
            status = 'degraded'
            issues.append(f"High error rate: {snapshot.error_rate_pct}%")
        
        if snapshot.latency_p99_ms > 5000:
            status = 'degraded'
            issues.append(f"High latency: {snapshot.latency_p99_ms}ms (p99)")
        
        if snapshot.cpu_usage_pct > 90:
            status = 'degraded'
            issues.append(f"High CPU usage: {snapshot.cpu_usage_pct}%")
        
        if snapshot.memory_usage_pct > 90:
            status = 'degraded'
            issues.append(f"High memory usage: {snapshot.memory_usage_pct}%")
        
        return jsonify({
            'success': True,
            'status': status,
            'version': monitor.VERSION,
            'components': {
                'metrics_monitor': 'operational',
                'request_tracking': 'operational',
                'resource_monitoring': 'operational',
                'websocket_tracking': 'operational',
                'background_collection': 'operational'
            },
            'summary': {
                'request_rate_rpm': snapshot.request_rate_rpm,
                'error_rate_pct': snapshot.error_rate_pct,
                'latency_p95_ms': snapshot.latency_p95_ms,
                'active_users': snapshot.active_users,
                'websocket_connections': snapshot.websocket_connections
            },
            'issues': issues,
            'uptime_seconds': snapshot.uptime_seconds,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Metrics health check failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# ==================== UTILITY FUNCTIONS ====================

def _format_uptime(seconds: float) -> str:
    """Format uptime seconds into human-readable string"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    
    return " ".join(parts)
