# 📊 BotV2 Dashboard - Professional Trading Interface

[![Version](https://img.shields.io/badge/version-7.5-blue.svg)]()
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange.svg)]()
[![Security](https://img.shields.io/badge/Security-Enterprise%20Grade-red.svg)]()

> **Dashboard Web Profesional para Trading en Tiempo Real con Seguridad de Nivel Empresarial**

Este módulo implementa el dashboard web completo para visualización, monitoreo y control del sistema de trading algorítmico BotV2.

---

## 🌟 Características Principales

### 🔐 Seguridad v7.5 - Nonce-Based CSP
| Feature | Descripción | Estado |
|---------|-------------|--------|
| **CSRF Protection** | Token-based validation (all forms + AJAX) | ✅ Production |
| **XSS Prevention** | Bleach backend + DOMPurify frontend | ✅ Production |
| **Input Validation** | Pydantic models for type-safe validation | ✅ Production |
| **Session Management** | Secure cookies + automatic timeout | ✅ Production |
| **Rate Limiting** | Redis backend + per-endpoint limits | ✅ Production |
| **Security Headers** | CSP with nonces, HSTS, X-Frame-Options | ✅ Production |
| **HTTPS Enforcement** | Flask-Talisman production-grade TLS | ✅ Production |
| **SRI Protection** | All CDN libraries with integrity checks | ✅ Production |

### 🎨 UI/UX Moderno
- **3 Temas Premium:** Dark, Light, Bloomberg Professional
- **Sidebar Colapsable:** Modo icono o etiquetas completas
- **Fully Responsive:** Desktop → Tablet → Mobile
- **60fps Animations:** Transiciones suaves y fluidas
- **Theme Persistence:** LocalStorage cached

### 📊 13 Tipos de Gráficos Avanzados
1. **Equity Curve** - Valor del portfolio en tiempo real
2. **P&L Waterfall** - Visualización de breakdown
3. **Correlation Heatmap** - Correlaciones entre estrategias
4. **Asset Treemap** - Asignación jerárquica
5. **Candlestick Chart** - OHLC con volumen
6. **Scatter Plot** - Análisis Risk vs Return
7. **Box Plot** - Distribuciones de retornos
8. **Drawdown Chart** - Visualización underwater
9. **Daily Returns** - Barras de rendimiento
10. **Strategy Comparison** - Vista multi-estrategia
11. **Risk Metrics** - Tabla comprehensiva
12. **Portfolio Pie** - Breakdown de activos
13. **Market Data** - Feeds de precios en vivo

---

## 📁 Estructura del Módulo

```
dashboard/
├── 🌐 api/                     # API REST Endpoints
│   ├── __init__.py
│   ├── portfolio.py            # Portfolio endpoints
│   ├── trades.py               # Trade management
│   ├── strategies.py           # Strategy endpoints (14 tests)
│   ├── market_data.py          # Market data v5.1
│   └── annotations.py          # Chart annotations v5.1
│
├── 🧩 components/              # Componentes Reutilizables
│   ├── charts.py               # Chart components
│   ├── tables.py               # Data tables
│   ├── forms.py                # Form components
│   └── widgets.py              # Dashboard widgets
│
├── 📄 pages/                   # Páginas del Dashboard
│   ├── dashboard.py            # Main dashboard
│   ├── control_panel.py        # Control Panel v4.2
│   ├── live_monitor.py         # Live Monitor v4.3
│   └── strategy_editor.py      # Strategy Editor v4.4
│
├── 🔀 routes/                  # Rutas Flask
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes
│   ├── api.py                  # API routes
│   └── websocket.py            # WebSocket handlers
│
├── 📁 static/                  # Archivos Estáticos
│   ├── css/                    # Estilos CSS
│   │   ├── main.css            # Estilos principales
│   │   ├── themes/             # Archivos de temas
│   │   └── components/         # Estilos de componentes
│   ├── js/                     # JavaScript
│   │   ├── app.js              # App principal
│   │   ├── charts.js           # Lógica de gráficos
│   │   ├── websocket.js        # Cliente WebSocket
│   │   └── utils.js            # Utilidades
│   └── service-worker.js       # PWA Support
│
├── 📝 templates/               # Templates Jinja2
│   ├── base.html               # Template base
│   ├── dashboard.html          # Dashboard principal
│   ├── login.html              # Página de login
│   └── partials/               # Componentes parciales
│
├── 🛠️ utils/                   # Utilidades
│   ├── formatters.py           # Formateo de datos
│   ├── validators.py           # Validadores
│   ├── helpers.py              # Funciones auxiliares
│   └── decorators.py           # Decoradores custom
│
├── WEB_APP_MODS.py             # Módulos de la aplicación web
├── __init__.py                 # Inicialización del módulo
├── bot_controller.py           # Control del bot desde dashboard
├── database.py                 # Gestión de base de datos
├── live_monitor.py             # Monitor en tiempo real
├── metrics_monitor.py          # Monitoreo de métricas
├── mock_data.py                # Datos de prueba
├── models.py                   # Modelos de datos
├── strategy_editor.py          # Editor de estrategias
└── web_app.py                  # Aplicación Flask principal (v7.5)
```

---

## 🚀 Quick Start

### Requisitos
- Python 3.11+
- Redis (para rate limiting en producción)
- Node.js (opcional, para assets)

### Instalación

```bash
# Desde la raíz del proyecto
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus credenciales

# Generar credenciales de seguridad
export DASHBOARD_PASSWORD=$(openssl rand -base64 16)
export SECRET_KEY=$(openssl rand -base64 32)
echo "DASHBOARD_PASSWORD=$DASHBOARD_PASSWORD" >> .env
echo "SECRET_KEY=$SECRET_KEY" >> .env
```

### Ejecutar Dashboard

```bash
# Modo desarrollo
python -m dashboard.web_app

# O desde la raíz
python main.py --dashboard

# Abrir navegador en http://localhost:5000
# Login: admin / [tu contraseña generada]
```

### Modo Producción

```bash
# Con Docker
docker-compose -f docker-compose.production.yml up -d

# O con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 dashboard.web_app:app
```

---

## 🔧 Configuración

### Variables de Entorno
```env
# Security
SECRET_KEY=your_secret_key_here
DASHBOARD_PASSWORD=your_password_here
DASHBOARD_USERNAME=admin

# Server
FLASK_ENV=production
FLASK_DEBUG=0
HOST=0.0.0.0
PORT=5000

# Rate Limiting
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_ENABLED=true

# WebSocket
WEBSOCKET_ENABLED=true
WS_PING_INTERVAL=25
```

### Configuración de Seguridad
```python
# En web_app.py
SECURITY_CONFIG = {
    'csrf_enabled': True,
    'rate_limit': '10/minute',
    'session_timeout': 3600,
    'https_redirect': True,
    'hsts_enabled': True,
    'csp_nonce': True
}
```

---

## 📊 API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | POST | User authentication |
| `/logout` | GET | End session |
| `/health` | GET | Health check (no auth) |

### Portfolio
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portfolio` | GET | Get portfolio data |
| `/api/portfolio/history` | GET | Historical data |
| `/api/portfolio/metrics` | GET | Performance metrics |

### Trades
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trades` | GET | List all trades |
| `/api/trades/<id>` | GET | Get specific trade |
| `/api/trades/recent` | GET | Recent trades |

### Strategies
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/strategies` | GET | List strategies |
| `/api/strategies/<id>` | GET | Strategy details |
| `/api/strategies/<id>/toggle` | POST | Enable/disable |
| `/api/strategies/<id>/backtest` | POST | Run backtest |

### Market Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/market/prices` | GET | Current prices |
| `/api/market/ohlcv` | GET | OHLCV data |
| `/api/market/orderbook` | GET | Order book |

---

## 🔌 WebSocket Events

### Client → Server
```javascript
// Subscribe to updates
socket.emit('subscribe', { channel: 'portfolio' });
socket.emit('subscribe', { channel: 'trades' });
socket.emit('subscribe', { channel: 'prices' });

// Request data
socket.emit('get_portfolio');
socket.emit('get_recent_trades', { limit: 10 });
```

### Server → Client
```javascript
// Portfolio updates
socket.on('portfolio_update', (data) => { ... });

// Trade notifications
socket.on('new_trade', (data) => { ... });

// Price updates
socket.on('price_update', (data) => { ... });

// System alerts
socket.on('alert', (data) => { ... });
```

---

## 🧪 Testing

### Test Suite Completo
```bash
# Todos los tests del dashboard
pytest tests/test_dashboard_v4_4.py -v

# Tests específicos
pytest tests/ -k "dashboard" -v

# Con coverage
pytest tests/test_dashboard_v4_4.py --cov=dashboard --cov-report=html
```

### Cobertura de Tests (70+ tests)
| Categoría | Tests | Estado |
|-----------|-------|--------|
| Authentication | 6 | ✅ |
| Dashboard UI | 5 | ✅ |
| API Endpoints | 40+ | ✅ |
| WebSocket | 3 | ✅ |
| Security | 4 | ✅ |
| Integration | 2 | ✅ |
| Performance | 2 | ✅ |

---

## 🎨 Temas Disponibles

### Dark Theme (Default)
- Fondo oscuro profesional
- Colores de acento cyan/blue
- Ideal para trading nocturno

### Light Theme
- Fondo claro limpio
- Colores de acento blue/indigo
- Alta legibilidad

### Bloomberg Theme
- Estilo Bloomberg Terminal
- Naranja característico
- Para traders profesionales

```javascript
// Cambiar tema
setTheme('dark');   // o 'light', 'bloomberg'
```

---

## 📈 Rendimiento

| Métrica | Target | Actual |
|---------|--------|--------|
| Initial Load | < 3s | 2.1s |
| Chart Render | < 100ms | 80ms |
| API Response | < 200ms | 150ms |
| Memory Usage | < 100MB | 62MB |
| WebSocket Latency | < 50ms | 30ms |

---

## 🔐 Seguridad Implementada

### Protecciones Activas
- ✅ **CSRF**: Token validation en todos los formularios
- ✅ **XSS**: Sanitización de inputs y outputs
- ✅ **SQL Injection**: ORM con parameterized queries
- ✅ **Rate Limiting**: 10 req/min por IP
- ✅ **Brute Force**: Bloqueo tras 5 intentos fallidos
- ✅ **Session Hijacking**: Secure + HttpOnly cookies
- ✅ **Clickjacking**: X-Frame-Options: DENY
- ✅ **Content Security Policy**: Nonce-based strict CSP

### Headers de Seguridad
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'; script-src 'nonce-xxx'
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 📚 Documentación Relacionada

- 📖 [README Principal](../README.md)
- 🤖 [Bot Module](../bot/README.md)
- 🔐 [Guía de Seguridad](../docs/SECURITY.md)
- 🧪 [Guía de Testing](../docs/TESTING_GUIDE.md)
- 📊 [API Reference](../docs/API.md)
- 🚀 [Deployment Guide](../docs/DEPLOYMENT.md)

---

## 👨‍💻 Autor

**Juan Carlos Garcia Arriero**
- GitHub: [@juankaspain](https://github.com/juankaspain)
- Email: juanca755@hotmail.com

---

*Parte del proyecto [BotV2](https://github.com/juankaspain/BotV2) - Professional Trading Dashboard*
