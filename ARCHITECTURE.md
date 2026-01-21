# 🏛️ BotV2 System Architecture

## 📊 Overview

BotV2 utiliza una arquitectura **sin capa de API** (API-less), donde el Dashboard se conecta directamente a la base de datos.

```
┌────────────────────┐
│   Trading Bot      │
│   (main.py)        │
│   Async Process    │
│   NO HTTP Server   │
└────────┬───────────┘
         │ Writes
         │
         │
         │
┌────────┴─────────────────────────────┐
│                                           │
│         PostgreSQL + Redis                │
│         (Data Layer)                      │
│                                           │
└────────┬─────────────────────────────┘
         │ Reads
         │
         │
         │
┌────────┴───────────┐
│   Dashboard        │
│   (web_app.py)     │
│   HTTP :8050       │
│   Dash/Flask       │
└────────────────────┘
```

---

## 🐝 Componentes

### 1️⃣ Trading Bot (`botv2-app`)

**Función:** Ejecuta estrategias de trading y gestiona el portfolio

**Características:**
- ✅ Proceso asyncio continuo (NO servidor HTTP)
- ✅ Ejecuta 21+ estrategias de trading
- ✅ Gestiona riesgo con circuit breakers
- ✅ Escribe datos en PostgreSQL
- ✅ Cachea datos en Redis
- ❌ NO expone puerto HTTP (no es una API)

**Entry Point:**
```bash
python src/main.py
```

**Puerto:** Ninguno (proceso background)

**Logs:**
```bash
docker compose logs -f botv2-app
```

---

### 2️⃣ Dashboard (`botv2-dashboard`)

**Función:** Interfaz web para monitoreo en tiempo real

**Características:**
- ✅ Servidor HTTP Dash/Flask
- ✅ Autenticación HTTP Basic (admin/admin)
- ✅ Gráficos en tiempo real con Plotly
- ✅ Conecta directamente a PostgreSQL/Redis
- ✅ Auto-refresh cada 5 segundos

**Entry Point:**
```bash
python -m src.dashboard.web_app
```

**Puerto:** 8050 (HTTP)

**URL:** http://localhost:8050

**Logs:**
```bash
docker compose logs -f botv2-dashboard
```

---

### 3️⃣ PostgreSQL (`botv2-postgres`)

**Función:** Base de datos principal

**Almacena:**
- Portfolio state
- Trade history
- Strategy performance
- Risk metrics
- Market data

**Puerto:** 5432

**Conexión:**
```bash
docker exec -it botv2-postgres psql -U botv2_user -d botv2_user
```

---

### 4️⃣ Redis (`botv2-redis`)

**Función:** Cache en memoria

**Cachea:**
- Market data reciente
- Liquidation events
- Temporary signals
- Session data

**Puerto:** 6379

**Conexión:**
```bash
docker exec -it botv2-redis redis-cli -a botv2_user
```

---

## ❓ FAQ: Por qué NO hay API en puerto 8000?

### ❌ Pregunta: "¿Por qué el bot no responde en localhost:8000?"

**Respuesta:** El bot de trading (`main.py`) es un **proceso asyncio continuo**, NO un servidor HTTP.

```python
# src/main.py (simplificado)
async def main_loop():
    while self.is_running:
        # 1. Fetch market data
        # 2. Run strategies
        # 3. Execute trades
        # 4. Save to DB
        await asyncio.sleep(60)

asyncio.run(main_loop())  # Loop infinito, NO servidor HTTP
```

No tiene sentido exponer un puerto HTTP porque:
- ✅ No necesita recibir requests externos
- ✅ Opera autónomamente en un loop
- ✅ Escribe resultados directamente a PostgreSQL

---

### ✅ Pregunta: "¿Cómo se comunican los componentes?"

**Respuesta:** A través de la **base de datos compartida** (PostgreSQL + Redis)

```
Trading Bot             Dashboard
    |                       |
    | WRITE                 | READ
    ↓                       ↓
  [──── PostgreSQL ────]
  [───── Redis ─────]
```

**Ventajas de este patrón:**
1. ✅ **Más simple** - No necesitas una API REST completa
2. ✅ **Menos latencia** - Sin capa intermedia
3. ✅ **Más rápido** - Queries directos a DB
4. ✅ **Menos código** - Sin endpoints, serializers, etc
5. ✅ **Más seguro** - Dashboard auth, DB interno

---

### 🛠️ Pregunta: "¿Cómo añadir una API si la necesito?"

**Respuesta:** Si en el futuro necesitas exponer una API (ej: para webhooks externos), crea un nuevo servicio:

```yaml
# docker-compose.yml (futuro)
botv2-api:
  container_name: botv2-api
  command: ["python", "src/api/server.py"]  # FastAPI o Flask
  ports:
    - "8000:8000"
  depends_on:
    - botv2-postgres
    - botv2-redis
```

Pero por ahora, **NO es necesario**.

---

## ✅ Verificación del Sistema

### Estado de servicios

```bash
docker compose ps
```

Deberías ver:

| Servicio | Estado | Puerto |
|----------|--------|--------|
| botv2-app | Up (healthy) | - (ninguno) |
| botv2-dashboard | Up (healthy) | 8050 |
| botv2-postgres | Up (healthy) | 5432 |
| botv2-redis | Up (healthy) | 6379 |

### Tests de conectividad

```bash
# PostgreSQL
docker exec botv2-postgres pg_isready -U botv2_user
# → ✅ accepting connections

# Redis
docker exec botv2-redis redis-cli -a botv2_user ping
# → ✅ PONG

# Dashboard
curl http://localhost:8050
# → ✅ HTTP/1.1 200 OK

# Trading Bot (NO HTTP, solo check proceso)
docker compose logs botv2-app --tail=10
# → ✅ Debe mostrar logs de trading
```

---

## 📊 Flujo de Datos

### Escritura (Trading Bot → DB)

```python
# Bot ejecuta trade
trade_result = await execute_trade(...)

# Guarda en PostgreSQL
await db.save_trade(trade_result)

# Actualiza cache en Redis
await redis.set(f"latest_trade", trade_result)
```

### Lectura (Dashboard → DB)

```python
# Dashboard hace query directo
trades = db.query("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10")

# O desde cache
latest = redis.get("latest_trade")

# Muestra en UI
return render_trades_table(trades)
```

---

## 📚 Referencias

- Trading Bot: `src/main.py`
- Dashboard: `src/dashboard/web_app.py`
- Docker Compose: `docker-compose.yml`
- DB Schema: `docs/DATABASE_SCHEMA.md` (si existe)

---

**Fecha:** 21 Enero 2026  
**Status:** ✅ ARQUITECTURA DOCUMENTADA  
**Patrón:** API-less (Direct DB access)
