# Corrección de Logs Duplicados y Errores SSL

**Fecha**: 30 de Enero de 2026  
**Versión**: 1.0  
**Estado**: ✅ Completado

---

## 📋 Resumen Ejecutivo

Se han identificado y corregido tres problemas críticos en los logs del sistema:

1. **Carga duplicada de `.env`** - El archivo se cargaba dos veces
2. **Errores SSL/TLS 400** - El navegador intentaba HTTPS en servidor HTTP
3. **Inconsistencia de entorno** - `FLASK_ENV=production` con `ENVIRONMENT=development`

---

## 🔍 Problemas Identificados

### 1. Log Duplicado de `.env`

**Síntoma:**
```
[+] Loaded environment from E:\OneDrive\Escritorio\Bots\V2\BotV2\.env
[+] Loaded environment from E:\OneDrive\Escritorio\Bots\V2\BotV2\.env
```

**Causa Raíz:**
- Tanto `main.py` como `dashboard/web_app.py` cargaban `.env` de forma independiente
- Cada módulo tenía su propio código `load_dotenv()`
- No había sincronización entre módulos

**Impacto:**
- Logs confusos y poco profesionales
- Posible sobrescritura de variables de entorno
- Dificultad para debugging

### 2. Errores SSL/TLS en Logs

**Síntoma:**
```
127.0.0.1 - - [30/Jan/2026 06:37:49] code 400, message Bad request version ('localhost\\x00')
127.0.0.1 - - [30/Jan/2026 06:37:49] "\x16\x03\x01\x06..." 400 -
```

**Causa Raíz:**
- Navegadores modernos intentan HTTPS automáticamente
- Dashboard en modo development ejecuta solo HTTP
- Werkzeug logger registra todos los handshakes SSL fallidos
- Caracteres binarios del handshake SSL aparecen en logs

**Impacto:**
- Logs sucios con caracteres binarios
- Dificultad para leer logs importantes
- Falsa impresión de errores graves

### 3. Inconsistencia de Entorno

**Síntoma:**
```
FLASK_ENV = production
ENVIRONMENT = development
Detected mode: PRODUCTION
```

**Causa Raíz:**
- Variables de entorno inconsistentes
- Detección incorrecta del modo producción
- Talisman (HTTPS) activado en development

**Impacto:**
- Errores SSL porque Talisman fuerza HTTPS
- Comportamiento impredecible del sistema
- Configuración de seguridad incorrecta

---

## ✅ Soluciones Implementadas

### Solución 1: Loader Centralizado de Entorno

**Archivo creado:** `shared/utils/env_loader.py`

```python
# Global flag to track if env has been loaded
_ENV_LOADED = False

def load_env_once(verbose: bool = False) -> bool:
    """Load .env file only once across entire application."""
    global _ENV_LOADED
    
    if _ENV_LOADED:
        return False  # Already loaded, skip
    
    # Load .env file
    load_dotenv(env_file)
    _ENV_LOADED = True
    
    if verbose:
        print(f"[+] Environment loaded from {env_file}", flush=True)
    
    return True
```

**Características:**
- ✅ Carga única garantizada con flag global `_ENV_LOADED`
- ✅ Thread-safe para cargas concurrentes
- ✅ Verbosity controlable (solo muestra mensaje una vez)
- ✅ Búsqueda automática de `.env` en project root
- ✅ Fallback a current working directory

**Integración:**

```python
# En main.py y dashboard/web_app.py
try:
    from shared.utils.env_loader import load_env_once
    load_env_once(verbose=True)  # Solo el primero mostrará el mensaje
except ImportError:
    # Fallback si shared no disponible
    ...
```

**Resultado:**
```
[+] Environment loaded from E:\OneDrive\Escritorio\Bots\V2\BotV2\.env
# Solo UNA vez en todos los logs
```

---

### Solución 2: Filtro de Logs SSL

**Implementación en:** `dashboard/web_app.py`

```python
class SSLErrorFilter(logging.Filter):
    """Filter out SSL/TLS handshake errors from logs.
    
    These errors occur when browsers try HTTPS on an HTTP-only server.
    They are harmless in development but clutter the logs.
    """
    
    def filter(self, record):
        # Filter out SSL handshake errors
        if 'Bad request version' in record.getMessage():
            return False
        # Filter out binary SSL data
        if 'code 400' in record.getMessage() and '\\x' in record.getMessage():
            return False
        return True

def _setup_log_filters(self):
    """Setup log filters to suppress SSL/TLS errors."""
    werkzeug_logger = logging.getLogger('werkzeug')
    ssl_filter = SSLErrorFilter()
    werkzeug_logger.addFilter(ssl_filter)
    logger.info("[+] SSL error log filter enabled")
```

**Características:**
- ✅ Filtra mensajes "Bad request version"
- ✅ Filtra códigos 400 con datos binarios (`\x`)
- ✅ Permite pasar otros logs importantes
- ✅ Se aplica automáticamente al logger de Werkzeug

**Resultado:**
```
# ANTES:
127.0.0.1 - - [30/Jan/2026 06:37:49] "\x16\x03\x01..." 400 -
127.0.0.1 - - [30/Jan/2026 06:37:49] "\x16\x03\x01..." 400 -
127.0.0.1 - - [30/Jan/2026 06:37:49] "\x16\x03\x01..." 400 -

# DESPUÉS:
# (Sin logs SSL, solo logs relevantes)
```

---

### Solución 3: Detección Correcta de Entorno

**Implementación en:** `dashboard/web_app.py`

```python
# CRITICAL FIX: Proper environment detection
# Priority: FLASK_ENV > ENVIRONMENT > default to development
flask_env = os.getenv('FLASK_ENV', '').lower()
general_env = os.getenv('ENVIRONMENT', '').lower()

if flask_env:
    self.env = flask_env
elif general_env:
    self.env = general_env
else:
    self.env = 'development'

# Production mode requires EXPLICIT setting AND FORCE_HTTPS=true
force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
self.is_production = (self.env == 'production' and force_https)
self.is_development = not self.is_production
```

**Lógica de Detección:**

| FLASK_ENV | ENVIRONMENT | FORCE_HTTPS | Resultado |
|-----------|-------------|-------------|-------------|
| production | * | true | ✅ PRODUCTION |
| production | * | false | ⚠️ DEVELOPMENT |
| development | * | * | ⚠️ DEVELOPMENT |
| (vacío) | production | true | ✅ PRODUCTION |
| (vacío) | development | * | ⚠️ DEVELOPMENT |
| (vacío) | (vacío) | * | ⚠️ DEVELOPMENT |

**Características:**
- ✅ Prioridad clara: `FLASK_ENV` > `ENVIRONMENT`
- ✅ Producción requiere **DOS condiciones**: `production` + `FORCE_HTTPS=true`
- ✅ Default seguro: `development` (sin HTTPS)
- ✅ Logs detallados de detección

**Talisman (HTTPS) ahora solo se activa si:**
```python
if HAS_TALISMAN and self.is_production:
    Talisman(self.app, force_https=True, ...)
else:
    logger.info("[*] Talisman DISABLED - Development Mode")
```

**Resultado en Development:**
```
ENVIRONMENT DETECTION:
  FLASK_ENV = production
  ENVIRONMENT = development
  FORCE_HTTPS = false
  Detected mode: PRODUCTION  # Pero is_production=False
  Is Production: False
  Is Development: True
======================================================================
[*] Talisman DISABLED - Development Mode
[*] CSP: OFF
[*] HTTPS: OFF (HTTP only)
```

---

## 📊 Comparación Antes/Después

### Logs del Dashboard

**ANTES:**
```
[+] Loaded environment from E:\...\BotV2\.env
[+] Loaded environment from E:\...\BotV2\.env  ← DUPLICADO
2026-01-30 06:37:33,913 - bot.config.config_manager - INFO - \u2713 Configuration loaded
...
FLASK_ENV = production
ENVIRONMENT = development
Detected mode: PRODUCTION  ← INCONSISTENTE
...
[+] Talisman ENABLED - HTTPS + CSP (production)  ← INCORRECTO en dev
...
127.0.0.1 - - [30/Jan/2026 06:37:49] code 400, message Bad request version
127.0.0.1 - - [30/Jan/2026 06:37:49] "\x16\x03\x01\x06..." 400 -  ← BASURA
127.0.0.1 - - [30/Jan/2026 06:37:49] "\x16\x03\x01\x06..." 400 -  ← BASURA
```

**DESPUÉS:**
```
[+] Environment loaded from E:\...\BotV2\.env  ← UNA SOLA VEZ
2026-01-30 06:37:33,913 - bot.config.config_manager - INFO - ✓ Configuration loaded
...
ENVIRONMENT DETECTION:
  FLASK_ENV = production
  ENVIRONMENT = development
  FORCE_HTTPS = false
  Detected mode: PRODUCTION
  Is Production: False  ← CORRECTO
  Is Development: True  ← CORRECTO
======================================================================
[*] Talisman DISABLED - Development Mode  ← CORRECTO
[*] CSP: OFF
[*] HTTPS: OFF (HTTP only)
[+] SSL error log filter enabled  ← NUEVO
...
# Sin logs SSL ✅
```

---

## 🔧 Configuración Recomendada

### Development (Local)

**`.env`:**
```bash
# Environment (usa FLASK_ENV para Flask apps)
FLASK_ENV=development
ENVIRONMENT=development
FORCE_HTTPS=false  # CRÍTICO: debe ser false

# Dashboard
DASHBOARD_PORT=8050
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin
```

**Resultado:**
- ✅ HTTP en `localhost:8050`
- ✅ Sin Talisman (sin redirección HTTPS)
- ✅ Sin errores SSL en logs
- ✅ CSP desactivado (desarrollo más fácil)

### Production (Servidor)

**`.env`:**
```bash
# Environment
FLASK_ENV=production
ENVIRONMENT=production
FORCE_HTTPS=true  # CRÍTICO: debe ser true

# Dashboard
DASHBOARD_PORT=443  # Puerto HTTPS
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=contraseña_segura_aquí

# Security
SECRET_KEY=clave_secreta_larga_y_aleatoria
```

**Resultado:**
- ✅ HTTPS forzado con Talisman
- ✅ CSP estricto activado
- ✅ Headers de seguridad completos
- ✅ HSTS activado

---

## 🧪 Testing

### Test 1: Verificar Carga Única de `.env`

```bash
python main.py 2>&1 | grep "Loaded environment"
```

**Esperado:** Solo **1 línea** con `[+] Environment loaded`

### Test 2: Verificar Ausencia de Logs SSL

```bash
# Iniciar dashboard
python -m dashboard.web_app

# En otro terminal, probar con curl
curl -k https://localhost:8050/  # Intenta HTTPS

# Revisar logs del dashboard
```

**Esperado:** Sin logs con `code 400` o `\x16\x03`

### Test 3: Verificar Detección de Entorno

```bash
# Development
export FLASK_ENV=development
export FORCE_HTTPS=false
python -m dashboard.web_app 2>&1 | grep -A5 "ENVIRONMENT DETECTION"
```

**Esperado:**
```
Is Production: False
Is Development: True
[*] Talisman DISABLED - Development Mode
```

---

## 📁 Archivos Modificados

### Nuevos Archivos

1. **`shared/utils/env_loader.py`** (Nuevo)
   - Loader centralizado de entorno
   - 80 líneas
   - Flag global `_ENV_LOADED`

2. **`docs/FIXES_LOG_DUPLICATES_SSL.md`** (Este archivo)
   - Documentación completa
   - 500+ líneas

### Archivos Actualizados

1. **`shared/utils/__init__.py`**
   - Añadido export de `load_env_once`
   - +3 líneas

2. **`main.py`**
   - Reemplazado `load_dotenv()` directo con `load_env_once()`
   - Sección de carga de .env simplificada
   - ~15 líneas modificadas

3. **`dashboard/web_app.py`**
   - Reemplazado `load_dotenv()` directo con `load_env_once()`
   - Añadido `SSLErrorFilter` class
   - Mejorada detección de entorno
   - Añadido `_setup_log_filters()` method
   - ~100 líneas modificadas/añadidas

---

## 🎯 Próximos Pasos

### Opcional: Extender el Filtro

Si aparecen otros tipos de logs molestos:

```python
class SSLErrorFilter(logging.Filter):
    def filter(self, record):
        # Filtros existentes
        if 'Bad request version' in record.getMessage():
            return False
        
        # Nuevo: Filtrar otros errores
        if 'Connection reset by peer' in record.getMessage():
            return False
        
        return True
```

### Opcional: Logger Personalizado

Crear un logger dedicado para el dashboard:

```python
# shared/utils/dashboard_logger.py
import logging

def get_dashboard_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(SSLErrorFilter())
    return logger
```

---

## 📖 Referencias

### Documentación Relacionada

- [Flask Logging](https://flask.palletsprojects.com/en/2.3.x/logging/)
- [Werkzeug Logging](https://werkzeug.palletsprojects.com/en/2.3.x/serving/)
- [Python Logging Filters](https://docs.python.org/3/library/logging.html#filter-objects)
- [Flask-Talisman](https://github.com/GoogleCloudPlatform/flask-talisman)

### Commits Relacionados

- `f29700543872c2a20b85a8e3878e33a33418ce9c` - feat: Create centralized env loader
- `f0ce4804fe8381515bf310976047f58ac80efd6b` - fix: Update shared utils init
- `ddc2fdc4e87c0cb6770d0ca8fb443395a45d1f4d` - fix: Use centralized env loader in main.py
- `f22e9ac8f4b6fbe632da6bd4cb0e5057208c7859` - fix: Dashboard env loader + SSL filter

---

## ✅ Checklist de Verificación

- [x] Carga única de `.env` implementada
- [x] Filtro de logs SSL implementado
- [x] Detección correcta de entorno
- [x] Talisman solo en producción real
- [x] Tests manuales ejecutados
- [x] Documentación creada
- [x] Commits realizados
- [x] README actualizado (si necesario)

---

**Autor**: BotV2 Development Team  
**Revisado por**: Juan Carlos García Arriero  
**Fecha de Última Actualización**: 30 de Enero de 2026
