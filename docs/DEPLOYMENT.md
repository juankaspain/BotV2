# 🚀 Guía Completa de Despliegue en Producción - BotV2

## Índice

1. [Introducción](#introducción)
2. [Prerequisitos](#prerequisitos)
3. [Despliegue con Docker](#despliegue-con-docker)
4. [Despliegue Manual](#despliegue-manual)
5. [Configuración de Producción](#configuración-de-producción)
6. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
7. [Backup y Recuperación](#backup-y-recuperación)
8. [Solución de Problemas](#solución-de-problemas)
9. [Mejores Prácticas](#mejores-prácticas)

---

## Introducción

Esta guía cubre todo lo necesario para desplegar BotV2 en producción de forma segura y profesional.

### Métodos de Despliegue

- **Docker Compose** (Recomendado) - Más fácil, aislado, reproducible
- **Manual** - Más control, requiere más configuración
- **Kubernetes** - Para escalabilidad (futuro)

---

## Prerequisitos

### Hardware Mínimo

```
CPU:       2 cores (4 recomendado)
RAM:       2GB (4GB recomendado)
Disco:     20GB SSD
Red:       Conexión estable a Internet
```

### Software Requerido

#### Para Docker (Recomendado)

```bash
# Docker 20.10+
docker --version

# Docker Compose 2.0+
docker-compose --version

# Git
git --version
```

#### Para Instalación Manual

```bash
# Python 3.10+
python3 --version

# PostgreSQL 13+
psql --version

# Redis (opcional)
redis-cli --version
```

### Sistema Operativo

- **Recomendado**: Ubuntu 22.04 LTS
- **Compatible**: Debian, CentOS, macOS, Windows (WSL2)

---

## Despliegue con Docker

### Paso 1: Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Verificar instalación
docker --version
docker compose version
```

### Paso 2: Clonar el Repositorio

```bash
# Clonar
cd ~
git clone https://github.com/juankaspain/BotV2.git
cd BotV2

# Crear estructura de directorios
mkdir -p logs backups data
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus valores
nano .env
```

**Configuración mínima requerida**:

```env
# .env
BOTV2_ENV=production

# Database (CAMBIAR PASSWORDS)
POSTGRES_PASSWORD=tu_password_seguro_aqui_123!
REDIS_PASSWORD=tu_redis_password_aqui_456!

# API Keys (al menos uno)
POLYMARKET_API_KEY=tu_api_key_aqui
```

**⚠️ IMPORTANTE**: Usa contraseñas fuertes y únicas.

### Paso 4: Configurar settings.yaml

```bash
# Editar configuración del bot
nano src/config/settings.yaml
```

**Verificar estas configuraciones**:

```yaml
system:
  environment: "production"  # ← IMPORTANTE
  log_level: "INFO"

trading:
  initial_capital: 3000  # Tu capital real

state_persistence:
  storage:
    host: "postgres"  # ← Nombre del servicio Docker
    port: 5432
    database: "botv2"
    user: "botv2_user"
```

### Paso 5: Construir y Lanzar

```bash
# Construir imágenes
docker compose build

# Lanzar servicios
docker compose up -d

# Ver logs
docker compose logs -f botv2
```

### Paso 6: Verificar Funcionamiento

```bash
# Ver estado de contenedores
docker compose ps

# Debe mostrar:
# botv2-postgres   Up (healthy)
# botv2-redis      Up (healthy)
# botv2-app        Up
# botv2-dashboard  Up

# Ver logs del bot
docker compose logs botv2 --tail=50

# Acceder al dashboard
http://localhost:8050
```

### Comandos Útiles de Docker

```bash
# Detener todos los servicios
docker compose down

# Detener pero mantener datos
docker compose stop

# Reiniciar solo el bot
docker compose restart botv2

# Ver logs en tiempo real
docker compose logs -f

# Ejecutar comando dentro del contenedor
docker compose exec botv2 python -c "print('test')"

# Limpiar volúmenes (⚠️ BORRA DATOS)
docker compose down -v
```

---

## Despliegue Manual

### Paso 1: Instalar Python y Dependencias

```bash
# Instalar Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Crear entorno virtual
python3.11 -m venv ~/botv2-env
source ~/botv2-env/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Instalar PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos y usuario
sudo -u postgres psql << EOF
CREATE DATABASE botv2;
CREATE USER botv2_user WITH ENCRYPTED PASSWORD 'tu_password_aqui';
GRANT ALL PRIVILEGES ON DATABASE botv2 TO botv2_user;
\q
EOF
```

### Paso 3: Configurar Variables de Entorno

```bash
# Agregar al ~/.bashrc o ~/.zshrc
export POSTGRES_HOST="localhost"
export POSTGRES_PASSWORD="tu_password_aqui"
export POLYMARKET_API_KEY="tu_api_key"
export BOTV2_ENV="production"

# Recargar
source ~/.bashrc
```

### Paso 4: Crear Servicio Systemd

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/botv2.service
```

**Contenido**:

```ini
[Unit]
Description=BotV2 Trading System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/BotV2
Environment="PYTHONPATH=/home/tu_usuario/BotV2"
EnvironmentFile=/home/tu_usuario/BotV2/.env
ExecStart=/home/tu_usuario/botv2-env/bin/python src/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/tu_usuario/BotV2/logs/botv2.log
StandardError=append:/home/tu_usuario/BotV2/logs/botv2-error.log

[Install]
WantedBy=multi-user.target
```

**Activar servicio**:

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable botv2

# Iniciar servicio
sudo systemctl start botv2

# Ver estado
sudo systemctl status botv2

# Ver logs
journalctl -u botv2 -f
```

### Paso 5: Configurar Dashboard como Servicio

```bash
# Crear servicio para dashboard
sudo nano /etc/systemd/system/botv2-dashboard.service
```

```ini
[Unit]
Description=BotV2 Dashboard
After=network.target botv2.service

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/BotV2
Environment="PYTHONPATH=/home/tu_usuario/BotV2"
EnvironmentFile=/home/tu_usuario/BotV2/.env
ExecStart=/home/tu_usuario/botv2-env/bin/python src/dashboard/web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable botv2-dashboard
sudo systemctl start botv2-dashboard
```

---

## Configuración de Producción

### Seguridad

#### 1. Firewall

```bash
# Instalar UFW
sudo apt install ufw -y

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8050/tcp  # Dashboard (solo si necesario)

# Habilitar
sudo ufw enable
```

#### 2. Fail2ban (Protección SSH)

```bash
# Instalar
sudo apt install fail2ban -y

# Configurar
sudo nano /etc/fail2ban/jail.local
```

```ini
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 3. HTTPS para Dashboard (Nginx + Let's Encrypt)

```bash
# Instalar Nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# Configurar Nginx
sudo nano /etc/nginx/sites-available/botv2
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/botv2 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com
```

### Optimización de PostgreSQL

```bash
# Editar configuración
sudo nano /etc/postgresql/15/main/postgresql.conf
```

**Optimizaciones recomendadas**:

```conf
# Memoria
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Connections
max_connections = 50
```

```bash
# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

---

## Monitoreo y Mantenimiento

### Script de Monitoreo

Crear `scripts/monitor.sh`:

```bash
#!/bin/bash
# Script de monitoreo BotV2

set -e

echo "=== BotV2 Health Check ==="
echo "Fecha: $(date)"
echo ""

# Docker (si aplica)
if command -v docker &> /dev/null; then
    echo "--- Docker Containers ---"
    docker compose ps
    echo ""
fi

# Systemd (si aplica)
if systemctl is-active --quiet botv2; then
    echo "✅ BotV2 Service: RUNNING"
else
    echo "❌ BotV2 Service: STOPPED"
fi

# Database
echo "--- Database ---"
psql -U botv2_user -d botv2 -c "SELECT COUNT(*) as total_trades FROM trades;" 2>/dev/null || echo "No se pudo conectar a DB"

# Disk Usage
echo "--- Disk Usage ---"
df -h | grep -E '(Filesystem|/$)'

# Recent Logs
echo "--- Recent Errors (last 10) ---"
tail -n 10 logs/botv2_$(date +%Y%m%d).log | grep -i error || echo "No errors found"

# Performance Metrics
echo "--- Latest Metrics ---"
psql -U botv2_user -d botv2 -c "SELECT sharpe_ratio, max_drawdown, total_return FROM performance_metrics ORDER BY timestamp DESC LIMIT 1;" 2>/dev/null

echo ""
echo "=== Check Complete ==="
```

```bash
chmod +x scripts/monitor.sh
./scripts/monitor.sh
```

### Cron para Monitoreo Automático

```bash
crontab -e
```

```cron
# Monitoreo cada hora
0 * * * * /home/tu_usuario/BotV2/scripts/monitor.sh >> /home/tu_usuario/BotV2/logs/monitor.log 2>&1

# Backup diario a las 3 AM
0 3 * * * /home/tu_usuario/BotV2/scripts/backup.sh

# Limpiar logs antiguos semanalmente
0 0 * * 0 find /home/tu_usuario/BotV2/logs -name "*.log" -mtime +30 -delete
```

### Alertas con Telegram

Crear `scripts/alert_telegram.sh`:

```bash
#!/bin/bash
# Enviar alerta a Telegram

BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
CHAT_ID="${TELEGRAM_CHAT_ID}"
MESSAGE="$1"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="🤖 BotV2 Alert: ${MESSAGE}"
```

---

## Backup y Recuperación

### Script de Backup

Crear `scripts/backup.sh`:

```bash
#!/bin/bash
# Backup completo de BotV2

set -e

BACKUP_DIR="$HOME/BotV2/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="botv2_backup_${DATE}.tar.gz"

echo "Iniciando backup: ${BACKUP_FILE}"

# Backup de base de datos
echo "Backup de PostgreSQL..."
pg_dump -U botv2_user -d botv2 -F c -f "${BACKUP_DIR}/db_${DATE}.dump"

# Backup de configuración y logs
echo "Backup de archivos..."
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    src/config/settings.yaml \
    .env \
    logs/ \
    data/ \
    2>/dev/null || true

echo "✅ Backup completado: ${BACKUP_FILE}"

# Limpiar backups antiguos (mantener 30 días)
find "${BACKUP_DIR}" -name "botv2_backup_*.tar.gz" -mtime +30 -delete
find "${BACKUP_DIR}" -name "db_*.dump" -mtime +30 -delete

echo "Backups antiguos limpiados"
```

```bash
chmod +x scripts/backup.sh
```

### Restaurar desde Backup

```bash
#!/bin/bash
# Restaurar desde backup

BACKUP_DATE="20260121_030000"  # Cambiar a tu backup

# Detener servicios
docker compose down
# O: sudo systemctl stop botv2

# Restaurar base de datos
pg_restore -U botv2_user -d botv2 -c backups/db_${BACKUP_DATE}.dump

# Restaurar archivos
tar -xzf backups/botv2_backup_${BACKUP_DATE}.tar.gz

# Reiniciar servicios
docker compose up -d
# O: sudo systemctl start botv2

echo "✅ Restauración completada"
```

### Backup Remoto (Opcional)

```bash
# Con rsync a servidor remoto
rsync -avz --delete \
    ~/BotV2/backups/ \
    usuario@servidor-backup.com:/backups/botv2/

# Con rclone a cloud (Google Drive, AWS S3, etc.)
rclone sync ~/BotV2/backups/ remote:botv2-backups/
```

---

## Solución de Problemas

### El bot no inicia

```bash
# Docker
docker compose logs botv2 --tail=100

# Manual
journalctl -u botv2 -n 100

# Verificar:
# 1. Variables de entorno
env | grep -E 'POSTGRES|POLYMARKET'

# 2. Conexión a DB
psql -U botv2_user -d botv2 -h localhost -c "\dt"

# 3. Permisos de archivos
ls -la logs/ backups/ data/
```

### Base de datos no responde

```bash
# Docker
docker compose exec postgres pg_isready

# Manual
sudo systemctl status postgresql

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Dashboard no accesible

```bash
# Verificar que el servicio corre
docker compose logs dashboard
# O: sudo systemctl status botv2-dashboard

# Verificar puerto
sudo netstat -tlnp | grep 8050

# Probar localmente
curl http://localhost:8050
```

### Consumo alto de memoria

```bash
# Ver uso de recursos (Docker)
docker stats

# Ver uso de recursos (Manual)
top -u tu_usuario

# Posibles causas:
# 1. Demasiadas estrategias activas
# 2. Lookback period muy largo
# 3. No hay límite de historia en memoria

# Solución: Reducir en settings.yaml
# - ensemble.adaptive_allocation.lookback_days
# - data.normalization.lookback_period
```

### Error de API keys

```bash
# Verificar variables de entorno
env | grep API_KEY

# Docker: Recrear con nuevas vars
docker compose down
docker compose up -d

# Manual: Recargar servicio
sudo systemctl restart botv2
```

---

## Mejores Prácticas

### Seguridad

1. ✅ **Nunca** commitear `.env` al repositorio
2. ✅ Usar **contraseñas fuertes** (mínimo 16 caracteres)
3. ✅ Rotar **API keys** regularmente
4. ✅ Configurar **firewall** (UFW)
5. ✅ Usar **HTTPS** para dashboard
6. ✅ Mantener sistema **actualizado**
7. ✅ Monitorear **logs de acceso**

### Monitoreo

1. ✅ Revisar **logs diariamente**
2. ✅ Configurar **alertas** (Telegram/Slack)
3. ✅ Monitorear **métricas de rendimiento**
4. ✅ Verificar **uso de disco**
5. ✅ Chequear **estado de servicios**

### Backups

1. ✅ Backup **automático diario**
2. ✅ Mantener **30 días** de backups
3. ✅ **Probar restauración** mensualmente
4. ✅ Backup **remoto** (cloud o servidor externo)
5. ✅ Incluir **configuración y logs**

### Mantenimiento

1. ✅ Actualizar **dependencias** mensualmente
2. ✅ Revisar **configuración** regularmente
3. ✅ Limpiar **logs antiguos**
4. ✅ Optimizar **base de datos** (VACUUM)
5. ✅ Monitorear **rendimiento**

### Operación

1. ✅ Empezar con **capital pequeño**
2. ✅ Usar perfil **conservador** inicialmente
3. ✅ Monitorear **primeras 24-48 horas** de cerca
4. ✅ Incrementar capital **gradualmente**
5. ✅ Documentar **cambios de configuración**
6. ✅ **Nunca** operar con dinero que no puedes perder

---

## Checklist de Despliegue

### Pre-Despliegue

- [ ] Servidor configurado con requisitos mínimos
- [ ] Docker instalado (si aplica)
- [ ] PostgreSQL funcionando
- [ ] Firewall configurado
- [ ] Dominio configurado (si usas dashboard público)
- [ ] Certificado SSL obtenido (si aplica)
- [ ] API keys obtenidas
- [ ] Variables de entorno configuradas
- [ ] `settings.yaml` revisado y ajustado
- [ ] Backups automáticos programados

### Post-Despliegue

- [ ] Bot iniciado correctamente
- [ ] Dashboard accesible
- [ ] Primera operación ejecutada exitosamente
- [ ] Logs escribiendo correctamente
- [ ] Base de datos registrando trades
- [ ] Métricas actualizándose
- [ ] Circuit breaker funcional (probar con datos simulados)
- [ ] Alertas funcionando (si configuradas)
- [ ] Monitoreo activo
- [ ] Documentación de configuración guardada

### Primera Semana

- [ ] Revisar logs diariamente
- [ ] Verificar todas las operaciones
- [ ] Ajustar configuración si necesario
- [ ] Documentar cualquier problema
- [ ] Verificar backups
- [ ] Monitorear rendimiento vs backtest

---

## Soporte

### Recursos

- **Documentación**: `/docs` en el repositorio
- **Issues**: [GitHub Issues](https://github.com/juankaspain/BotV2/issues)
- **Logs**: `logs/botv2_*.log`

### Contacto

**Autor**: Juan Carlos Garcia Arriero  
**GitHub**: [juankaspain](https://github.com/juankaspain)

---

**Versión**: 1.0.0  
**Última Actualización**: Enero 2026  
**Estado**: Producción Ready

---

**⚠️ ADVERTENCIA FINAL**

Este bot opera con dinero real. Asegúrate de:
1. Entender completamente la configuración
2. Haber probado exhaustivamente en desarrollo
3. Empezar con capital que puedas permitirte perder
4. Monitorear constantemente las primeras semanas
5. Tener plan de contingencia si algo sale mal

**El autor no se hace responsable de pérdidas financieras.**
