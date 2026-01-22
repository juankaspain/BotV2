# 🎛️ Control Panel v4.2 - Quick Start

## ⚡ 5-Minute Setup

### Step 1: Verify Installation

El Control Panel ya está instalado en tu repo:

```bash
cd ~/BotV2
git pull origin main
```

**Commits incluidos:**
- [029c6f5](https://github.com/juankaspain/BotV2/commit/029c6f5) - `bot_controller.py` (Backend)
- [8c7b6d9](https://github.com/juankaspain/BotV2/commit/8c7b6d9) - `control_routes.py` (API)
- [b7fc2a5](https://github.com/juankaspain/BotV2/commit/b7fc2a5) - `control.html` (UI)
- [be1b31c](https://github.com/juankaspain/BotV2/commit/be1b31c) - Integration scripts
- [bc63090](https://github.com/juankaspain/BotV2/commit/bc63090) - Documentation

### Step 2: Integrate into Dashboard

Edita `src/dashboard/web_app.py`:

```python
# Añadir con otros imports (línea ~15)
from .control_routes import control_bp

# Añadir con otros blueprints (línea ~50)
app.register_blueprint(control_bp)

# Añadir nueva ruta (línea ~150, después de @app.route('/dashboard'))
@app.route('/control')
@login_required
def control_panel():
    """Control panel page"""
    return render_template('control.html')
```

### Step 3: Restart Dashboard

```bash
bash UPDATE.sh
```

### Step 4: Access Control Panel

```
URL: http://localhost:8050/control
Login: admin / your_password
```

---

## ✨ Features Included

### 🤖 Bot Operations
- ▶ Start / ⏸ Stop / 🔄 Restart
- 🚨 Emergency Stop (close all + shutdown)
- ⏸ Pause/Resume trading
- 📊 Real-time status (uptime, PID)

### ⚡ Quick Actions
- ❌ Close All Positions
- 📉 Reduce Positions 50%
- ⏸ Pause Trading

### 🛡️ Risk Parameters
- Max Drawdown slider (5-30%)
- Position Size slider (1-10%)
- Stop Loss slider (0.5-5%)
- Take Profit slider (1-20%)
- 💾 Save Changes button

### 📊 Strategy Management
- List all 22 strategies
- Enable/Disable individual strategies
- Bulk Enable/Disable All
- Category grouping

---

## 🧪 Testing

### Quick Test (2 minutos)

1. **Abrir Control Panel**
   ```
   http://localhost:8050/control
   ```

2. **Verificar Status**
   - Badge muestra "Stopped" o "Running"
   - Uptime actualiza cada 5s si está running

3. **Probar Bot Control**
   ```
   Click "Start" → Esperar 2s → Ver status "Running"
   Click "Stop" → Confirmar → Ver status "Stopped"
   ```

4. **Probar Risk Sliders**
   ```
   Mover slider "Max Drawdown" → Ver valor actualizar
   Click "Save Changes" → Ver toast de éxito
   ```

5. **Verificar Strategies**
   ```
   Scroll a "Strategy Management"
   Ver lista de 22 estrategias
   Toggle ON/OFF una estrategia
   ```

---

## 📚 API Endpoints

### Bot Control
```bash
# Get status
curl http://localhost:8050/api/control/status

# Start bot
curl -X POST http://localhost:8050/api/control/start

# Stop bot
curl -X POST http://localhost:8050/api/control/stop

# Emergency stop
curl -X POST http://localhost:8050/api/control/emergency-stop
```

### Quick Actions
```bash
# Close all positions
curl -X POST http://localhost:8050/api/control/close-positions

# Reduce positions
curl -X POST http://localhost:8050/api/control/reduce-positions \
  -H "Content-Type: application/json" \
  -d '{"percentage": 50}'
```

### Strategies
```bash
# List strategies
curl http://localhost:8050/api/control/strategies

# Update strategy
curl -X PUT http://localhost:8050/api/control/strategies/momentum \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## 🔧 Troubleshooting

### Control Panel no aparece en el menú

**Solución**: Añade el link manualmente al template del dashboard:

```html
<!-- En src/dashboard/templates/dashboard.html -->
<nav>
  <a href="/dashboard">Dashboard</a>
  <a href="/control">Control Panel</a> <!-- AÑADIR ESTO -->
  <a href="/portfolio">Portfolio</a>
</nav>
```

### Error 404 en /control

**Problema**: Ruta no registrada

**Solución**:
1. Verifica que añadiste la ruta en `web_app.py`
2. Restart el dashboard: `bash UPDATE.sh`
3. Check logs: `tail -f dashboard.log`

### Error 500 en /api/control/*

**Problema**: Blueprint no registrado

**Solución**:
1. Verifica import: `from .control_routes import control_bp`
2. Verifica registro: `app.register_blueprint(control_bp)`
3. Restart dashboard

### Bot no arranca desde Control Panel

**Problema**: Path incorrecto a main.py

**Solución**:
1. Verifica que existe: `ls -la src/main.py`
2. Check permisos: `chmod +x src/main.py`
3. Prueba manual: `python3 src/main.py`

---

## 🗺️ Next Steps: Roadmap v4.3-v4.6

### v4.3 - Live Monitoring (1 week)
- WebSocket para activity log stream
- Real-time strategy signals
- Position monitor con P&L live
- Browser alerts

### v4.4 - Strategy Editor (1 week)
- Parameter editor UI
- Presets (Conservative/Balanced/Aggressive)
- Quick backtest (7 days)
- Change history + rollback

### v4.5 - Performance Analytics (1 week)
- Strategy comparison table
- Trade journal + CSV export
- Risk metrics (VaR, Beta)
- Advanced charts (Plotly)

### v4.6 - Automation (1-2 weeks)
- Scheduled actions (cron)
- Conditional rules (if/then)
- Auto-rebalancing
- Backup & recovery

**Total timeline: 5-6 weeks**

---

## 📋 Files Added

```
src/dashboard/
  bot_controller.py          (342 lines) - Backend controller
  control_routes.py          (291 lines) - API endpoints  
  templates/
    control.html             (850 lines) - UI frontend

docs/
  CONTROL_PANEL_v4.2.md      (650 lines) - Full documentation

CONTROL_PANEL_README.md      (This file) - Quick start
UPDATE_CONTROL.sh            (Integration script)
```

**Total:** ~2,200 lines of professional code

---

## ✅ What's Working

- ✅ Backend controller (process management)
- ✅ REST API (14 endpoints)
- ✅ Professional UI (v4.1 design system)
- ✅ Real-time status updates (5s polling)
- ✅ Strategy management (22 strategies)
- ✅ Risk sliders with validation
- ✅ Toast notifications
- ✅ Confirmation dialogs
- ✅ Loading states
- ✅ Responsive design

---

## ⚠️ What's TODO (for full production)

- ⚠️ Config hot-reload (currently queued)
- ⚠️ Strategy parameter persistence
- ⚠️ main.py integration for command file monitoring
- ⚠️ HTTPS/SSL for production
- ⚠️ 2FA authentication
- ⚠️ RBAC for multi-user
- ⚠️ Redis instead of file-based signaling

---

## 👍 Summary

**Control Panel v4.2 te da:**

1. 🎮 **Control total del bot** sin tocar código
2. ⚡ **Acciones rápidas** para emergencias
3. 🔧 **Risk management** en tiempo real
4. 📊 **Strategy control** granular
5. 🎨 **UI profesional** nivel enterprise

**Todo en 5 minutos de setup** 🚀

Para documentación completa: [CONTROL_PANEL_v4.2.md](docs/CONTROL_PANEL_v4.2.md)

---

**🎉 Ready to rock!** 

Comienza usando el Control Panel y dame feedback para v4.3.
