# Dashboard Endpoints Integration Patch v5.1

**Target**: `src/dashboard/web_app.py`  
**Version**: 5.0 → 5.1  
**Date**: 2026-01-23

---

## Changes Summary

1. **Version bump**: `__version__ = '5.0'` → `__version__ = '5.1'`
2. **Add market data endpoints** (2 endpoints)
3. **Add annotations endpoints** (3 endpoints)
4. **Update startup banner**

---

## STEP 1: Update Version

**Location**: Line 67  
**Change**:
```python
# OLD:
__version__ = '5.0'

# NEW:
__version__ = '5.1'
```

---

## STEP 2: Add Market Data Endpoints

**Location**: After `get_alerts()` endpoint (around line 790)  
**Add before**: `# ==================== HEALTH CHECK ====================`

**Insert this code**:

```python
        # ==================== API - MARKET DATA 🆕 ====================
        
        @self.app.route('/api/market/<symbol>')
        @self.limiter.limit("30 per minute")
        @self.login_required
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
            import random
            
            # Mock data generator
            base_prices = {
                'AAPL': 175.0,
                'GOOGL': 2850.0,
                'MSFT': 295.0,
                'TSLA': 185.0,
                'BTC/USD': 43500.0,
                'ETH/USD': 2300.0,
                'EUR/USD': 1.085
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
        
        @self.app.route('/api/market/<symbol>/ohlcv')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_ohlcv_data(symbol):
            """Get OHLCV candlestick data for symbol
            
            Query Parameters:
                timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d) - default: 1h
                limit: Number of candles (1-500) - default: 100
            
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
            import random
            
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
```

---

## STEP 3: Add Annotations Endpoints

**Location**: Immediately after the OHLCV endpoint you just added  
**Add before**: `# ==================== HEALTH CHECK ====================`

**Insert this code**:

```python
        # ==================== API - ANNOTATIONS 🆕 ====================
        
        @self.app.route('/api/annotations/<chart_id>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_annotations(chart_id):
            """Get annotations for specific chart
            
            Args:
                chart_id: Chart identifier (equity, trades, risk, etc.)
            
            Returns:
                {
                    'success': True,
                    'chart_id': 'equity',
                    'annotations': [
                        {
                            'id': 1,
                            'chart_id': 'equity',
                            'type': 'text',
                            'x': '2026-01-15',
                            'y': 10500,
                            'text': 'Market peak',
                            'color': '#ff0000',
                            'created_at': '2026-01-23T20:00:00Z'
                        },
                        ...
                    ],
                    'count': 5
                }
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
            
            return jsonify({
                'success': True,
                'annotation': annotation,
                'message': 'Annotation created successfully'
            }), 201
        
        @self.app.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
        @self.limiter.limit("30 per minute")
        @self.login_required
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
            
            return jsonify({
                'success': True,
                'message': 'Annotation deleted successfully'
            })
```

---

## STEP 4: Update Startup Banner

**Location**: In `_log_startup_banner()` method (around line 470)  
**Find**: `logger.info(f"   BotV2 Professional Dashboard v{__version__} - Complete Integration")`

**Keep as is** (version will auto-update from `__version__` variable)

---

## STEP 5: Update Docstring (Optional)

**Location**: Top of file (line 1)  
**Change first line**:

```python
# OLD:
"""BotV2 Professional Dashboard v5.0 - Complete Integration Edition

# NEW:
"""BotV2 Professional Dashboard v5.1 - Complete API Integration
```

**Add to features list** (around line 29):
```python
- 🗄️ Database Integration v5.0 (SQLAlchemy + Mock fallback)
- 📊 Market Data v5.1 (OHLCV candlesticks)  # 🆕 ADD THIS
- 📝 Annotations v5.1 (Chart notes CRUD)   # 🆕 ADD THIS
```

---

## Verification

After applying patch, test with:

```bash
# Test market price
curl http://localhost:8050/api/market/AAPL

# Test OHLCV
curl "http://localhost:8050/api/market/AAPL/ohlcv?timeframe=1h&limit=50"

# Test get annotations
curl http://localhost:8050/api/annotations/equity

# Test create annotation
curl -X POST http://localhost:8050/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "equity",
    "type": "text",
    "x": "2026-01-23",
    "y": 10500,
    "text": "Test annotation",
    "color": "#ff0000"
  }'

# Test delete annotation
curl -X DELETE http://localhost:8050/api/annotations/1
```

---

## Summary of Changes

✅ **5 new endpoints added:**
1. `GET /api/market/<symbol>` - Latest price
2. `GET /api/market/<symbol>/ohlcv` - Candlestick OHLCV data
3. `GET /api/annotations/<chart_id>` - Get chart annotations
4. `POST /api/annotations` - Create annotation
5. `DELETE /api/annotations/<id>` - Delete annotation

✅ **2 new WebSocket events:**
- `annotation_created` - Broadcast when annotation created
- `annotation_deleted` - Broadcast when annotation deleted

✅ **Version bumped:** 5.0 → 5.1

✅ **Mock data generators included**

✅ **Full authentication and rate limiting**

---

## Alternative: Automated Integration

If you prefer, you can copy the complete endpoints from:
[`additional_endpoints.py`](https://github.com/juankaspain/BotV2/blob/main/src/dashboard/additional_endpoints.py)

Then paste them into `web_app.py` at the location specified above.

---

**Integration complete after applying this patch!** 🎉
