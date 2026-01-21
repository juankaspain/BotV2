# 📊 Dashboard Access Guide

## ❌ PROBLEMA RESUELTO: Dashboard no accesible

### Causa del problema
El contenedor `botv2-dashboard` estaba ejecutando **`python src/main.py`** (el bot de trading), en lugar de **`python -m src.dashboard.web_app`** (el dashboard web).

### Solución aplicada
- Actualizado `docker-compose.yml` con comando correcto para cada servicio
- `botv2-app` → ejecuta `python src/main.py` (trading bot)
- `botv2-dashboard` → ejecuta `python -m src.dashboard.web_app` (web dashboard)

---

## 🚀 Cómo acceder al Dashboard

### 1️⃣ Detener servicios actuales

```bash
docker compose down
```

### 2️⃣ Descargar cambios de GitHub

```bash
git pull origin main
```

### 3️⃣ Reconstruir imágenes

```bash
docker compose build --no-cache
```

### 4️⃣ Iniciar servicios

```bash
docker compose up -d
```

### 5️⃣ Verificar que servicios están corriendo

```bash
docker compose ps
```

Deberías ver:
```
NAME              STATUS
botv2-app         Up (healthy)
botv2-dashboard   Up (healthy)
botv2-postgres    Up (healthy)
botv2-redis       Up (healthy)
```

### 6️⃣ Ver logs del dashboard

```bash
docker compose logs -f botv2-dashboard
```

Deberías ver:
```
✅ All REQUIRED secrets validated
✅ Dashboard starting on 0.0.0.0:8050
🚀 Dash is running on http://0.0.0.0:8050/
```

### 7️⃣ Acceder al Dashboard

Abre tu navegador en:

**🌐 http://localhost:8050**

O prueba desde terminal:
```bash
curl http://localhost:8050
```

---

## 🔧 Troubleshooting

### Problema: "Cannot GET /"

**Causa:** Dashboard aún no está listo (está inicializando)

**Solución:**
```bash
# Espera 30-60 segundos y verifica logs
docker compose logs botv2-dashboard --tail=50

# Busca esta línea:
# 🚀 Dash is running on http://0.0.0.0:8050/
```

### Problema: "Connection refused"

**Causa:** Contenedor no está corriendo o puerto no mapeado

**Solución:**
```bash
# Verificar estado
docker compose ps botv2-dashboard

# Si no está Up, ver por qué
docker compose logs botv2-dashboard

# Reiniciar si es necesario
docker compose restart botv2-dashboard
```

### Problema: "Health check failed"

**Causa:** Dashboard no responde en el endpoint esperado

**Solución:**
```bash
# Ver logs detallados
docker compose logs botv2-dashboard --tail=100

# Verificar si hay errores de Python
# Buscar líneas con "ERROR" o "CRITICAL"

# Entrar al contenedor para debug
docker exec -it botv2-dashboard /bin/sh
ps aux | grep python
netstat -tuln | grep 8050
```

### Problema: "Dashboard carga pero no muestra datos"

**Causa:** PostgreSQL o Redis no conectados

**Solución:**
```bash
# Verificar conexión a base de datos
docker exec botv2-dashboard python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://botv2_user:botv2_user@botv2-postgres:5432/botv2_user'); conn = engine.connect(); print('DB OK')"

# Verificar conexión a Redis
docker exec botv2-redis redis-cli -a botv2_user ping
```

---

## 📊 Endpoints disponibles

| Endpoint | Descripción |
|----------|-------------|
| `http://localhost:8050/` | Dashboard principal |
| `http://localhost:8050/health` | Health check |
| `http://localhost:8000` | Trading bot API |
| `http://localhost:5432` | PostgreSQL (DB client) |
| `http://localhost:6379` | Redis (Redis client) |

---

## ✅ Verificación completa

Ejecuta este script para verificar todo:

```bash
#!/bin/bash

echo "=== Verificando servicios ==="

# PostgreSQL
echo -n "PostgreSQL: "
docker exec botv2-postgres pg_isready -U botv2_user && echo "✅" || echo "❌"

# Redis
echo -n "Redis: "
docker exec botv2-redis redis-cli -a botv2_user ping > /dev/null 2>&1 && echo "✅" || echo "❌"

# Trading Bot
echo -n "Trading Bot: "
docker compose ps botv2-app | grep -q "Up" && echo "✅" || echo "❌"

# Dashboard
echo -n "Dashboard: "
curl -s http://localhost:8050 > /dev/null && echo "✅ http://localhost:8050" || echo "❌"

echo ""
echo "=== Estado de contenedores ==="
docker compose ps

echo ""
echo "=== Últimos logs del dashboard ==="
docker compose logs botv2-dashboard --tail=10
```

Guarda como `check_services.sh`, dale permisos y ejecútalo:
```bash
chmod +x check_services.sh
./check_services.sh
```

---

## 🔑 Credenciales por defecto

Según tu `local.env`:

```
Dashboard URL: http://localhost:8050
Username: admin
Password: admin

PostgreSQL:
Host: localhost
Port: 5432
Database: botv2_user
User: botv2_user
Password: botv2_user
```

---

## 📚 Referencias

- Trading Bot: `src/main.py`
- Dashboard: `src/dashboard/web_app.py`
- Docker Compose: `docker-compose.yml`
- Config: `local.env` → `.env`

---

**Fecha:** 21 Enero 2026  
**Status:** ✅ PROBLEMA RESUELTO  
**Próximo paso:** `docker compose down && git pull && docker compose up -d`
