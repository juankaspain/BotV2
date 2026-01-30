# Solucion Definitiva - Modo Desarrollo

## Resumen del Problema

El dashboard estaba intentando aplicar politicas de seguridad CSP y Talisman en modo desarrollo, causando:

- Errores de CSP bloqueando recursos CDN
- 404 en favicon.ico
- Headers de seguridad innecesarios en desarrollo
- HTTPS forzado cuando no era necesario

## Solucion Implementada

### 1. Script de Arranque (run.sh)

Variables de entorno configuradas automaticamente:

```bash
export ENVIRONMENT="development"
export FLASK_ENV="development"
export FLASK_DEBUG="1"
export FORCE_HTTPS="false"
export TRADING_MODE="paper"
```

### 2. Dashboard (dashboard/web_app.py)

#### Cambios Criticos

**A. Deteccion de Entorno Mejorada**

```python
# Chequea FLASK_ENV (variable oficial de Flask)
self.env = os.getenv('FLASK_ENV', 'development').lower()
self.is_production = self.env == 'production'
self.is_development = self.env == 'development'
```

**B. Talisman Completamente Desactivado en Desarrollo**

```python
force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'

if HAS_TALISMAN and self.is_production and force_https:
    # Inicializar Talisman con CSP estricto
    Talisman(...)
else:
    # DESARROLLO: COMPLETAMENTE SKIP
    logger.warning("[!] Talisman DISABLED - Development Mode")
```

**C. Favicon Handler**

```python
@self.app.route('/favicon.ico')
def favicon():
    favicon_path = Path(self.app.static_folder) / 'favicon.ico'
    if favicon_path.exists():
        return send_from_directory(...)
    else:
        return '', 204  # No Content
```

## Uso

### Modo Desarrollo

```bash
# Opcion 1: Script automatico (RECOMENDADO)
./run.sh

# Opcion 2: Manual
export FLASK_ENV="development"
export FORCE_HTTPS="false"
python main.py
```

**Comportamiento:**
- Sin CSP (todos los CDN funcionan)
- Sin HTTPS forzado
- Logs detallados
- Favicon 204 en lugar de 404

### Modo Produccion

```bash
export FLASK_ENV="production"
export FORCE_HTTPS="true"
python main.py
```

## Verificacion

### 1. Variables de entorno

Al arrancar `./run.sh`, deberias ver:

```
=====================================
BotV2 Trading System
=====================================
Environment: development
Flask mode: development
HTTPS: false
Trading: paper
=====================================
```

### 2. Logs del dashboard

Busca estas lineas:

```
======================================================================
ENVIRONMENT DETECTION:
  FLASK_ENV = development
  Detected mode: DEVELOPMENT
  Is Production: False
  Is Development: True
======================================================================

[!] Talisman DISABLED - Development Mode
[!] CSP: OFF
[!] HTTPS: OFF
======================================================================
```

### 3. DevTools del navegador

**Console Tab:**
- No debe haber errores de CSP
- Todos los scripts CDN cargados correctamente

**Network Tab:**
- favicon.ico: Status 204
- Todos los recursos externos: 200 OK

## Troubleshooting

### Problema: Aun veo errores de CSP

1. Verifica FLASK_ENV:
```bash
echo $FLASK_ENV  # Debe mostrar: development
```

2. Limpia cache del navegador o usa modo incognito

3. Reinicia el dashboard:
```bash
pkill -f dashboard
./run.sh
```

### Problema: 404 en favicon.ico

1. Crea un favicon:
```bash
touch dashboard/static/favicon.ico
```

2. O ignora - el handler devuelve 204 automaticamente

### Problema: Variables no se aplican

1. Dale permisos:
```bash
chmod +x run.sh
```

2. Ejecuta desde root del proyecto

3. Usa `./run.sh` no `sh run.sh`

## Variables de Entorno - Referencia

### Modo Desarrollo

```bash
FLASK_ENV=development
FLASK_DEBUG=1
FORCE_HTTPS=false
ENVIRONMENT=development
TRADING_MODE=paper
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin
```

### Modo Produccion

```bash
FLASK_ENV=production
FLASK_DEBUG=0
FORCE_HTTPS=true
ENVIRONMENT=production
TRADING_MODE=live
DASHBOARD_USERNAME=<secreto>
DASHBOARD_PASSWORD=<secreto>
SECRET_KEY=<random-64-chars>
```

## Checklist

### Desarrollo Local

- [x] ./run.sh ejecuta correctamente
- [x] Variables mostradas en salida
- [x] Logs muestran "Talisman DISABLED"
- [x] Dashboard en http://localhost:8050
- [x] Login funciona (admin/admin)
- [x] Sin errores CSP en DevTools
- [x] favicon.ico devuelve 204

### Produccion

- [ ] FLASK_ENV=production
- [ ] FORCE_HTTPS=true
- [ ] Certificado SSL valido
- [ ] Variables secretas seguras
- [ ] Logs muestran "Talisman ENABLED"
- [ ] CSP headers presentes

## Notas

1. **run.sh es la forma recomendada** de arrancar en desarrollo
2. **FLASK_ENV es la variable critica**
3. **FORCE_HTTPS debe ser false** en desarrollo
4. **Lee siempre los logs** del startup
5. **Limpia cache del navegador** si ves comportamientos extranos

---

**Ultima actualizacion:** 2026-01-30
**Version Dashboard:** v7.5
**Estado:** FUNCIONANDO CORRECTAMENTE
