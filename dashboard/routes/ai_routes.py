#!/usr/bin/env python3
"""AI API Routes for BotV2 Dashboard

Provides REST API endpoints for AI features:
- Anomaly detection
- Pattern recognition (coming soon)
- Market regime classification (coming soon)

Integration:
    from src.dashboard.ai_routes import register_ai_routes
    from flask import Flask
    from flask_socketio import SocketIO
    
    app = Flask(__name__)
    socketio = SocketIO(app)
    register_ai_routes(app, socketio)
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ai.anomaly_detector import AnomalyDetector

# Initialize AI components
anomal_detector = AnomalyDetector(model_path='models/anomaly_detector.pkl')

# In-memory anomaly history (in production, use database)
ANOMALY_HISTORY = []
MAX_HISTORY_SIZE = 1000


def register_ai_routes(app, socketio=None):
    """Register AI routes with Flask app
    
    Args:
        app: Flask application instance
        socketio: SocketIO instance for real-time updates (optional)
    """
    
    # ============================================
    # ANOMALY DETECTION ENDPOINTS
    # ============================================
    
    @app.route('/api/ai/detect-anomalies', methods=['POST'])
    def detect_anomalies():
        """Detect anomalies in provided market data
        
        Request Body:
            {
                "data": [
                    {
                        "timestamp": "2026-01-21T22:00:00Z",
                        "open": 100.5,
                        "high": 101.2,
                        "low": 100.1,
                        "close": 100.8,
                        "volume": 50000
                    },
                    ...
                ],
                "symbol": "EUR/USD",  // optional
                "broadcast": true      // emit via WebSocket
            }
        
        Response:
            {
                "success": true,
                "anomalies": [
                    {
                        "type": "volume_spike",
                        "timestamp": "2026-01-21T22:00:00Z",
                        "severity": 85,
                        "description": "Volume is 4.2x the 20-period average",
                        "recommendations": [...]
                    }
                ],
                "count": 3,
                "detection_time_ms": 67
            }
        """
        try:
            start_time = datetime.now()
            
            # Parse request
            data = request.get_json()
            if not data or 'data' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing "data" field in request body'
                }), 400
            
            # Convert to DataFrame
            df = pd.DataFrame(data['data'])
            
            # Validate required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return jsonify({
                    'success': False,
                    'error': f'Missing required columns: {missing_cols}'
                }), 400
            
            # Detect anomalies
            anomalies = anomaly_detector.detect(df)
            
            # Generate alerts
            alerts = [anomaly_detector.generate_alert(a) for a in anomalies]
            
            # Store in history
            symbol = data.get('symbol', 'UNKNOWN')
            for anomaly in anomalies:
                anomaly['symbol'] = symbol
                ANOMALY_HISTORY.append(anomaly)
            
            # Trim history if too large
            if len(ANOMALY_HISTORY) > MAX_HISTORY_SIZE:
                ANOMALY_HISTORY[:] = ANOMALY_HISTORY[-MAX_HISTORY_SIZE:]
            
            # Broadcast via WebSocket if requested
            if data.get('broadcast', False) and socketio and len(anomalies) > 0:
                for alert in alerts:
                    socketio.emit('anomaly_detected', alert)
                    
                    # High severity alerts
                    if alert['severity'] in ['critical', 'high']:
                        socketio.emit('high_severity_alert', alert)
            
            # Calculate detection time
            detection_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return jsonify({
                'success': True,
                'anomalies': anomalies,
                'alerts': alerts,
                'count': len(anomalies),
                'detection_time_ms': round(detection_time, 2)
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/api/ai/anomalies/history', methods=['GET'])
    def get_anomaly_history():
        """Get historical anomaly log
        
        Query Parameters:
            start_date: ISO timestamp (default: 24h ago)
            end_date: ISO timestamp (default: now)
            severity: Filter by min severity (0-100)
            type: Filter by anomaly type
            symbol: Filter by symbol
            page: Page number (default: 1)
            per_page: Results per page (default: 50, max: 100)
        
        Response:
            {
                "success": true,
                "anomalies": [...],
                "total": 145,
                "page": 1,
                "per_page": 50,
                "has_more": true
            }
        """
        try:
            # Parse query parameters
            end_date = request.args.get('end_date', datetime.now().isoformat())
            start_date = request.args.get('start_date', 
                                         (datetime.now() - timedelta(days=1)).isoformat())
            min_severity = int(request.args.get('severity', 0))
            anomaly_type = request.args.get('type')
            symbol = request.args.get('symbol')
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 50)), 100)
            
            # Filter anomalies
            filtered = ANOMALY_HISTORY.copy()
            
            if min_severity > 0:
                filtered = [a for a in filtered if a.get('severity', 0) >= min_severity]
            
            if anomaly_type:
                filtered = [a for a in filtered if a.get('type') == anomaly_type]
            
            if symbol:
                filtered = [a for a in filtered if a.get('symbol') == symbol]
            
            # Sort by timestamp (newest first)
            filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Paginate
            total = len(filtered)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated = filtered[start_idx:end_idx]
            
            return jsonify({
                'success': True,
                'anomalies': paginated,
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_more': end_idx < total
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/ai/train-detector', methods=['POST'])
    def train_detector():
        """Train/retrain anomaly detection model
        
        Request Body:
            {
                "data": [...],          // Historical OHLCV data
                "contamination": 0.05   // Expected anomaly rate
            }
        
        Response:
            {
                "success": true,
                "metrics": {
                    "total_samples": 10000,
                    "anomalies_detected": 500,
                    "anomaly_percentage": 5.0,
                    "trained_at": "2026-01-21T22:00:00Z"
                }
            }
        """
        try:
            # TODO: Add API key authentication for this endpoint
            
            data = request.get_json()
            if not data or 'data' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Missing "data" field'
                }), 400
            
            # Convert to DataFrame
            df = pd.DataFrame(data['data'])
            contamination = float(data.get('contamination', 0.05))
            
            # Train model
            metrics = anomaly_detector.train(df, contamination=contamination)
            
            return jsonify({
                'success': True,
                'metrics': metrics,
                'message': 'Model trained successfully'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @app.route('/api/ai/model/status', methods=['GET'])
    def get_model_status():
        """Get anomaly detection model status
        
        Response:
            {
                "success": true,
                "model": {
                    "type": "isolation_forest",
                    "status": "trained",
                    "version": "1.0",
                    "last_trained": "2026-01-21T20:00:00Z",
                    "features": [...],
                    "thresholds": {...}
                },
                "performance": {
                    "avg_detection_time_ms": 65,
                    "total_detections": 1247
                }
            }
        """
        try:
            model_exists = anomaly_detector.model is not None
            
            status = {
                'success': True,
                'model': {
                    'type': 'isolation_forest',
                    'status': 'trained' if model_exists else 'not_trained',
                    'version': '1.0',
                    'features': anomaly_detector.feature_names if model_exists else [],
                    'thresholds': anomaly_detector.thresholds
                },
                'performance': {
                    'total_detections': len(ANOMALY_HISTORY),
                    'history_size': len(ANOMALY_HISTORY)
                }
            }
            
            # Check if model file exists
            if os.path.exists(anomaly_detector.model_path):
                stat = os.stat(anomaly_detector.model_path)
                status['model']['last_trained'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                status['model']['file_size_mb'] = round(stat.st_size / 1024 / 1024, 2)
            
            return jsonify(status)
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/ai/recommendations', methods=['GET'])
    def get_recommendations():
        """Get AI-powered trading recommendations
        
        Query Parameters:
            symbol: Trading pair (optional)
        
        Response:
            {
                "success": true,
                "recommendations": [
                    {
                        "type": "risk_reduction",
                        "priority": "high",
                        "message": "Reduce position sizes by 50%",
                        "reason": "Multiple high-severity anomalies detected"
                    }
                ]
            }
        """
        try:
            symbol = request.args.get('symbol')
            
            # Get recent high-severity anomalies
            recent_anomalies = [a for a in ANOMALY_HISTORY[-50:] 
                               if a.get('severity', 0) >= 60]
            
            if symbol:
                recent_anomalies = [a for a in recent_anomalies 
                                   if a.get('symbol') == symbol]
            
            recommendations = []
            
            # Generate recommendations based on recent anomalies
            if len(recent_anomalies) >= 3:
                recommendations.append({
                    'type': 'risk_reduction',
                    'priority': 'high',
                    'message': 'Reduce position sizes by 30-50%',
                    'reason': f'{len(recent_anomalies)} high-severity anomalies in last hour',
                    'action': 'reduce_positions'
                })
            
            critical_anomalies = [a for a in recent_anomalies if a.get('severity', 0) >= 80]
            if critical_anomalies:
                recommendations.append({
                    'type': 'trading_halt',
                    'priority': 'critical',
                    'message': 'Consider pausing automated trading',
                    'reason': 'Critical market anomalies detected',
                    'action': 'pause_trading'
                })
            
            volume_spikes = [a for a in recent_anomalies if a.get('type') == 'volume_spike']
            if len(volume_spikes) >= 2:
                recommendations.append({
                    'type': 'opportunity',
                    'priority': 'medium',
                    'message': 'Monitor for potential breakout',
                    'reason': 'Multiple volume spikes detected',
                    'action': 'watch_closely'
                })
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'based_on_anomalies': len(recent_anomalies)
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ============================================
    # WEBSOCKET EVENT HANDLERS (if socketio provided)
    # ============================================
    
    if socketio:
        @socketio.on('request_anomaly_check')
        def handle_anomaly_check(data):
            """Handle real-time anomaly check request via WebSocket"""
            try:
                df = pd.DataFrame(data['data'])
                anomalies = anomaly_detector.detect(df)
                
                emit('anomaly_check_result', {
                    'success': True,
                    'anomalies': anomalies,
                    'count': len(anomalies)
                })
            except Exception as e:
                emit('anomaly_check_result', {
                    'success': False,
                    'error': str(e)
                })
        
        @socketio.on('subscribe_anomaly_alerts')
        def handle_subscribe():
            """Subscribe client to anomaly alerts"""
            emit('subscribed', {
                'message': 'Subscribed to anomaly alerts',
                'timestamp': datetime.now().isoformat()
            })
    
    print("✅ AI routes registered successfully")


# ============================================
# UTILITY FUNCTIONS
# ============================================

def clear_anomaly_history():
    """Clear anomaly history (useful for testing)"""
    global ANOMALY_HISTORY
    ANOMALY_HISTORY.clear()


def export_anomaly_history(filepath: str):
    """Export anomaly history to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(ANOMALY_HISTORY, f, indent=2, default=str)


def import_anomaly_history(filepath: str):
    """Import anomaly history from JSON file"""
    global ANOMALY_HISTORY
    with open(filepath, 'r') as f:
        ANOMALY_HISTORY = json.load(f)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == '__main__':
    from flask import Flask
    from flask_socketio import SocketIO
    from flask_cors import CORS
    
    # Create Flask app
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register AI routes
    register_ai_routes(app, socketio)
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'BotV2 AI API'})
    
    print("\n" + "="*60)
    print("🤖 BotV2 AI API Server")
    print("="*60)
    print("\nAvailable Endpoints:")
    print("  POST   /api/ai/detect-anomalies")
    print("  GET    /api/ai/anomalies/history")
    print("  POST   /api/ai/train-detector")
    print("  GET    /api/ai/model/status")
    print("  GET    /api/ai/recommendations")
    print("\nWebSocket Events:")
    print("  emit: 'anomaly_detected'")
    print("  emit: 'high_severity_alert'")
    print("  on: 'request_anomaly_check'")
    print("  on: 'subscribe_anomaly_alerts'")
    print("\n" + "="*60)
    print("🚀 Starting server on http://localhost:5000")
    print("="*60 + "\n")
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)