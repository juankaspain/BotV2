#!/usr/bin/env python3
"""Additional API Endpoints for BotV2 Dashboard v5.0

Provides additional market data and annotations endpoints:
- /api/market/<symbol> - Current market price
- /api/market/<symbol>/ohlcv - OHLCV candlestick data
- /api/annotations - CRUD for chart annotations
"""

import numpy as np
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
import random
import logging

logger = logging.getLogger(__name__)

# Create Blueprint for additional endpoints
additional_bp = Blueprint('additional', __name__)

# In-memory storage for annotations (in production, use database)
_annotations_storage = []


# ==================== MARKET DATA ENDPOINTS ====================

@additional_bp.route('/api/market/<symbol>')
def get_market_price(symbol):
    """Get latest price for symbol
    
    Returns:
        {
            'success': True,
            'symbol': 'AAPL',
            'price': 175.23,
            'change': 2.15,
            'change_pct': 1.24,
            'volume': 45678900,
            'timestamp': '2026-01-23T22:00:00Z'
        }
    """
    # Base prices per symbol
    base_prices = {
        'AAPL': 175.0,
        'GOOGL': 2850.0,
        'MSFT': 295.0,
        'TSLA': 185.0,
        'NVDA': 480.0,
        'AMZN': 152.0,
        'BTC/USD': 43500.0,
        'ETH/USD': 2300.0,
        'EUR/USD': 1.085,
        'GBP/USD': 1.265
    }
    
    base_price = base_prices.get(symbol.upper(), 100.0)
    current_price = base_price * (1 + np.random.normal(0, 0.02))
    previous_close = base_price
    
    change = current_price - previous_close
    change_pct = (change / previous_close) * 100
    
    return jsonify({
        'success': True,
        'symbol': symbol.upper(),
        'price': round(current_price, 2),
        'change': round(change, 2),
        'change_pct': round(change_pct, 2),
        'volume': random.randint(1000000, 100000000),
        'timestamp': datetime.now().isoformat() + 'Z'
    })


@additional_bp.route('/api/market/<symbol>/ohlcv')
def get_ohlcv_data(symbol):
    """Get OHLCV candlestick data for symbol
    
    Query Parameters:
        timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d) - default: 1h
        limit: Number of candles (1-500) - default: 100
        start: Start timestamp (ISO format)
        end: End timestamp (ISO format)
    
    Returns:
        {
            'success': True,
            'symbol': 'AAPL',
            'timeframe': '1h',
            'data': [
                {
                    'timestamp': '2026-01-23T22:00:00Z',
                    'open': 175.20,
                    'high': 176.50,
                    'low': 174.80,
                    'close': 175.90,
                    'volume': 1234567
                },
                ...
            ],
            'count': 100
        }
    
    Example:
        GET /api/market/AAPL/ohlcv?timeframe=1h&limit=50
    """
    # Parse query parameters
    timeframe = request.args.get('timeframe', '1h')
    limit = min(int(request.args.get('limit', 100)), 500)
    
    # Timeframe to minutes mapping
    timeframe_minutes = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }
    
    minutes = timeframe_minutes.get(timeframe, 60)
    
    # Base prices per symbol
    base_prices = {
        'AAPL': 175.0,
        'GOOGL': 2850.0,
        'MSFT': 295.0,
        'TSLA': 185.0,
        'NVDA': 480.0,
        'AMZN': 152.0,
        'BTC/USD': 43500.0,
        'ETH/USD': 2300.0,
        'EUR/USD': 1.085,
        'GBP/USD': 1.265
    }
    
    base_price = base_prices.get(symbol.upper(), 100.0)
    
    # Generate OHLCV data
    ohlcv_data = []
    current_time = datetime.now()
    current_price = base_price
    
    for i in range(limit):
        # Calculate timestamp (going backwards)
        timestamp = current_time - timedelta(minutes=minutes * (limit - i))
        
        # Generate realistic OHLC
        open_price = current_price
        
        # Price movement for this candle (random walk)
        price_change = np.random.normal(0, base_price * 0.005)
        close_price = open_price + price_change
        
        # High/Low around open/close
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.002)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.002)))
        
        # Volume (more volume when price moves more)
        base_volume = random.randint(500000, 2000000)
        volume_multiplier = 1 + abs(price_change / base_price) * 10
        volume = int(base_volume * volume_multiplier)
        
        ohlcv_data.append({
            'timestamp': timestamp.isoformat() + 'Z',
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
        
        # Update current price for next candle
        current_price = close_price
    
    return jsonify({
        'success': True,
        'symbol': symbol.upper(),
        'timeframe': timeframe,
        'data': ohlcv_data,
        'count': len(ohlcv_data)
    })


# ==================== ANNOTATIONS ENDPOINTS ====================

@additional_bp.route('/api/annotations/<chart_id>')
def get_annotations(chart_id):
    """Get annotations for specific chart
    
    Args:
        chart_id: Chart identifier (equity, trades, risk, etc.)
    
    Returns:
        {
            'success': True,
            'chart_id': 'equity',
            'annotations': [...],
            'count': 5
        }
    """
    # Filter annotations for this chart
    chart_annotations = [
        ann for ann in _annotations_storage 
        if ann.get('chart_id') == chart_id
    ]
    
    return jsonify({
        'success': True,
        'chart_id': chart_id,
        'annotations': chart_annotations,
        'count': len(chart_annotations)
    })


@additional_bp.route('/api/annotations', methods=['POST'])
def create_annotation():
    """Create new chart annotation
    
    Request Body:
        {
            'chart_id': 'equity',
            'type': 'text',
            'x': '2026-01-23',
            'y': 10500,
            'text': 'Important note',
            'color': '#00ff00'
        }
    
    Returns:
        {
            'success': True,
            'annotation': {...},
            'message': 'Annotation created'
        }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['chart_id', 'type', 'x', 'y', 'text']
    missing_fields = [f for f in required_fields if f not in data]
    
    if missing_fields:
        return jsonify({
            'success': False,
            'error': f'Missing fields: {missing_fields}'
        }), 400
    
    # Generate ID
    annotation_id = len(_annotations_storage) + 1
    
    # Create annotation
    annotation = {
        'id': annotation_id,
        'chart_id': data['chart_id'],
        'type': data['type'],
        'x': data['x'],
        'y': data['y'],
        'text': data['text'],
        'color': data.get('color', '#ffffff'),
        'created_at': datetime.now().isoformat() + 'Z'
    }
    
    # Store annotation
    _annotations_storage.append(annotation)
    
    # Broadcast via SocketIO if available
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('annotation_created', annotation, broadcast=True)
    except Exception as e:
        logger.debug(f"SocketIO broadcast skipped: {e}")
    
    return jsonify({
        'success': True,
        'annotation': annotation,
        'message': 'Annotation created successfully'
    }), 201


@additional_bp.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id):
    """Delete chart annotation
    
    Args:
        annotation_id: Annotation ID to delete
    
    Returns:
        {
            'success': True,
            'message': 'Annotation deleted'
        }
    """
    global _annotations_storage
    
    # Find annotation
    annotation = next(
        (ann for ann in _annotations_storage if ann['id'] == annotation_id),
        None
    )
    
    if not annotation:
        return jsonify({
            'success': False,
            'error': 'Annotation not found'
        }), 404
    
    # Remove annotation
    _annotations_storage = [ann for ann in _annotations_storage if ann['id'] != annotation_id]
    
    # Broadcast via SocketIO if available
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('annotation_deleted', {'id': annotation_id}, broadcast=True)
    except Exception as e:
        logger.debug(f"SocketIO broadcast skipped: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Annotation deleted successfully'
    })


@additional_bp.route('/api/annotations', methods=['GET'])
def get_all_annotations():
    """Get all annotations
    
    Returns:
        {
            'success': True,
            'annotations': [...],
            'count': 10
        }
    """
    return jsonify({
        'success': True,
        'annotations': _annotations_storage,
        'count': len(_annotations_storage)
    })


# ==================== HELPER FUNCTIONS ====================

def setup_market_endpoints(app, dashboard_instance):
    """
    Legacy helper function for backward compatibility.
    The endpoints are now registered via the Blueprint.
    """
    logger.info("Market endpoints already registered via additional_bp Blueprint")


def setup_annotations_endpoints(app, dashboard_instance):
    """
    Legacy helper function for backward compatibility.
    The endpoints are now registered via the Blueprint.
    """
    logger.info("Annotations endpoints already registered via additional_bp Blueprint")


def add_websocket_broadcasts(dashboard_instance):
    """
    Additional WebSocket broadcast functions.
    These can be called from the dashboard instance.
    """
    
    def broadcast_portfolio_update(portfolio_data: dict):
        """Broadcast portfolio update to all connected clients"""
        try:
            dashboard_instance.socketio.emit('portfolio_update', {
                'type': 'portfolio',
                'data': portfolio_data,
                'timestamp': datetime.now().isoformat() + 'Z'
            }, broadcast=True)
        except Exception as e:
            logger.error(f"Failed to broadcast portfolio update: {e}")
    
    def broadcast_trade_execution(trade_data: dict):
        """Broadcast trade execution to all connected clients"""
        try:
            dashboard_instance.socketio.emit('trade_executed', {
                'type': 'trade',
                'data': trade_data,
                'timestamp': datetime.now().isoformat() + 'Z'
            }, broadcast=True)
        except Exception as e:
            logger.error(f"Failed to broadcast trade execution: {e}")
    
    def broadcast_alert(alert_data: dict):
        """Broadcast alert/notification to all connected clients"""
        try:
            dashboard_instance.socketio.emit('alert', {
                'type': 'alert',
                'data': alert_data,
                'timestamp': datetime.now().isoformat() + 'Z'
            }, broadcast=True)
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {e}")
    
    # Attach methods to dashboard instance
    dashboard_instance.broadcast_portfolio_update = broadcast_portfolio_update
    dashboard_instance.broadcast_trade_execution = broadcast_trade_execution
    dashboard_instance.broadcast_alert = broadcast_alert
    
    logger.info("✓ WebSocket broadcast methods attached to dashboard instance")
