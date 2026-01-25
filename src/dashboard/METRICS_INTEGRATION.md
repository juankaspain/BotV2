# 📊 Metrics System Integration Guide

**Version**: 1.0  
**Date**: 25 Enero 2026

## ✅ System Components

1. **metrics_monitor.py** - Core metrics tracking (✅ Created)
2. **metrics_routes.py** - REST API endpoints (✅ Created)
3. **web_app.py** - Integration required (⚠️ Pending)
4. **Frontend** - Dashboard UI (⚠️ Pending)

---

## 🔧 Step 1: Install Dependencies

```bash
pip install psutil
```

**Required packages**:
- `psutil` - System resource monitoring (CPU, Memory)
- `numpy` - Percentile calculations (already installed)

---

## 🔧 Step 2: Update web_app.py

### Add Imports (after line 42)

```python
# ==================== METRICS IMPORTS ====================
try:
    from .metrics_monitor import get_metrics_monitor, MetricsMiddleware
    from .metrics_routes import metrics_bp
    HAS_METRICS = True
except ImportError:
    HAS_METRICS = False
    logger.warning("⚠️ Metrics module not available")
```

### Register Blueprint (after line 287, where other blueprints are registered)

```python
# Register blueprints
self.app.register_blueprint(control_bp)
self.app.register_blueprint(monitoring_bp)
self.app.register_blueprint(strategy_bp)

# ✅ ADD THIS:
if HAS_METRICS:
    self.app.register_blueprint(metrics_bp)
    logger.info("✅ Metrics blueprint registered")
```

### Initialize Metrics Monitor (in `__init__` method, after blueprints registration)

```python
# ✅ ADD THIS after blueprint registration:
if HAS_METRICS:
    self.metrics_monitor = get_metrics_monitor(window_seconds=300)
    MetricsMiddleware(self.app, self.metrics_monitor)
    logger.info("✅ Metrics monitoring enabled")
else:
    self.metrics_monitor = None
```

### Update Startup Banner (in `_log_startup_banner` method)

```python
logger.info(f"GZIP: {'✅ Enabled (60-85% reduction)' if HAS_COMPRESS else '⚠️ Disabled'}")
logger.info(f"Metrics: {'✅ Enabled' if HAS_METRICS else '⚠️ Disabled'}"  # ✅ ADD THIS
logger.info(f"Auth: {self.auth.username} / {'✓' if self.auth.password_hash else '✗'}")
```

### Add WebSocket Handler for Metrics (in `_setup_websocket_handlers` method)

```python
def _setup_websocket_handlers(self):
    @self.socketio.on('connect')
    def handle_connect():
        emit('connected', {'message': f'Connected to BotV2 v{__version__}', 'version': __version__})
        
        # ✅ ADD THIS:
        if HAS_METRICS and self.metrics_monitor:
            self.metrics_monitor.increment_websocket_connections()
    
    @self.socketio.on('disconnect')
    def handle_disconnect():
        # ✅ ADD THIS:
        if HAS_METRICS and self.metrics_monitor:
            self.metrics_monitor.decrement_websocket_connections()
    
    # ✅ ADD THIS NEW HANDLER:
    @self.socketio.on('request_metrics')
    def handle_metrics_request():
        """Send current metrics snapshot to requesting client"""
        if HAS_METRICS and self.metrics_monitor:
            snapshot = self.metrics_monitor.get_current_snapshot()
            emit('metrics_update', snapshot.to_dict())
```

### Add Background Metrics Broadcast (new method in ProfessionalDashboard class)

```python
def _start_metrics_broadcast(self):
    """Start background thread for broadcasting metrics via WebSocket"""
    if not HAS_METRICS or not self.metrics_monitor:
        return
    
    import threading
    import time
    
    def broadcast_loop():
        while True:
            try:
                time.sleep(5)  # Broadcast every 5 seconds
                snapshot = self.metrics_monitor.get_current_snapshot()
                self.socketio.emit('metrics_update', snapshot.to_dict(), broadcast=True)
            except Exception as e:
                logger.error(f"Error broadcasting metrics: {e}")
    
    thread = threading.Thread(target=broadcast_loop, daemon=True)
    thread.start()
    logger.info("✅ Metrics broadcast thread started (5s interval)")
```

**Call this method in `__init__`** (after WebSocket setup):

```python
self._setup_routes()
self._setup_websocket_handlers()
self._start_metrics_broadcast()  # ✅ ADD THIS
self._log_startup_banner()
```

---

## 🌐 Step 3: API Endpoints

All endpoints require authentication except `/health`.

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics/current` | GET | Current metrics snapshot |
| `/api/metrics/history?minutes=60` | GET | Historical data (1 hour max) |
| `/api/metrics/statistics` | GET | Comprehensive statistics |
| `/api/metrics/reset` | POST | Reset all statistics |
| `/api/metrics/export/json` | GET | Export to JSON file |
| `/api/metrics/export/csv` | GET | Export to CSV file |
| `/api/metrics/health` | GET | Health check (no auth) |

### Example API Response

**GET /api/metrics/current**

```json
{
  "success": true,
  "metrics": {
    "timestamp": "2026-01-25T00:15:30",
    "request_rate_rpm": 45.2,
    "error_rate_pct": 1.5,
    "latency_p50_ms": 12.5,
    "latency_p95_ms": 45.3,
    "latency_p99_ms": 89.7,
    "active_users": 3,
    "memory_usage_pct": 2.5,
    "memory_usage_mb": 125.3,
    "cpu_usage_pct": 8.2,
    "websocket_connections": 2,
    "total_requests": 1250,
    "total_errors": 15
  },
  "timestamp": "2026-01-25T00:15:30"
}
```

---

## 🎨 Step 4: Frontend Integration

### Add Menu Item (in `dashboard.html`)

```html
<a class="menu-item" data-section="metrics">
    <i class="fas fa-chart-line"></i> Metrics
</a>
```

### Add Renderer Function (in `dashboard.js`)

```javascript
function renderMetrics(data) {
    const c = document.getElementById('main-container');
    
    c.innerHTML = `
        <div class="section-header">
            <h1><i class="fas fa-chart-line"></i> System Metrics</h1>
            <p>Real-time monitoring of system performance and resources</p>
        </div>
        
        <!-- KPI Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fas fa-tachometer-alt"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">Request Rate</div>
                    <div class="kpi-value" id="metric-rpm">0</div>
                    <div class="kpi-unit">req/min</div>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon danger"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">Error Rate</div>
                    <div class="kpi-value" id="metric-errors">0</div>
                    <div class="kpi-unit">%</div>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon info"><i class="fas fa-clock"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">P95 Latency</div>
                    <div class="kpi-value" id="metric-latency">0</div>
                    <div class="kpi-unit">ms</div>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon success"><i class="fas fa-users"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">Active Users</div>
                    <div class="kpi-value" id="metric-users">0</div>
                    <div class="kpi-unit">users</div>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon warning"><i class="fas fa-memory"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">Memory Usage</div>
                    <div class="kpi-value" id="metric-memory">0</div>
                    <div class="kpi-unit">MB</div>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fas fa-microchip"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">CPU Usage</div>
                    <div class="kpi-value" id="metric-cpu">0</div>
                    <div class="kpi-unit">%</div>
                </div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="chart-row">
            <div class="chart-container">
                <div class="chart-header">
                    <h3>Request Rate (RPM)</h3>
                </div>
                <div id="chart-rpm" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-header">
                    <h3>Latency Percentiles</h3>
                </div>
                <div id="chart-latency" class="chart"></div>
            </div>
        </div>
        
        <div class="chart-row">
            <div class="chart-container">
                <div class="chart-header">
                    <h3>System Resources</h3>
                </div>
                <div id="chart-resources" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-header">
                    <h3>WebSocket Connections</h3>
                </div>
                <div id="chart-websockets" class="chart"></div>
            </div>
        </div>
    `;
    
    // Load initial data
    loadMetricsData();
    
    // Subscribe to real-time updates
    socket.on('metrics_update', updateMetricsDisplay);
}

function loadMetricsData() {
    fetch('/api/metrics/current')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateMetricsDisplay(data.metrics);
            }
        })
        .catch(err => Logger.error('Failed to load metrics', err));
    
    // Also load history for charts
    fetch('/api/metrics/history?minutes=60')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                createMetricsCharts(data.history);
            }
        })
        .catch(err => Logger.error('Failed to load metrics history', err));
}

function updateMetricsDisplay(metrics) {
    // Update KPI cards
    document.getElementById('metric-rpm').textContent = metrics.request_rate_rpm.toFixed(1);
    document.getElementById('metric-errors').textContent = metrics.error_rate_pct.toFixed(2);
    document.getElementById('metric-latency').textContent = metrics.latency_p95_ms.toFixed(1);
    document.getElementById('metric-users').textContent = metrics.active_users;
    document.getElementById('metric-memory').textContent = metrics.memory_usage_mb.toFixed(1);
    document.getElementById('metric-cpu').textContent = metrics.cpu_usage_pct.toFixed(1);
    
    // Update error card styling based on error rate
    const errorCard = document.getElementById('metric-errors').closest('.kpi-card');
    if (metrics.error_rate_pct > 5) {
        errorCard.classList.add('alert');
    } else {
        errorCard.classList.remove('alert');
    }
}

function createMetricsCharts(history) {
    // Extract data
    const timestamps = history.map(h => h.timestamp);
    const rpm = history.map(h => h.request_rate_rpm);
    const p50 = history.map(h => h.latency_p50_ms);
    const p95 = history.map(h => h.latency_p95_ms);
    const p99 = history.map(h => h.latency_p99_ms);
    const memory = history.map(h => h.memory_usage_mb);
    const cpu = history.map(h => h.cpu_usage_pct);
    const ws = history.map(h => h.websocket_connections);
    
    // Request Rate Chart
    const rpmTrace = {
        x: timestamps,
        y: rpm,
        type: 'scatter',
        mode: 'lines',
        name: 'RPM',
        line: { color: COLORS[currentTheme].primary, width: 2 }
    };
    
    Plotly.newPlot('chart-rpm', [rpmTrace], {
        ...getStandardChartConfig('chart-rpm').layout,
        yaxis: { title: 'Requests/min' }
    }, getStandardChartConfig('chart-rpm').config);
    
    // Latency Chart
    const latencyTraces = [
        { x: timestamps, y: p50, name: 'P50', line: { color: '#4CAF50' } },
        { x: timestamps, y: p95, name: 'P95', line: { color: '#FF9800' } },
        { x: timestamps, y: p99, name: 'P99', line: { color: '#F44336' } }
    ];
    
    Plotly.newPlot('chart-latency', latencyTraces, {
        ...getStandardChartConfig('chart-latency').layout,
        yaxis: { title: 'Latency (ms)' }
    }, getStandardChartConfig('chart-latency').config);
    
    // Resources Chart
    const resourceTraces = [
        { x: timestamps, y: memory, name: 'Memory (MB)', yaxis: 'y', line: { color: '#2196F3' } },
        { x: timestamps, y: cpu, name: 'CPU (%)', yaxis: 'y2', line: { color: '#9C27B0' } }
    ];
    
    Plotly.newPlot('chart-resources', resourceTraces, {
        ...getStandardChartConfig('chart-resources').layout,
        yaxis: { title: 'Memory (MB)' },
        yaxis2: { title: 'CPU (%)', overlaying: 'y', side: 'right' }
    }, getStandardChartConfig('chart-resources').config);
    
    // WebSocket Chart
    const wsTrace = {
        x: timestamps,
        y: ws,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Connections',
        line: { color: COLORS[currentTheme].success, width: 2 }
    };
    
    Plotly.newPlot('chart-websockets', [wsTrace], {
        ...getStandardChartConfig('chart-websockets').layout,
        yaxis: { title: 'Active Connections' }
    }, getStandardChartConfig('chart-websockets').config);
    
    // Register chart instances
    chartInstances['chart-rpm'] = true;
    chartInstances['chart-latency'] = true;
    chartInstances['chart-resources'] = true;
    chartInstances['chart-websockets'] = true;
}
```

### Register Renderer (add to `renderers` object)

```javascript
const renderers = {
    dashboard: renderDashboard,
    portfolio: renderPortfolio,
    trades: renderTrades,
    performance: renderPerformance,
    risk: renderRisk,
    markets: renderMarkets,
    strategies: renderStrategies,
    backtesting: renderBacktesting,
    live_monitor: renderLiveMonitor,
    control_panel: renderControlPanel,
    settings: renderSettings,
    metrics: renderMetrics  // ✅ ADD THIS
};
```

---

## 🧪 Testing

### 1. Start Dashboard

```bash
python -m src.dashboard.web_app
```

### 2. Check Logs

Expected output:
```
✅ MetricsMonitor initialized (window: 300s)
✅ MetricsMiddleware registered
✅ Metrics blueprint registered
✅ Metrics monitoring enabled
✅ Metrics broadcast thread started (5s interval)
```

### 3. Test API

```bash
# Health check (no auth)
curl http://localhost:8050/api/metrics/health

# Current metrics (requires auth)
curl -b cookies.txt http://localhost:8050/api/metrics/current

# Export to JSON
curl -b cookies.txt http://localhost:8050/api/metrics/export/json -o metrics.json
```

### 4. Test Frontend

1. Login to dashboard
2. Click "Metrics" in menu
3. Verify:
   - KPI cards update every 5 seconds
   - Charts display historical data
   - Error rates show in red if >5%
   - WebSocket connection count increments

### 5. Generate Load

```bash
# Simple load test
for i in {1..100}; do
    curl -b cookies.txt http://localhost:8050/api/section/dashboard > /dev/null 2>&1
    sleep 0.1
done
```

Watch metrics update in real-time!

---

## 📊 Metrics Explained

### Request Metrics

- **Request Rate (RPM)**: Requests per minute over rolling window (5 min default)
- **Error Rate (%)**: Percentage of requests with 4xx/5xx status codes
- **P50 Latency**: Median response time (50% of requests faster)
- **P95 Latency**: 95th percentile (95% of requests faster)
- **P99 Latency**: 99th percentile (99% of requests faster)

### User Metrics

- **Active Users**: Users with activity in last 5 minutes
- **WebSocket Connections**: Current active WebSocket connections

### System Metrics

- **Memory Usage (MB)**: Process memory consumption
- **Memory Usage (%)**: Process memory as % of system total
- **CPU Usage (%)**: Process CPU utilization

### Statistics

- **Total Requests**: All requests since start/reset
- **Total Errors**: All errors since start/reset
- **Total Error Rate**: Overall error percentage

---

## 🔧 Configuration

### Change Rolling Window

```python
# Default: 300 seconds (5 minutes)
metrics_monitor = get_metrics_monitor(window_seconds=600)  # 10 minutes
```

### Change User Timeout

```python
monitor = get_metrics_monitor()
monitor._user_timeout = 600  # 10 minutes
```

### Change Broadcast Interval

In `_start_metrics_broadcast()` method:

```python
time.sleep(10)  # Change from 5 to 10 seconds
```

---

## 🚀 Production Recommendations

### 1. Enable Redis for Rate Limiting

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

Metrics will be more accurate with centralized storage.

### 2. Set Alerts

Add alerting logic in metrics_monitor.py:

```python
if snapshot.error_rate_pct > 10:
    # Send alert to admin
    logger.critical(f"High error rate: {snapshot.error_rate_pct}%")

if snapshot.cpu_usage_pct > 80:
    # Send alert to admin
    logger.critical(f"High CPU usage: {snapshot.cpu_usage_pct}%")
```

### 3. Export Metrics Regularly

Add cron job:

```bash
# Export metrics daily at midnight
0 0 * * * curl -b /path/to/cookies.txt http://localhost:8050/api/metrics/export/csv -o /backups/metrics_$(date +\%Y\%m\%d).csv
```

### 4. Monitor Metrics Endpoint

Use external monitoring to check:

```bash
curl http://localhost:8050/api/metrics/health
```

Alert if response is not `{"status": "healthy"}`.

---

## 📚 Additional Resources

- **metrics_monitor.py**: Core monitoring logic
- **metrics_routes.py**: REST API documentation
- **VERIFICATION_REPORT.md**: System verification checklist
- **psutil docs**: https://psutil.readthedocs.io/

---

**Status**: ✅ Ready for integration  
**Next Steps**: Update web_app.py as described above
