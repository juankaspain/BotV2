# 🔒 GUÍA DE SEGURIDAD - BotV2

**Versión:** 1.1.0  
**Fecha:** 21 de Enero, 2026  
**Estado:** Implementación Fase 1 - Auditoría Completada

---

## 🎯 RESUMEN

Este documento describe las medidas de seguridad implementadas en BotV2 y cómo configurarlas correctamente.

### Mejoras de Seguridad Implementadas

- ✅ **Autenticación HTTP Basic** en Dashboard
- ✅ **Hash SHA-256** para contraseñas
- ✅ **Comparación de tiempo constante** (previene timing attacks)
- ✅ **Variables de entorno** para credenciales
- ✅ **Logging de intentos de login** fallidos
- ✅ **Contraseña temporal auto-generada** para primer uso
- ✅ **Badge de seguridad** en UI del dashboard

---

## 🔑 CONFIGURACIÓN DE CREDENCIALES

### Variables de Entorno Requeridas

BotV2 utiliza variables de entorno para gestionar credenciales de forma segura:

```bash
# Dashboard Authentication
export DASHBOARD_USERNAME="admin"              # Usuario del dashboard (default: admin)
export DASHBOARD_PASSWORD="your_secure_pass"   # ⚠️ OBLIGATORIO - Sin default

# Database
export POSTGRES_PASSWORD="your_db_password"    # Contraseña PostgreSQL
export POSTGRES_USER="botv2_user"              # Usuario PostgreSQL
export POSTGRES_HOST="localhost"               # Host de la base de datos
export POSTGRES_PORT="5432"                     # Puerto PostgreSQL
export POSTGRES_DB="botv2"                      # Nombre de la base de datos

# Exchange APIs
export POLYMARKET_API_KEY="your_api_key"       # API Key de Polymarket
export POLYMARKET_SECRET="your_api_secret"     # Secret de Polymarket

# Optional: Notifications
export TELEGRAM_BOT_TOKEN="your_token"         # Token del bot de Telegram
export SLACK_WEBHOOK_URL="your_webhook"        # Webhook de Slack
```

### Archivo .env (Recomendado)

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
# BotV2 Environment Variables
# IMPORTANT: Never commit this file to Git!

# Dashboard
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=my_super_secure_password_123!

# Database
POSTGRES_PASSWORD=db_secure_pass_456
POSTGRES_USER=botv2_user
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=botv2

# Exchanges
POLYMARKET_API_KEY=pk_live_your_key_here
POLYMARKET_SECRET=your_secret_here

# Notifications (Optional)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**⚠️ IMPORTANTE:** Añade `.env` a tu `.gitignore`:

```bash
echo ".env" >> .gitignore
```

### Cargar Variables de Entorno

#### Opción 1: Usar python-dotenv (Recomendado)

```python
# Al inicio de main.py o config_manager.py
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

# Acceder a las variables
password = os.getenv('DASHBOARD_PASSWORD')
```

#### Opción 2: Export manual

```bash
# Linux/Mac
source .env

# O exportar individualmente
export DASHBOARD_PASSWORD="my_password"
```

#### Opción 3: Systemd service

```ini
# /etc/systemd/system/botv2.service
[Unit]
Description=BotV2 Trading System
After=network.target postgresql.service

[Service]
Type=simple
User=botv2
WorkingDirectory=/opt/botv2
EnvironmentFile=/opt/botv2/.env
ExecStart=/opt/botv2/venv/bin/python src/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## 🚪 ACCESO AL DASHBOARD

### Primer Uso

Si no has configurado `DASHBOARD_PASSWORD`, el sistema generará una **contraseña temporal** al iniciar:

```
⚠️ DASHBOARD_PASSWORD not set! Dashboard will be INSECURE.
Set environment variable before starting.
🔑 Temporary password generated: x8K9mQpL2vN4rT6w
IMPORTANT: Set DASHBOARD_PASSWORD env var for production!
```

**⚠️ Esta contraseña es válida solo para la sesión actual.**

### Login al Dashboard

1. **Inicia el dashboard:**
   ```bash
   python src/dashboard/web_app.py
   ```

2. **Abre tu navegador:**
   ```
   http://localhost:8050
   ```

3. **Se mostrará prompt de autenticación:**
   ```
   Username: admin
   Password: [tu_password_configurado]
   ```

4. **Dashboard secured badge:**
   - Verás un badge verde "🔒 Secured" en el header
   - Indica que la autenticación está activa

### Intentos Fallidos

Todos los intentos fallidos se loguean:

```
WARNING - Failed login attempt from 192.168.1.100 (username: attacker)
```

---

## 🛡️ MEJORES PRÁCTICAS

### Contraseñas Seguras

**✅ BUENAS contraseñas:**
```
My$ecure!P@ssw0rd2026
Tr4d1ng-B0t_Sup3r$ecret!
9Kp#mQ2@vN8xL4rT
```

**❌ MALAS contraseñas:**
```
admin123
password
12345678
botv2
```

### Generador de Contraseñas

```bash
# Linux/Mac - Generar contraseña aleatoria fuerte
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Rotación de Credenciales

**Rotar cada 90 días:**

1. Generar nueva contraseña
2. Actualizar `.env`
3. Reiniciar bot
4. Verificar acceso
5. Guardar credenciales anteriores durante 7 días (rollback)

### No Commitear Credenciales

**⚠️ NUNCA hacer:**

```bash
# MAL - Commitear .env
git add .env
git commit -m "Add credentials"

# MAL - Credenciales en código
password = "my_password_123"  # ❌ NO!
```

**✅ HACER:**

```bash
# BIEN - Usar variables de entorno
password = os.getenv('DASHBOARD_PASSWORD')

# BIEN - .env en .gitignore
echo ".env" >> .gitignore
```

---

## 🔍 AUDITORÍA Y MONITOREO

### Verificar Configuración de Seguridad

```python
# Script de verificación
# scripts/verify_security.py

import os
import sys

REQUIRED_VARS = [
    'DASHBOARD_PASSWORD',
    'POSTGRES_PASSWORD',
    'POLYMARKET_API_KEY'
]

OPTIONAL_VARS = [
    'DASHBOARD_USERNAME',
    'TELEGRAM_BOT_TOKEN',
    'SLACK_WEBHOOK_URL'
]

def verify_security():
    print("\n🔍 BotV2 Security Verification\n")
    print("="*50)
    
    # Check required
    missing = []
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if not value:
            print(f"❌ {var}: NOT SET")
            missing.append(var)
        else:
            print(f"✅ {var}: Configured")
    
    print("\nOptional Variables:")
    for var in OPTIONAL_VARS:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configured")
        else:
            print(f"⚠️  {var}: Not set (optional)")
    
    print("="*50)
    
    if missing:
        print(f"\n❌ SECURITY CHECK FAILED")
        print(f"Missing required variables: {', '.join(missing)}")
        print("\nSet these variables before starting BotV2!")
        sys.exit(1)
    else:
        print(f"\n✅ SECURITY CHECK PASSED")
        print("All required credentials configured.")

if __name__ == "__main__":
    verify_security()
```

**Ejecutar antes de iniciar el bot:**

```bash
python scripts/verify_security.py
```

### Logs de Seguridad

Todos los eventos de seguridad se loguean en `logs/security.log`:

```
2026-01-21 01:30:15 INFO - Dashboard authentication initialized (user: admin)
2026-01-21 01:35:22 WARNING - Failed login attempt from 203.0.113.45 (username: root)
2026-01-21 01:35:25 WARNING - Failed login attempt from 203.0.113.45 (username: admin)
2026-01-21 01:40:10 DEBUG - Authenticated user: admin from 192.168.1.100
```

### Monitoreo de Intentos de Acceso

```bash
# Ver intentos fallidos en tiempo real
tail -f logs/security.log | grep "Failed login"

# Contar intentos fallidos
grep "Failed login" logs/security.log | wc -l

# IPs que intentaron acceder
grep "Failed login" logs/security.log | awk '{print $(NF-1)}' | sort | uniq -c | sort -rn
```

---

## 🔥 FIREWALL Y RED

### Restringir Acceso al Dashboard

#### Opción 1: UFW (Ubuntu)

```bash
# Permitir solo desde IP local
sudo ufw allow from 192.168.1.0/24 to any port 8050

# Bloquear acceso externo
sudo ufw deny 8050
```

#### Opción 2: iptables

```bash
# Permitir solo localhost
sudo iptables -A INPUT -p tcp --dport 8050 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8050 -j DROP
```

#### Opción 3: Nginx Reverse Proxy con HTTPS

```nginx
# /etc/nginx/sites-available/botv2-dashboard

server {
    listen 443 ssl http2;
    server_name dashboard.botv2.local;
    
    ssl_certificate /etc/ssl/certs/botv2.crt;
    ssl_certificate_key /etc/ssl/private/botv2.key;
    
    # Restrict to internal network
    allow 192.168.1.0/24;
    deny all;
    
    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### VPN Recomendado

Para acceso remoto seguro:

1. **WireGuard** (recomendado)
2. **OpenVPN**
3. **Tailscale** (más fácil)

```bash
# Instalar Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Conectar
sudo tailscale up

# Acceder al dashboard vía Tailscale
http://100.x.x.x:8050
```

---

## ⚠️ INCIDENTES DE SEGURIDAD

### Si Sospechas de Acceso No Autorizado

**1. Inmediato:**
```bash
# Detener el bot
pkill -f "python src/main.py"

# Cambiar todas las contraseñas
vim .env

# Revisar logs
grep "Authenticated" logs/security.log
grep "Failed login" logs/security.log
```

**2. Investigación:**
```bash
# Ver conexiones activas
netstat -an | grep :8050

# Ver procesos sospechosos
ps aux | grep python

# Revisar historial de comandos
history | grep -i password
```

**3. Recuperación:**
- Rotar todas las credenciales
- Revisar trades recientes
- Verificar saldo del portfolio
- Analizar logs completos
- Considerar restaurar desde backup

### Contacto de Emergencia

```
Para reportar incidentes de seguridad:
- Email: security@botv2.local (configurar)
- Telegram: @botv2_security (configurar)
```

---

## 🚀 MEJORAS FUTURAS (Roadmap V5)

### Fase 2: Autenticación Avanzada

- [ ] **JWT Tokens** para API
- [ ] **OAuth2** integration (Google, GitHub)
- [ ] **2FA (TOTP)** para dashboard
- [ ] **Session management** con Redis
- [ ] **Role-Based Access Control (RBAC)**

### Fase 3: Cifrado

- [ ] **TLS/HTTPS** obligatorio en dashboard
- [ ] **Cifrado de credenciales** en BD
- [ ] **Vault integration** (HashiCorp Vault)
- [ ] **Certificados auto-renovables** (Let's Encrypt)

### Fase 4: Auditoría

- [ ] **Audit trail** completo
- [ ] **SIEM integration** (Splunk, ELK)
- [ ] **Automated security scans** (Bandit, Safety)
- [ ] **Penetration testing** anual
- [ ] **SOC2/ISO27001** compliance

---

## 📚 REFERENCIAS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Python Cryptography](https://cryptography.io/en/latest/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

---

## ✅ CHECKLIST DE SEGURIDAD

Antes de pasar a producción:

- [ ] `DASHBOARD_PASSWORD` configurado (mínimo 16 caracteres)
- [ ] `.env` en `.gitignore`
- [ ] Todas las credenciales en variables de entorno
- [ ] Logs de seguridad activados
- [ ] Firewall configurado (solo IPs permitidas)
- [ ] HTTPS activado (o VPN)
- [ ] Script de verificación ejecutado sin errores
- [ ] Plan de rotación de credenciales definido
- [ ] Backups encriptados configurados
- [ ] Procedimiento de incidentes documentado

---

**Última actualización:** 21 de Enero, 2026  
**Mantenedor:** Equipo BotV2  
**Estado:** Activo - Fase 1 Completada

🔒 **BotV2 - Trading Seguro y Profesional**
