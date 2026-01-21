# 🐳 Docker Setup Guide - BotV2

## 🚨 PROBLEMA RESUELTO

### Problemas anteriores:
1. ❌ Docker Compose no leía el archivo `.env`
2. ❌ Bucle infinito de reintentos cuando fallaba la validación
3. ❌ Logs repetidos infinitamente

### Solución aplicada:
1. ✅ Añadido `env_file: ['.env']` a todos los servicios
2. ✅ Cambiado restart policy a `on-failure:3` (máximo 3 reintentos)
3. ✅ Configuración de variables de entorno corregida

---

## 📋 PASOS PARA ARRANCAR DOCKER

### 1. Renombrar tu archivo de configuración

```bash
# Tu archivo se llama local.env, Docker necesita .env
cp local.env .env
```

**IMPORTANTE:** No elimines `local.env`, solo cópialo. De esta forma tienes:
- `local.env` → Tu copia de backup (no tracked en git)
- `.env` → El que usa Docker (no tracked en git)

### 2. Verificar que .env tiene todos los secretos requeridos

```bash
# Verificar que las variables críticas están presentes
grep -E "(POSTGRES_DATABASE|POSTGRES_USER|SECRET_KEY)" .env
```

Deberías ver:
```
POSTGRES_DATABASE=botv2_user
POSTGRES_USER=botv2_user
SECRET_KEY=<your_secret_key>
```

### 3. Detener y limpiar contenedores anteriores

```bash
# Detener todos los contenedores
docker compose down

# Limpiar contenedores con errores (opcional)
docker compose down -v  # -v elimina también los volúmenes
```

### 4. Construir imágenes desde cero

```bash
# Reconstruir imágenes (forzar rebuild)
docker compose build --no-cache
```

### 5. Iniciar servicios

```bash
# Iniciar en modo detached (background)
docker compose up -d

# O ver logs en tiempo real
docker compose up
```

### 6. Verificar estado

```bash
# Ver estado de todos los contenedores
docker compose ps

# Deberías ver:
# botv2-app        running   0.0.0.0:8000->5000/tcp
# botv2-dashboard  running   0.0.0.0:8050->8050/tcp
# botv2-postgres   running   0.0.0.0:5432->5432/tcp
# botv2-redis      running   0.0.0.0:6379->6379/tcp
```

### 7. Ver logs sin bucle infinito

```bash
# Logs del dashboard (ahora sin repeticiones infinitas)
docker compose logs -f botv2-dashboard

# Logs de todos los servicios
docker compose logs -f

# Últimas 50 líneas
docker compose logs --tail=50
```

---

## 🔧 TROUBLESHOOTING

### Problema: "Missing REQUIRED secret: POSTGRES_DATABASE"

**Causa:** El archivo `.env` no existe o no se está leyendo

**Solución:**
```bash
# 1. Verificar que .env existe
ls -la .env

# 2. Si no existe, copiar desde local.env
cp local.env .env

# 3. Reiniciar contenedores
docker compose down
docker compose up -d
```

### Problema: "Bucle infinito de logs"

**Causa:** Restart policy era `unless-stopped` (reinicia infinitamente)

**Solución:** Ya está corregido en el nuevo `docker-compose.yml`
- Ahora usa `restart: on-failure:3` (máximo 3 intentos)
- Si falla 3 veces, el contenedor se detiene

### Problema: "Container keeps restarting"

```bash
# Ver por qué está fallando
docker compose logs botv2-dashboard --tail=100

# Ver estado detallado
docker inspect botv2-dashboard

# Reiniciar manualmente
docker compose restart botv2-dashboard
```

### Problema: "Cannot connect to PostgreSQL"

```bash
# Verificar que PostgreSQL está corriendo
docker compose ps botv2-postgres

# Ver logs de PostgreSQL
docker compose logs botv2-postgres

# Conectar manualmente para verificar
docker exec -it botv2-postgres psql -U botv2_user -d botv2_user
```

---

## 📊 MONITOREO

### Ver recursos usados

```bash
# CPU, memoria, red de todos los contenedores
docker stats

# Solo BotV2
docker stats botv2-app botv2-dashboard botv2-postgres botv2-redis
```

### Healthchecks

```bash
# Ver estado de health de todos los servicios
docker compose ps --format json | jq '.[].Health'

# Verificar endpoints manualmente
curl http://localhost:8000/health  # Main app
curl http://localhost:8050/health  # Dashboard
```

---

## 🧹 LIMPIEZA

### Detener todo

```bash
# Detener servicios (mantiene volúmenes)
docker compose down

# Detener y eliminar volúmenes (datos se pierden)
docker compose down -v
```

### Limpiar imágenes antiguas

```bash
# Eliminar imágenes no usadas
docker image prune -a

# Limpiar todo (cuidado!)
docker system prune -a --volumes
```

---

## ✅ VERIFICACIÓN FINAL

Después de arrancar Docker, verifica:

```bash
# 1. Todos los contenedores corriendo
docker compose ps
# Todos deberían estar "Up" o "healthy"

# 2. No hay logs de error
docker compose logs --tail=50 | grep -i error
# No debería haber errores críticos

# 3. Servicios accesibles
curl http://localhost:8000/health  # → {"status": "ok"}
curl http://localhost:8050/health  # → {"status": "ok"}

# 4. Base de datos funciona
docker exec botv2-postgres pg_isready -U botv2_user
# → accepting connections

# 5. Redis funciona
docker exec botv2-redis redis-cli -a botv2_user ping
# → PONG
```

---

## 🎯 RESULTADO ESPERADO

```bash
$ docker compose up -d
[+] Running 4/4
 ✔ Container botv2-postgres   Healthy
 ✔ Container botv2-redis      Healthy
 ✔ Container botv2-app        Started
 ✔ Container botv2-dashboard  Started

$ docker compose ps
NAME                IMAGE                  STATUS
botv2-app           botv2-botv2:latest     Up (healthy)
botv2-dashboard     botv2-dashboard:latest Up (healthy)
botv2-postgres      postgres:16-alpine     Up (healthy)
botv2-redis         redis:7-alpine         Up (healthy)

$ docker compose logs botv2-dashboard --tail=20
✅ All REQUIRED secrets validated
✅ Dashboard starting on 0.0.0.0:8050
✅ Connected to PostgreSQL: botv2_user@botv2-postgres:5432/botv2_user
✅ Connected to Redis: botv2-redis:6379/0
🚀 BotV2 Dashboard ready!
```

---

## 📚 REFERENCIAS

- [Docker Compose Env File](https://docs.docker.com/compose/environment-variables/set-environment-variables/)
- [Docker Restart Policies](https://docs.docker.com/config/containers/start-containers-automatically/)
- [Docker Healthchecks](https://docs.docker.com/engine/reference/builder/#healthcheck)

---

**Fecha:** 21 Enero 2026  
**Status:** ✅ PROBLEMAS RESUELTOS
