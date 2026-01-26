# 📊 Dashboard Access Guide

## 🚀 Quick Access

**URL:** http://localhost:8050

**Credenciales por defecto:**
- Username: `admin`
- Password: (definido en `.env`)

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

### Problema: "Dashboard carga pero no muestra datos"

**Causa:** PostgreSQL o Redis no conectados

**Solución:**
```bash
# Verificar conexión a base de datos
docker exec botv2-postgres pg_isready -U botv2_user

# Verificar conexión a Redis
docker exec botv2-redis redis-cli -a botv2_user ping
```

---

## 📊 Endpoints disponibles

| Endpoint | Descripción |
|----------|-------------|
| `http://localhost:8050/` | Dashboard principal |
| `http://localhost:8050/health` | Health check |
| `http://localhost:8050/control` | Control Panel |

---

## ✅ Verificación completa

```bash
# Verificar todos los servicios
docker compose ps

# Dashboard accesible
curl http://localhost:8050

# PostgreSQL
docker exec botv2-postgres pg_isready -U botv2_user

# Redis
docker exec botv2-redis redis-cli -a botv2_user ping
```

---

**Fecha:** 26 Enero 2026  
**Status:** ✅ DOCUMENTADO
