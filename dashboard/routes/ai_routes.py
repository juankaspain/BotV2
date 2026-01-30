#!/usr/bin/env python3
"""AI API Routes for BotV2 Dashboard

Provides REST API endpoints for AI features:
- Anomaly detection
- Pattern recognition (coming soon)
- Market regime classification (coming soon)

Integration:
    from dashboard.routes.ai_routes import ai_bp
    app.register_blueprint(ai_bp)
"""

from flask import Blueprint, request, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback
import os
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Lazy load AI components to avoid import errors
_anomaly_detector = None

def get_anomaly_detector():
    """Lazy load anomaly detector"""
    global _anomaly_detector
    if _anomaly_detector is None:
        try:
            from bot.ai.anomaly_detector import AnomalyDetector
            _anomaly_detector = AnomalyDetector(model_path='models/anomaly_detector.pkl')
            logger.info("✓ AnomalyDetector loaded successfully")
        except ImportError as e:
            logger.warning(f"AnomalyDetector not available: {e}")
            _anomaly_detector = None
        except Exception as e:
            logger.warning(f"Error loading AnomalyDetector: {e}")
            _anomaly_detector = None
    return _anomaly_detector


# In-memory anomaly history (in production, use database)
ANOMALY_HISTORY = []
MAX_HISTORY_SIZE = 1000


# ============================================
# ANOMALY DETECTION ENDPOINTS
# ============================================

@ai_bp.route('/detect-anomalies', methods=['POST'])
def detect_anomalies():
    """Detect anomalies in provided market data"""
    try:
        detector = get_anomaly_detector()
        if detector is None:
            return jsonify({
                'success': False,
                'error': 'Anomaly detector not available',
                'message': 'AI features require additional dependencies'
            }), 503
        
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
        anomalies = detector.detect(df)
        
        # Generate alerts
        alerts = [detector.generate_alert(a) for a in anomalies]
        
        # Store in history
        symbol = data.get('symbol', 'UNKNOWN')
        for anomaly in anomalies:
            anomaly['symbol'] = symbol
            ANOMALY_HISTORY.append(anomaly)
        
        # Trim history if too large
        if len(ANOMALY_HISTORY) > MAX_HISTORY_SIZE:
            ANOMALY_HISTORY[:] = ANOMALY_HISTORY[-MAX_HISTORY_SIZE:]
        
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
        logger.error(f"Error detecting anomalies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/anomalies/history', methods=['GET'])
def get_anomaly_history():
    """Get historical anomaly log"""
    try:
        # Parse query parameters
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
        logger.error(f"Error getting anomaly history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/model/status', methods=['GET'])
def get_model_status():
    """Get anomaly detection model status"""
    try:
        detector = get_anomaly_detector()
        
        if detector is None:
            return jsonify({
                'success': True,
                'model': {
                    'type': 'isolation_forest',
                    'status': 'not_available',
                    'message': 'AI features require additional dependencies'
                }
            })
        
        model_exists = detector.model is not None
        
        status = {
            'success': True,
            'model': {
                'type': 'isolation_forest',
                'status': 'trained' if model_exists else 'not_trained',
                'version': '1.0',
                'features': detector.feature_names if model_exists else [],
                'thresholds': getattr(detector, 'thresholds', {})
            },
            'performance': {
                'total_detections': len(ANOMALY_HISTORY),
                'history_size': len(ANOMALY_HISTORY)
            }
        }
        
        # Check if model file exists
        if hasattr(detector, 'model_path') and os.path.exists(detector.model_path):
            stat = os.stat(detector.model_path)
            status['model']['last_trained'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            status['model']['file_size_mb'] = round(stat.st_size / 1024 / 1024, 2)
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-powered trading recommendations"""
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
                'reason': f'{len(recent_anomalies)} high-severity anomalies detected',
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
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'based_on_anomalies': len(recent_anomalies)
        })
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/health', methods=['GET'])
def ai_health():
    """AI module health check"""
    detector = get_anomaly_detector()
    return jsonify({
        'success': True,
        'status': 'healthy',
        'anomaly_detector_available': detector is not None,
        'history_size': len(ANOMALY_HISTORY)
    })


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
