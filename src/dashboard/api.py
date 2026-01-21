"""REST API backend for BotV2 Dashboard

Flask-based REST API providing data endpoints for the dashboard.

Endpoints:
- /api/portfolio - Portfolio data
- /api/trades - Trade history
- /api/strategies - Strategy performance
- /api/risk - Risk metrics
- /api/market - Market data
- /api/annotations - Chart annotations
- /api/alerts - System alerts

Run with:
    python src/dashboard/api.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine, and_, or_, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta
import os
import json

from models import (
    Base, Portfolio, Trade, Strategy, StrategyPerformance,
    RiskMetrics, MarketData, Annotation, Alert
)

# ============================================
# APP INITIALIZATION
# ============================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# CORS for local development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# SocketIO for WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*")

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dashboard.db')
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
Session = scoped_session(sessionmaker(bind=engine))

# Initialize database
Base.metadata.create_all(engine)

print("✅ Flask API server initialized")
print(f"📦 Database: {DATABASE_URL}")


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_db():
    """Get database session"""
    return Session()

def success_response(data, message=None, status=200):
    """Standard success response format"""
    response = {'success': True, 'data': data}
    if message:
        response['message'] = message
    return jsonify(response), status

def error_response(message, status=400):
    """Standard error response format"""
    return jsonify({'success': False, 'error': message}), status

def parse_date_param(date_str, default=None):
    """Parse date parameter from query string"""
    if not date_str:
        return default
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return default


# ============================================
# PORTFOLIO ENDPOINTS
# ============================================

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio state
    
    Returns:
        Current portfolio with all positions and P&L
    """
    db = get_db()
    try:
        # Get latest portfolio snapshot
        portfolio = db.query(Portfolio).order_by(desc(Portfolio.timestamp)).first()
        
        if not portfolio:
            # Return empty portfolio if no data
            return success_response({
                'total_value': 100000,  # Initial capital
                'daily_change': 0,
                'total_pnl': 0,
                'positions': []
            })
        
        return success_response(portfolio.to_dict())
    
    except Exception as e:
        return error_response(f"Error fetching portfolio: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/portfolio/history', methods=['GET'])
def get_portfolio_history():
    """Get historical portfolio snapshots
    
    Query params:
        - start: Start date (ISO format)
        - end: End date (ISO format)
        - limit: Max records (default 100)
    """
    db = get_db()
    try:
        start = parse_date_param(request.args.get('start'), datetime.now() - timedelta(days=30))
        end = parse_date_param(request.args.get('end'), datetime.now())
        limit = int(request.args.get('limit', 100))
        
        query = db.query(Portfolio).filter(
            and_(
                Portfolio.timestamp >= start,
                Portfolio.timestamp <= end
            )
        ).order_by(Portfolio.timestamp).limit(limit)
        
        snapshots = [p.to_dict() for p in query.all()]
        
        return success_response({
            'snapshots': snapshots,
            'count': len(snapshots),
            'start': start.isoformat(),
            'end': end.isoformat()
        })
    
    except Exception as e:
        return error_response(f"Error fetching portfolio history: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/portfolio/equity', methods=['GET'])
def get_equity_curve():
    """Get equity curve data for chart
    
    Returns:
        Timestamps and equity values for line chart
    """
    db = get_db()
    try:
        days = int(request.args.get('days', 30))
        start = datetime.now() - timedelta(days=days)
        
        portfolios = db.query(Portfolio).filter(
            Portfolio.timestamp >= start
        ).order_by(Portfolio.timestamp).all()
        
        timestamps = [p.timestamp.isoformat() for p in portfolios]
        values = [p.total_value for p in portfolios]
        
        return success_response({
            'timestamps': timestamps,
            'equity': values,
            'start_value': values[0] if values else 100000,
            'end_value': values[-1] if values else 100000,
            'return_pct': ((values[-1] / values[0] - 1) * 100) if values else 0
        })
    
    except Exception as e:
        return error_response(f"Error fetching equity curve: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# TRADE ENDPOINTS
# ============================================

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history with optional filters
    
    Query params:
        - symbol: Filter by symbol
        - strategy: Filter by strategy name
        - status: Filter by status (open, closed)
        - start: Start date
        - end: End date
        - limit: Max records (default 100)
        - offset: Pagination offset
    """
    db = get_db()
    try:
        query = db.query(Trade)
        
        # Apply filters
        if symbol := request.args.get('symbol'):
            query = query.filter(Trade.symbol == symbol)
        
        if strategy_name := request.args.get('strategy'):
            query = query.join(Strategy).filter(Strategy.name == strategy_name)
        
        if status := request.args.get('status'):
            query = query.filter(Trade.status == status)
        
        if start := parse_date_param(request.args.get('start')):
            query = query.filter(Trade.entry_time >= start)
        
        if end := parse_date_param(request.args.get('end')):
            query = query.filter(Trade.entry_time <= end)
        
        # Pagination
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        total = query.count()
        trades = query.order_by(desc(Trade.entry_time)).limit(limit).offset(offset).all()
        
        return success_response({
            'trades': [t.to_dict() for t in trades],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        })
    
    except Exception as e:
        return error_response(f"Error fetching trades: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    """Get specific trade details"""
    db = get_db()
    try:
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        
        if not trade:
            return error_response("Trade not found", 404)
        
        return success_response(trade.to_dict())
    
    except Exception as e:
        return error_response(f"Error fetching trade: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/trades/recent', methods=['GET'])
def get_recent_trades():
    """Get recent trades (last 24 hours)"""
    db = get_db()
    try:
        since = datetime.now() - timedelta(hours=24)
        
        trades = db.query(Trade).filter(
            Trade.entry_time >= since
        ).order_by(desc(Trade.entry_time)).all()
        
        return success_response({
            'trades': [t.to_dict() for t in trades],
            'count': len(trades),
            'since': since.isoformat()
        })
    
    except Exception as e:
        return error_response(f"Error fetching recent trades: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/trades/stats', methods=['GET'])
def get_trade_stats():
    """Get trade statistics"""
    db = get_db()
    try:
        # Get all closed trades
        trades = db.query(Trade).filter(Trade.status == 'closed').all()
        
        if not trades:
            return success_response({
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            })
        
        winning = [t for t in trades if t.net_pnl and t.net_pnl > 0]
        losing = [t for t in trades if t.net_pnl and t.net_pnl <= 0]
        
        avg_win = sum(t.net_pnl for t in winning) / len(winning) if winning else 0
        avg_loss = abs(sum(t.net_pnl for t in losing) / len(losing)) if losing else 0
        profit_factor = abs(sum(t.net_pnl for t in winning) / sum(t.net_pnl for t in losing)) if losing else 0
        
        return success_response({
            'total_trades': len(trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(trades)) * 100 if trades else 0,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': sum(t.net_pnl for t in trades if t.net_pnl)
        })
    
    except Exception as e:
        return error_response(f"Error calculating trade stats: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# STRATEGY ENDPOINTS
# ============================================

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all strategies"""
    db = get_db()
    try:
        strategies = db.query(Strategy).all()
        
        return success_response({
            'strategies': [s.to_dict() for s in strategies],
            'count': len(strategies)
        })
    
    except Exception as e:
        return error_response(f"Error fetching strategies: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """Get strategy details"""
    db = get_db()
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            return error_response("Strategy not found", 404)
        
        return success_response(strategy.to_dict())
    
    except Exception as e:
        return error_response(f"Error fetching strategy: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/strategies/<int:strategy_id>/performance', methods=['GET'])
def get_strategy_performance(strategy_id):
    """Get strategy performance history"""
    db = get_db()
    try:
        days = int(request.args.get('days', 30))
        start = datetime.now() - timedelta(days=days)
        
        performance = db.query(StrategyPerformance).filter(
            and_(
                StrategyPerformance.strategy_id == strategy_id,
                StrategyPerformance.timestamp >= start
            )
        ).order_by(StrategyPerformance.timestamp).all()
        
        if not performance:
            return error_response("No performance data found", 404)
        
        return success_response({
            'performance': [p.to_dict() for p in performance],
            'count': len(performance)
        })
    
    except Exception as e:
        return error_response(f"Error fetching strategy performance: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/strategies/comparison', methods=['GET'])
def compare_strategies():
    """Compare multiple strategies
    
    Query params:
        - ids: Comma-separated strategy IDs (e.g., "1,2,3")
    """
    db = get_db()
    try:
        ids_str = request.args.get('ids', '')
        strategy_ids = [int(id) for id in ids_str.split(',') if id]
        
        if not strategy_ids:
            return error_response("No strategy IDs provided", 400)
        
        strategies = db.query(Strategy).filter(Strategy.id.in_(strategy_ids)).all()
        
        comparison_data = []
        for strategy in strategies:
            # Get latest performance
            latest_perf = db.query(StrategyPerformance).filter(
                StrategyPerformance.strategy_id == strategy.id
            ).order_by(desc(StrategyPerformance.timestamp)).first()
            
            if latest_perf:
                comparison_data.append({
                    'strategy': strategy.to_dict(),
                    'performance': latest_perf.to_dict()
                })
        
        return success_response({
            'strategies': comparison_data,
            'count': len(comparison_data)
        })
    
    except Exception as e:
        return error_response(f"Error comparing strategies: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# RISK ENDPOINTS
# ============================================

@app.route('/api/risk/metrics', methods=['GET'])
def get_risk_metrics():
    """Get current risk metrics"""
    db = get_db()
    try:
        # Get latest risk metrics
        metrics = db.query(RiskMetrics).order_by(desc(RiskMetrics.timestamp)).first()
        
        if not metrics:
            return error_response("No risk metrics available", 404)
        
        return success_response(metrics.to_dict())
    
    except Exception as e:
        return error_response(f"Error fetching risk metrics: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/risk/correlation', methods=['GET'])
def get_correlation_matrix():
    """Get strategy correlation matrix"""
    db = get_db()
    try:
        strategies = db.query(Strategy).filter(Strategy.enabled == True).all()
        
        # Mock correlation matrix (in production, calculate from returns)
        import numpy as np
        n = len(strategies)
        correlation = np.eye(n).tolist()
        
        # Add some mock correlations
        for i in range(n):
            for j in range(i+1, n):
                corr_value = np.random.uniform(0.3, 0.8)
                correlation[i][j] = corr_value
                correlation[j][i] = corr_value
        
        return success_response({
            'strategies': [s.name for s in strategies],
            'correlations': correlation
        })
    
    except Exception as e:
        return error_response(f"Error calculating correlation: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# MARKET DATA ENDPOINTS
# ============================================

@app.route('/api/market/<symbol>', methods=['GET'])
def get_market_price(symbol):
    """Get latest price for symbol"""
    db = get_db()
    try:
        latest = db.query(MarketData).filter(
            MarketData.symbol == symbol
        ).order_by(desc(MarketData.timestamp)).first()
        
        if not latest:
            return error_response(f"No data for symbol {symbol}", 404)
        
        return success_response(latest.to_dict())
    
    except Exception as e:
        return error_response(f"Error fetching market data: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/market/<symbol>/ohlcv', methods=['GET'])
def get_ohlcv(symbol):
    """Get OHLCV data for candlestick chart
    
    Query params:
        - timeframe: Candle timeframe (1m, 5m, 1h, 1d)
        - limit: Max candles (default 100)
    """
    db = get_db()
    try:
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 100))
        
        candles = db.query(MarketData).filter(
            and_(
                MarketData.symbol == symbol,
                MarketData.timeframe == timeframe
            )
        ).order_by(desc(MarketData.timestamp)).limit(limit).all()
        
        if not candles:
            return error_response(f"No OHLCV data for {symbol}", 404)
        
        # Reverse to chronological order
        candles = reversed(candles)
        
        return success_response({
            'symbol': symbol,
            'timeframe': timeframe,
            'candles': [c.to_dict() for c in candles],
            'count': len(candles)
        })
    
    except Exception as e:
        return error_response(f"Error fetching OHLCV: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# ANNOTATION ENDPOINTS
# ============================================

@app.route('/api/annotations/<chart_id>', methods=['GET'])
def get_annotations(chart_id):
    """Get annotations for a chart"""
    db = get_db()
    try:
        annotations = db.query(Annotation).filter(
            Annotation.chart_id == chart_id
        ).order_by(Annotation.date).all()
        
        return success_response({
            'annotations': [a.to_dict() for a in annotations],
            'count': len(annotations)
        })
    
    except Exception as e:
        return error_response(f"Error fetching annotations: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/annotations', methods=['POST'])
def create_annotation():
    """Create new annotation"""
    db = get_db()
    try:
        data = request.get_json()
        
        annotation = Annotation(
            chart_id=data['chart_id'],
            date=datetime.fromisoformat(data['date']),
            text=data['text'],
            type=data.get('type', 'custom'),
            color=data.get('color'),
            icon=data.get('icon')
        )
        
        db.add(annotation)
        db.commit()
        
        return success_response(annotation.to_dict(), "Annotation created", 201)
    
    except Exception as e:
        db.rollback()
        return error_response(f"Error creating annotation: {str(e)}", 500)
    finally:
        db.close()


@app.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id):
    """Delete annotation"""
    db = get_db()
    try:
        annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
        
        if not annotation:
            return error_response("Annotation not found", 404)
        
        db.delete(annotation)
        db.commit()
        
        return success_response(None, "Annotation deleted")
    
    except Exception as e:
        db.rollback()
        return error_response(f"Error deleting annotation: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# ALERT ENDPOINTS
# ============================================

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get active alerts"""
    db = get_db()
    try:
        alerts = db.query(Alert).filter(
            Alert.status == 'active'
        ).order_by(desc(Alert.created_at)).limit(50).all()
        
        return success_response({
            'alerts': [a.to_dict() for a in alerts],
            'count': len(alerts)
        })
    
    except Exception as e:
        return error_response(f"Error fetching alerts: {str(e)}", 500)
    finally:
        db.close()


# ============================================
# WEBSOCKET HANDLERS
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"✅ WebSocket client connected: {request.sid}")
    emit('connection_response', {'status': 'connected', 'message': 'Welcome to BotV2 Dashboard'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"❌ WebSocket client disconnected: {request.sid}")


@socketio.on('subscribe_portfolio')
def handle_subscribe_portfolio():
    """Subscribe to portfolio updates"""
    print(f"📊 Client {request.sid} subscribed to portfolio updates")
    # In production, add client to portfolio update room
    # emit('portfolio_update', get_latest_portfolio_data())


def broadcast_portfolio_update(portfolio_data):
    """Broadcast portfolio update to all connected clients"""
    socketio.emit('portfolio_update', portfolio_data, broadcast=True)


def broadcast_trade_execution(trade_data):
    """Broadcast trade execution to all connected clients"""
    socketio.emit('trade_executed', trade_data, broadcast=True)


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", 500)


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("✅ Starting BotV2 Dashboard API server...")
    print("🌐 API endpoints available at: http://localhost:5000/api")
    print("🔌 WebSocket available at: ws://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)