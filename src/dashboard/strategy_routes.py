#!/usr/bin/env python3
"""
Strategy Editor v4.4 - API Routes

RESTful API for strategy parameter management:
- GET  /strategies              - List all strategies
- GET  /strategies/<name>       - Get strategy parameters
- POST /strategies/<name>/param - Update parameter
- POST /strategies/<name>/preset- Apply preset
- POST /strategies/preset       - Apply preset to all
- GET  /history                 - Get change history
- POST /rollback                - Rollback configuration
- POST /estimate                - Estimate parameter impact
- POST /backtest                - Run quick backtest
- GET  /presets                 - Get available presets
- GET  /stats                   - Get editor statistics
- POST /export                  - Export configurations

Author: Juan Carlos Garcia Arriero
Date: 22 Enero 2026
Version: 4.4.0
"""

import logging
from flask import Blueprint, jsonify, request, render_template
from functools import wraps
from datetime import datetime
import json

from .strategy_editor import get_strategy_editor, PresetType

logger = logging.getLogger(__name__)

# Create Blueprint
strategy_bp = Blueprint('strategy_editor', __name__, url_prefix='/api/strategies')


# ==================== DECORATORS ====================

def login_required(f):
    """Require authentication (placeholder)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement actual authentication check
        # For now, always allow access
        return f(*args, **kwargs)
    return decorated_function


def audit_log(action: str):
    """Audit log decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                logger.info(f"✅ Strategy Editor: {action} - Success")
                return result
            except Exception as e:
                logger.error(f"❌ Strategy Editor: {action} - Failed: {str(e)}")
                raise
        return wrapper
    return decorator


# ==================== UI ROUTE ====================

@strategy_bp.route('/', methods=['GET'])
@login_required
def strategy_editor_ui():
    """Strategy Editor UI page"""
    return render_template('strategy_editor.html')


# ==================== API ROUTES ====================

@strategy_bp.route('/list', methods=['GET'])
@login_required
@audit_log('List strategies')
def list_strategies():
    """List all strategies
    
    Returns:
        JSON with strategy list
        
    Example:
        GET /api/strategies/list
    """
    try:
        editor = get_strategy_editor()
        strategies = editor.get_strategy_list()
        
        return jsonify({
            'success': True,
            'strategies': strategies,
            'count': len(strategies),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to list strategies: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/<strategy_name>', methods=['GET'])
@login_required
@audit_log('Get strategy parameters')
def get_strategy(strategy_name: str):
    """Get parameters for a specific strategy
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        JSON with strategy parameters
        
    Example:
        GET /api/strategies/RSI
    """
    try:
        editor = get_strategy_editor()
        strategy_data = editor.get_strategy_parameters(strategy_name)
        
        return jsonify({
            'success': True,
            'strategy': strategy_data,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 404
    
    except Exception as e:
        logger.error(f"Failed to get strategy {strategy_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/<strategy_name>/param', methods=['POST'])
@login_required
@audit_log('Update parameter')
def update_parameter(strategy_name: str):
    """Update a strategy parameter
    
    Args:
        strategy_name: Name of the strategy
        
    Request Body:
        {
            "parameter": "overbought",
            "value": 75.0,
            "user": "admin"
        }
        
    Returns:
        JSON with updated strategy
        
    Example:
        POST /api/strategies/RSI/param
        {"parameter": "overbought", "value": 75.0}
    """
    try:
        data = request.get_json()
        
        if not data or 'parameter' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: parameter, value',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        parameter = data['parameter']
        value = data['value']
        user = data.get('user', 'user')
        
        editor = get_strategy_editor()
        updated_strategy = editor.update_parameter(strategy_name, parameter, value, user)
        
        return jsonify({
            'success': True,
            'message': f'Parameter {parameter} updated',
            'strategy': updated_strategy,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    
    except Exception as e:
        logger.error(f"Failed to update parameter: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/<strategy_name>/preset', methods=['POST'])
@login_required
@audit_log('Apply preset')
def apply_preset_single(strategy_name: str):
    """Apply preset to a single strategy
    
    Args:
        strategy_name: Name of the strategy
        
    Request Body:
        {
            "preset": "conservative",
            "user": "admin"
        }
        
    Returns:
        JSON with updated strategy
        
    Example:
        POST /api/strategies/RSI/preset
        {"preset": "aggressive"}
    """
    try:
        data = request.get_json()
        
        if not data or 'preset' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: preset',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        preset_str = data['preset']
        user = data.get('user', 'user')
        
        try:
            preset = PresetType(preset_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid preset: {preset_str}. Valid options: conservative, balanced, aggressive',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        editor = get_strategy_editor()
        updated_strategy = editor.apply_preset(strategy_name, preset, user)
        
        return jsonify({
            'success': True,
            'message': f'Preset {preset.value} applied to {strategy_name}',
            'strategy': updated_strategy,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    
    except Exception as e:
        logger.error(f"Failed to apply preset: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/preset/all', methods=['POST'])
@login_required
@audit_log('Apply preset to all')
def apply_preset_all():
    """Apply preset to all strategies
    
    Request Body:
        {
            "preset": "balanced",
            "user": "admin"
        }
        
    Returns:
        JSON with all updated strategies
        
    Example:
        POST /api/strategies/preset/all
        {"preset": "balanced"}
    """
    try:
        data = request.get_json()
        
        if not data or 'preset' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: preset',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        preset_str = data['preset']
        user = data.get('user', 'user')
        
        try:
            preset = PresetType(preset_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid preset: {preset_str}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        editor = get_strategy_editor()
        result = editor.apply_preset('all', preset, user)
        
        return jsonify({
            'success': True,
            'message': f'Preset {preset.value} applied to all strategies',
            'strategies': result['strategies'],
            'count': len(result['strategies']),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to apply preset to all: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/history', methods=['GET'])
@login_required
@audit_log('Get change history')
def get_history():
    """Get change history
    
    Query Parameters:
        strategy: Filter by strategy name (optional)
        limit: Maximum number of changes (default: 50)
        
    Returns:
        JSON with change history
        
    Example:
        GET /api/strategies/history?strategy=RSI&limit=20
    """
    try:
        strategy_name = request.args.get('strategy')
        limit = int(request.args.get('limit', 50))
        
        editor = get_strategy_editor()
        history = editor.get_change_history(strategy_name, limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get change history: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/rollback', methods=['POST'])
@login_required
@audit_log('Rollback configuration')
def rollback():
    """Rollback to a previous configuration
    
    Request Body:
        {
            "strategy": "RSI",
            "timestamp": "2026-01-22T10:30:00",
            "user": "admin"
        }
        
    Returns:
        JSON with rolled back strategy
        
    Example:
        POST /api/strategies/rollback
        {"strategy": "RSI", "timestamp": "2026-01-22T10:30:00"}
    """
    try:
        data = request.get_json()
        
        if not data or 'strategy' not in data or 'timestamp' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: strategy, timestamp',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        strategy_name = data['strategy']
        timestamp = data['timestamp']
        user = data.get('user', 'user')
        
        editor = get_strategy_editor()
        updated_strategy = editor.rollback_change(strategy_name, timestamp, user)
        
        return jsonify({
            'success': True,
            'message': f'Configuration rolled back to {timestamp}',
            'strategy': updated_strategy,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    
    except Exception as e:
        logger.error(f"Failed to rollback: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/estimate', methods=['POST'])
@login_required
@audit_log('Estimate impact')
def estimate_impact():
    """Estimate impact of parameter change
    
    Request Body:
        {
            "strategy": "RSI",
            "parameter": "overbought",
            "value": 75.0
        }
        
    Returns:
        JSON with impact estimation
        
    Example:
        POST /api/strategies/estimate
        {"strategy": "RSI", "parameter": "overbought", "value": 75.0}
    """
    try:
        data = request.get_json()
        
        if not data or 'strategy' not in data or 'parameter' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: strategy, parameter, value',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        strategy_name = data['strategy']
        parameter = data['parameter']
        value = data['value']
        
        editor = get_strategy_editor()
        impact = editor.estimate_impact(strategy_name, parameter, value)
        
        return jsonify({
            'success': True,
            'impact': impact,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    
    except Exception as e:
        logger.error(f"Failed to estimate impact: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/<strategy_name>/backtest', methods=['POST'])
@login_required
@audit_log('Quick backtest')
def quick_backtest(strategy_name: str):
    """Run quick backtest with current parameters
    
    Args:
        strategy_name: Name of the strategy
        
    Request Body:
        {
            "days": 7
        }
        
    Returns:
        JSON with backtest results
        
    Example:
        POST /api/strategies/RSI/backtest
        {"days": 7}
    """
    try:
        data = request.get_json() or {}
        days = data.get('days', 7)
        
        editor = get_strategy_editor()
        results = editor.quick_backtest(strategy_name, days)
        
        return jsonify({
            'success': True,
            'backtest': results,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    
    except Exception as e:
        logger.error(f"Failed to run backtest: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/presets', methods=['GET'])
@login_required
@audit_log('Get presets')
def get_presets():
    """Get available presets
    
    Returns:
        JSON with preset definitions
        
    Example:
        GET /api/strategies/presets
    """
    try:
        presets = {
            'conservative': {
                'name': 'Conservative',
                'description': 'Lower risk, fewer signals, wider thresholds',
                'icon': '🛡️',
                'color': '#10b981'
            },
            'balanced': {
                'name': 'Balanced',
                'description': 'Standard parameters, moderate risk/reward',
                'icon': '⚖️',
                'color': '#2f81f7'
            },
            'aggressive': {
                'name': 'Aggressive',
                'description': 'Higher risk, more signals, tighter thresholds',
                'icon': '🔥',
                'color': '#f85149'
            }
        }
        
        return jsonify({
            'success': True,
            'presets': presets,
            'count': len(presets),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get presets: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/stats', methods=['GET'])
@login_required
@audit_log('Get statistics')
def get_stats():
    """Get editor statistics
    
    Returns:
        JSON with statistics
        
    Example:
        GET /api/strategies/stats
    """
    try:
        editor = get_strategy_editor()
        stats = editor.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@strategy_bp.route('/export', methods=['POST'])
@login_required
@audit_log('Export configurations')
def export_configurations():
    """Export all strategy configurations
    
    Request Body:
        {
            "format": "json",  // or "yaml"
            "include_history": false
        }
        
    Returns:
        JSON with exported configurations
        
    Example:
        POST /api/strategies/export
        {"format": "json", "include_history": true}
    """
    try:
        data = request.get_json() or {}
        format_type = data.get('format', 'json')
        include_history = data.get('include_history', False)
        
        editor = get_strategy_editor()
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'version': '4.4.0',
            'strategies': {}
        }
        
        # Export all strategies
        for strategy_name in editor.strategies.keys():
            strategy_data = editor.get_strategy_parameters(strategy_name)
            export_data['strategies'][strategy_name] = strategy_data
        
        # Optionally include history
        if include_history:
            export_data['history'] = editor.get_change_history(limit=1000)
        
        # Add statistics
        export_data['statistics'] = editor.get_statistics()
        
        return jsonify({
            'success': True,
            'export': export_data,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to export configurations: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# ==================== ERROR HANDLERS ====================

@strategy_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404


@strategy_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500
