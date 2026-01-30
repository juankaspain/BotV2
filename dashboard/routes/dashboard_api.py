#!/usr/bin/env python3
"""
Dashboard API Routes v1.0

Provides REST endpoints for dashboard data:
- Overview statistics
- Portfolio performance
- Asset allocation
- Open positions
- Recent trades

Author: Juan Carlos Garcia Arriero
Date: 30 Enero 2026
Version: 1.0.0
"""

import logging
from flask import Blueprint, jsonify, session
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Create blueprint
dashboard_api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/section')


# ==================== DECORATORS ====================

def login_required(f):
    """Require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== MOCK DATA GENERATORS ====================

def generate_dashboard_data() -> Dict[str, Any]:
    """
    Generate comprehensive dashboard data.
    
    Returns:
        Dict containing all dashboard sections
    """
    return {
        'overview': generate_overview(),
        'performance': generate_performance_data(),
        'allocation': generate_allocation_data(),
        'positions': generate_positions_data(),
        'trades': generate_trades_data(),
        'timestamp': datetime.now().isoformat()
    }


def generate_overview() -> Dict[str, Any]:
    """
    Generate overview statistics.
    
    Returns:
        Dict with equity, P&L, win rate, etc.
    """
    return {
        'equity': '€3,250.75',
        'equity_raw': 3250.75,
        'total_pnl': '+€250.75',
        'total_pnl_pct': '+8.35%',
        'daily_pnl': '+€42.50',
        'daily_pnl_pct': '+1.32%',
        'win_rate': 68.5,
        'total_trades': 47,
        'daily_trades': 5,
        'winning_trades': 32,
        'losing_trades': 15,
        'bot_status': 'Paper Trading',
        'bot_state': 'RUNNING',
        'uptime': '3h 42m',
        'last_update': datetime.now().isoformat()
    }


def generate_performance_data() -> Dict[str, Any]:
    """
    Generate performance chart data.
    
    Returns:
        Dict with labels and data points
    """
    # Generate 24 hours of data
    now = datetime.now()
    labels = []
    data = []
    base_value = 3000.0
    
    for i in range(24):
        time = (now - timedelta(hours=23-i)).strftime('%H:%M')
        labels.append(time)
        
        # Simulate gradual growth with some volatility
        progress = i / 23
        value = base_value + (250 * progress) + (20 * (i % 3 - 1))
        data.append(round(value, 2))
    
    return {
        'labels': labels,
        'data': data,
        'period': '24h'
    }


def generate_allocation_data() -> Dict[str, Any]:
    """
    Generate asset allocation pie chart data.
    
    Returns:
        Dict with labels and allocation percentages
    """
    return {
        'labels': ['BTC', 'ETH', 'USDT', 'Other'],
        'data': [42.5, 28.3, 20.2, 9.0],
        'values': {
            'BTC': '€1,381.57',
            'ETH': '€919.93',
            'USDT': '€656.65',
            'Other': '€292.60'
        }
    }


def generate_positions_data() -> List[Dict[str, Any]]:
    """
    Generate open positions data.
    
    Returns:
        List of open position dictionaries
    """
    return [
        {
            'id': 'pos_1',
            'symbol': 'BTC/USDT',
            'side': 'LONG',
            'size': 0.065,
            'entry': 51234.50,
            'current': 52100.00,
            'pnl': 56.25,
            'pnl_pct': 1.69,
            'duration': '2h 15m',
            'strategy': 'MA_Crossover'
        },
        {
            'id': 'pos_2',
            'symbol': 'ETH/USDT',
            'side': 'LONG',
            'size': 0.85,
            'entry': 3045.20,
            'current': 3012.50,
            'pnl': -27.80,
            'pnl_pct': -1.07,
            'duration': '1h 42m',
            'strategy': 'RSI_Oversold'
        },
        {
            'id': 'pos_3',
            'symbol': 'BNB/USDT',
            'side': 'SHORT',
            'size': 2.5,
            'entry': 425.80,
            'current': 422.10,
            'pnl': 9.25,
            'pnl_pct': 0.87,
            'duration': '45m',
            'strategy': 'Momentum'
        }
    ]


def generate_trades_data() -> List[Dict[str, Any]]:
    """
    Generate recent trades data.
    
    Returns:
        List of recent trade dictionaries
    """
    now = datetime.now()
    trades = [
        {
            'id': 'trade_1',
            'time': (now - timedelta(minutes=15)).strftime('%H:%M'),
            'timestamp': (now - timedelta(minutes=15)).isoformat(),
            'symbol': 'BTC/USDT',
            'type': 'SELL',
            'side': 'CLOSE_LONG',
            'size': 0.05,
            'price': 51890.00,
            'pnl': 82.75,
            'pnl_pct': 1.59,
            'strategy': 'MA_Crossover'
        },
        {
            'id': 'trade_2',
            'time': (now - timedelta(minutes=45)).strftime('%H:%M'),
            'timestamp': (now - timedelta(minutes=45)).isoformat(),
            'symbol': 'ETH/USDT',
            'type': 'BUY',
            'side': 'OPEN_LONG',
            'size': 0.85,
            'price': 3045.20,
            'pnl': 0.00,
            'pnl_pct': 0.00,
            'strategy': 'RSI_Oversold'
        },
        {
            'id': 'trade_3',
            'time': (now - timedelta(hours=1, minutes=20)).strftime('%H:%M'),
            'timestamp': (now - timedelta(hours=1, minutes=20)).isoformat(),
            'symbol': 'SOL/USDT',
            'type': 'SELL',
            'side': 'CLOSE_LONG',
            'size': 12.5,
            'price': 105.30,
            'pnl': -18.45,
            'pnl_pct': -1.41,
            'strategy': 'Breakout'
        },
        {
            'id': 'trade_4',
            'time': (now - timedelta(hours=2, minutes=5)).strftime('%H:%M'),
            'timestamp': (now - timedelta(hours=2, minutes=5)).isoformat(),
            'symbol': 'AVAX/USDT',
            'type': 'BUY',
            'side': 'OPEN_LONG',
            'size': 25.0,
            'price': 42.15,
            'pnl': 35.60,
            'pnl_pct': 3.38,
            'strategy': 'Volume_Surge'
        },
        {
            'id': 'trade_5',
            'time': (now - timedelta(hours=3, minutes=10)).strftime('%H:%M'),
            'timestamp': (now - timedelta(hours=3, minutes=10)).isoformat(),
            'symbol': 'BNB/USDT',
            'type': 'SELL',
            'side': 'OPEN_SHORT',
            'size': 2.5,
            'price': 425.80,
            'pnl': 0.00,
            'pnl_pct': 0.00,
            'strategy': 'Momentum'
        }
    ]
    
    return trades


# ==================== API ENDPOINTS ====================

@dashboard_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """
    Get complete dashboard data.
    
    Returns:
        JSON with all dashboard sections
    """
    try:
        data = generate_dashboard_data()
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_api_bp.route('/dashboard/overview', methods=['GET'])
@login_required
def get_overview():
    """
    Get dashboard overview statistics.
    
    Returns:
        JSON with overview data
    """
    try:
        data = generate_overview()
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting overview: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_api_bp.route('/dashboard/performance', methods=['GET'])
@login_required
def get_performance():
    """
    Get performance chart data.
    
    Returns:
        JSON with performance data
    """
    try:
        data = generate_performance_data()
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting performance: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_api_bp.route('/dashboard/allocation', methods=['GET'])
@login_required
def get_allocation():
    """
    Get asset allocation data.
    
    Returns:
        JSON with allocation data
    """
    try:
        data = generate_allocation_data()
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting allocation: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_api_bp.route('/dashboard/positions', methods=['GET'])
@login_required
def get_positions():
    """
    Get open positions.
    
    Returns:
        JSON with positions data
    """
    try:
        data = generate_positions_data()
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting positions: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@dashboard_api_bp.route('/dashboard/trades', methods=['GET'])
@login_required
def get_trades():
    """
    Get recent trades.
    
    Returns:
        JSON with trades data
    """
    try:
        data = generate_trades_data()
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting trades: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@dashboard_api_bp.route('/health', methods=['GET'])
def dashboard_api_health():
    """
    Health check endpoint.
    
    Returns:
        JSON with health status
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'dashboard_api',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })
