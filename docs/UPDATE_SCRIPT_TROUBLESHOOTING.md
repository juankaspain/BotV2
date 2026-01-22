# 🔧 UPDATE.sh Troubleshooting Guide

**Version:** 3.1  
**Date:** 2026-01-22  
**Status:** ✅ Production Ready

---

## 📚 Table of Contents

1. [Common Issues](#common-issues)
2. [Error Messages](#error-messages)
3. [Platform-Specific Issues](#platform-specific-issues)
4. [Docker Issues](#docker-issues)
5. [Network Issues](#network-issues)
6. [Recovery Procedures](#recovery-procedures)

---

## ✅ Script Improvements (v3.1)

### What Was Fixed

✅ **Error Handling**
- Better capture of docker-compose up errors
- Detailed error messages with exit codes
- Verbose output for debugging
- Graceful fallbacks for missing services

✅ **Color Scheme**
- Removed magenta (not professional)
- Professional blue/green/yellow/red palette
- Better readability in GitBash/Windows
- Consistent styling throughout

✅ **Formatting**
- Fixed tab alignment
- Proper spacing in menus
- Better visual hierarchy
- Dimmed text for secondary info

✅ **Service Detection**
- More robust service checking
- Better healthcheck waiting
- Improved status reporting
- Fallback for services without healthchecks

---

## 🚨 Common Issues

### Issue 1: "Error iniciando servicios"

**Síntoma:**
```bash
✗ Error iniciando servicios (exit code: 1)
```

**Causas Comunes:**

1. **Puerto ya en uso**
   ```bash
   # Verificar puertos
   netstat -ano | findstr :8050  # Windows
   lsof -i :8050                 # Linux/Mac
   
   # Solución: Cambiar puerto en .env
   echo "DASHBOARD_PORT=8051" >> .env
   ```

2. **Docker daemon no responde**
   ```bash
   # Verificar Docker
   docker info
   
   # Si falla, reiniciar Docker Desktop (Windows/Mac)
   # O reiniciar servicio (Linux):
   sudo systemctl restart docker
   ```

3. **Archivo .env faltante o incompleto**
   ```bash
   # Crear desde plantilla
   cp .env.example .env
   
   # Verificar variables requeridas
   cat .env | grep -E "DASHBOARD_PASSWORD|POSTGRES_PASSWORD"
   ```

4. **Imágenes corruptas**
   ```bash
   # Limpiar y reconstruir
   docker-compose -f docker-compose.demo.yml down
   docker-compose -f docker-compose.demo.yml build --no-cache
   docker-compose -f docker-compose.demo.yml up -d
   ```

**Diagnóstico:**
```bash
# Ver logs detallados
docker-compose -f docker-compose.demo.yml logs

# Ver estado de contenedores
docker-compose -f docker-compose.demo.yml ps -a

# Verificar recursos
docker stats --no-stream
```

---

### Issue 2: Healthcheck no pasa

**Síntoma:**
```bash
⚠ botv2-dashboard: healthcheck no pasó (verificar logs)
```

**Causas:**

1. **Servicio tarda en iniciar**
   - **Solución:** Esperar más tiempo (hasta 60s)
   - El healthcheck tiene timeout de 40s, pero puede necesitar más

2. **Dependencias no disponibles**
   ```bash
   # Modo producción: verificar PostgreSQL y Redis
   docker-compose -f docker-compose.production.yml exec botv2-postgres pg_isready -U botv2
   docker-compose -f docker-compose.production.yml exec botv2-redis redis-cli ping
   ```

3. **Error en la aplicación**
   ```bash
   # Ver logs del dashboard
   docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard
   
   # Buscar errores
   docker-compose -f docker-compose.demo.yml logs botv2-dashboard | grep -i error
   ```

**Verificación manual:**
```bash
# Verificar HTTP directamente
curl -v http://localhost:8050/health

# Si retorna 200, 401 o 302 = OK
# Si retorna 000 o timeout = problema
```

---

### Issue 3: "Docker no está instalado"

**En Windows (GitBash):**
```bash
# Docker Desktop debe estar instalado
# Descargar desde: https://www.docker.com/products/docker-desktop

# Verificar instalación
which docker
docker --version
```

**En Linux:**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Añadir usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión
```

**En macOS:**
```bash
# Instalar Docker Desktop
brew install --cask docker

# O descargar desde:
# https://www.docker.com/products/docker-desktop
```

---

### Issue 4: "docker-compose no está instalado"

**Verificar versión:**
```bash
docker-compose --version
```

**Si falla, instalar:**

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Windows/Mac
# Viene incluido con Docker Desktop
# Si no funciona, reinstalar Docker Desktop
```

---

### Issue 5: "Archivo docker-compose.demo.yml no encontrado"

**Verificar archivos:**
```bash
# Listar archivos docker-compose
ls -la docker-compose*.yml

# Deberían existir:
# - docker-compose.yml
# - docker-compose.demo.yml
# - docker-compose.production.yml
```

**Si faltan:**
```bash
# Verificar que estás en el directorio correcto
pwd
# Debe ser: .../BotV2

# Si no estás en el directorio correcto
cd /ruta/a/BotV2

# Actualizar desde Git
git pull origin main
```

---

## 💻 Platform-Specific Issues

### Windows (GitBash)

**Issue: Colores no se muestran correctamente**

```bash
# Habilitar colores en GitBash
export TERM=xterm-256color

# Añadir a ~/.bashrc para permanencia
echo 'export TERM=xterm-256color' >> ~/.bashrc
```

**Issue: Permisos de archivo**

```bash
# Dar permisos de ejecución
chmod +x UPDATE.sh

# Si da error "command not found"
bash UPDATE.sh
```

**Issue: Line endings (CRLF vs LF)**

```bash
# Convertir a LF (Unix style)
dos2unix UPDATE.sh

# O con Git
git config core.autocrlf input
git rm --cached -r .
git reset --hard
```

---

### Linux

**Issue: Permisos de Docker**

```bash
# Añadir usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar
docker ps
```

**Issue: Puertos privilegiados**

```bash
# Si usas puerto < 1024, necesitas sudo
# O cambiar a puerto > 1024
echo "DASHBOARD_PORT=8050" >> .env
```

---

### macOS

**Issue: Docker Desktop no inicia**

```bash
# Verificar recursos asignados
# Docker Desktop > Settings > Resources
# Mínimo recomendado:
# - CPUs: 2
# - Memory: 4GB
# - Swap: 1GB
```

**Issue: Network issues**

```bash
# Reiniciar networking de Docker
# Docker Desktop > Troubleshoot > Reset to factory defaults
# (solo networking, no datos)
```

---

## 🐛 Docker Issues

### Issue: "Cannot connect to Docker daemon"

**Windows/Mac:**
```bash
# Verificar Docker Desktop está corriendo
# Icono en system tray debe estar verde

# Si no, iniciar Docker Desktop manualmente
```

**Linux:**
```bash
# Verificar servicio
sudo systemctl status docker

# Iniciar si está detenido
sudo systemctl start docker

# Habilitar al inicio
sudo systemctl enable docker
```

---

### Issue: "no space left on device"

**Limpiar imágenes y contenedores:**

```bash
# Ver uso de espacio
docker system df

# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes no usadas
docker image prune -a -f

# Limpiar volúmenes no usados
docker volume prune -f

# Limpiar todo (CUIDADO: elimina volúmenes)
docker system prune -a --volumes -f
```

---

### Issue: "port is already allocated"

**Encontrar proceso usando el puerto:**

```bash
# Windows
netstat -ano | findstr :8050
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8050 | xargs kill -9

# O cambiar puerto
echo "DASHBOARD_PORT=8051" >> .env
```

---

## 🌐 Network Issues

### Issue: "Connection refused" en dashboard

**Verificar contenedor está corriendo:**
```bash
docker-compose -f docker-compose.demo.yml ps

# Debe mostrar "Up" en State
```

**Verificar puerto binding:**
```bash
docker-compose -f docker-compose.demo.yml ps | grep 8050

# Debe mostrar: 0.0.0.0:8050->8050/tcp
```

**Verificar desde dentro del contenedor:**
```bash
docker-compose -f docker-compose.demo.yml exec botv2-dashboard curl http://localhost:8050/health

# Si funciona = problema de red en host
# Si falla = problema en aplicación
```

---

### Issue: "Network not found"

**Recrear red de Docker:**
```bash
# Eliminar contenedores
docker-compose -f docker-compose.demo.yml down

# Listar redes
docker network ls | grep botv2

# Eliminar red (si existe)
docker network rm botv2-network

# Recrear
docker-compose -f docker-compose.demo.yml up -d
```

---

## 🔄 Recovery Procedures

### Procedimiento 1: Reset completo (sin perder datos)

```bash
# 1. Detener servicios
docker-compose -f docker-compose.demo.yml down

# 2. Limpiar contenedores e imágenes (NO volúmenes)
docker-compose -f docker-compose.demo.yml rm -f
docker-compose -f docker-compose.demo.yml build --no-cache

# 3. Reiniciar
docker-compose -f docker-compose.demo.yml up -d

# 4. Ver logs
docker-compose -f docker-compose.demo.yml logs -f
```

---

### Procedimiento 2: Reset completo (con pérdida de datos)

**⚠️ ADVERTENCIA:** Esto eliminará TODOS los datos

```bash
# 1. Backup (solo producción)
mkdir -p backups
docker-compose -f docker-compose.production.yml exec botv2-postgres \
  pg_dump -U botv2 botv2_db > backups/emergency-$(date +%Y%m%d_%H%M%S).sql

# 2. Detener y eliminar TODO
docker-compose -f docker-compose.demo.yml down -v

# 3. Limpiar imágenes
docker-compose -f docker-compose.demo.yml rm -f
docker image prune -a -f

# 4. Reconstruir desde cero
docker-compose -f docker-compose.demo.yml build --no-cache
docker-compose -f docker-compose.demo.yml up -d
```

---

### Procedimiento 3: Rollback a versión anterior

```bash
# 1. Ver commits recientes
git log --oneline -10

# 2. Hacer rollback
git checkout <commit-hash>

# 3. Reconstruir
docker-compose -f docker-compose.demo.yml down
docker-compose -f docker-compose.demo.yml build
docker-compose -f docker-compose.demo.yml up -d

# 4. Volver a main cuando esté listo
git checkout main
```

---

## 📊 Logs y Diagnóstico

### Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose -f docker-compose.demo.yml logs -f

# Solo dashboard
docker-compose -f docker-compose.demo.yml logs -f botv2-dashboard

# Solo PostgreSQL (producción)
docker-compose -f docker-compose.production.yml logs -f botv2-postgres

# Últimas 100 líneas
docker-compose -f docker-compose.demo.yml logs --tail=100
```

### Buscar errores específicos

```bash
# Buscar "ERROR"
docker-compose -f docker-compose.demo.yml logs | grep -i error

# Buscar "CRITICAL"
docker-compose -f docker-compose.demo.yml logs | grep -i critical

# Ver logs de Python exceptions
docker-compose -f docker-compose.demo.yml logs | grep -A 10 "Traceback"
```

### Estado del sistema

```bash
# Ver recursos usados
docker stats --no-stream

# Ver información de contenedores
docker-compose -f docker-compose.demo.yml ps

# Ver información detallada
docker inspect botv2-dashboard

# Ver healthcheck status
docker inspect botv2-dashboard | grep -A 10 Health
```

---

## ❓ FAQ

### ¿Por qué el script tarda tanto?

**Respuesta:** El script realiza varias operaciones:
- Build de imágenes Docker (2-5 min primera vez)
- Pull de dependencias Python (1-2 min)
- Inicialización de servicios (15-30s)
- Healthchecks (hasta 40s por servicio)

**Total esperado:** 5-10 minutos primera ejecución, 2-3 minutos subsecuentes

---

### ¿Puedo cancelar el script?

**Sí**, usa `Ctrl+C`

**Consecuencias:**
- Servicios pueden quedar a medio iniciar
- Imágenes pueden estar incompletas

**Recovery:**
```bash
# Limpiar estado inconsistente
docker-compose -f docker-compose.demo.yml down

# Reintentar
bash UPDATE.sh
```

---

### ¿Qué pasa si se corta la luz?

**Docker preserva:**
- Volúmenes (datos de PostgreSQL, Redis)
- Imágenes construidas

**Docker NO preserva:**
- Contenedores en ejecución (se detienen)
- Datos en memoria

**Recovery:**
```bash
# Simplemente reiniciar
docker-compose -f docker-compose.demo.yml up -d
```

---

### ¿Cómo sé si todo funciona correctamente?

**Verificaciones:**

1. **Contenedores corriendo:**
   ```bash
   docker-compose -f docker-compose.demo.yml ps
   # Todos deben tener State=Up
   ```

2. **Dashboard accesible:**
   ```bash
   curl -I http://localhost:8050/health
   # Debe retornar HTTP 200 o 401
   ```

3. **Logs sin errores críticos:**
   ```bash
   docker-compose -f docker-compose.demo.yml logs | grep -i "critical\|error" | tail -20
   # No debe haber errores recientes
   ```

4. **Acceso web:**
   - Abrir http://localhost:8050
   - Debe mostrar login o dashboard

---

## 📧 Soporte

Si ninguna de estas soluciones funciona:

1. **Recopilar información:**
   ```bash
   # Crear reporte de diagnóstico
   echo "=== Docker Info ===" > diagnostic.txt
   docker info >> diagnostic.txt
   echo "\n=== Docker Compose PS ===" >> diagnostic.txt
   docker-compose -f docker-compose.demo.yml ps >> diagnostic.txt
   echo "\n=== Logs ===" >> diagnostic.txt
   docker-compose -f docker-compose.demo.yml logs --tail=200 >> diagnostic.txt
   ```

2. **Compartir:**
   - Subir `diagnostic.txt` a GitHub issue
   - Incluir OS y versión (Windows 11, Ubuntu 22.04, etc.)
   - Incluir comando exacto que falló

---

**Document Version:** 3.1  
**Last Updated:** 2026-01-22  
**Status:** ✅ Production Ready
