# 🎛️ Control Panel v4.2 - Complete Documentation

## 📝 Overview

El **Control Panel v4.2** es una interfaz web profesional para gestionar completamente BotV2 sin necesidad de editar código o acceder a la consola.

### ✨ Características Principales

#### 1. **Bot Operations** 🤖
- **Start/Stop/Restart**: Control completo del bot
- **Emergency Stop**: Cierre inmediato de posiciones + shutdown
- **Pause/Resume**: Pausar trading sin detener el bot
- **Status Monitor**: Estado en tiempo real (running/stopped/paused)
- **Uptime Tracking**: Tiempo de actividad del bot
- **Process Info**: PID del proceso para debugging

#### 2. **Quick Actions** ⚡
- **Close All Positions**: Cierra todas las posiciones abiertas
- **Reduce Positions 50%**: Reduce el tamaño de todas las posiciones
- **Pause Trading**: Detiene ejecución de nuevos trades
- **One-Click**: Acciones críticas con confirmación

#### 3. **Risk Parameters** 🛡️
- **Max Drawdown**: 5-30% (slider)
- **Position Size**: 1-10% (slider)
- **Stop Loss**: 0.5-5% (slider)
- **Take Profit**: 1-20% (slider)
- **Live Preview**: Valores actualizados en tiempo real
- **Validation**: Rangos seguros automáticos

#### 4. **Strategy Management** 📊
- **List All Strategies**: 22 estrategias disponibles
- **Enable/Disable**: Toggle individual por estrategia
- **Bulk Actions**: Activar/Desactivar todas
- **Categories**: Agrupadas por tipo (momentum, mean reversion, etc.)
- **Status Indicators**: Visual feedback de estado

---

## 🚀 Instalación e Integración

### Prerequisitos

El Control Panel ya está instalado con los commits recientes:

```bash
Commit 029c6f5: Bot Controller (backend)
Commit 8c7b6d9: API Routes (REST endpoints)
Commit b7fc2a5: UI Template (frontend)
Commit be1b31c: Integration scripts
```

### Paso 1: Integrar en web_app.py

Añade estas líneas a `src/dashboard/web_app.py`:

```python
# Import control routes (añadir con otros imports)
from .control_routes import control_bp

# Register blueprint (añadir después de otros blueprints)
app.register_blueprint(control_bp)

# Add control panel route (añadir con otras rutas)
@app.route('/control')
@login_required
def control_panel():
    """Control panel page"""
    return render_template('control.html')
```

### Paso 2: Actualizar Dashboard Navigation

Edita el template principal del dashboard para añadir el enlace:

```html
<!-- En el sidebar del dashboard -->
<nav>
    <a href="/dashboard">Dashboard</a>
    <a href="/control" class="active">Control Panel</a> <!-- NUEVO -->
    <a href="/portfolio">Portfolio</a>
    <a href="/strategies">Strategies</a>
</nav>
```

### Paso 3: Restart Dashboard

```bash
cd ~/BotV2
bash UPDATE.sh
```

### Paso 4: Acceder

```
URL: http://localhost:8050/control
Login: admin / tu_password
```

---

## 📚 API Reference

### Bot Control Endpoints

#### `GET /api/control/status`
Obtiene el estado actual del bot.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "pid": 12345,
    "uptime": 3600,
    "start_time": "2026-01-22T20:00:00",
    "is_trading": true
  }
}
```

#### `POST /api/control/start`
Inicia el bot.

**Response:**
```json
{
  "success": true,
  "message": "Bot started successfully",
  "data": {"pid": 12345}
}
```

#### `POST /api/control/stop?graceful=true`
Detiene el bot gracefully.

**Query Params:**
- `graceful`: `true|false` (default: `true`)

**Response:**
```json
{
  "success": true,
  "message": "Bot stopping gracefully"
}
```

#### `POST /api/control/restart`
Reinicia el bot (stop + start).

**Response:**
```json
{
  "success": true,
  "message": "Bot restarted",
  "data": {"pid": 54321}
}
```

#### `POST /api/control/emergency-stop`
Parada de emergencia (cierra posiciones + shutdown inmediato).

**Response:**
```json
{
  "success": true,
  "message": "Emergency stop executed"
}
```

#### `POST /api/control/pause`
Pausa el trading (bot sigue corriendo pero no ejecuta trades).

**Response:**
```json
{
  "success": true,
  "message": "Trading paused"
}
```

#### `POST /api/control/resume`
Reanuda el trading.

**Response:**
```json
{
  "success": true,
  "message": "Trading resumed"
}
```

### Quick Actions Endpoints

#### `POST /api/control/close-positions`
Cierra todas las posiciones abiertas.

**Response:**
```json
{
  "success": true,
  "message": "Command sent to close all positions"
}
```

#### `POST /api/control/reduce-positions`
Reduce todas las posiciones por un porcentaje.

**Request Body:**
```json
{"percentage": 50.0}
```

**Response:**
```json
{
  "success": true,
  "message": "Command sent to reduce positions by 50%"
}
```

### Strategy Management Endpoints

#### `GET /api/control/strategies`
Lista todas las estrategias disponibles.

**Response:**
```json
{
  "success": true,
  "data": {
    "strategies": [
      {
        "name": "momentum",
        "enabled": true,
        "category": "momentum",
        "description": "Momentum Strategy"
      },
      ...
    ],
    "total": 22,
    "categories": ["momentum", "mean_reversion", "arbitrage", "macro"]
  }
}
```

#### `PUT /api/control/strategies/<strategy_name>`
Actualiza una estrategia específica.

**Request Body:**
```json
{
  "enabled": true,
  "parameters": {
    "threshold": 0.7
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Strategy momentum update queued"
}
```

### Config Management Endpoints

#### `GET /api/control/config`
Obtiene la configuración actual.

**Response:**
```json
{
  "success": true,
  "data": {
    "risk": {...},
    "trading": {...}
  }
}
```

#### `PUT /api/control/config/risk`
Actualiza parámetros de riesgo.

**Request Body:**
```json
{
  "max_drawdown": 0.15,
  "position_size": 0.05,
  "stop_loss": 0.02,
  "take_profit": 0.05
}
```

**Validations:**
- `max_drawdown`: 0.05 - 0.50 (5% - 50%)
- `position_size`: 0.01 - 0.20 (1% - 20%)
- `stop_loss`: 0.005 - 0.05 (0.5% - 5%)
- `take_profit`: 0.01 - 0.20 (1% - 20%)

**Response:**
```json
{
  "success": true,
  "message": "Risk parameters update queued"
}
```

---

## 📱 UI Guide

### Layout

```
┌──────────────────────────────────────────────────┐
│  🎛️ Control Panel       [● Running]                  │
│  Manage bot operations, strategies, and risk            │
└──────────────────────────────────────────────────┘

┌───────────────────────┐ ┌───────────────────────┐
│ 🤖 Bot Operations      │ │ ⚡ Quick Actions       │
├───────────────────────┤ ├───────────────────────┤
│ Uptime: 3h 24m        │ │ ❌ Close All Positions │
│ PID: 12345            │ │ 📉 Reduce Positions   │
│                       │ │ ⏸ Pause Trading       │
│ [▶ Start] [⏸ Stop]   │ └───────────────────────┘
│ [🔄 Restart]          │
│                       │
│ [🚨 Emergency Stop]   │
└───────────────────────┘

┌──────────────────────────────────────────────────┐
│ 🛡️ Risk Parameters                                     │
├──────────────────────────────────────────────────┤
│ Max Drawdown:     15% ────○──────────           │
│ Position Size:     5% ────○──────────           │
│ Stop Loss:         2% ────○──────────           │
│ Take Profit:       5% ────○──────────           │
│                                                  │
│ [💾 Save Changes]                                   │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ 📊 Strategy Management                               │
├──────────────────────────────────────────────────┤
│ [✓ Enable All] [✗ Disable All]                     │
│                                                  │
│ ● Momentum         [momentum • enabled]    ␣ ON   │
│ ● Mean Reversion   [mean_rev • enabled]    ␣ ON   │
│ ○ Breakout         [breakout • disabled]   ␣ OFF  │
│ ... (22 total strategies)                        │
└──────────────────────────────────────────────────┘
```

### Color Scheme (v4.1)

```css
Background: #0d1117 (dark)
Cards: #161b22 (darker gray)
Borders: #30363d (subtle)
Text: #e6edf3 (white)
Accent Blue: #2f81f7 (primary actions)
Accent Green: #3fb950 (success)
Accent Red: #f85149 (danger)
Accent Orange: #d29922 (warning)
```

### Interactive Elements

- **Buttons**: Hover effect + disabled states
- **Sliders**: Smooth dragging + live value update
- **Toggles**: Animated switch (iOS-style)
- **Toasts**: Auto-dismiss after 3s
- **Status Badge**: Color-coded (green/gray/orange)
- **Loading**: Spinner animation for async actions

---

## 🔧 Troubleshooting

### El bot no arranca desde el Control Panel

**Síntoma**: Click en "Start" pero el bot no se inicia

**Soluciones**:
1. Check que `main.py` existe en `src/main.py`
2. Verifica permisos de ejecución: `chmod +x src/main.py`
3. Revisa logs del dashboard: `tail -f dashboard.log`
4. Intenta arrancar manualmente: `python3 src/main.py`

### Los sliders no guardan cambios

**Síntoma**: Mover sliders pero los valores no se aplican

**Soluciones**:
1. Click en "Save Changes" después de ajustar
2. Verifica que `trading_config.yaml` existe
3. Check permisos de escritura: `ls -la src/config/`
4. Revisa la consola del navegador (F12) para errores

### Las estrategias no se listan

**Síntoma**: "No strategies found" en Strategy Management

**Soluciones**:
1. Verifica que existen archivos en `src/strategies/`
2. Check que no sean archivos privados (`_*.py`)
3. Revisa endpoint: `curl http://localhost:8050/api/control/strategies`
4. Restart dashboard

### Emergency Stop no funciona

**Síntoma**: Click en Emergency Stop pero el bot sigue

**Soluciones**:
1. Usa `kill -9 <PID>` manualmente
2. Check `.bot_command.json` se está creando
3. Verifica que main.py lee el command file
4. Restart completo del sistema

---

## 🔒 Security Considerations

### Authentication
- ✅ Control Panel requiere login
- ✅ Session-based auth con cookies
- ⚠️ Considera añadir 2FA en producción

### Authorization
- ✅ Solo usuarios admin pueden acceder
- ⚠️ Implementar RBAC para multi-usuario
- ⚠️ Rate limiting en endpoints críticos

### Critical Actions
- ✅ Confirmación para Emergency Stop
- ✅ Confirmación para Close All Positions
- ✅ Validación de rangos en risk parameters

### File-based Signaling
- ⚠️ `.bot_state.json` y `.bot_command.json` son sensibles
- ⚠️ Asegurar permisos restrictivos: `chmod 600`
- ⚠️ Considerar usar Redis/DB en producción

### API Security
- ✅ CSRF protection (Flask-WTF)
- ⚠️ Añadir API keys para integraciones externas
- ⚠️ SSL/TLS en producción (HTTPS)

---

## 🗺️ Roadmap

### v4.3 - Live Monitoring (Next)
- ☐ Activity log stream (WebSocket)
- ☐ Real-time strategy signals display
- ☐ Position monitor con P&L live
- ☐ Browser alerts system

### v4.4 - Strategy Editor
- ☐ Parameter editor UI
- ☐ Parameter presets (Conservative/Balanced/Aggressive)
- ☐ Quick backtest (7 días)
- ☐ Change history + rollback

### v4.5 - Performance Analytics
- ☐ Strategy comparison table
- ☐ Trade journal con export CSV
- ☐ Risk metrics dashboard (VaR, Beta, Correlation)
- ☐ Advanced charts (Plotly)

### v4.6 - Automation
- ☐ Scheduled actions (cron-like)
- ☐ Conditional rules (if/then automation)
- ☐ Auto-rebalancing
- ☐ Backup & recovery

---

## 📄 File Structure

```
BotV2/
├── src/
│   ├── dashboard/
│   │   ├── bot_controller.py      # Backend controller
│   │   ├── control_routes.py      # API endpoints
│   │   ├── web_app.py             # Flask app (integrate here)
│   │   └── templates/
│   │       └── control.html       # UI frontend
│   ├── main.py                    # Bot entry point
│   └── strategies/               # 22 strategies
├── .bot_state.json              # Bot status file
├── .bot_command.json            # Command signaling
├── UPDATE_CONTROL.sh            # Integration script
└── docs/
    └── CONTROL_PANEL_v4.2.md    # This file
```

---

## ❓ FAQ

**Q: ¿Puedo usar el Control Panel en producción?**  
A: Sí, pero añade HTTPS, 2FA, y migra file-signaling a Redis.

**Q: ¿El bot se puede controlar desde móvil?**  
A: Sí, la UI es responsive y funciona en navegadores móviles.

**Q: ¿Qué pasa si cierro el navegador con el bot corriendo?**  
A: El bot sigue corriendo independientemente. El dashboard solo es una interfaz.

**Q: ¿Puedo tener múltiples usuarios?**  
A: Sí, pero necesitas implementar RBAC y permisos granulares.

**Q: ¿Los cambios de risk parameters se aplican inmediatamente?**  
A: Depende de la implementación. Actualmente se "queue" y requieren restart.

**Q: ¿Puedo revertir cambios de configuración?**  
A: Planificado para v4.4 (Change History + Rollback).

---

## ✅ Testing Checklist

### Bot Operations
- [ ] Start bot (debe aparecer PID)
- [ ] Stop bot gracefully (debe tardar ~2s)
- [ ] Restart bot (stop + start automático)
- [ ] Emergency stop (inmediato)
- [ ] Pause trading (status cambia a "paused")
- [ ] Resume trading (status vuelve a "running")
- [ ] Uptime counter actualiza cada 5s

### Quick Actions
- [ ] Close all positions (confirmación)
- [ ] Reduce positions 50% (confirmación)
- [ ] Pause/Resume toggle funciona

### Risk Parameters
- [ ] Sliders se mueven suavemente
- [ ] Valores se actualizan en tiempo real
- [ ] Save Changes muestra toast de éxito
- [ ] Validación de rangos (ej: position size > 20% rechazado)

### Strategy Management
- [ ] Lista carga las 22 estrategias
- [ ] Toggle ON/OFF individual
- [ ] Enable All activa todas
- [ ] Disable All desactiva todas
- [ ] Categorías correctas (momentum, mean_reversion, etc.)

### UI/UX
- [ ] Status badge cambia color según estado
- [ ] Toasts aparecen y desaparecen (3s)
- [ ] Confirmaciones para acciones críticas
- [ ] Loading spinners durante acciones async
- [ ] Responsive en móvil

---

## 👏 Contributors

- **Backend**: `bot_controller.py` (Process management, signaling)
- **API**: `control_routes.py` (REST endpoints, validation)
- **Frontend**: `control.html` (Professional UI v4.1)
- **Integration**: `UPDATE_CONTROL.sh` (Auto-integration script)

---

## 📝 License

Propietario - Uso personal BotV2

---

**🎉 ¡Control Panel v4.2 listo para producción!**

Para soporte o issues, contacta al equipo de desarrollo.
