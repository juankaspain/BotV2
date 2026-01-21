# 🤖 BotV2 - Sistema Avanzado de Trading Algorítmico

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Dashboard](https://img.shields.io/badge/dashboard-v2.0-brightgreen.svg)
![License](https://img.shields.io/badge/license-Personal%20Use-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)
![Strategies](https://img.shields.io/badge/strategies-20-orange.svg)

**BotV2** es un sistema de trading algorítmico de grado profesional que implementa 26 mejoras de auditoría en validación de datos, gestión de riesgo, estrategias ensemble y simulación realista de ejecución.

## ✨ Características Principales

### 📋 Capacidades Core

- **20 Estrategias de Trading** (15 base + 5 avanzadas de alto rendimiento)
- **Circuit Breaker de 3 Niveles** para protección de capital
- **Asignación Adaptativa de Estrategias** basada en Sharpe Ratios en tiempo real
- **Gestión de Correlación** para reducción de riesgo de portfolio
- **Votación Ensemble** con agregación ponderada
- **Backtesting Realista** con simulación de microestructura de mercado
- **Persistencia de Estado** con PostgreSQL para recuperación automática
- **🌟 Dashboard v2.0 Profesional** - Interfaz web en tiempo real con WebSocket y 9 visualizaciones avanzadas
- **Despliegue Docker** listo para producción con Docker Compose

### ✅ 26 Mejoras de Auditoría Implementadas

#### Ronda 1: Fundación (Mejoras 1-7)

1. ✅ Validación exhaustiva de datos (NaN, Inf, outliers, OHLC)
2. ✅ Pipeline de normalización Z-score
3. ✅ Circuit breaker de 3 niveles (-5%, -10%, -15%)
4. ✅ Dimensionamiento de posiciones con Kelly Criterion
5. ✅ Persistencia de estado con PostgreSQL
6. ✅ Recuperación automática de crashes
7. ✅ Logging estructurado con rotación

#### Ronda 2: Inteligencia (Mejoras 8-14)

8. ✅ Asignación adaptativa de estrategias (basada en Sharpe)
9. ✅ Suavizado exponencial para estabilidad
10. ✅ Cálculo de matriz de correlación
11. ✅ Dimensionamiento de posiciones consciente de correlación
12. ✅ Sistema de votación ensemble
13. ✅ Votación por promedio ponderado
14. ✅ Umbrales de confianza

#### Ronda 3: Ejecución (Mejoras 15-22)

15. ✅ Modelado realista de slippage
16. ✅ Simulación de spread bid-ask
17. ✅ Cálculo de impacto de mercado
18. ✅ Efectos de hora del día
19. ✅ Simulación de llenado parcial
20. ✅ Modelado de profundidad de libro de órdenes
21. ✅ Detección de cascadas de liquidación
22. ✅ Modelo de microestructura de mercado

#### Adicionales (Mejoras 23-26)

23. ✅ 20 estrategias diversificadas
24. ✅ Dashboard de rendimiento en tiempo real con WebSocket
25. ✅ Suite de tests exhaustiva
26. ✅ Despliegue listo para producción

---

## 🚀 Inicio Rápido

### Método 1: Docker Compose (Recomendado)

**La forma más rápida y fácil para producción**

```bash
# 1. Clonar repositorio
git clone https://github.com/juankaspain/BotV2.git
cd BotV2

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus credenciales

# 3. Lanzar todo el stack
docker compose up -d

# 4. Ver logs
docker compose logs -f botv2

# 5. Acceder al dashboard
http://localhost:8050
```

**✅ Incluye automáticamente**:
- PostgreSQL 15 (base de datos)
- Redis (caching)
- BotV2 (aplicación principal)
- Dashboard v2.0 Professional (interfaz web con WebSocket)
- Health checks automáticos
- Restart automático en caso de fallos
- Volúmenes persistentes para datos

### Método 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/juankaspain/BotV2.git
cd BotV2

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos (PostgreSQL)
createdb botv2

# 5. Configurar variables de entorno
export POSTGRES_PASSWORD="tu_password"
export POLYMARKET_API_KEY="tu_api_key"
export DASHBOARD_PASSWORD="tu_password_dashboard"

# 6. Ejecutar el bot
python src/main.py

# 7. En otra terminal, ejecutar el dashboard
python -m src.dashboard.web_app
```

### Prerequisitos

#### Para Docker
- **Docker 20.10+** y **Docker Compose 2.0+**
- **2GB RAM mínimo** (4GB recomendado)
- **20GB espacio en disco SSD**

#### Para Instalación Manual
- **Python 3.10+**
- **PostgreSQL 13+**
- **2GB RAM mínimo**
- **Sistema operativo**: Linux, macOS, o Windows

### Configuración Básica

Edita `src/config/settings.yaml`:

```yaml
trading:
  initial_capital: 3000  # Capital inicial en EUR
  trading_interval: 60   # Intervalo en segundos
  max_position_size: 0.15  # 15% máximo por posición

risk:
  circuit_breaker:
    level_1_drawdown: -5.0   # Precaución al -5%
    level_2_drawdown: -10.0  # Alerta al -10%
    level_3_drawdown: -15.0  # STOP al -15%

dashboard:
  host: 0.0.0.0
  port: 8050
  debug: false
```

**📚 Para detalles completos, consulta:**
- **[CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md)** - Guía completa de configuración
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Guía completa de despliegue en producción

---

## 📋 Dashboard v2.0 Profesional

### 🌟 Interfaz de Monitoreo en Tiempo Real con WebSocket

El **Dashboard v2.0 Professional** es una interfaz web de última generación construida con **Flask + Socket.IO** que proporciona actualizaciones en tiempo real mediante WebSocket, inspirado en el diseño de Bloomberg Terminal.

**🔗 Acceso**: `http://localhost:8050` (después de `docker compose up -d`)

### 🔥 Características Destacadas

#### ⚡ Tecnología WebSocket
- 🔄 **Actualizaciones instantáneas** sin polling
- 🚀 **Latencia ultra baja** (< 50ms)
- 📊 **Push de datos** desde el servidor
- 🔔 **Alertas en tiempo real** con notificaciones toast
- 🔗 **Conexión persistente** con reconexión automática

#### 1️⃣ Curva de Equity en Tiempo Real
- 💵 Visualización de evolución del capital
- 📈 Línea base de capital inicial
- 🔴 Zonas de drawdown resaltadas
- ⏱️ Actualización instantánea vía WebSocket
- 🎯 Indicadores SMA 20/50
- 📊 Gráfico interactivo con Plotly

#### 2️⃣ Retornos Diarios
- 📉 Gráfico de barras por día
- 🟢 Verdes para días ganadores
- 🔴 Rojos para días perdedores
- 📋 Análisis de tendencias

#### 3️⃣ Rendimiento por Estrategia
- 🎯 Comparación de las 20 estrategias
- 📈 ROI individual de cada estrategia
- 🎮 Peso actual en el ensemble
- ⭐ Top 10 estrategias destacadas
- ⚠️ Estrategias con bajo rendimiento identificadas

#### 4️⃣ Métricas de Riesgo en Vivo

**Tabla dinámica con indicadores avanzados**:

| Métrica | Descripción | Umbral |
|---------|-------------|--------|
| **Sharpe Ratio** | Retorno ajustado por riesgo | > 2.5 🟢 |
| **Sortino Ratio** | Retorno vs downside risk | > 2.0 🟢 |
| **Calmar Ratio** | Retorno vs max drawdown | > 3.0 🟢 |
| **Max Drawdown** | Pérdida máxima histórica | < -15% 🔴 |
| **Current Drawdown** | Pérdida desde máximo | < -10% 🟡 |
| **Volatility** | Volatilidad anualizada | < 30% 🟢 |
| **VaR 95%** | Value at Risk (95% confianza) | Métrica de riesgo |
| **CVaR 95%** | Conditional VaR (tail risk) | Riesgo extremo |

**Indicadores de estado en tiempo real**:
- 🟢 Verde: Óptimo
- 🟡 Amarillo: Precaución
- 🔴 Rojo: Crítico
- 🔵 Azul: Informativo

#### 5️⃣ Estado del Circuit Breaker

**Panel visual del sistema de protección con actualización instantánea**:

```
┌─────────────────────────────────────┐
│  CIRCUIT BREAKER STATUS             │
│                                     │
│  Nivel 1 (-5%):  ✅ Inactivo         │
│  Nivel 2 (-10%): ✅ Inactivo         │
│  Nivel 3 (-15%): ✅ Inactivo         │
│                                     │
│  Drawdown Actual: -2.3%             │
│  Estado: 🟢 OPERATIVO              │
│                                     │
│  Tamaño Posiciones: 100%            │
└─────────────────────────────────────┘
```

Estados posibles:
- 🟢 **OPERATIVO**: Todo normal, operando al 100%
- 🟡 **PRECAUCIÓN**: Nivel 1 activo, posiciones al 50%
- 🟠 **ALERTA**: Nivel 2 activo, posiciones al 25%
- 🔴 **STOP**: Nivel 3 activo, todas las posiciones cerradas

#### 6️⃣ Log de Trades Recientes

**Tabla interactiva con los últimos trades actualizada en tiempo real**:

| Timestamp | Símbolo | Acción | Precio | Tamaño | PnL | Estrategia |
|-----------|---------|--------|--------|---------|------|------------|
| 2026-01-21 01:45:32 | BTC/EUR | BUY | 42,350 | 0.05 | - | Momentum |
| 2026-01-21 01:42:18 | ETH/EUR | SELL | 2,890 | 1.2 | +145€ | Mean Reversion |
| 2026-01-21 01:38:55 | BTC/EUR | CLOSE | 42,100 | 0.05 | +230€ | Momentum |

**Características**:
- 🔄 Actualización instantánea vía WebSocket
- 🟢 Trades ganadores en verde
- 🔴 Trades perdedores en rojo
- 🔍 Filtros por estrategia y símbolo
- 📅 Exportable a CSV

#### 7️⃣ Mapa de Calor de Correlaciones

**Matriz visual de correlaciones entre estrategias actualizada en vivo**:

```
                 Momentum  MeanRev  StatArb  Breakout  ...
Momentum           1.00     -0.15    0.23     0.67    ...
Mean Reversion    -0.15      1.00   -0.42     0.08    ...
Stat Arb           0.23     -0.42    1.00     0.15    ...
Breakout           0.67      0.08    0.15     1.00    ...
...
```

**Escala de colores**:
- 🔴 Rojo oscuro: Correlación alta (> 0.7) - ⚠️ Riesgo concentrado
- 🟡 Amarillo: Correlación media (0.3 - 0.7)
- 🟢 Verde: Correlación baja (< 0.3) - ✅ Diversificación óptima
- 🔵 Azul: Correlación negativa - 🎯 Cobertura natural

#### 8️⃣ Distribución de PnL

**Histograma de ganancias y pérdidas por trade**:
- 📉 Distribución normal esperada vs real
- 🎯 Media y mediana marcadas
- 📦 Outliers identificados
- 📋 Estadísticas descriptivas
- 🔔 Alertas de fat tails (riesgo de cola)

#### 9️⃣ Asignación Dinámica de Capital

**Gráfico de pastel interactivo actualizado en tiempo real**:
- 🥧 Peso actual de cada estrategia
- 🔄 Cambios respecto a última hora
- ⭐ Top 5 estrategias con mayor asignación
- 🚫 Estrategias desactivadas (bajo rendimiento)
- 📋 Evolución temporal de pesos

---

### 🛠️ Arquitectura WebSocket

**Cliente (Navegador) ↔️ Servidor (Flask-SocketIO)**

```
Cliente                          Servidor
  │                                  │
  ├─────── connect ────────────────→  │
  │←────── connected (welcome) ────┤
  │                                  │
  ├── request_update (component) ─→  │
  │←────── update (data) ────────┤
  │                                  │
  │                     ┌───────────┐
  │←───── alert ──────┤ Trading  │
  │                     │ Bot push │
  │←───── update ──────┤ updates  │
  │                     └───────────┘
```

**Eventos WebSocket**:
- `connect`: Cliente se conecta al servidor
- `connected`: Servidor confirma conexión
- `request_update`: Cliente solicita actualización
- `update`: Servidor envía datos actualizados
- `alert`: Servidor envía alerta crítica
- `disconnect`: Cliente se desconecta

---

### 🚀 Acceso al Dashboard

#### Con Docker (Recomendado)
```bash
# Dashboard se inicia automáticamente
docker compose up -d

# Verificar que está corriendo
docker compose ps botv2-dashboard

# Ver logs
docker compose logs -f botv2-dashboard

# Acceder
http://localhost:8050
```

**Credenciales**:
- Usuario: `admin` (o valor de `DASHBOARD_USERNAME` en `.env`)
- Contraseña: Valor de `DASHBOARD_PASSWORD` en `.env`

#### Manual
```bash
# Terminal 1: Ejecutar el bot
python src/main.py

# Terminal 2: Ejecutar el dashboard
python -m src.dashboard.web_app

# Acceder
http://localhost:8050
```

#### Health Check (Sin autenticación)
```bash
curl http://localhost:8050/health

# Respuesta:
{
  "status": "healthy",
  "version": "2.0",
  "service": "dashboard",
  "uptime": "Running",
  "last_update": "2026-01-21T04:30:15.123456",
  "authenticated": false
}
```

---

### ⚡ Rendimiento del Dashboard

- **Carga inicial**: < 2 segundos
- **Latencia WebSocket**: < 50ms
- **Actualización de datos**: Instantánea (push)
- **Consumo de memoria**: ~180MB
- **Consumo de CPU**: < 5%
- **Consultas a DB optimizadas**: Caché + índices

---

### 🎯 Casos de Uso del Dashboard

#### Para Trading Diario
1. ✅ Verificar estado del circuit breaker al inicio del día
2. ✅ Revisar rendimiento de estrategias overnight
3. ✅ Monitorear trades en tiempo real vía WebSocket
4. ✅ Ajustar configuración según métricas
5. ✅ Recibir alertas instantáneas de eventos críticos

#### Para Análisis Post-Mortem
1. 🔍 Investigar por qué una estrategia falló
2. 🔍 Identificar patrones de pérdidas
3. 🔍 Analizar correlaciones problemáticas
4. 🔍 Revisar trades alrededor de eventos de circuit breaker
5. 🔍 Optimizar asignación de capital

#### Para Demostraciones
1. 🎬 Mostrar rendimiento en vivo a inversores
2. 🎬 Presentar métricas de riesgo profesionales
3. 🎬 Demostrar capacidades de gestión de riesgo en tiempo real
4. 🎬 Comparar con benchmarks del mercado

---

## 📚 Documentación

### Guías Principales

| Documento | Descripción | Audiencia |
|-----------|-------------|-------|
| **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** | ⭐ **Guía completa de despliegue con Docker y manual** | **Todos** |
| **[CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md)** | Guía completa de configuración con explicaciones detalladas | Todos los usuarios |
| **[DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md)** | Diccionario de datos, conceptos y métricas explicados | Principiantes y todos |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Arquitectura del sistema y componentes | Desarrolladores |
| **[STRATEGIES_DETAILED.md](docs/STRATEGIES_DETAILED.md)** | Documentación detallada de las 20 estrategias | Traders e inversores |
| **[AUDIT_IMPROVEMENTS.md](docs/AUDIT_IMPROVEMENTS.md)** | Las 26 mejoras implementadas | Técnico |

### Estructura del Proyecto

```
BotV2/
├── Dockerfile                  # Imagen Docker del bot
├── docker-compose.yml          # Orquestación de servicios
├── .env.example                # Plantilla de variables de entorno
├── requirements.txt            # Dependencias Python
├── src/
│   ├── main.py                 # Punto de entrada principal
│   ├── config/
│   │   ├── settings.yaml       # Configuración del sistema
│   │   └── config_manager.py   # Gestor de configuración
│   ├── core/
│   │   ├── risk_manager.py     # Gestión de riesgo
│   │   ├── execution_engine.py # Motor de ejecución
│   │   ├── state_manager.py    # Gestión de estado
│   │   └── liquidation_detector.py
│   ├── data/
│   │   ├── data_validator.py   # Validación de datos
│   │   └── normalization_pipeline.py
│   ├── ensemble/
│   │   ├── adaptive_allocation.py
│   │   ├── correlation_manager.py
│   │   └── ensemble_voting.py
│   ├── strategies/             # 20 estrategias de trading
│   │   ├── momentum.py
│   │   ├── stat_arb.py
│   │   ├── cross_exchange_arb.py
│   │   └── ...
│   ├── backtesting/
│   │   ├── realistic_simulator.py
│   │   └── market_microstructure.py
│   └── dashboard/
│       ├── web_app.py          # Dashboard v2.0 Professional (Flask-SocketIO)
│       ├── templates/
│       │   └── dashboard.html  # UI con WebSocket
│       └── static/
├── scripts/
│   ├── init-db.sql             # Inicialización de base de datos
│   ├── monitor.sh              # Script de monitoreo
│   └── backup.sh               # Script de backup
├── tests/                      # Suite de tests
├── docs/                       # Documentación completa
├── logs/                       # Archivos de log
└── backups/                    # Backups de base de datos
```

---

## 📜 Licencia

**Uso Personal** - Este software es para uso personal exclusivo. No está permitido:
- Ofrecer como servicio (SaaS)
- Revender o sublicenciar
- Uso comercial sin autorización

---

## ⚠️ Advertencia Legal

**IMPORTANTE - LEE CUIDADOSAMENTE**

Este software es para **propósitos educativos** exclusivamente.

- **Trading implica riesgo sustancial de pérdida**
- **Rendimientos pasados NO garantizan resultados futuros**
- **Solo invierte dinero que puedas permitirte perder**
- **No somos asesores financieros** - este no es consejo de inversión
- **Siempre haz tu propia investigación (DYOR)**
- **Prueba exhaustivamente** en modo desarrollo antes de usar dinero real
- **Los mercados son impredecibles** - ninguna estrategia es infalible
- **Riesgo de pérdida total del capital**

**El autor no se hace responsable de pérdidas financieras.**

---

## 📞 Contacto y Soporte

**Autor**: Juan Carlos Garcia Arriero  
**Empresa**: Santander Digital  
**Rol**: Technical Lead & Software Architect  
**Ubicación**: Madrid, Spain

**Repositorio**: [https://github.com/juankaspain/BotV2](https://github.com/juankaspain/BotV2)

### Obtener Ayuda

1. **Documentación**: Consulta primero los documentos en `/docs`
2. **Issues**: Abre un issue en GitHub con descripción detallada
3. **Logs**: Siempre incluye logs relevantes al reportar problemas

---

**Versión**: 1.0.0  
**Dashboard**: v2.0 Professional (Flask-SocketIO + WebSocket)  
**Última Actualización**: Enero 2026  
**Estado**: Producción  
**Mejoras Completadas**: 26/26 ✅

---

<div align="center">

**⚠️ Opera con responsabilidad. Solo invierte lo que puedas permitirte perder. ⚠️**

**📋 Trading es arriesgado - La educación y la gestión de riesgo son esenciales 📋**

**🌟 Monitorea con el Dashboard v2.0 Professional - Tu centro de control en tiempo real 🌟**

</div>