#!/usr/bin/env python3
"""
Monitoring Routes v4.3 - API endpoints for Live Monitoring

Provides REST and WebSocket endpoints for:
- Activity log streaming
- Strategy signals
- Open positions monitoring
- Browser alerts

Author: Juan Carlos Garcia Arriero
Date: 22 Enero 2026
Version: 4.3.0
"""

import logging
from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from functools import wraps
from datetime import datetime
from typing import Dict, Any

from .live_monitor import (
    get_live_monitor,
    EventType,
    AlertSeverity,
    StrategySignal,
    OpenPosition
)

logger = logging.getLogger(__name__)

# Create blueprint WITHOUT url_prefix for UI route
monitoring_bp = Blueprint('monitoring', __name__)


# ==================== DECORATORS ====================

def login_required(f):
    """Require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def login_required_ui(f):
    """Decorator for UI routes requiring login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== UI ROUTE ====================

@monitoring_bp.route('/monitoring', methods=['GET'])
@login_required_ui
def monitoring_ui():
    """Live Monitoring UI page"""
    return render_template('monitoring.html', user=session.get('user'))


# ==================== ACTIVITY LOG ENDPOINTS ====================

@monitoring_bp.route('/api/monitoring/activity', methods=['GET'])
@login_required
def get_activity_log():
    """
    Get recent activity events.
    
    Query params:
    - event_type: Filter by event type (optional)
    - limit: Max number of events (default: 50)
    
    Returns:
        JSON with activity events
    """
    try:
        monitor = get_live_monitor()
        
        # Parse query parameters
        event_type_str = request.args.get('event_type')
        limit = int(request.args.get('limit', 50))
        
        # Convert event type string to enum
        event_type = None
        if event_type_str:
            try:
                event_type = EventType(event_type_str)
            except ValueError:
                return jsonify({'error': f'Invalid event_type: {event_type_str}'}), 400
        
        # Get activity log
        events = monitor.get_activity_log(event_type=event_type, limit=limit)
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting activity log: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/monitoring/activity/clear', methods=['POST'])
@login_required
def clear_activity_log():
    """
    Clear all activity events.
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_live_monitor()
        monitor.clear_activity_log()
        
        return jsonify({
            'success': True,
            'message': 'Activity log cleared',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error clearing activity log: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== STRATEGY SIGNALS ENDPOINTS ====================

@monitoring_bp.route('/api/monitoring/signals', methods=['GET'])
@login_required
def get_strategy_signals():
    """
    Get current strategy signals.
    
    Query params:
    - strategy: Filter by strategy name (optional)
    
    Returns:
        JSON with strategy signals
    """
    try:
        monitor = get_live_monitor()
        
        # Parse query parameters
        strategy_name = request.args.get('strategy')
        
        # Get signals
        signals = monitor.get_strategy_signals(strategy_name=strategy_name)
        
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting strategy signals: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/monitoring/signals/update', methods=['POST'])
@login_required
def update_strategy_signal():
    """
    Update a strategy signal.
    
    Body:
        {
            "strategy_name": "MA_Crossover",
            "symbol": "BTCUSDT",
            "signal_type": "BUY",
            "confidence": 0.85,
            "indicators": {"sma_50": 50000, "sma_200": 48000},
            "ensemble_vote": "BUY"
        }
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_live_monitor()
        data = request.get_json()
        
        # Validate required fields
        required = ['strategy_name', 'symbol', 'signal_type', 'confidence']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create signal object
        signal = StrategySignal(
            strategy_name=data['strategy_name'],
            symbol=data['symbol'],
            signal_type=data['signal_type'],
            confidence=float(data['confidence']),
            timestamp=datetime.now(),
            indicators=data.get('indicators', {}),
            ensemble_vote=data.get('ensemble_vote')
        )
        
        # Update signal
        monitor.update_signal(signal)
        
        return jsonify({
            'success': True,
            'message': 'Signal updated',
            'signal': signal.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error updating strategy signal: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/monitoring/signals/clear', methods=['POST'])
@login_required
def clear_strategy_signals():
    """
    Clear all strategy signals.
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_live_monitor()
        monitor.clear_signals()
        
        return jsonify({
            'success': True,
            'message': 'Strategy signals cleared',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error clearing strategy signals: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== POSITIONS ENDPOINTS ====================

@monitoring_bp.route('/api/monitoring/positions', methods=['GET'])
@login_required
def get_open_positions():
    """
    Get all open positions.
    
    Returns:
        JSON with open positions
    """
    try:
        monitor = get_live_monitor()
        
        # Get positions
        positions = monitor.get_open_positions()
        
        # Calculate summary statistics
        total_unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
        avg_pnl_pct = sum(p['unrealized_pnl_pct'] for p in positions) / len(positions) if positions else 0
        
        return jsonify({
            'success': True,
            'positions': positions,
            'count': len(positions),
            'summary': {
                'total_unrealized_pnl': round(total_unrealized_pnl, 2),
                'avg_pnl_pct': round(avg_pnl_pct, 2)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting open positions: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/monitoring/positions/update', methods=['POST'])
@login_required
def update_position():
    """
    Update an open position.
    
    Body:
        {
            "position_id": "pos_123",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "entry_price": 50000,
            "current_price": 51000,
            "size": 0.1,
            "unrealized_pnl": 100,
            "unrealized_pnl_pct": 2.0,
            "time_in_position": "01:30:00",
            "stop_loss": 49000,
            "stop_loss_pct": 50,
            "take_profit": 52000,
            "strategy": "MA_Crossover"
        }
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_live_monitor()
        data = request.get_json()
        
        # Validate required fields
        required = ['position_id', 'symbol', 'side', 'entry_price', 'current_price', 
                   'size', 'unrealized_pnl', 'unrealized_pnl_pct', 'time_in_position',
                   'stop_loss', 'stop_loss_pct']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse time_in_position (format: HH:MM:SS)
        from datetime import timedelta
        time_parts = data['time_in_position'].split(':')
        time_in_position = timedelta(
            hours=int(time_parts[0]),
            minutes=int(time_parts[1]),
            seconds=int(time_parts[2])
        )
        
        # Create position object
        position = OpenPosition(
            position_id=data['position_id'],
            symbol=data['symbol'],
            side=data['side'],
            entry_price=float(data['entry_price']),
            current_price=float(data['current_price']),
            size=float(data['size']),
            unrealized_pnl=float(data['unrealized_pnl']),
            unrealized_pnl_pct=float(data['unrealized_pnl_pct']),
            time_in_position=time_in_position,
            stop_loss=float(data['stop_loss']),
            stop_loss_pct=float(data['stop_loss_pct']),
            take_profit=float(data['take_profit']) if data.get('take_profit') else None,
            strategy=data.get('strategy')
        )
        
        # Update position
        monitor.update_position(position)
        
        return jsonify({
            'success': True,
            'message': 'Position updated',
            'position': position.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error updating position: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/monitoring/positions/close', methods=['POST'])
@login_required
def close_position():
    """
    Close a position.
    
    Body:
        {
            "position_id": "pos_123",
            "final_pnl": 100,
            "final_pnl_pct": 2.0
        }
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_live_monitor()
        data = request.get_json()
        
        # Validate required fields
        required = ['position_id', 'final_pnl', 'final_pnl_pct']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Close position
        monitor.close_position(
            position_id=data['position_id'],
            final_pnl=float(data['final_pnl']),
            final_pnl_pct=float(data['final_pnl_pct'])
        )
        
        return jsonify({
            'success': True,
            'message': 'Position closed',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error closing position: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== ALERTS ENDPOINTS ====================

@monitoring_bp.route('/api/monitoring/alerts', methods=['GET'])
@login_required
def get_pending_alerts():
    """
    Get pending browser alerts.
    
    Query params:
    - clear: Clear alerts after retrieval (default: true)
    
    Returns:
        JSON with pending alerts
    """
    try:
        monitor = get_live_monitor()
        
        # Parse query parameters
        clear = request.args.get('clear', 'true').lower() == 'true'
        
        # Get alerts
        alerts = monitor.get_pending_alerts(clear=clear)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting pending alerts: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== STATISTICS ENDPOINTS ====================

@monitoring_bp.route('/api/monitoring/stats', methods=['GET'])
@login_required
def get_monitoring_statistics():
    """
    Get monitoring statistics.
    
    Returns:
        JSON with statistics
    """
    try:
        monitor = get_live_monitor()
        
        # Get statistics
        stats = monitor.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting monitoring statistics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/monitoring/stats/reset', methods=['POST'])
@login_required
def reset_monitoring_statistics():
    """
    Reset monitoring statistics.
    
    Returns:
        JSON confirmation
    """
    try:
        monitor = get_live_monitor()
        monitor.reset_statistics()
        
        return jsonify({
            'success': True,
            'message': 'Statistics reset',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error resetting statistics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@monitoring_bp.route('/api/monitoring/health', methods=['GET'])
def monitoring_health():
    """
    Health check endpoint for monitoring system.
    
    Returns:
        JSON with health status
    """
    try:
        monitor = get_live_monitor()
        stats = monitor.get_statistics()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'version': '4.3.0',
            'uptime': stats.get('last_update'),
            'components': {
                'activity_log': 'operational',
                'strategy_signals': 'operational',
                'position_monitor': 'operational',
                'alerts_system': 'operational'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
