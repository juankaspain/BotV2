# 🎯 BotV2 Mode Selection Guide

**Version:** 3.2  
**Date:** 2026-01-22  
**Status:** ✅ Production Ready

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Modes Available](#modes-available)
3. [Quick Start](#quick-start)
4. [UPDATE.sh Menu](#updatesh-menu)
5. [Docker Compose Files](#docker-compose-files)
6. [Environment Variables](#environment-variables)
7. [Migration Guide](#migration-guide)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

BotV2 ahora incluye un sistema profesional de selección de modo con **configuraciones separadas** para Demo y Producción.

### ✨ Key Features

- **Menú interactivo** en `UPDATE.sh` para elegir modo
- **Docker Compose separados** por modo (no más comentar/descomentar)
- **Detección automática** de servicios y configuración
- **Transición sin fricción** entre modos
- **Backup automático** en modo producción
- **Preservación de datos** en todas las operaciones

### 📊 Architecture Comparison

| Aspecto | Demo Mode | Production Mode |
|---------|-----------|----------------|
| **Archivo** | `docker-compose.demo.yml` | `docker-compose.production.yml` |
| **Servicios** | Bot + Dashboard (demo data) | Bot + Dashboard + DB + Redis |
| **Datos** | Generados (demo) | Reales (trading) |
| **PostgreSQL** | ❌ No requerido | ✓ Requerido |
| **Redis** | ❌ No requerido (usa memoria) | ✓ Requerido |
| **Trading Mode** | Paper (simulado) | Paper o Live |
| **Backups** | ❌ No | ✓ Automáticos |
| **Recursos** | Bajos (~300MB RAM) | Moderados (~1GB RAM) |
| **Inicio** | Rápido (< 30s) | Medio (< 60s) |
| **Uso ideal** | Desarrollo, demos, pruebas | Trading real, staging |

---

## 🎮 Modes Available

### 1. Demo Mode (🎮)

**Propósito:** Desarrollo, pruebas, demostraciones

**Características:**
- **Trading Bot + Dashboard** con datos de demostración
- NO requiere base de datos (usa memoria)
- Generación automática de trades y métricas
- Paper trading mode activado
- Inicio ultra rápido
- Ideal para:
  - Probar el sistema completo
  - Desarrollo de features
  - Demos a clientes
  - Testing de estrategias
  - Pruebas de integración

**Servicios incluidos:**
```
├── botv2-app (trading bot - paper mode)
├── botv2-dashboard (port 8050)
└── botv2-demo-network
```

**Comando de inicio:**
```bash
docker-compose -f docker-compose.demo.yml up -d
```

---

### 2. Production Mode (🏭)

**Propósito:** Trading real, staging, producción

**Características:**
- Sistema completo con todas las dependencias
- Trading bot activo
- Persistencia de datos en PostgreSQL
- Rate limiting con Redis
- Backups automáticos
- Healthchecks completos
- Ideal para:
  - Trading con dinero real
  - Paper trading serio con persistencia
  - Entornos de staging
  - Producción

**Servicios incluidos:**
```
├── botv2-app (trading bot)
├── botv2-dashboard (port 8050)
├── botv2-postgres (port 5432)
├── botv2-redis (port 6379)
└── botv2-network
```

**Comando de inicio:**
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

## 🚀 Quick Start

### Opción 1: Usando UPDATE.sh (Recomendado)

```bash
# 1. Asegúrate de tener .env configurado
cp .env.example .env
# Edita .env según tus necesidades (mínimo para demo ya está OK)

# 2. Ejecuta el script de actualización
chmod +x UPDATE.sh
./UPDATE.sh

# 3. Sigue el menú interactivo:
#    - Opción 1: Demo Mode (Bot + Dashboard con demo data)
#    - Opción 2: Production Mode (Sistema completo)
#    - Opción 3: Cancelar
```

### Opción 2: Inicio Manual

**Demo Mode:**
```bash
# Crear .env (mínimo requerido)
cp .env.example .env

# Iniciar en modo demo
docker-compose -f docker-compose.demo.yml up -d

# Verificar estado
docker-compose -f docker-compose.demo.yml ps

# Ver logs
docker-compose -f docker-compose.demo.yml logs -f

# Acceder
# http://localhost:8050
# Usuario: admin
# Password: admin (default en demo)
```

**Production Mode:**
```bash
# Crear y configurar .env (TODOS los valores requeridos)
cp .env.example .env
# IMPORTANTE: Configurar:
# - TRADING_MODE=live (o paper)
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - DASHBOARD_PASSWORD
# - API keys

# Iniciar en modo producción
docker-compose -f docker-compose.production.yml up -d

# Verificar estado
docker-compose -f docker-compose.production.yml ps

# Ver logs de todos los servicios
docker-compose -f docker-compose.production.yml logs -f

# Acceder
# http://localhost:8050
```

---

## 📖 UPDATE.sh Menu

### Interfaz del Menú

El script `UPDATE.sh` presenta un menú interactivo profesional:

```
█████████████████████████████████████████████████████████████████████████████
██                                                                             ██
██                      🎯 SELECCIÓN DE MODO DE OPERACIÓN                      ██
██                                                                             ██
█████████████████████████████████████████████████████████████████████████████

Selecciona el modo en el que deseas actualizar el sistema:

  1) 🎮 MODO DEMO
     • Trading Bot + Dashboard con datos demo
     • NO requiere PostgreSQL ni Redis
     • Paper trading mode activado
     • Perfecto para pruebas y desarrollo
     • Ligero y rápido de iniciar
     • Archivo: docker-compose.demo.yml

  2) 🏭 MODO PRODUCCIÓN
     • Sistema completo con base de datos
     • PostgreSQL + Redis + Trading Bot + Dashboard
     • Persistencia de datos real
     • Rate limiting con Redis
     • Archivo: docker-compose.production.yml

  3) 🚫 Cancelar

Elige una opción (1-3):
```

### Flujo de Actualización

1. **Selección de modo** - Menú interactivo
2. **Validación** - Verifica archivo docker-compose existe
3. **Confirmación** - Solicita confirmación antes de proceder
4. **Verificación de requisitos** - Docker, docker-compose
5. **Detección de servicios** - Analiza qué servicios están definidos
6. **Backup** (solo producción) - Backup de PostgreSQL si existe
7. **Actualización de código** - Git pull
8. **Reconstrucción de imágenes** - Docker build
9. **Reinicio de servicios** - Docker-compose up
10. **Verificación** - Healthchecks y conectividad
11. **Resumen** - Estado final y comandos útiles

---

## 📂 Docker Compose Files

### docker-compose.demo.yml

**Ubicación:** `./docker-compose.demo.yml`

**Contenido:**
- 2 servicios: `botv2-app` (paper mode) + `botv2-dashboard`
- Sin dependencias de base de datos
- Demo data auto-generado
- Rate limiting en memoria
- Configuración mínima requerida

**Variables requeridas en .env:**
```bash
# Mínimo para demo (todo tiene defaults)
DASHBOARD_PORT=8050
LOG_LEVEL=INFO

# Opcionales (ya tienen defaults en demo)
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin
SECRET_KEY=demo-secret-key-change-in-production
```

### docker-compose.production.yml

**Ubicación:** `./docker-compose.production.yml`

**Contenido:**
- 4 servicios: `botv2-app`, `botv2-dashboard`, `botv2-postgres`, `botv2-redis`
- Dependencias completas
- Volúmenes persistentes
- Healthchecks robustos
- Configuración completa requerida

**Variables requeridas en .env:**
```bash
# Trading
TRADING_MODE=paper  # o 'live'

# Database
POSTGRES_USER=botv2
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DATABASE=botv2_db
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=your-redis-password
REDIS_PORT=6379

# Dashboard
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your-dashboard-password
DASHBOARD_PORT=8050
SECRET_KEY=your-secret-key

# Exchanges (según necesidad)
BINANCE_API_KEY=
BINANCE_API_SECRET=
# ... otros exchanges

# Logs
LOG_LEVEL=INFO
```

---

## 🔧 Troubleshooting

### Problema: Dashboard no responde en modo demo

**Síntoma:**
```bash
HTTP 000 o connection refused
```

**Diagnóstico:**
```bash
# Ver logs del dashboard
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard

# Ver estado del contenedor
docker-compose -f docker-compose.demo.yml ps botv2-dashboard

# Verificar healthcheck
docker inspect botv2-dashboard | grep -A 10 Health
```

**Soluciones:**

1. **Esperar más tiempo**
   ```bash
   # El dashboard puede tardar hasta 60s en iniciarse
   sleep 30
   curl http://localhost:8050/health
   ```

2. **Verificar puerto no está ocupado**
   ```bash
   # Windows
   netstat -ano | findstr :8050
   
   # Linux/Mac
   lsof -i :8050
   
   # Si está ocupado, cambiar puerto
   echo "DASHBOARD_PORT=8051" >> .env
   docker-compose -f docker-compose.demo.yml down
   docker-compose -f docker-compose.demo.yml up -d
   ```

3. **Healthcheck acepta 401/302**
   - El healthcheck ahora acepta 200, 401 o 302 como respuestas válidas
   - 401 = auth requerido (normal)
   - 302 = redirect a login (normal)
   - Si aún falla, verificar logs

---

### Problema: Bot no inicia en modo demo

**Síntoma:**
```bash
botv2-app | ERROR: ...
```

**Verificar:**
```bash
# Ver logs completos
docker-compose -f docker-compose.demo.yml logs botv2-app

# Verificar que está en paper mode
docker-compose -f docker-compose.demo.yml exec botv2-app env | grep TRADING_MODE
# Debe mostrar: TRADING_MODE=paper
```

**Solución:**
- El bot en demo mode no requiere API keys
- Si da error de conexión a DB, es normal (usa memoria)
- Los trades son simulados

---

### Problema: "version is obsolete" warning

**Síntoma:**
```
the attribute `version` is obsolete
```

**Acción:**
- Este es solo un WARNING, no un error
- Docker Compose v2 no requiere el campo `version`
- El sistema funciona correctamente
- Se puede ignorar de forma segura

---

## 📚 Comandos Útiles

### Demo Mode

```bash
# Iniciar
docker-compose -f docker-compose.demo.yml up -d

# Ver logs de ambos servicios
docker-compose -f docker-compose.demo.yml logs -f

# Ver solo logs del bot
docker-compose -f docker-compose.demo.yml logs -f botv2-app

# Ver solo logs del dashboard
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard

# Estado
docker-compose -f docker-compose.demo.yml ps

# Detener
docker-compose -f docker-compose.demo.yml down

# Reiniciar un servicio
docker-compose -f docker-compose.demo.yml restart botv2-dashboard

# Reconstruir imagen
docker-compose -f docker-compose.demo.yml build botv2-dashboard
docker-compose -f docker-compose.demo.yml up -d

# Ver estadísticas de recursos
docker stats botv2-app botv2-dashboard
```

### Production Mode

```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.production.yml up -d

# Ver logs de todos
docker-compose -f docker-compose.production.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose.production.yml logs -f botv2-app
docker-compose -f docker-compose.production.yml logs -f botv2-dashboard
docker-compose -f docker-compose.production.yml logs -f botv2-postgres
docker-compose -f docker-compose.production.yml logs -f botv2-redis

# Estado
docker-compose -f docker-compose.production.yml ps

# Detener
docker-compose -f docker-compose.production.yml down

# Detener y eliminar volúmenes (CUIDADO: borra datos)
docker-compose -f docker-compose.production.yml down -v

# Conectar a PostgreSQL
docker-compose -f docker-compose.production.yml exec botv2-postgres \
  psql -U botv2 -d botv2_db

# Conectar a Redis
docker-compose -f docker-compose.production.yml exec botv2-redis redis-cli

# Backup PostgreSQL
docker-compose -f docker-compose.production.yml exec botv2-postgres \
  pg_dump -U botv2 botv2_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## ✅ Best Practices

### Desarrollo Local

1. **Usa Demo Mode** para desarrollo rápido
2. **No commitees .env** (está en .gitignore)
3. **Usa variables de entorno** para configuración
4. **Verifica logs** regularmente durante desarrollo
5. **Prueba ambos modos** antes de desplegar

### Staging/Production

1. **Usa Production Mode** siempre
2. **Configura secrets** correctamente (.env seguro)
3. **Backups automáticos** de PostgreSQL
4. **Monitoreo activo** de healthchecks
5. **Logs centralizados** (ELK, Splunk, etc.)
6. **Rate limiting** con Redis configurado

---

## 📝 Summary

### Ventajas del Nuevo Sistema

✅ **Separación clara** entre demo y producción  
✅ **Demo mode completo** con bot + dashboard  
✅ **No más edición manual** de docker-compose.yml  
✅ **Menú interactivo** profesional en UPDATE.sh  
✅ **Transición suave** entre modos  
✅ **Preservación de datos** garantizada  
✅ **Backups automáticos** en producción  
✅ **Healthcheck mejorado** (acepta 401/302)  
✅ **Verificación robusta** post-despliegue  

---

**Version:** 3.2  
**Last Updated:** 2026-01-22  
**Status:** ✅ Production Ready
