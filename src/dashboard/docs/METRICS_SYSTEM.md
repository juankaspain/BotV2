# 📊 BotV2 Metrics System - Complete Documentation

**Version**: 1.0.0  
**Date**: 25 Enero 2026  
**Author**: Juan Carlos Garcia Arriero  
**Status**: ✅ Production Ready

---

## 🎯 Overview

El **Sistema de Métricas** de BotV2 es un sistema profesional de monitoreo en tiempo real que rastrea y analiza el rendimiento del dashboard y las operaciones del bot. Proporciona métricas clave sobre requests, latencia, errores, recursos del sistema y usuarios activos.

### 🎓 Features Principales

- ✅ **Real-time Monitoring**: Métricas actualizadas en tiempo real
- ✅ **Rolling Windows**: Ventanas deslizantes de 5 minutos para análisis temporal
- ✅ **Percentile Latency**: P50, P95, P99 latency tracking
- ✅ **Resource Monitoring**: CPU y memoria del proceso
- ✅ **User Tracking**: Usuarios activos y sesiones
- ✅ **WebSocket Monitoring**: Conexiones activas en tiempo real
- ✅ **Historical Data**: Hasta 60 minutos de historia con snapshots por minuto
- ✅ **Export Capabilities**: JSON y CSV export
- ✅ **Thread-Safe**: Diseñado para entornos multi-threaded
- ✅ **Automatic Cleanup**: Background thread para limpieza de datos antiguos

---

## 🏛️ Architecture

### System Components

```
┌───────────────────────────────────────────────────────┐
│                                                               │
│                    BotV2 Metrics System                       │
│                                                               │
└───────────────────────────────────────────────────────┘
                           │
          ┌────────────┼────────────┐
          │                │                │
  ┌───────┴───────┐   ┌────┴────┐   ┌────┴────┐
  │ MetricsMonitor │   │ Routes │   │Middleware│
  │   (Core)       │   │  (API)  │   │  (Auto) │
  └────────────────┘   └─────────┘   └──────────┘
          │                │                │
          │                │                │
  ┌───────┴──────────────────────────────────────────┐
  │                                                    │
  │              Data Storage Layer                   │
  │                                                    │
  │  - Request Deque (10K max)                        │
  │  - Active Users Dict                              │
  │  - Metrics History Deque (60 snapshots)           │
  │  - Statistics Counters                            │
  │                                                    │
  └──────────────────────────────────────────────────┘
          │
  ┌───────┴──────────────────────────────────────────┐
  │                                                    │
  │           Background Cleanup Thread               │
  │                                                    │
  │  - Runs every 60 seconds                          │
  │  - Cleans expired user sessions                   │
  │  - Saves snapshot to history                      │
  │                                                    │
  └──────────────────────────────────────────────────┘
```

### Component Descriptions

#### 1. **MetricsMonitor** (Core Engine)

- **Ubicación**: `src/dashboard/metrics_monitor.py`
- **Responsabilidad**: Captura, almacena y calcula todas las métricas
- **Features**:
  - Request tracking con rolling windows
  - Latency percentile calculation (P50, P95, P99)
  - User activity tracking
  - WebSocket connection monitoring
  - System resource monitoring (CPU, Memory)
  - Historical snapshots storage
  - Thread-safe operations

#### 2. **Metrics Routes** (REST API)

- **Ubicación**: `src/dashboard/metrics_routes.py`
- **Responsabilidad**: Expone métricas vía REST API
- **Endpoints**:
  - `GET /api/metrics/current` - Current snapshot
  - `GET /api/metrics/history` - Historical data
  - `GET /api/metrics/statistics` - Comprehensive stats
  - `POST /api/metrics/reset` - Reset counters
  - `GET /api/metrics/export/json` - Export JSON
  - `GET /api/metrics/export/csv` - Export CSV
  - `GET /api/metrics/health` - Health check

#### 3. **MetricsMiddleware** (Auto-tracking)

- **Ubicación**: `src/dashboard/metrics_monitor.py`
- **Responsabilidad**: Captura automática de requests en Flask
- **Features**:
  - Before/after request hooks
  - Automatic latency calculation
  - Error detection (status ≥ 400)
  - User session tracking

---

## 📊 Metrics Tracked

### Request Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| **Request Rate** | Gauge | RPM | Requests per minute (rolling 5min window) |
| **Error Rate** | Gauge | % | Percentage of failed requests (status ≥ 400) |
| **Total Requests** | Counter | Count | Total requests since start |
| **Total Errors** | Counter | Count | Total errors since start |

### Latency Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| **P50 Latency** | Gauge | ms | 50th percentile (median) response time |
| **P95 Latency** | Gauge | ms | 95th percentile response time |
| **P99 Latency** | Gauge | ms | 99th percentile response time |

### User Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| **Active Users** | Gauge | Count | Users active in last 5 minutes |
| **WebSocket Connections** | Gauge | Count | Active WebSocket connections |

### Resource Metrics

| Metric | Type | Unit | Description |
|--------|------|------|-------------|
| **Memory Usage** | Gauge | % | Process memory as % of system total |
| **Memory Usage MB** | Gauge | MB | Process memory in megabytes |
| **CPU Usage** | Gauge | % | Process CPU usage percentage |

---

## 👨‍💻 Usage Guide

### Basic Setup

#### 1. Initialize MetricsMonitor

```python
from src.dashboard.metrics_monitor import get_metrics_monitor

# Get singleton instance (5 minute rolling window)
monitor = get_metrics_monitor(window_seconds=300)
```

#### 2. Register Flask Middleware (Automatic Tracking)

```python
from flask import Flask
from src.dashboard.metrics_monitor import MetricsMiddleware, get_metrics_monitor

app = Flask(__name__)
monitor = get_metrics_monitor()

# Register middleware for automatic request tracking
MetricsMiddleware(app, monitor)

# Now all requests are automatically tracked!
```

#### 3. Register API Routes

```python
from src.dashboard.metrics_routes import metrics_bp

app.register_blueprint(metrics_bp)

# API available at /api/metrics/*
```

### Manual Request Tracking

```python
import time
from src.dashboard.metrics_monitor import get_metrics_monitor

monitor = get_metrics_monitor()

# Track a successful request
start_time = time.time()
# ... do work ...
latency_ms = (time.time() - start_time) * 1000

monitor.record_request(
    latency_ms=latency_ms,
    is_error=False,
    user_id="user123"
)

# Track an error
monitor.record_request(
    latency_ms=500.0,
    is_error=True,
    user_id="user123"
)
```

### Get Current Metrics

```python
from src.dashboard.metrics_monitor import get_metrics_monitor

monitor = get_metrics_monitor()

# Get snapshot
snapshot = monitor.get_current_snapshot()

print(f"Request Rate: {snapshot.request_rate_rpm} RPM")
print(f"Error Rate: {snapshot.error_rate_pct}%")
print(f"P95 Latency: {snapshot.latency_p95_ms} ms")
print(f"Active Users: {snapshot.active_users}")
print(f"Memory Usage: {snapshot.memory_usage_mb} MB")
print(f"CPU Usage: {snapshot.cpu_usage_pct}%")
```

### Get Statistics

```python
monitor = get_metrics_monitor()

stats = monitor.get_statistics()

print("Current Metrics:")
for key, value in stats['current'].items():
    print(f"  {key}: {value}")

print("\nTotals:")
for key, value in stats['totals'].items():
    print(f"  {key}: {value}")
```

### Track User Activity

```python
monitor = get_metrics_monitor()

# Record user activity
monitor.record_user_activity("user123")

# Get active user count
active_count = monitor.get_active_users()
print(f"Active users: {active_count}")

# Get active user IDs
active_ids = monitor.get_active_user_ids()
print(f"Active user IDs: {active_ids}")
```

### WebSocket Tracking

```python
from flask_socketio import SocketIO
from src.dashboard.metrics_monitor import get_metrics_monitor

monitor = get_metrics_monitor()
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    monitor.increment_websocket_connections()
    print(f"WebSocket connections: {monitor.get_websocket_connections()}")

@socketio.on('disconnect')
def handle_disconnect():
    monitor.decrement_websocket_connections()
    print(f"WebSocket connections: {monitor.get_websocket_connections()}")
```

### Export Metrics

```python
monitor = get_metrics_monitor()

# Export to JSON
monitor.export_to_json('metrics_export.json')

# Export to CSV
monitor.export_to_csv('metrics_history.csv')
```

---

## 🌐 REST API Reference

### Base URL

```
http://localhost:8050/api/metrics
```

### Authentication

All endpoints require session-based authentication (except `/health`).

### Endpoints

#### 1. Get Current Metrics

```http
GET /api/metrics/current
```

**Response**:
```json
{
  "success": true,
  "metrics": {
    "timestamp": "2026-01-25T01:16:30.123456",
    "request_rate_rpm": 42.5,
    "error_rate_pct": 2.3,
    "latency_p50_ms": 15.2,
    "latency_p95_ms": 45.8,
    "latency_p99_ms": 78.5,
    "active_users": 12,
    "memory_usage_pct": 3.5,
    "memory_usage_mb": 125.4,
    "cpu_usage_pct": 12.3,
    "websocket_connections": 5,
    "total_requests": 1250,
    "total_errors": 35
  },
  "timestamp": "2026-01-25T01:16:30.123456"
}
```

#### 2. Get Metrics History

```http
GET /api/metrics/history?minutes=60
```

**Query Parameters**:
- `minutes` (optional): Number of minutes (default: 60, max: 60)

**Response**:
```json
{
  "success": true,
  "history": [
    {
      "timestamp": "2026-01-25T00:16:00.000000",
      "request_rate_rpm": 40.2,
      "error_rate_pct": 1.8,
      "latency_p50_ms": 14.5,
      "latency_p95_ms": 42.1,
      "latency_p99_ms": 75.3,
      "active_users": 10,
      "memory_usage_pct": 3.2,
      "memory_usage_mb": 120.1,
      "cpu_usage_pct": 11.5,
      "websocket_connections": 4,
      "total_requests": 1150,
      "total_errors": 30
    },
    // ... more snapshots
  ],
  "count": 60,
  "minutes": 60,
  "timestamp": "2026-01-25T01:16:30.123456"
}
```

#### 3. Get Statistics

```http
GET /api/metrics/statistics
```

**Response**:
```json
{
  "success": true,
  "statistics": {
    "current": {
      // ... current snapshot
    },
    "totals": {
      "total_requests": 1250,
      "total_errors": 35,
      "total_error_rate_pct": 2.8
    },
    "configuration": {
      "window_seconds": 300,
      "user_timeout_seconds": 300,
      "max_history_minutes": 60
    }
  },
  "timestamp": "2026-01-25T01:16:30.123456"
}
```

#### 4. Reset Statistics

```http
POST /api/metrics/reset
```

**Response**:
```json
{
  "success": true,
  "message": "Metrics statistics reset successfully",
  "timestamp": "2026-01-25T01:16:30.123456"
}
```

#### 5. Export to JSON

```http
GET /api/metrics/export/json
```

**Response**: JSON file download (`metrics_20260125_011630.json`)

#### 6. Export to CSV

```http
GET /api/metrics/export/csv
```

**Response**: CSV file download (`metrics_history_20260125_011630.csv`)

#### 7. Health Check

```http
GET /api/metrics/health
```

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "metrics_monitor": "operational",
    "request_tracking": "operational",
    "resource_monitoring": "operational",
    "websocket_tracking": "operational"
  },
  "current_rpm": 42.5,
  "timestamp": "2026-01-25T01:16:30.123456"
}
```

---

## 🚨 Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Error message details"
}
```

### Error Tracking

Requests with status code ≥ 400 are automatically tracked as errors:

```python
# Automatic error tracking via middleware
@app.route('/api/test')
def test_endpoint():
    if some_error:
        return jsonify({'error': 'Something went wrong'}), 500
        # Automatically tracked as error with latency
```

---

## 🎯 Best Practices

### 1. Use Singleton Pattern

```python
# ✅ GOOD - Use singleton
from src.dashboard.metrics_monitor import get_metrics_monitor
monitor = get_metrics_monitor()

# ❌ BAD - Don't create new instances
from src.dashboard.metrics_monitor import MetricsMonitor
monitor = MetricsMonitor()  # Creates duplicate!
```

### 2. Let Middleware Handle Request Tracking

```python
# ✅ GOOD - Automatic tracking
MetricsMiddleware(app, monitor)
# All requests automatically tracked!

# ❌ BAD - Manual tracking for every request
@app.route('/api/test')
def test():
    start = time.time()
    result = do_work()
    monitor.record_request((time.time()-start)*1000, False)
    return result
```

### 3. Use Context-Specific Tracking for Special Cases

```python
# Manual tracking for non-HTTP operations
def background_task():
    start = time.time()
    try:
        process_data()
        latency_ms = (time.time() - start) * 1000
        monitor.record_request(latency_ms, is_error=False)
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        monitor.record_request(latency_ms, is_error=True)
        raise
```

### 4. Monitor Key Thresholds

```python
monitor = get_metrics_monitor()
snapshot = monitor.get_current_snapshot()

# Alert on high error rate
if snapshot.error_rate_pct > 5.0:
    logger.warning(f"⚠️ High error rate: {snapshot.error_rate_pct}%")
    send_alert("High error rate detected")

# Alert on high P99 latency
if snapshot.latency_p99_ms > 1000:
    logger.warning(f"⚠️ High P99 latency: {snapshot.latency_p99_ms}ms")
    send_alert("Slow response times detected")

# Alert on high memory usage
if snapshot.memory_usage_pct > 80:
    logger.warning(f"⚠️ High memory usage: {snapshot.memory_usage_pct}%")
    send_alert("High memory usage detected")
```

### 5. Regular Exports for Analysis

```python
import schedule
from datetime import datetime

def export_daily_metrics():
    monitor = get_metrics_monitor()
    filename = f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
    monitor.export_to_json(f"data/metrics/{filename}")
    logger.info(f"✅ Daily metrics exported: {filename}")

# Schedule daily export at midnight
schedule.every().day.at("00:00").do(export_daily_metrics)
```

---

## 🔍 Monitoring Strategies

### Real-Time Dashboard Integration

```javascript
// Frontend: dashboard.js
function fetchMetrics() {
    fetch('/api/metrics/current')
        .then(r => r.json())
        .then(data => {
            const m = data.metrics;
            
            // Update KPIs
            updateKPI('rpm', m.request_rate_rpm, 'RPM');
            updateKPI('error-rate', m.error_rate_pct, '%');
            updateKPI('p95-latency', m.latency_p95_ms, 'ms');
            updateKPI('active-users', m.active_users, 'users');
            updateKPI('memory', m.memory_usage_mb, 'MB');
            updateKPI('cpu', m.cpu_usage_pct, '%');
            
            // Update charts
            updateLatencyChart(m);
        });
}

// Poll every 5 seconds
setInterval(fetchMetrics, 5000);
```

### Historical Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

monitor = get_metrics_monitor()
history = monitor.get_metrics_history(minutes=60)

# Convert to DataFrame
df = pd.DataFrame(history)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Plot latency over time
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['latency_p50_ms'], label='P50')
plt.plot(df['timestamp'], df['latency_p95_ms'], label='P95')
plt.plot(df['timestamp'], df['latency_p99_ms'], label='P99')
plt.xlabel('Time')
plt.ylabel('Latency (ms)')
plt.title('Request Latency Over Time')
plt.legend()
plt.tight_layout()
plt.savefig('latency_analysis.png')
```

### Alerting System

```python
import threading
import time

class MetricsAlerter:
    def __init__(self, monitor, check_interval=30):
        self.monitor = monitor
        self.check_interval = check_interval
        self.thresholds = {
            'error_rate_pct': 5.0,
            'latency_p99_ms': 1000.0,
            'memory_usage_pct': 80.0,
            'cpu_usage_pct': 80.0
        }
        
        # Start monitoring thread
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def _monitor_loop(self):
        while True:
            try:
                snapshot = self.monitor.get_current_snapshot()
                
                # Check thresholds
                if snapshot.error_rate_pct > self.thresholds['error_rate_pct']:
                    self._send_alert('ERROR_RATE', snapshot.error_rate_pct)
                
                if snapshot.latency_p99_ms > self.thresholds['latency_p99_ms']:
                    self._send_alert('HIGH_LATENCY', snapshot.latency_p99_ms)
                
                if snapshot.memory_usage_pct > self.thresholds['memory_usage_pct']:
                    self._send_alert('HIGH_MEMORY', snapshot.memory_usage_pct)
                
                if snapshot.cpu_usage_pct > self.thresholds['cpu_usage_pct']:
                    self._send_alert('HIGH_CPU', snapshot.cpu_usage_pct)
                
            except Exception as e:
                logger.error(f"Error in alerter: {e}")
            
            time.sleep(self.check_interval)
    
    def _send_alert(self, alert_type, value):
        logger.warning(f"⚠️ ALERT: {alert_type} = {value}")
        # Send email, Slack, etc.

# Usage
monitor = get_metrics_monitor()
alerter = MetricsAlerter(monitor, check_interval=30)
```

---

## ⚡ Performance Considerations

### Memory Usage

- **Request Deque**: Max 10,000 entries (~1 MB)
- **History Deque**: Max 60 snapshots (~50 KB)
- **Active Users Dict**: Grows with users, cleaned every 60s
- **Total Estimated**: ~2-5 MB depending on load

### CPU Impact

- **Per Request**: <0.1ms overhead
- **Cleanup Thread**: Runs every 60s, <10ms CPU time
- **Percentile Calculation**: O(n log n) where n ≤ 10,000

### Thread Safety

- All operations use `threading.RLock()`
- Safe for multi-threaded Flask/Gunicorn
- No blocking operations in hot path

### Optimization Tips

1. **Adjust Window Size**: Smaller window = less memory, faster calculations
```python
# 1 minute window for high-frequency services
monitor = get_metrics_monitor(window_seconds=60)
```

2. **Reduce History**: Less history = less memory
```python
# Modify in metrics_monitor.py
self._metrics_history = deque(maxlen=30)  # 30 minutes instead of 60
```

3. **Disable Resource Monitoring**: If CPU/Memory not needed
```python
# Skip in snapshot
def get_current_snapshot_lightweight(self):
    snapshot = self.get_current_snapshot()
    snapshot.memory_usage_pct = 0
    snapshot.memory_usage_mb = 0
    snapshot.cpu_usage_pct = 0
    return snapshot
```

---

## 🔧 Troubleshooting

### Issue: Metrics Not Updating

**Symptoms**: API returns stale data

**Solutions**:
1. Check middleware is registered:
```python
MetricsMiddleware(app, monitor)
```

2. Verify requests are being tracked:
```python
monitor = get_metrics_monitor()
print(monitor._total_requests)  # Should be > 0
```

3. Check cleanup thread is running:
```python
print(monitor._cleanup_thread.is_alive())  # Should be True
```

### Issue: High Memory Usage

**Symptoms**: Memory grows over time

**Solutions**:
1. Check request deque size:
```python
print(len(monitor._requests))  # Should be ≤ 10,000
```

2. Check active users cleanup:
```python
print(len(monitor._active_users))  # Should decrease over time
```

3. Reduce history size:
```python
# In metrics_monitor.py
self._metrics_history = deque(maxlen=30)  # Reduce from 60
```

### Issue: Percentiles Incorrect

**Symptoms**: P50/P95/P99 values seem wrong

**Solutions**:
1. Check window size:
```python
print(monitor.window_seconds)  # Should be 300 (5 min)
```

2. Verify enough data points:
```python
with monitor._lock:
    now = time.time()
    cutoff = now - monitor.window_seconds
    count = sum(1 for ts, _, _ in monitor._requests if ts >= cutoff)
    print(f"Data points in window: {count}")  # Should be > 10
```

3. Check latency values are reasonable:
```python
with monitor._lock:
    latencies = [lat for ts, lat, _ in monitor._requests]
    print(f"Min: {min(latencies)}, Max: {max(latencies)}")
```

### Issue: WebSocket Count Wrong

**Symptoms**: Connection count doesn't match reality

**Solutions**:
1. Ensure increment/decrement are called:
```python
@socketio.on('connect')
def handle_connect():
    monitor.increment_websocket_connections()
    print(f"WS connected: {monitor.get_websocket_connections()}")

@socketio.on('disconnect')
def handle_disconnect():
    monitor.decrement_websocket_connections()
    print(f"WS disconnected: {monitor.get_websocket_connections()}")
```

2. Manual reset if needed:
```python
with monitor._lock:
    monitor._websocket_connections = 0  # Reset to 0
```

---

## 📝 Integration Examples

### Example 1: Production Flask App

```python
# main.py
from flask import Flask
from flask_socketio import SocketIO
from src.dashboard.metrics_monitor import get_metrics_monitor, MetricsMiddleware
from src.dashboard.metrics_routes import metrics_bp

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize metrics
monitor = get_metrics_monitor(window_seconds=300)

# Register middleware (automatic tracking)
MetricsMiddleware(app, monitor)

# Register API routes
app.register_blueprint(metrics_bp)

# WebSocket tracking
@socketio.on('connect')
def handle_connect():
    monitor.increment_websocket_connections()

@socketio.on('disconnect')
def handle_disconnect():
    monitor.decrement_websocket_connections()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8050)
```

### Example 2: Custom Monitoring Endpoint

```python
# custom_metrics.py
from flask import Blueprint, jsonify
from src.dashboard.metrics_monitor import get_metrics_monitor

custom_bp = Blueprint('custom_metrics', __name__)

@custom_bp.route('/api/custom/health')
def custom_health():
    monitor = get_metrics_monitor()
    snapshot = monitor.get_current_snapshot()
    
    # Custom health logic
    is_healthy = (
        snapshot.error_rate_pct < 5.0 and
        snapshot.latency_p99_ms < 1000 and
        snapshot.memory_usage_pct < 80 and
        snapshot.cpu_usage_pct < 80
    )
    
    return jsonify({
        'status': 'healthy' if is_healthy else 'degraded',
        'checks': {
            'error_rate': snapshot.error_rate_pct < 5.0,
            'latency': snapshot.latency_p99_ms < 1000,
            'memory': snapshot.memory_usage_pct < 80,
            'cpu': snapshot.cpu_usage_pct < 80
        },
        'metrics': snapshot.to_dict()
    })
```

### Example 3: Metrics Dashboard Widget

```html
<!-- templates/metrics_widget.html -->
<div id="metrics-widget" class="widget">
    <h3>System Metrics</h3>
    <div class="metrics-grid">
        <div class="metric">
            <span class="label">Request Rate</span>
            <span id="rpm" class="value">--</span>
            <span class="unit">RPM</span>
        </div>
        <div class="metric">
            <span class="label">Error Rate</span>
            <span id="error-rate" class="value">--</span>
            <span class="unit">%</span>
        </div>
        <div class="metric">
            <span class="label">P95 Latency</span>
            <span id="p95-latency" class="value">--</span>
            <span class="unit">ms</span>
        </div>
        <div class="metric">
            <span class="label">Active Users</span>
            <span id="active-users" class="value">--</span>
            <span class="unit">users</span>
        </div>
    </div>
</div>

<script>
function updateMetrics() {
    fetch('/api/metrics/current')
        .then(r => r.json())
        .then(data => {
            const m = data.metrics;
            document.getElementById('rpm').textContent = m.request_rate_rpm;
            document.getElementById('error-rate').textContent = m.error_rate_pct;
            document.getElementById('p95-latency').textContent = m.latency_p95_ms;
            document.getElementById('active-users').textContent = m.active_users;
        });
}

// Update every 5 seconds
setInterval(updateMetrics, 5000);
updateMetrics();
</script>
```

---

## 📚 Additional Resources

### Related Files

- `src/dashboard/metrics_monitor.py` - Core metrics engine
- `src/dashboard/metrics_routes.py` - REST API endpoints
- `src/dashboard/web_app.py` - Flask app with middleware integration
- `src/dashboard/VERIFICATION_REPORT.md` - System verification

### External Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [NumPy Percentile](https://numpy.org/doc/stable/reference/generated/numpy.percentile.html)

---

## ✅ Testing

### Unit Tests

```python
# tests/test_metrics_monitor.py
import pytest
import time
from src.dashboard.metrics_monitor import MetricsMonitor

def test_request_tracking():
    monitor = MetricsMonitor(window_seconds=60)
    
    # Record some requests
    monitor.record_request(10.0, is_error=False)
    monitor.record_request(20.0, is_error=False)
    monitor.record_request(30.0, is_error=True)
    
    # Check totals
    assert monitor._total_requests == 3
    assert monitor._total_errors == 1
    
    # Check error rate
    error_rate = monitor.get_error_rate_pct()
    assert error_rate == 33.33  # 1/3 = 33.33%

def test_latency_percentiles():
    monitor = MetricsMonitor(window_seconds=60)
    
    # Record 100 requests with known latencies
    for i in range(100):
        monitor.record_request(float(i), is_error=False)
    
    p50, p95, p99 = monitor.get_latency_percentiles()
    
    assert 45 <= p50 <= 55  # P50 should be around 50
    assert 90 <= p95 <= 96  # P95 should be around 95
    assert 97 <= p99 <= 100  # P99 should be around 99

def test_user_tracking():
    monitor = MetricsMonitor(window_seconds=60)
    
    # Record user activity
    monitor.record_user_activity('user1')
    monitor.record_user_activity('user2')
    monitor.record_user_activity('user3')
    
    # Check active users
    assert monitor.get_active_users() == 3
    
    # Check user IDs
    user_ids = monitor.get_active_user_ids()
    assert 'user1' in user_ids
    assert 'user2' in user_ids
    assert 'user3' in user_ids
```

### Integration Tests

```python
# tests/test_metrics_api.py
import pytest
from flask import Flask
from src.dashboard.metrics_routes import metrics_bp
from src.dashboard.metrics_monitor import get_metrics_monitor, MetricsMiddleware

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    app.register_blueprint(metrics_bp)
    
    monitor = get_metrics_monitor()
    MetricsMiddleware(app, monitor)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_current_metrics_endpoint(client):
    # Login first
    with client.session_transaction() as sess:
        sess['user'] = 'test_user'
    
    # Get current metrics
    response = client.get('/api/metrics/current')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] == True
    assert 'metrics' in data
    assert 'timestamp' in data['metrics']

def test_health_endpoint(client):
    response = client.get('/api/metrics/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] == True
    assert data['status'] == 'healthy'
    assert data['version'] == '1.0.0'
```

---

## 🏆 Changelog

### Version 1.0.0 (2026-01-25)

**Initial Release**

- ✅ Core MetricsMonitor engine
- ✅ Request tracking with rolling windows
- ✅ Latency percentiles (P50, P95, P99)
- ✅ User activity tracking
- ✅ WebSocket connection monitoring
- ✅ System resource monitoring (CPU, Memory)
- ✅ Historical snapshots (60 minutes)
- ✅ REST API endpoints
- ✅ JSON/CSV export
- ✅ Flask middleware for automatic tracking
- ✅ Thread-safe operations
- ✅ Background cleanup thread
- ✅ Comprehensive documentation

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-01-25 01:16 CET  
**Maintained By**: Juan Carlos Garcia Arriero  
**Status**: ✅ Complete & Production Ready
