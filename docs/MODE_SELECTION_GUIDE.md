# 🎯 BotV2 Mode Selection Guide

**Version:** 3.0  
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
| **Servicios** | Dashboard standalone | Bot + Dashboard + DB + Redis |
| **Datos** | Generados (demo) | Reales (trading) |
| **PostgreSQL** | ❌ No requerido | ✓ Requerido |
| **Redis** | ❌ No requerido (usa memoria) | ✓ Requerido |
| **Backups** | ❌ No | ✓ Automáticos |
| **Recursos** | Mínimos (~200MB RAM) | Moderados (~1GB RAM) |
| **Inicio** | Rápido (< 30s) | Medio (< 60s) |
| **Uso ideal** | Desarrollo, demos, pruebas | Trading real, staging |

---

## 🎮 Modes Available

### 1. Demo Mode (🎮)

**Propósito:** Desarrollo, pruebas, demostraciones

**Características:**
- Dashboard standalone con datos de demostración
- NO requiere base de datos (usa memoria)
- Generación automática de trades y métricas
- Inicio ultra rápido
- Ideal para:
  - Probar el dashboard
  - Desarrollo de features
  - Demos a clientes
  - Testing de UI/UX

**Servicios incluidos:**
```
├── botv2-dashboard (port 8050)
└── botv2-network
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
  - Paper trading serio
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
# Edita .env según tus necesidades

# 2. Ejecuta el script de actualización
chmod +x UPDATE.sh
./UPDATE.sh

# 3. Sigue el menú interactivo:
#    - Opción 1: Demo Mode
#    - Opción 2: Production Mode
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
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard

# Acceder
# http://localhost:8050
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
     • Dashboard standalone con datos de demostración
     • NO requiere PostgreSQL ni Redis
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
- 1 servicio: `botv2-dashboard`
- Sin dependencias de base de datos
- Demo data auto-generado
- Rate limiting en memoria
- Configuración mínima requerida

**Variables requeridas en .env:**
```bash
# Mínimo para demo
DASHBOARD_PORT=8050
LOG_LEVEL=INFO

# Opcionales (se auto-generan)
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=
SECRET_KEY=
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

### docker-compose.yml (Original)

**Estado:** Se mantiene para compatibilidad hacia atrás

**Recomendación:** Usar los archivos específicos (`demo.yml` o `production.yml`) en su lugar

---

## ⚙️ Environment Variables

### Variables Comunes

| Variable | Demo | Production | Default | Descripción |
|----------|------|------------|---------|---------------|
| `LOG_LEVEL` | ✓ | ✓ | INFO | Nivel de logs (DEBUG, INFO, WARNING, ERROR) |
| `DASHBOARD_PORT` | ✓ | ✓ | 8050 | Puerto del dashboard |
| `DASHBOARD_USERNAME` | ✓ | ✓ | admin | Usuario del dashboard |
| `DASHBOARD_PASSWORD` | Opcional | **Requerido** | - | Contraseña del dashboard |
| `SECRET_KEY` | Auto | **Requerido** | - | Clave secreta de Flask |

### Variables Solo Production

| Variable | Required | Default | Descripción |
|----------|----------|---------|---------------|
| `TRADING_MODE` | ✓ | paper | Modo de trading (paper/live) |
| `POSTGRES_USER` | ✓ | botv2 | Usuario PostgreSQL |
| `POSTGRES_PASSWORD` | ✓ | - | Contraseña PostgreSQL |
| `POSTGRES_DATABASE` | ✓ | botv2_db | Nombre base de datos |
| `POSTGRES_PORT` | ❌ | 5432 | Puerto PostgreSQL |
| `REDIS_PASSWORD` | ✓ | - | Contraseña Redis |
| `REDIS_PORT` | ❌ | 6379 | Puerto Redis |

### Exchange API Keys (Production)

```bash
# Binance
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=false

# Coinbase
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_SANDBOX=false

# ... otros exchanges
```

---

## 🔄 Migration Guide

### Desde docker-compose.yml Antiguo

Si ya estabas usando `docker-compose.yml` con comentarios:

#### Paso 1: Identificar tu modo actual

```bash
# Verifica qué servicios están corriendo
docker-compose ps
```

**Si solo ves `botv2-dashboard`:** Estás en modo Demo
**Si ves todos los servicios:** Estás en modo Production

#### Paso 2: Migrar a nuevo archivo

**Para Demo:**
```bash
# Detener servicios actuales
docker-compose down

# Iniciar con nuevo archivo
docker-compose -f docker-compose.demo.yml up -d
```

**Para Production:**
```bash
# Detener servicios actuales (sin eliminar volúmenes)
docker-compose down

# Iniciar con nuevo archivo
docker-compose -f docker-compose.production.yml up -d
```

#### Paso 3: Verificar

```bash
# Demo
docker-compose -f docker-compose.demo.yml ps

# Production
docker-compose -f docker-compose.production.yml ps
```

### Cambiar de Demo a Production

```bash
# 1. Detener demo
docker-compose -f docker-compose.demo.yml down

# 2. Configurar .env para producción
# Agregar todas las variables requeridas

# 3. Iniciar producción
docker-compose -f docker-compose.production.yml up -d
```

### Cambiar de Production a Demo

```bash
# 1. Backup (importante!)
docker-compose -f docker-compose.production.yml exec botv2-postgres \
  pg_dump -U botv2 botv2_db > backup_$(date +%Y%m%d).sql

# 2. Detener producción (datos se preservan en volúmenes)
docker-compose -f docker-compose.production.yml down

# 3. Iniciar demo
docker-compose -f docker-compose.demo.yml up -d

# Nota: Los volúmenes de PostgreSQL/Redis quedan intactos
# Puedes volver a production en cualquier momento
```

---

## 🔧 Troubleshooting

### Problema: "Archivo docker-compose no encontrado"

**Síntoma:**
```
ERROR: Can't find a suitable configuration file
```

**Solución:**
```bash
# Verifica que el archivo existe
ls -la docker-compose.*.yml

# Si no existe, verifica que estás en el directorio correcto
pwd

# Debe ser el directorio raíz de BotV2
```

### Problema: "Service 'botv2-dashboard' not defined"

**Causa:** Usando archivo incorrecto

**Solución:**
```bash
# Usa el archivo correcto
docker-compose -f docker-compose.demo.yml ps      # Para demo
docker-compose -f docker-compose.production.yml ps # Para production
```

### Problema: Variables de entorno faltantes

**Síntoma:**
```
WARNING: The POSTGRES_PASSWORD variable is not set
```

**Solución:**
```bash
# 1. Copia el ejemplo
cp .env.example .env

# 2. Edita .env con tus valores
nano .env

# 3. Verifica que las variables están configuradas
cat .env | grep POSTGRES_PASSWORD
```

### Problema: Puerto ya en uso

**Síntoma:**
```
ERROR: for botv2-dashboard  Cannot start service: 
driver failed: Bind for 0.0.0.0:8050 failed: port is already allocated
```

**Solución:**
```bash
# Opción 1: Cambiar puerto en .env
echo "DASHBOARD_PORT=8051" >> .env

# Opción 2: Detener servicio que usa el puerto
lsof -ti:8050 | xargs kill -9

# Opción 3: Detener contenedores antiguos
docker-compose down
docker-compose -f docker-compose.demo.yml down
docker-compose -f docker-compose.production.yml down
```

### Problema: Dashboard muestra "Unhealthy"

**Diagnóstico:**
```bash
# Ver logs del dashboard
docker-compose -f docker-compose.demo.yml logs botv2-dashboard

# Ver estado detallado
docker inspect botv2-dashboard | grep -A 10 Health
```

**Soluciones comunes:**

1. **Redis no disponible (solo production):**
   ```bash
   # Verificar Redis
   docker-compose -f docker-compose.production.yml exec botv2-redis redis-cli ping
   
   # Reiniciar Redis si es necesario
   docker-compose -f docker-compose.production.yml restart botv2-redis
   ```

2. **PostgreSQL no disponible (solo production):**
   ```bash
   # Verificar PostgreSQL
   docker-compose -f docker-compose.production.yml exec botv2-postgres pg_isready -U botv2
   
   # Reiniciar PostgreSQL si es necesario
   docker-compose -f docker-compose.production.yml restart botv2-postgres
   ```

3. **Esperar más tiempo:**
   ```bash
   # El healthcheck puede tardar hasta 40 segundos
   sleep 45
   docker-compose -f docker-compose.demo.yml ps
   ```

### Problema: UPDATE.sh no encuentra servicios

**Síntoma:**
```
WARNING: Dashboard (botv2-dashboard): NO DEFINIDO
```

**Solución:**
```bash
# Verifica que elegiste el modo correcto en el menú
# Verifica que el archivo docker-compose existe
ls -la docker-compose.*.yml

# Prueba manualmente
docker-compose -f docker-compose.demo.yml config | grep botv2-dashboard
```

---

## 📚 Comandos Útiles

### Demo Mode

```bash
# Iniciar
docker-compose -f docker-compose.demo.yml up -d

# Ver logs
docker-compose -f docker-compose.demo.yml logs -f

# Ver solo logs del dashboard
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard

# Estado
docker-compose -f docker-compose.demo.yml ps

# Detener
docker-compose -f docker-compose.demo.yml down

# Reiniciar dashboard
docker-compose -f docker-compose.demo.yml restart botv2-dashboard

# Reconstruir imagen
docker-compose -f docker-compose.demo.yml build botv2-dashboard
docker-compose -f docker-compose.demo.yml up -d
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

# Restaurar backup
cat backup_20260122_120000.sql | \
  docker-compose -f docker-compose.production.yml exec -T botv2-postgres \
  psql -U botv2 -d botv2_db
```

### Monitoreo

```bash
# Estadísticas de recursos en tiempo real
docker stats

# Solo servicios de BotV2
docker stats botv2-app botv2-dashboard botv2-postgres botv2-redis

# Healthcheck status
docker inspect botv2-dashboard | grep -A 5 Health

# Verificar conectividad HTTP
curl -I http://localhost:8050/health
```

---

## ✅ Best Practices

### Desarrollo Local

1. **Usa Demo Mode** para desarrollo rápido
2. **No commitees .env** (está en .gitignore)
3. **Usa variables de entorno** para configuración
4. **Verifica logs** regularmente durante desarrollo

### Staging/Production

1. **Usa Production Mode** siempre
2. **Configura secrets** correctamente (.env seguro)
3. **Backups automáticos** de PostgreSQL
4. **Monitoreo activo** de healthchecks
5. **Logs centralizados** (ELK, Splunk, etc.)
6. **Rate limiting** con Redis configurado

### Seguridad

1. **Passwords fuertes** para todos los servicios
2. **SECRET_KEY único** generado con `openssl rand -base64 32`
3. **No expongas** puertos de DB/Redis si no es necesario
4. **HTTPS** en producción (reverse proxy como nginx)
5. **Firewall** configurado adecuadamente

---

## 📝 Summary

### Ventajas del Nuevo Sistema

✅ **Separación clara** entre demo y producción  
✅ **No más edición manual** de docker-compose.yml  
✅ **Menú interactivo** profesional en UPDATE.sh  
✅ **Transición suave** entre modos  
✅ **Preservación de datos** garantizada  
✅ **Backups automáticos** en producción  
✅ **Detección inteligente** de servicios  
✅ **Verificación robusta** post-despliegue  

### Files Overview

```
BotV2/
├── UPDATE.sh                          # Script con menú de selección
├── docker-compose.demo.yml           # Configuración modo demo
├── docker-compose.production.yml     # Configuración modo producción
├── docker-compose.yml                # Original (mantener compatibilidad)
├── .env.example                      # Plantilla de variables
├── .env                              # Tu configuración (no versionado)
└── docs/MODE_SELECTION_GUIDE.md      # Este documento
```

---

## 🔗 Related Documentation

- [README.md](../README.md) - Documentación general del proyecto
- [DOCKER_SETUP.md](../DOCKER_SETUP.md) - Guía de configuración Docker
- [DASHBOARD_ACCESS.md](../DASHBOARD_ACCESS.md) - Acceso y uso del dashboard
- [LOGGING_IMPROVEMENTS.md](./LOGGING_IMPROVEMENTS.md) - Mejoras de logging

---

## 📞 Support

Si encuentras problemas:

1. Revisa esta guía completa
2. Verifica logs: `docker-compose -f <file> logs -f`
3. Consulta la sección [Troubleshooting](#troubleshooting)
4. Verifica issues en GitHub

---

**Version:** 3.0  
**Last Updated:** 2026-01-22  
**Status:** ✅ Production Ready
