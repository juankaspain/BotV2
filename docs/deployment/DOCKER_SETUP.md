# 🐳 Docker Setup Guide - BotV2

## 📝 Quick Start

### 1. Preparar archivo de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

### 2. Construir imágenes

```bash
docker compose build --no-cache
```

### 3. Iniciar servicios

```bash
# Modo background
docker compose up -d

# Ver logs en tiempo real
docker compose up
```

### 4. Verificar estado

```bash
docker compose ps
```

Resultado esperado:

| Servicio | Estado | Puerto |
|----------|--------|--------|
| botv2-app | Up (healthy) | - |
| botv2-dashboard | Up (healthy) | 8050 |
| botv2-postgres | Up (healthy) | 5432 |
| botv2-redis | Up (healthy) | 6379 |

---

## 🔧 Troubleshooting

### Problema: "Missing REQUIRED secret"

```bash
# Verificar que .env existe
ls -la .env

# Si no existe, copiar
cp .env.example .env

# Reiniciar
docker compose down
docker compose up -d
```

### Problema: "Container keeps restarting"

```bash
# Ver por qué está fallando
docker compose logs botv2-dashboard --tail=100

# Reiniciar manualmente
docker compose restart botv2-dashboard
```

### Problema: "Cannot connect to PostgreSQL"

```bash
# Verificar PostgreSQL
docker compose ps botv2-postgres

# Ver logs
docker compose logs botv2-postgres

# Conectar manualmente
docker exec -it botv2-postgres psql -U botv2_user -d botv2_user
```

---

## 📊 Monitoreo

```bash
# Recursos de todos los contenedores
docker stats

# Logs de un servicio
docker compose logs -f botv2-app

# Healthchecks
docker compose ps
```

---

## 🧹 Limpieza

```bash
# Detener servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v

# Limpiar imágenes no usadas
docker image prune -a
```

---

**Fecha:** 26 Enero 2026  
**Status:** ✅ DOCUMENTADO
