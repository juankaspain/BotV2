# Live Monitoring v4.3 - Comprehensive Documentation

## 📊 Overview

El **Live Monitoring v4.3** es un sistema de monitoreo en tiempo real completamente integrado en BotV2 que proporciona visibilidad instantánea de todas las operaciones del bot de trading.

### Features Principales

- ✅ **Activity Log Streaming**: Registro de eventos en tiempo real
- ✅ **Strategy Signals**: Visualización de señales de trading
- ✅ **Open Positions Monitor**: Seguimiento de posiciones abiertas
- ✅ **Browser Alerts**: Notificaciones instantáneas
- ✅ **WebSocket Real-time**: Actualizaciones sin polling
- ✅ **API RESTful**: Integración programable

---

## 🏛️ Architecture

### Component Stack

```
┌──────────────────────────────────────────────────────────────┐
│              BotV2 Live Monitoring v4.3 Architecture              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│   ┌────────────────────────────────────────────────────┐   │
│   │        monitoring.html (Live UI)                        │   │
│   │   - Activity Feed                                        │   │
│   │   - Strategy Signals Panel                               │   │
│   │   - Positions Monitor                                    │   │
│   │   - Real-time Charts                                     │   │
│   └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket / REST API
                              │
┌──────────────────────────────────────────────────────────────┐
│                     API LAYER                                    │
│   ┌────────────────────────────────────────────────────┐   │
│   │         monitoring_routes.py                           │   │
│   │   Flask Blueprint (/api/monitoring)                  │   │
│   │                                                          │   │
│   │   Endpoints:                                           │   │
│   │   - GET  /activity                                     │   │
│   │   - POST /activity/clear                               │   │
│   │   - GET  /signals                                      │   │
│   │   - POST /signals/update                               │   │
│   │   - GET  /positions                                    │   │
│   │   - POST /positions/update                             │   │
│   │   - GET  /alerts                                       │   │
│   │   - GET  /stats                                        │   │
│   └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              │
┌──────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                          │
│   ┌────────────────────────────────────────────────────┐   │
│   │           live_monitor.py                            │   │
│   │   LiveMonitoringSystem (Singleton)                   │   │
│   │                                                          │   │
│   │   Components:                                          │   │
│   │   - ActivityLogManager                                 │   │
│   │   - StrategySignalTracker                              │   │
│   │   - OpenPositionMonitor                                │   │
│   │   - BrowserAlertSystem                                 │   │
│   │                                                          │   │
│   │   Thread-safe operations                               │   │
│   │   Deque-based ring buffers                             │   │
│   │   Statistics tracking                                  │   │
│   └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              │
┌──────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                 │
│   Trading Bot │ Strategy Engine │ Portfolio Manager          │
└──────────────────────────────────────────────────────────────┘
```

### Files Structure

```
BotV2/
├── src/
│   ├── dashboard/
│   │   ├── web_app.py                # Dashboard principal v4.3
│   │   ├── monitoring_routes.py      # 🆕 Routes API del Live Monitoring
│   │   ├── live_monitor.py           # 🆕 Core del Live Monitoring
│   │   ├── templates/
│   │   │   ├── dashboard.html        # UI principal (v4.3)
│   │   │   └── monitoring.html       # 🆕 UI del Live Monitoring
│   │   └── static/
│   │       └── js/
│   │           └── monitoring.js     # 🆕 JavaScript del Live Monitoring
├── docs/
│   └── LIVE_MONITORING_V4.3.md   # Este documento
└── README.md
```

---

## 🚀 Integration in Dashboard

### Navigation Menu

El Live Monitoring v4.3 está integrado en el sidebar del dashboard con un diseño distintivo:

```html
<!-- Nueva sección en el menú -->
<div class="menu-section">
    <div class="menu-section-title">Monitoring</div>
    <div class="menu-item live-monitoring" data-section="live-monitor">
        <svg class="menu-icon" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5z..."/>
            <!-- Animated indicator -->
            <circle cx="10" cy="4" r="3" fill="currentColor" opacity="0.3">
                <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite" />
            </circle>
        </svg>
        <span>Live Monitor</span>
        <span class="menu-badge new">v4.3</span>
    </div>
</div>
```

### Visual Design

```css
/* Degradado verde esmeralda distintivo */
.menu-item.live-monitoring {
    background: linear-gradient(135deg, var(--accent-monitoring) 0%, #059669 100%);
    color: white;
    font-weight: 600;
    position: relative;
    overflow: hidden;
}

/* Efecto shimmer al hover */
.menu-item.live-monitoring::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

.menu-item.live-monitoring:hover::before {
    left: 100%;
}
```

### Access Points

1. **Sidebar**: Sección "Monitoring" → Botón "Live Monitor"
2. **User Menu**: Dropdown → "Live Monitor"
3. **URL Directa**: `http://localhost:8050/monitoring`

---

## 📚 API Reference

### Base URL

```
http://localhost:8050/api/monitoring
```

### Authentication

Todas las rutas requieren autenticación de sesión:

```python
@login_required
def endpoint():
    # ...
```

### Activity Log Endpoints

#### GET /activity

Obtener eventos de actividad recientes.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `event_type` | string | null | Filtrar por tipo de evento |
| `limit` | integer | 50 | Número máximo de eventos |

**Event Types:**
- `ORDER`: Ejecución de órdenes
- `STRATEGY`: Cambios de estrategia
- `RISK`: Alertas de riesgo
- `SYSTEM`: Eventos del sistema
- `ALERT`: Alertas generales

**Example Request:**

```bash
curl -X GET 'http://localhost:8050/api/monitoring/activity?event_type=ORDER&limit=10' \
  -H 'Cookie: session=...' \
  -H 'Content-Type: application/json'
```

**Example Response:**

```json
{
  "success": true,
  "events": [
    {
      "timestamp": "2026-01-22T20:30:15.123456Z",
      "event_type": "ORDER",
      "message": "Market order executed: BUY 0.1 BTC at $50,000",
      "severity": "INFO",
      "metadata": {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 50000
      }
    },
    {
      "timestamp": "2026-01-22T20:29:45.987654Z",
      "event_type": "STRATEGY",
      "message": "MA Crossover: BUY signal generated",
      "severity": "INFO",
      "metadata": {
        "strategy": "MA_Crossover",
        "signal": "BUY",
        "confidence": 0.85
      }
    }
  ],
  "count": 2,
  "timestamp": "2026-01-22T20:30:20.000000Z"
}
```

#### POST /activity/clear

Limpiar todos los eventos de actividad.

**Example Request:**

```bash
curl -X POST 'http://localhost:8050/api/monitoring/activity/clear' \
  -H 'Cookie: session=...' \
  -H 'Content-Type: application/json'
```

**Example Response:**

```json
{
  "success": true,
  "message": "Activity log cleared",
  "timestamp": "2026-01-22T20:31:00.000000Z"
}
```

---

### Strategy Signals Endpoints

#### GET /signals

Obtener señales de estrategia actuales.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy` | string | null | Filtrar por nombre de estrategia |

**Example Request:**

```bash
curl -X GET 'http://localhost:8050/api/monitoring/signals?strategy=MA_Crossover' \
  -H 'Cookie: session=...' \
  -H 'Content-Type: application/json'
```

**Example Response:**

```json
{
  "success": true,
  "signals": [
    {
      "strategy_name": "MA_Crossover",
      "symbol": "BTCUSDT",
      "signal_type": "BUY",
      "confidence": 0.85,
      "timestamp": "2026-01-22T20:29:45.987654Z",
      "indicators": {
        "sma_50": 50000,
        "sma_200": 48000,
        "rsi": 65
      },
      "ensemble_vote": "BUY"
    }
  ],
  "count": 1,
  "timestamp": "2026-01-22T20:31:10.000000Z"
}
```

#### POST /signals/update

Actualizar una señal de estrategia.

**Request Body:**

```json
{
  "strategy_name": "MA_Crossover",
  "symbol": "BTCUSDT",
  "signal_type": "BUY",
  "confidence": 0.85,
  "indicators": {
    "sma_50": 50000,
    "sma_200": 48000
  },
  "ensemble_vote": "BUY"
}
```

**Example Response:**

```json
{
  "success": true,
  "message": "Signal updated",
  "signal": {
    "strategy_name": "MA_Crossover",
    "symbol": "BTCUSDT",
    "signal_type": "BUY",
    "confidence": 0.85,
    "timestamp": "2026-01-22T20:31:30.000000Z"
  },
  "timestamp": "2026-01-22T20:31:30.000000Z"
}
```

---

### Positions Endpoints

#### GET /positions

Obtener todas las posiciones abiertas.

**Example Response:**

```json
{
  "success": true,
  "positions": [
    {
      "position_id": "pos_123456",
      "symbol": "BTCUSDT",
      "side": "LONG",
      "entry_price": 50000,
      "current_price": 51000,
      "size": 0.1,
      "unrealized_pnl": 100,
      "unrealized_pnl_pct": 2.0,
      "time_in_position": "01:30:00",
      "stop_loss": 49000,
      "stop_loss_pct": 2.0,
      "take_profit": 52000,
      "strategy": "MA_Crossover"
    }
  ],
  "count": 1,
  "summary": {
    "total_unrealized_pnl": 100.0,
    "avg_pnl_pct": 2.0
  },
  "timestamp": "2026-01-22T20:32:00.000000Z"
}
```

#### POST /positions/update

Actualizar una posición abierta.

**Request Body:**

```json
{
  "position_id": "pos_123456",
  "symbol": "BTCUSDT",
  "side": "LONG",
  "entry_price": 50000,
  "current_price": 51500,
  "size": 0.1,
  "unrealized_pnl": 150,
  "unrealized_pnl_pct": 3.0,
  "time_in_position": "02:00:00",
  "stop_loss": 49500,
  "stop_loss_pct": 1.0,
  "take_profit": 52000,
  "strategy": "MA_Crossover"
}
```

#### POST /positions/close

Cerrar una posición.

**Request Body:**

```json
{
  "position_id": "pos_123456",
  "final_pnl": 200,
  "final_pnl_pct": 4.0
}
```

---

### Alerts Endpoint

#### GET /alerts

Obtener alertas pendientes del navegador.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clear` | boolean | true | Limpiar alertas después de obtenerlas |

**Example Response:**

```json
{
  "success": true,
  "alerts": [
    {
      "title": "Stop Loss Triggered",
      "message": "Position BTCUSDT closed at stop loss",
      "severity": "WARNING",
      "timestamp": "2026-01-22T20:33:00.000000Z"
    }
  ],
  "count": 1,
  "timestamp": "2026-01-22T20:33:05.000000Z"
}
```

---

### Statistics Endpoint

#### GET /stats

Obtener estadísticas del sistema de monitoreo.

**Example Response:**

```json
{
  "success": true,
  "statistics": {
    "total_events": 1234,
    "total_signals": 45,
    "total_positions": 12,
    "active_positions": 3,
    "total_alerts_sent": 67,
    "last_update": "2026-01-22T20:33:10.000000Z",
    "uptime_seconds": 3600
  },
  "timestamp": "2026-01-22T20:33:15.000000Z"
}
```

---

## 🛠️ Usage Examples

### Python Integration

```python
from src.dashboard.live_monitor import get_live_monitor, EventType, AlertSeverity

# Get singleton instance
monitor = get_live_monitor()

# Log an activity event
monitor.log_event(
    event_type=EventType.ORDER,
    message="Market order executed: BUY 0.1 BTC at $50,000",
    severity="INFO",
    metadata={
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 50000
    }
)

# Update strategy signal
from src.dashboard.live_monitor import StrategySignal
from datetime import datetime

signal = StrategySignal(
    strategy_name="MA_Crossover",
    symbol="BTCUSDT",
    signal_type="BUY",
    confidence=0.85,
    timestamp=datetime.now(),
    indicators={"sma_50": 50000, "sma_200": 48000},
    ensemble_vote="BUY"
)
monitor.update_signal(signal)

# Update open position
from src.dashboard.live_monitor import OpenPosition
from datetime import timedelta

position = OpenPosition(
    position_id="pos_123456",
    symbol="BTCUSDT",
    side="LONG",
    entry_price=50000,
    current_price=51000,
    size=0.1,
    unrealized_pnl=100,
    unrealized_pnl_pct=2.0,
    time_in_position=timedelta(hours=1, minutes=30),
    stop_loss=49000,
    stop_loss_pct=2.0,
    take_profit=52000,
    strategy="MA_Crossover"
)
monitor.update_position(position)

# Send browser alert
monitor.send_alert(
    title="Stop Loss Triggered",
    message="Position BTCUSDT closed at stop loss",
    severity=AlertSeverity.WARNING
)

# Get statistics
stats = monitor.get_statistics()
print(f"Total events: {stats['total_events']}")
print(f"Active positions: {stats['active_positions']}")
```

### JavaScript/Frontend Integration

```javascript
// Fetch activity log
async function fetchActivityLog() {
    const response = await fetch('/api/monitoring/activity?limit=50');
    const data = await response.json();
    
    if (data.success) {
        data.events.forEach(event => {
            console.log(`[${event.timestamp}] ${event.event_type}: ${event.message}`);
        });
    }
}

// Fetch strategy signals
async function fetchStrategySignals() {
    const response = await fetch('/api/monitoring/signals');
    const data = await response.json();
    
    if (data.success) {
        data.signals.forEach(signal => {
            console.log(`${signal.strategy_name} - ${signal.symbol}: ${signal.signal_type} (${signal.confidence})`);
        });
    }
}

// Fetch open positions
async function fetchOpenPositions() {
    const response = await fetch('/api/monitoring/positions');
    const data = await response.json();
    
    if (data.success) {
        console.log(`Total unrealized P&L: $${data.summary.total_unrealized_pnl}`);
        data.positions.forEach(pos => {
            console.log(`${pos.symbol}: ${pos.side} ${pos.size} @ $${pos.current_price} (P&L: ${pos.unrealized_pnl_pct}%)`);
        });
    }
}

// Poll for alerts
setInterval(async () => {
    const response = await fetch('/api/monitoring/alerts?clear=true');
    const data = await response.json();
    
    if (data.success && data.count > 0) {
        data.alerts.forEach(alert => {
            // Show browser notification
            if (Notification.permission === 'granted') {
                new Notification(alert.title, {
                    body: alert.message,
                    icon: '/static/img/logo.png'
                });
            }
        });
    }
}, 5000); // Check every 5 seconds
```

---

## 🐛 Troubleshooting

### Live Monitoring No Aparece en el Menú

**Síntoma**: El botón del Live Monitoring no es visible.

**Solución**:
1. Verificar que `dashboard.html` está actualizado a v4.3:
   ```bash
   grep "v4.3" src/dashboard/templates/dashboard.html
   ```
2. Limpiar caché del navegador (Ctrl+F5)
3. Verificar versión del servidor:
   ```bash
   curl http://localhost:8050/health | jq '.version'
   # Debe retornar: "4.3"
   ```

### Error 404 al Acceder a /monitoring

**Síntoma**: Página no encontrada.

**Solución**:
1. Verificar que el blueprint está registrado en `web_app.py`:
   ```python
   self.app.register_blueprint(monitoring_bp)
   ```
2. Verificar que `monitoring_routes.py` existe y no tiene errores de sintaxis
3. Reiniciar el servidor Flask
4. Verificar logs del servidor para errores de importación:
   ```bash
   tail -f logs/dashboard.log | grep -i error
   ```

### Datos No Se Actualizan en Tiempo Real

**Síntoma**: La UI del Live Monitoring no muestra datos actualizados.

**Solución**:
1. Verificar que el singleton del LiveMonitoringSystem está inicializado:
   ```python
   from src.dashboard.live_monitor import get_live_monitor
   monitor = get_live_monitor()
   print(monitor.get_statistics())
   ```
2. Verificar que el bot está enviando eventos al monitor
3. Comprobar que no hay errores en la consola del navegador (F12)
4. Verificar que el polling está activo en `monitoring.js`

### API Endpoints Retornan 401 Unauthorized

**Síntoma**: Peticiones a `/api/monitoring/*` retornan error 401.

**Solución**:
1. Verificar que estás autenticado:
   ```bash
   curl -c cookies.txt -X POST http://localhost:8050/login \
     -d 'username=admin&password=yourpassword'
   
   curl -b cookies.txt http://localhost:8050/api/monitoring/activity
   ```
2. Verificar que la sesión no ha expirado (timeout: 30 minutos)
3. Comprobar que el decorador `@login_required` está correctamente importado

---

## 🚀 Roadmap

### v4.4 (Planificado)

- 📊 **Enhanced Charts**: Gráficos interactivos de Plotly en el Live Monitor
- 🔔 **Advanced Alerts**: Configuración de alertas personalizadas por usuario
- 📄 **Export Logs**: Exportar activity log a CSV/JSON
- 🔍 **Advanced Filtering**: Búsqueda y filtros avanzados en activity log

### v4.5 (Futuro)

- 📧 **Email Notifications**: Alertas por email para eventos críticos
- 📱 **Mobile App**: App nativa iOS/Android con push notifications
- 🤖 **AI Insights**: Análisis predictivo de señales con ML
- 🌍 **Multi-Instance**: Monitorear múltiples bots simultáneamente

---

## 📝 Changelog v4.3

### Nuevas Características

✅ **Live Monitoring System**
   - Sistema de monitoreo en tiempo real completamente funcional
   - Activity log con ring buffer (maxlen=1000)
   - Strategy signal tracking
   - Open positions monitor
   - Browser alert system

✅ **API REST Completa**
   - 11 endpoints RESTful documentados
   - Rate limiting integrado
   - Autenticación por sesión
   - Audit logging de todas las acciones

✅ **Integración en Dashboard**
   - Botón distintivo con degradado verde esmeralda
   - Badge "v4.3" con animación
   - Icono animado con pulso
   - Acceso desde múltiples puntos (sidebar y user menu)

✅ **Thread-Safe Operations**
   - Singleton pattern para instancia única
   - threading.Lock para operaciones concurrentes
   - Deque-based ring buffers (O(1) append/pop)

✅ **Statistics Tracking**
   - Total events, signals, positions
   - Active positions count
   - Alerts sent counter
   - Uptime tracking

---

## 📞 Support

### Resources

- [Main Documentation](../README.md)
- [Control Panel v4.2 Docs](./CONTROL_PANEL_V4.2.md)
- [API Reference](./API_REFERENCE.md) _(pendiente)_
- [GitHub Issues](https://github.com/juankaspain/BotV2/issues)

### Contact

- **Email**: juanca755@hotmail.com
- **GitHub**: [juankaspain/BotV2](https://github.com/juankaspain/BotV2)

---

## 📝 License

Este proyecto es de **uso personal** y no se monetiza como SaaS.

---

**Última Actualización**: 22 de Enero de 2026  
**Versión del Documento**: 1.0  
**Autor**: Juan Carlos Garcia Arriero