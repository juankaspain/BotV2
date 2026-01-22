#!/usr/bin/env python3
"""
BotV2 - Control Panel API Routes v4.2

Provides REST API endpoints for dashboard control panel.
"""

from flask import Blueprint, jsonify, request
from functools import wraps
import logging
import yaml
from pathlib import Path
from typing import Dict, Any

from .bot_controller import get_bot_controller

logger = logging.getLogger(__name__)

# Create blueprint
control_bp = Blueprint('control', __name__, url_prefix='/api/control')


def error_handler(f):
    """Decorator for error handling"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Internal error: {str(e)}'
            }), 500
    return decorated


# ==================== BOT CONTROL ENDPOINTS ====================

@control_bp.route('/status', methods=['GET'])
@error_handler
def get_bot_status():
    """
    Get current bot status
    
    Returns:
        {
            "success": true,
            "data": {
                "status": "running|stopped|paused",
                "pid": 12345,
                "uptime": 3600,
                "start_time": "2026-01-22T20:00:00",
                "is_trading": true
            }
        }
    """
    controller = get_bot_controller()
    status = controller.get_status()
    
    return jsonify({
        'success': True,
        'data': status
    })


@control_bp.route('/start', methods=['POST'])
@error_handler
def start_bot():
    """
    Start the bot
    
    Returns:
        {
            "success": true,
            "message": "Bot started successfully",
            "data": {"pid": 12345}
        }
    """
    controller = get_bot_controller()
    result = controller.start_bot()
    
    status_code = 200 if result['success'] else 400
    
    return jsonify({
        'success': result['success'],
        'message': result['message'],
        'data': {'pid': result.get('pid')}
    }), status_code


@control_bp.route('/stop', methods=['POST'])
@error_handler
def stop_bot():
    """
    Stop the bot gracefully
    
    Query params:
        graceful: bool (default: true)
    
    Returns:
        {"success": true, "message": "Bot stopping gracefully"}
    """
    graceful = request.args.get('graceful', 'true').lower() == 'true'
    
    controller = get_bot_controller()
    result = controller.stop_bot(graceful=graceful)
    
    status_code = 200 if result['success'] else 400
    
    return jsonify(result), status_code


@control_bp.route('/restart', methods=['POST'])
@error_handler
def restart_bot():
    """
    Restart the bot
    
    Returns:
        {"success": true, "message": "Bot restarted", "data": {"pid": 12345}}
    """
    controller = get_bot_controller()
    result = controller.restart_bot()
    
    status_code = 200 if result['success'] else 400
    
    return jsonify({
        'success': result['success'],
        'message': result['message'],
        'data': {'pid': result.get('pid')}
    }), status_code


@control_bp.route('/emergency-stop', methods=['POST'])
@error_handler
def emergency_stop():
    """
    Emergency stop: Close all positions + immediate shutdown
    
    Returns:
        {"success": true, "message": "Emergency stop executed"}
    """
    controller = get_bot_controller()
    result = controller.emergency_stop()
    
    return jsonify(result)


@control_bp.route('/pause', methods=['POST'])
@error_handler
def pause_trading():
    """
    Pause trading (bot runs but doesn't execute trades)
    
    Returns:
        {"success": true, "message": "Trading paused"}
    """
    controller = get_bot_controller()
    result = controller.pause_trading()
    
    return jsonify(result)


@control_bp.route('/resume', methods=['POST'])
@error_handler
def resume_trading():
    """
    Resume trading after pause
    
    Returns:
        {"success": true, "message": "Trading resumed"}
    """
    controller = get_bot_controller()
    result = controller.resume_trading()
    
    return jsonify(result)


# ==================== QUICK ACTIONS ====================

@control_bp.route('/close-positions', methods=['POST'])
@error_handler
def close_all_positions():
    """
    Close all open positions
    
    Returns:
        {"success": true, "message": "Command sent to close all positions"}
    """
    controller = get_bot_controller()
    result = controller.close_all_positions()
    
    return jsonify(result)


@control_bp.route('/reduce-positions', methods=['POST'])
@error_handler
def reduce_positions():
    """
    Reduce all positions by percentage
    
    JSON body:
        {"percentage": 50.0}
    
    Returns:
        {"success": true, "message": "Command sent to reduce positions by 50%"}
    """
    data = request.get_json() or {}
    percentage = data.get('percentage', 50.0)
    
    controller = get_bot_controller()
    result = controller.reduce_positions(percentage)
    
    status_code = 200 if result['success'] else 400
    
    return jsonify(result), status_code


# ==================== STRATEGY MANAGEMENT ====================

@control_bp.route('/strategies', methods=['GET'])
@error_handler
def list_strategies():
    """
    List all available strategies with their status
    
    Returns:
        {
            "success": true,
            "data": {
                "strategies": [
                    {
                        "name": "momentum",
                        "enabled": true,
                        "category": "momentum",
                        "description": "..."
                    },
                    ...
                ]
            }
        }
    """
    # Read strategies from config or scan strategies directory
    strategies_dir = Path(__file__).parent.parent / 'strategies'
    
    strategies = []
    
    # Scan Python files in strategies directory
    for py_file in strategies_dir.glob('*.py'):
        if py_file.name.startswith('_') or py_file.name == 'base_strategy.py':
            continue
        
        strategy_name = py_file.stem
        
        # Categorize based on name patterns
        category = 'other'
        if any(x in strategy_name for x in ['momentum', 'macd']):
            category = 'momentum'
        elif any(x in strategy_name for x in ['mean_reversion', 'bollinger', 'rsi']):
            category = 'mean_reversion'
        elif any(x in strategy_name for x in ['arb', 'stat']):
            category = 'arbitrage'
        elif any(x in strategy_name for x in ['regime', 'sector']):
            category = 'macro'
        
        strategies.append({
            'name': strategy_name,
            'enabled': True,  # Default to enabled
            'category': category,
            'description': f'{strategy_name.replace("_", " ").title()} Strategy'
        })
    
    return jsonify({
        'success': True,
        'data': {
            'strategies': sorted(strategies, key=lambda x: x['name']),
            'total': len(strategies),
            'categories': list(set(s['category'] for s in strategies))
        }
    })


@control_bp.route('/strategies/<strategy_name>', methods=['PUT'])
@error_handler
def update_strategy(strategy_name: str):
    """
    Update strategy settings
    
    JSON body:
        {
            "enabled": true,
            "parameters": {
                "threshold": 0.7,
                ...
            }
        }
    
    Returns:
        {"success": true, "message": "Strategy updated"}
    """
    data = request.get_json() or {}
    
    # TODO: Implement strategy parameter updates
    # For now, just acknowledge
    
    return jsonify({
        'success': True,
        'message': f'Strategy {strategy_name} update queued'
    })


# ==================== CONFIG MANAGEMENT ====================

@control_bp.route('/config', methods=['GET'])
@error_handler
def get_config():
    """
    Get current configuration
    
    Returns:
        {
            "success": true,
            "data": {
                "risk": {...},
                "trading": {...},
                "strategies": {...}
            }
        }
    """
    config_file = Path(__file__).parent.parent / 'config' / 'trading_config.yaml'
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    return jsonify({
        'success': True,
        'data': config
    })


@control_bp.route('/config/risk', methods=['PUT'])
@error_handler
def update_risk_config():
    """
    Update risk management parameters
    
    JSON body:
        {
            "max_drawdown": 0.15,
            "position_size": 0.05,
            "stop_loss": 0.02,
            "take_profit": 0.05,
            "circuit_breaker": {
                "level_1": 0.10,
                "level_2": 0.20,
                "level_3": 0.30
            }
        }
    
    Returns:
        {"success": true, "message": "Risk parameters updated"}
    """
    data = request.get_json() or {}
    
    # Validate parameters
    if 'max_drawdown' in data:
        if not 0.05 <= data['max_drawdown'] <= 0.50:
            return jsonify({
                'success': False,
                'message': 'Max drawdown must be between 5% and 50%'
            }), 400
    
    if 'position_size' in data:
        if not 0.01 <= data['position_size'] <= 0.20:
            return jsonify({
                'success': False,
                'message': 'Position size must be between 1% and 20%'
            }), 400
    
    # TODO: Write to config file and signal bot to reload
    
    return jsonify({
        'success': True,
        'message': 'Risk parameters update queued'
    })


# ==================== HEALTH CHECK ====================

@control_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        {"status": "ok", "timestamp": "..."}
    """
    from datetime import datetime
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'control-panel'
    })
