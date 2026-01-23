# 📋 Manual Integration Instructions - web_app.py v5.1

**Target**: Integrate OHLCV and Annotations endpoints into `web_app.py`  
**Source**: `additional_endpoints.py`  
**Estimated Time**: 15 minutes  
**Difficulty**: ⭐⭐ Medium

---

## 📝 WHAT YOU'RE INTEGRATING

### New Endpoints (5 total):
1. `GET /api/market/<symbol>` - Get latest price for symbol
2. `GET /api/market/<symbol>/ohlcv` - Get OHLCV candlestick data
3. `GET /api/annotations/<chart_id>` - Get chart annotations
4. `POST /api/annotations` - Create annotation
5. `DELETE /api/annotations/<int:id>` - Delete annotation

### Features:
- ✅ Mock data generators (realistic OHLCV candles)
- ✅ Timeframe support (1m, 5m, 15m, 1h, 4h, 1d)
- ✅ WebSocket broadcast for real-time sync
- ✅ Full validation and error handling
- ✅ Rate limiting ready
- ✅ Authentication required

---

## 🎯 STEP-BY-STEP INTEGRATION

### ⚠️ PREREQUISITES

1. **Backup your current file**
```bash
cp src/dashboard/web_app.py src/dashboard/web_app.py.backup_$(date +%Y%m%d_%H%M%S)
```

2. **Open files side by side**
```bash
# Terminal 1: Source
cat src/dashboard/additional_endpoints.py

# Terminal 2: Target (edit)
nano src/dashboard/web_app.py
# or
code src/dashboard/web_app.py
```

---

### 📍 STEP 1: Find Insert Location

**In `web_app.py`, find this section:**

```python
# ==================== API - ALERTS ====================

@self.app.route('/api/alerts')
@self.limiter.limit("30 per minute")
@self.login_required
def get_alerts():
    """Get active alerts"""
    return jsonify({
        'success': True,
        'alerts': self.alerts,
        'count': len(self.alerts)
    })

# ==================== HEALTH CHECK ====================  <-- INSERT BEFORE THIS
```

**Location**: Around line 650-670

---

### 📍 STEP 2: Add Market Data Endpoints

**Insert BEFORE the `# ==================== HEALTH CHECK ====================` comment:**

```python
# ==================== API - MARKET DATA ====================

@self.app.route('/api/market/<symbol>')
@self.limiter.limit("30 per minute")
@self.login_required
def get_market_price(symbol):
    """Get latest price for symbol
    
    Args:
        symbol: Trading symbol (AAPL, BTC/USD, etc.)
    
    Returns:
        JSON with current price, change, volume
    
    Example:
        GET /api/market/AAPL
    """
    # Base prices for mock data
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
        'volume': np.random.randint(1000000, 100000000),
        'timestamp': datetime.now().isoformat() + 'Z'
    })

@self.app.route('/api/market/<symbol>/ohlcv')
@self.limiter.limit("30 per minute")
@self.login_required
def get_ohlcv_data(symbol):
    """Get OHLCV candlestick data for symbol
    
    Query Parameters:
        timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d) - default: 1h
        limit: Number of candles (1-500) - default: 100
    
    Returns:
        JSON with OHLCV array
    
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
        base_volume = np.random.randint(500000, 2000000)
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
```

---

### 📍 STEP 3: Add Annotations Endpoints

**Insert RIGHT AFTER the market endpoints you just added:**

```python
# ==================== API - ANNOTATIONS ====================

@self.app.route('/api/annotations/<chart_id>')
@self.limiter.limit("30 per minute")
@self.login_required
def get_annotations(chart_id):
    """Get annotations for specific chart
    
    Args:
        chart_id: Chart identifier (equity, trades, risk, etc.)
    
    Returns:
        JSON with annotations array
    
    Example:
        GET /api/annotations/equity
    """
    # Filter annotations for this chart
    chart_annotations = [
        ann for ann in self.annotations 
        if ann.get('chart_id') == chart_id
    ]
    
    return jsonify({
        'success': True,
        'chart_id': chart_id,
        'annotations': chart_annotations,
        'count': len(chart_annotations)
    })

@self.app.route('/api/annotations', methods=['POST'])
@self.limiter.limit("30 per minute")
@self.login_required
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
        JSON with created annotation
    
    Example:
        POST /api/annotations
    """
    try:
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
        annotation_id = len(self.annotations) + 1
        
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
        self.annotations.append(annotation)
        
        # Broadcast via WebSocket
        self.socketio.emit('annotation_created', annotation, broadcast=True)
        
        logger.info(f"📌 Annotation created: {annotation_id} on {data['chart_id']}")
        
        return jsonify({
            'success': True,
            'annotation': annotation,
            'message': 'Annotation created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating annotation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@self.app.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
@self.limiter.limit("30 per minute")
@self.login_required
def delete_annotation(annotation_id):
    """Delete chart annotation
    
    Args:
        annotation_id: Annotation ID to delete
    
    Returns:
        JSON with success message
    
    Example:
        DELETE /api/annotations/1
    """
    # Find annotation
    annotation = next(
        (ann for ann in self.annotations if ann['id'] == annotation_id),
        None
    )
    
    if not annotation:
        return jsonify({
            'success': False,
            'error': 'Annotation not found'
        }), 404
    
    # Remove annotation
    self.annotations.remove(annotation)
    
    # Broadcast via WebSocket
    self.socketio.emit('annotation_deleted', {'id': annotation_id}, broadcast=True)
    
    logger.info(f"🗑️ Annotation deleted: {annotation_id}")
    
    return jsonify({
        'success': True,
        'message': 'Annotation deleted successfully'
    })
```

---

### 📍 STEP 4: Update Version Number

**Find this line near the top:**

```python
__version__ = '5.0'
```

**Change to:**

```python
__version__ = '5.1'
```

**Also update the docstring:**

```python
"""BotV2 Professional Dashboard v5.1 - Complete Integration Edition
Ultra-professional real-time trading dashboard with production-grade security

🆕 VERSION 5.1 - MARKET DATA & ANNOTATIONS:
- Added OHLCV candlestick endpoint with timeframe support
- Added chart annotations CRUD endpoints
- Real-time WebSocket sync for annotations
- Complete API integration from api.py
```

---

### 📍 STEP 5: Save and Verify

**Save the file and verify syntax:**

```bash
# Check Python syntax
python -m py_compile src/dashboard/web_app.py

# If no errors, you're good!
echo "✅ Syntax OK"
```

---

## 🧪 TESTING

### 1. Start Dashboard

```bash
python -m src.dashboard.web_app
```

**Expected output:**
```
============================================================
   BotV2 Professional Dashboard v5.1 - Complete Integration
============================================================
...
🚀 Starting dashboard server...
```

### 2. Test New Endpoints

```bash
# Test 1: Get market price
curl http://localhost:8050/api/market/AAPL

# Expected:
{
  "success": true,
  "symbol": "AAPL",
  "price": 175.23,
  "change": 2.15,
  "change_pct": 1.24,
  "volume": 45678900,
  "timestamp": "2026-01-23T22:00:00Z"
}

# Test 2: Get OHLCV data
curl "http://localhost:8050/api/market/BTC/USD/ohlcv?timeframe=1h&limit=10"

# Expected:
{
  "success": true,
  "symbol": "BTC/USD",
  "timeframe": "1h",
  "data": [
    {
      "timestamp": "2026-01-23T13:00:00Z",
      "open": 43500.0,
      "high": 43650.0,
      "low": 43400.0,
      "close": 43520.0,
      "volume": 1234567
    },
    ...
  ],
  "count": 10
}

# Test 3: Get annotations
curl http://localhost:8050/api/annotations/equity

# Expected:
{
  "success": true,
  "chart_id": "equity",
  "annotations": [],
  "count": 0
}

# Test 4: Create annotation
curl -X POST http://localhost:8050/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "equity",
    "type": "text",
    "x": "2026-01-23",
    "y": 10500,
    "text": "Market peak",
    "color": "#ff0000"
  }'

# Expected:
{
  "success": true,
  "annotation": {
    "id": 1,
    "chart_id": "equity",
    "type": "text",
    "x": "2026-01-23",
    "y": 10500,
    "text": "Market peak",
    "color": "#ff0000",
    "created_at": "2026-01-23T22:00:00Z"
  },
  "message": "Annotation created successfully"
}

# Test 5: Delete annotation
curl -X DELETE http://localhost:8050/api/annotations/1

# Expected:
{
  "success": true,
  "message": "Annotation deleted successfully"
}
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] File backed up
- [ ] Code inserted in correct location
- [ ] Version number updated to 5.1
- [ ] Docstring updated
- [ ] Syntax check passed
- [ ] Dashboard starts without errors
- [ ] All 5 endpoints return valid JSON
- [ ] WebSocket events work (check browser console)
- [ ] No errors in logs

---

## 🔙 ROLLBACK (If Needed)

**If something goes wrong:**

```bash
# Find your backup
ls -la src/dashboard/web_app.py.backup_*

# Restore backup
cp src/dashboard/web_app.py.backup_YYYYMMDD_HHMMSS src/dashboard/web_app.py

# Restart dashboard
python -m src.dashboard.web_app
```

---

## 📊 WHAT YOU'VE ADDED

**Lines of Code**: ~250 lines  
**New Endpoints**: 5  
**Features**: OHLCV candles + Annotations CRUD  
**WebSocket Events**: 2 (annotation_created, annotation_deleted)  
**Supported Symbols**: 10 (AAPL, GOOGL, MSFT, TSLA, NVDA, AMZN, BTC/USD, ETH/USD, EUR/USD, GBP/USD)  
**Timeframes**: 7 (1m, 5m, 15m, 30m, 1h, 4h, 1d)  

---

## 🎯 NEXT STEPS

1. **Test in browser:**
   - Open dashboard
   - Check browser console for WebSocket events
   - Test creating annotations

2. **Optional enhancements:**
   - Add more symbols to base_prices dict
   - Customize OHLCV generation logic
   - Add database persistence for annotations

3. **Production deployment:**
   - Ensure all environment variables set
   - Test with real market data API
   - Enable database for annotations

---

## ❓ TROUBLESHOOTING

**Problem**: `NameError: name 'np' is not defined`  
**Solution**: Check imports at top of file - `import numpy as np` should be present

**Problem**: `AttributeError: 'ProfessionalDashboard' object has no attribute 'annotations'`  
**Solution**: Add `self.annotations = []` in `__init__` method

**Problem**: Endpoints return 404  
**Solution**: Check that endpoints are inside `_setup_routes()` method

**Problem**: Rate limit errors  
**Solution**: Endpoints have `@self.limiter.limit("30 per minute")` decorator

---

## 📞 SUPPORT

If you encounter issues:
1. Check `logs/security_audit.log` for errors
2. Review `INTEGRATION_COMPLETE.md` for architecture
3. Compare with `additional_endpoints.py` source

---

**Integration Prepared By**: AI Assistant  
**Date**: 2026-01-23  
**Target Version**: 5.1  
**Status**: ✅ Ready for Integration
