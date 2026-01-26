# 🎮 Control Panel v4.2 - Documentation

## ⚡ Quick Setup (5 minutos)

### Step 1: Verificar Instalación

```bash
cd ~/BotV2
git pull origin main
```

### Step 2: Acceder al Control Panel

```
URL: http://localhost:8050/control
Login: admin / your_password
```

---

## ✨ Features

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

### Control Panel no aparece

**Solución**: Verificar que la ruta está registrada en `dashboard/web_app.py`

### Error 404 en /control

**Solución**:
1. Verifica rutas en `web_app.py`
2. Restart el dashboard
3. Check logs

### Bot no arranca desde Control Panel

**Solución**:
1. Verifica que existe: `ls -la bot/main.py`
2. Check permisos
3. Prueba manual: `python3 bot/main.py`

---

## ✅ What's Working

- ✅ Backend controller (process management)
- ✅ REST API (14 endpoints)
- ✅ Professional UI
- ✅ Real-time status updates
- ✅ Strategy management (22 strategies)
- ✅ Risk sliders with validation
- ✅ Toast notifications
- ✅ Responsive design

---

**Fecha:** 26 Enero 2026  
**Version:** v4.2
