#!/usr/bin/env python3
"""Metrics API Routes v1.0

REST API endpoints for metrics monitoring.

Author: Juan Carlos Garcia Arriero
Date: 25 Enero 2026
Version: 1.0.0
"""

import logging
from flask import Blueprint, jsonify, request, session, send_file
from functools import wraps
from datetime import datetime
import tempfile
import os

from .metrics_monitor import get_metrics_monitor

logger = logging.getLogger(__name__)

# Create blueprint
metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')


# ==================== DECORATORS ====================

def login_required(f):
    """Require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== ENDPOINTS ====================

@metrics_bp.route('/current', methods=['GET'])
@login_required
def get_current_metrics():
    """
    Get current metrics snapshot.
    
    Returns:
        JSON with current metrics:
        - request_rate_rpm: Requests per minute
        - error_rate_pct: Error rate percentage
        - latency_p50_ms: 50th percentile latency
        - latency_p95_ms: 95th percentile latency
        - latency_p99_ms: 99th percentile latency
        - active_users: Number of active users
        - memory_usage_pct: Memory usage percentage
        - memory_usage_mb: Memory usage in MB
        - cpu_usage_pct: CPU usage percentage
        - websocket_connections: Active WebSocket connections
        - total_requests: Total requests since start
        - total_errors: Total errors since start
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        return jsonify({
            'success': True,
            'metrics': snapshot.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/history', methods=['GET'])
@login_required
def get_metrics_history():
    """
    Get metrics history.
    
    Query params:
    - minutes: Number of minutes of history (default: 60, max: 60)
    
    Returns:
        JSON with metrics history array
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
        JSON with:
        - current: Current snapshot
        - totals: Total requests, errors, error rate
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


@metrics_bp.route('/reset', methods=['POST'])
@login_required
def reset_metrics():
    """
    Reset all metrics statistics.
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_metrics_monitor()
        monitor.reset_statistics()
        
        return jsonify({
            'success': True,
            'message': 'Metrics statistics reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/export/json', methods=['GET'])
@login_required
def export_metrics_json():
    """
    Export metrics to JSON file.
    
    Returns:
        JSON file download
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
    
    Returns:
        CSV file download
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


@metrics_bp.route('/health', methods=['GET'])
def metrics_health():
    """
    Health check endpoint for metrics system.
    
    Returns:
        JSON with health status
    """
    try:
        monitor = get_metrics_monitor()
        snapshot = monitor.get_current_snapshot()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'version': '1.0.0',
            'components': {
                'metrics_monitor': 'operational',
                'request_tracking': 'operational',
                'resource_monitoring': 'operational',
                'websocket_tracking': 'operational'
            },
            'current_rpm': snapshot.request_rate_rpm,
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
