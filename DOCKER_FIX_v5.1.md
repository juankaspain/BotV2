# 🐛 Docker Fix - Dashboard v5.1 Upgrade

**Issue**: Dashboard container failing after v5.1 upgrade  
**Cause**: Docker compose using old `dashboard_standalone.py` (removed)  
**Solution**: Rebuild containers with updated compose files  
**Date**: 2026-01-23

---

## ⚡ QUICK FIX

```bash
# 1. Stop containers
docker-compose -f docker-compose.demo.yml down

# 2. Remove old images
docker rmi botv2-dashboard:latest botv2-app:latest

# 3. Rebuild with new configuration
docker-compose -f docker-compose.demo.yml build --no-cache

# 4. Start containers
docker-compose -f docker-compose.demo.yml up -d

# 5. Check logs
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard
```

---

## 🔍 WHAT CHANGED

### Files Updated
- ✅ `docker-compose.yml` - Updated dashboard command
- ✅ `docker-compose.demo.yml` - Updated dashboard command
- ✅ `src/dashboard/web_app.py` - Upgraded to v5.1

### Old Configuration (Broken)
```yaml
command: ["python", "src/dashboard/dashboard_standalone.py"]
```

### New Configuration (Fixed)
```yaml
command: ["python", "-u", "-m", "src.dashboard.web_app"]
```

---

## 🛠️ STEP-BY-STEP FIX

### 1. Stop All Containers
```bash
# For demo mode
docker-compose -f docker-compose.demo.yml down

# For standard mode
docker-compose down
```

### 2. Clean Old Images
```bash
# Remove dashboard image
docker rmi botv2-dashboard:latest

# Remove app image
docker rmi botv2-app:latest

# Optional: Remove all unused images
docker image prune -a
```

### 3. Pull Latest Code
```bash
# Make sure you have latest changes
git pull origin main
```

### 4. Rebuild Containers
```bash
# For demo mode
docker-compose -f docker-compose.demo.yml build --no-cache

# For standard mode
docker-compose build --no-cache
```

### 5. Start Containers
```bash
# For demo mode
docker-compose -f docker-compose.demo.yml up -d

# For standard mode
docker-compose up -d
```

### 6. Verify Health
```bash
# Check container status
docker-compose -f docker-compose.demo.yml ps

# Check logs
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard

# Check health endpoint
curl http://localhost:8050/health
```

---

## ✅ VERIFICATION

### Expected Output

**Container Logs:**
```
===============================================================================
   BotV2 Professional Dashboard v5.1 - Market Data & Annotations
===============================================================================
Environment: DEVELOPMENT
URL: http://0.0.0.0:8050
Database: ⚠️ Mock Data Mode
Auth: admin / ✓
===============================================================================

🚀 Starting dashboard server...
 * Running on http://0.0.0.0:8050
```

**Health Check:**
```bash
$ curl http://localhost:8050/health
{
  "status": "healthy",
  "version": "5.1",
  "database": false
}
```

**Container Status:**
```bash
$ docker-compose -f docker-compose.demo.yml ps
NAME                IMAGE                      STATUS
botv2-app           botv2-app:latest           Up (healthy)
botv2-dashboard     botv2-dashboard:latest     Up (healthy)
```

---

## 🐛 TROUBLESHOOTING

### Problem: Container Exits Immediately

**Check logs:**
```bash
docker-compose -f docker-compose.demo.yml logs botv2-dashboard
```

**Common causes:**
- Missing environment variables
- Python import errors
- Port already in use

**Solution:**
```bash
# Check if port 8050 is free
lsof -i :8050

# Kill process if needed
kill -9 <PID>

# Restart
docker-compose -f docker-compose.demo.yml up -d
```

### Problem: Healthcheck Failing

**Symptoms:**
- Container shows "unhealthy" status
- `/health` endpoint not responding

**Solution:**
```bash
# Increase healthcheck start_period
# Edit docker-compose file:
# start_period: 60s  # was 40s

# Rebuild and restart
docker-compose -f docker-compose.demo.yml up -d --build
```

### Problem: Import Error for web_app

**Error:**
```
ModuleNotFoundError: No module named 'src.dashboard.web_app'
```

**Solution:**
```bash
# Rebuild without cache
docker-compose -f docker-compose.demo.yml build --no-cache

# Verify Dockerfile includes all files
docker-compose -f docker-compose.demo.yml run botv2-dashboard ls -la src/dashboard/
```

### Problem: "dashboard_standalone.py not found"

**This means you're using old images.**

**Solution:**
```bash
# Force rebuild
docker-compose -f docker-compose.demo.yml down
docker rmi botv2-dashboard:latest
docker-compose -f docker-compose.demo.yml build --no-cache
docker-compose -f docker-compose.demo.yml up -d
```

---

## 📊 VERIFICATION CHECKLIST

- [ ] Containers running
- [ ] Health check passing
- [ ] Dashboard accessible at http://localhost:8050
- [ ] Login page loads
- [ ] Can login with admin/admin
- [ ] Dashboard shows data
- [ ] No errors in logs
- [ ] Health endpoint returns v5.1

---

## 📦 TESTING NEW ENDPOINTS

Once dashboard is running, test v5.1 features:

```bash
# Test OHLCV endpoint
curl "http://localhost:8050/api/market/AAPL/ohlcv?timeframe=1h&limit=10"

# Test annotations
curl http://localhost:8050/api/annotations/equity

# Test market price
curl http://localhost:8050/api/market/BTC/USD
```

---

## 📝 WHAT'S NEW IN v5.1

### New Endpoints
1. `GET /api/market/<symbol>` - Latest price
2. `GET /api/market/<symbol>/ohlcv` - OHLCV candlesticks
3. `GET /api/annotations/<chart_id>` - Get annotations
4. `POST /api/annotations` - Create annotation
5. `DELETE /api/annotations/<id>` - Delete annotation

### Features
- ✅ 7 timeframes (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- ✅ 10 trading symbols with mock data
- ✅ WebSocket real-time sync
- ✅ Chart annotations CRUD
- ✅ Realistic random walk price generation

---

## 🔗 RELATED DOCUMENTATION

- [README_FINAL.md](src/dashboard/README_FINAL.md) - Complete dashboard guide
- [INTEGRATION_COMPLETE.md](src/dashboard/INTEGRATION_COMPLETE.md) - Full integration status
- [web_app.py](src/dashboard/web_app.py) - Source code

---

## ❓ NEED HELP?

### Check Logs
```bash
# Real-time logs
docker-compose -f docker-compose.demo.yml logs -f

# Last 100 lines
docker-compose -f docker-compose.demo.yml logs --tail=100

# Specific service
docker-compose -f docker-compose.demo.yml logs botv2-dashboard
```

### Exec into Container
```bash
# Access container shell
docker-compose -f docker-compose.demo.yml exec botv2-dashboard sh

# Check files
ls -la src/dashboard/

# Test Python import
python -c "from src.dashboard.web_app import ProfessionalDashboard; print('OK')"
```

### Complete Reset
```bash
# Nuclear option - reset everything
docker-compose -f docker-compose.demo.yml down -v
docker system prune -a
git pull origin main
docker-compose -f docker-compose.demo.yml build --no-cache
docker-compose -f docker-compose.demo.yml up -d
```

---

**Last Updated**: 2026-01-23 22:55 CET  
**Version**: 5.1  
**Status**: ✅ FIXED
