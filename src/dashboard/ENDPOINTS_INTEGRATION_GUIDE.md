# REST API Endpoints Integration Guide

## Overview
This document provides complete implementation instructions for integrating all missing REST API endpoints into `web_app.py`. All endpoints have been implemented in the `database.py` layer via DAOs (Data Access Objects).

## Phase 1: Database Layer ✅ COMPLETE

### Files Created
- `database.py`: DatabaseManager, PortfolioDAO, TradeDAO, StrategyDAO, RiskDAO

## Phase 2: Endpoints Integration (IN PROGRESS)

### Portfolio Endpoints

#### GET /api/portfolio
**Description**: Get current portfolio state
**Response**:
```json
{
  "success": true,
  "data": {
    "total_value": 10000.50,
    "cash": 2000.00,
    "invested": 8000.50,
    "created_at": "2026-01-26T01:00:00Z"
  }
}
```

**Implementation in web_app.py**:
```python
@self.app.route('/api/portfolio')
@self.login_required
def get_portfolio():
    """📊 Get current portfolio state"""
    try:
        from .database import get_database
        db = get_database()
        if db:
            portfolio_dao = PortfolioDAO(db)
            data = portfolio_dao.get_current()
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify(self._get_fallback_data('portfolio'))
    except Exception as e:
        logger.error(f"Portfolio error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

#### GET /api/portfolio/history
**Query Parameters**: `days=30` (optional)
**Response**:
```json
{
  "success": true,
  "data": [
    {"date": "2026-01-25T00:00:00Z", "total_value": 9900.00, "cash": 2100.00},
    {"date": "2026-01-26T00:00:00Z", "total_value": 10000.50, "cash": 2000.00}
  ]
}
```

#### GET /api/portfolio/equity
**Description**: Get equity curve data
**Response**: Same as history but optimized for charting

### Trade Endpoints

#### GET /api/trades
**Query Parameters**:
- `symbol` (optional): Filter by symbol
- `strategy` (optional): Filter by strategy
- `status` (optional): "open", "closed", "cancelled"
- `limit` (default: 100)
- `offset` (default: 0)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "EURUSD",
      "strategy": "scalper_v1",
      "entry_price": 1.0950,
      "exit_price": 1.0960,
      "pnl": 100.50,
      "status": "closed",
      "entry_time": "2026-01-26T10:00:00Z",
      "exit_time": "2026-01-26T11:30:00Z"
    }
  ],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

#### GET /api/trades/recent
**Query Parameters**: `hours=24` (optional)
**Description**: Get recent trades for real-time display

#### GET /api/trades/stats
**Response**:
```json
{
  "success": true,
  "data": {
    "total": 150,
    "winners": 95,
    "losers": 55,
    "win_rate": 0.6333,
    "total_profit": 5250.00,
    "avg_profit": 35.00
  }
}
```

#### GET /api/trades/<int:trade_id>
**Description**: Get specific trade details

### Strategy Endpoints

#### GET /api/strategies
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "scalper_v1",
      "description": "High-frequency scalping strategy",
      "active": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/strategies/<int:strategy_id>/performance
**Response**:
```json
{
  "success": true,
  "data": [
    {"date": "2026-01-25", "return": 0.025, "sharpe": 1.5},
    {"date": "2026-01-26", "return": 0.032, "sharpe": 1.7}
  ]
}
```

#### GET /api/strategies/comparison
**Query Parameters**: `ids=1,2,3` (comma-separated)
**Response**: Comparison metrics across multiple strategies

### Risk Endpoints

#### GET /api/risk/metrics
**Response**:
```json
{
  "success": true,
  "data": {
    "var_95": -500.00,
    "max_drawdown": -0.125,
    "sharpe_ratio": 1.85,
    "created_at": "2026-01-26T01:00:00Z"
  }
}
```

### Market Data Endpoints

#### GET /api/market/<symbol>/ohlcv
**Query Parameters**:
- `timeframe`: "1m", "5m", "1h", "4h", "1d"
- `limit` (default: 100)

**Response**:
```json
{
  "success": true,
  "data": [
    {"time": "2026-01-26T10:00:00Z", "open": 1.0950, "high": 1.0960, "low": 1.0945, "close": 1.0955, "volume": 1000000},
    {"time": "2026-01-26T10:05:00Z", "open": 1.0955, "high": 1.0965, "low": 1.0950, "close": 1.0960, "volume": 950000}
  ]
}
```

### Alert Endpoints

#### GET /api/alerts
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "High Drawdown",
      "message": "Portfolio drawdown exceeded 10%",
      "severity": "warning",
      "created_at": "2026-01-26T00:30:00Z",
      "read": false
    }
  ]
}
```

## WebSocket Events

### Subscribe to Portfolio Updates
```javascript
socket.emit('subscribe_portfolio');
socket.on('portfolio_update', (data) => {
  console.log('Portfolio updated:', data);
});
```

### Subscribe to Trade Executions
```javascript
socket.emit('subscribe_trades');
socket.on('trade_executed', (trade) => {
  console.log('Trade executed:', trade);
});
```

### Subscribe to Risk Alerts
```javascript
socket.emit('subscribe_risk');
socket.on('risk_alert', (alert) => {
  console.log('Risk alert:', alert);
});
```

## Integration Steps

### Step 1: Import Database Layer
Add to top of `web_app.py`:
```python
from .database import (
    init_database,
    get_database,
    PortfolioDAO,
    TradeDAO,
    StrategyDAO,
    RiskDAO
)
```

### Step 2: Initialize Database in ProfessionalDashboard.__init__()
Add to `_setup_database()` method:
```python
self.db_manager = init_database()
self.portfolio_dao = PortfolioDAO(self.db_manager) if self.db_manager else None
self.trade_dao = TradeDAO(self.db_manager) if self.db_manager else None
self.strategy_dao = StrategyDAO(self.db_manager) if self.db_manager else None
self.risk_dao = RiskDAO(self.db_manager) if self.db_manager else None
```

### Step 3: Add Endpoints in `_setup_routes()`
Add all endpoint methods before `def run(self)`

### Step 4: Add WebSocket Handlers in `_setup_websocket_handlers()`
Add subscription handlers for real-time updates

### Step 5: Register AI Routes Blueprint
Add to `_register_blueprints()`:
```python
try:
    from .ai_routes import ai_bp
    self.app.register_blueprint(ai_bp)
    logger.info("✅ AI routes registered at /api/ai")
except ImportError:
    logger.warning("⚠️ AI routes not available")
```

## Testing

### Test Portfolio Endpoint
```bash
curl http://localhost:8050/api/portfolio \
  -H "Authorization: Bearer TOKEN"
```

### Test Trades with Filters
```bash
curl "http://localhost:8050/api/trades?symbol=EURUSD&status=closed&limit=10" \
  -H "Authorization: Bearer TOKEN"
```

### Test Stats
```bash
curl http://localhost:8050/api/trades/stats \
  -H "Authorization: Bearer TOKEN"
```

## Error Handling

All endpoints follow standard error response format:
```json
{
  "success": false,
  "error": "Error message here",
  "error_code": "INVALID_PARAM"
}
```

## Pagination

Endpoints supporting pagination:
- `/api/trades`: `limit`, `offset`
- `/api/portfolio/history`: `limit`, `offset`

Default limit: 100
Max limit: 1000

## Rate Limiting

All endpoints are protected by rate limiter:
- Default: 60 requests/minute per IP
- Can be configured via environment variables

## Next Steps

1. ✅ Database layer created (database.py)
2. ⏳ Integrate all endpoints into web_app.py
3. ⏳ Add WebSocket handlers
4. ⏳ Integrate AI routes as Blueprint
5. ⏳ Create comprehensive tests
6. ⏳ Update API documentation

## File Structure After Integration

```
src/dashboard/
├── web_app.py (MAIN - 831 lines → ~1200 lines with all endpoints)
├── database.py (NEW - Database layer with DAOs) ✅
├── control_routes.py (Blueprint)
├── monitoring_routes.py (Blueprint)
├── strategy_routes.py (Blueprint)
├── ai_routes.py (Blueprint - to be integrated)
├── bot_controller.py (Logic)
├── live_monitor.py (Logic)
├── strategy_editor.py (Logic)
├── metrics_monitor.py (Metrics)
├── models.py (SQLAlchemy models)
└── mock_data.py (Test data)
```
