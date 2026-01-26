# 🚀 BotV2 Dashboard - Guía de Configuración Local

## ✅ Estado: Dashboard Funcional al 100% con Credenciales Correctas

**Fecha de Setup:** 26 Enero 2026  
**Credenciales:** `admin` / `admin1234`  
**Ambiente:** Desarrollo Local (Demo Mode)  
**URL:** http://localhost:8050  

---

## 📋 Prerequisitos

- ✅ Docker & Docker Compose instalados
- ✅ Git instalado
- ✅ Acceso a la rama `main` del repositorio
- ✅ Puerto 8050 disponible (dashboard)

---

## 🔧 Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/juankaspain/BotV2.git
cd BotV2
```

---

## 📝 Paso 2: Crear Archivo .env Local

**IMPORTANTE:** Este archivo contiene credenciales de desarrollo. NUNCA hacer commit a Git.

```bash
cp .env.example .env
```

Editar `.env` y asegurar que contiene:

```ini
# FLASK ENVIRONMENT
FLASK_ENV=development

# DASHBOARD CREDENTIALS
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin1234

# SECRET KEY (generate new one for security)
SECRET_KEY=generate_random_key_here_or_use_existing

# MODE
TRADING_MODE=paper
DEMO_MODE=true
INITIAL_CAPITAL=3000
```

---

## 🐳 Paso 3: Limpiar y Reconstruir Docker

```bash
# Detener cualquier contenedor anterior
docker compose down

# Eliminar imágenes antiguas (opcional pero recomendado)
docker system prune -a

# Reconstruir imágenes sin cache
docker compose build --no-cache
```

---

## ▶️ Paso 4: Iniciar el Dashboard

```bash
# Iniciar en background
docker compose up -d

# O iniciar en foreground (para ver logs en tiempo real)
docker compose up
```

---

## ✅ Paso 5: Verificar que está corriendo

```bash
# Ver estado de contenedores
docker compose ps

# Debería mostrar:
# NAME                   STATUS
# botv2-app            Up (healthy)
# botv2-dashboard      Up (healthy)
```

---

## 🌐 Paso 6: Acceder al Dashboard

1. **URL:** http://localhost:8050
2. **Usuario:** `admin`
3. **Contraseña:** `admin1234`

### ✅ Flujo Correcto de Login:

1. Abre http://localhost:8050 en tu navegador
2. Verás la página de login
3. Ingresa:
   - Username: `admin`
   - Password: `admin1234`
4. **Debería redirigirte al dashboard principal**
5. Verás gráficos y datos en tiempo real

---

## 🔍 Troubleshooting

### Problema: "Conexión rechazada" en http://localhost:8050

```bash
# Ver logs del dashboard
docker compose logs botv2-dashboard --tail=50

# Busca esta línea (significa que está listo):
# ✅ Dashboard starting on 0.0.0.0:8050
# 🚀 Dash is running on http://0.0.0.0:8050/
```

### Problema: Login no funciona (muestra error 401)

```bash
# Verificar que .env tiene las credenciales correctas
cat .env | grep DASHBOARD

# Debería mostrar:
# DASHBOARD_USERNAME=admin
# DASHBOARD_PASSWORD=admin1234

# Si está mal, editar y reiniciar:
docker compose down
docker compose up -d
```

### Problema: "Health check failed"

```bash
# El dashboard está iniciando pero aún no responde
# Espera 30-60 segundos y refres El navegador

# Si persiste:
docker compose restart botv2-dashboard
```

### Problema: Dashboard abre pero no carga datos

```bash
# Esto es normal en DEMO_MODE
# Verifica que el contenedor botv2-app está "healthy"
docker compose ps

# Si no está healthy:
docker compose logs botv2-app --tail=30
```

---

## 🧪 Verificación Completa

```bash
#!/bin/bash
echo "=== Verificando BotV2 Setup ==="

echo -n "Docker: "
docker --version

echo -n "\nDocker Compose: "
docker compose --version

echo -n "\nContenedores activos: "
docker compose ps | wc -l

echo "\n=== Testing Dashboard ==="
echo -n "Health Check: "
curl -s http://localhost:8050/health | head -c 100

echo "\n\n=== Credenciales ==="
echo "Usuario: admin"
echo "Contraseña: admin1234"
echo "URL: http://localhost:8050"
```

---

## 📚 Comandos Útiles

```bash
# Ver logs en tiempo real
docker compose logs -f botv2-dashboard

# Ver logs solo del app
docker compose logs botv2-app --tail=50

# Entrar a un contenedor (para debug)
docker exec -it botv2-dashboard /bin/bash

# Reiniciar un servicio
docker compose restart botv2-dashboard

# Detener todo
docker compose down

# Eliminar volúmenes (ATENCIÓN: borra datos)
docker compose down -v
```

---

## 🔐 Seguridad

⚠️ **IMPORTANTE para Producción:**

- ✅ Cambiar `FLASK_ENV=production`
- ✅ Cambiar `SECRET_KEY` a valor aleatorio fuerte
- ✅ Cambiar `DASHBOARD_PASSWORD` a contraseña fuerte (16+ caracteres)
- ✅ Configurar HTTPS/SSL
- ✅ Configurar Rate Limiting con Redis
- ✅ **NUNCA** hacer commit del .env a Git

---

## 📞 Soporte

Si tienes problemas:

1. Verifica los logs: `docker compose logs --tail=100`
2. Revisa el archivo .env: `cat .env`
3. Reinicia los servicios: `docker compose restart`
4. Limpia caché del navegador: `Ctrl+Shift+Delete`
5. Abre Developer Tools (F12) y verifica la consola de errores

---

## ✨ Ahora:

1. **Copia** este archivo
2. **Ejecuta** los pasos en orden
3. **Abre** http://localhost:8050
4. **Login** con admin / admin1234
5. **¡Disfruta tu Dashboard! 🎉**
