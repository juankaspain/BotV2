# 📊 Dashboard Profesional BotV2 v2.0

## 🎉 Introducción

El **Dashboard Profesional v2.0** de BotV2 es una interfaz web de grado institucional inspirada en Bloomberg Terminal, diseñada para monitoreo en tiempo real de tu sistema de trading algorítmico.

### ✨ Características Principales

- 📊 **Gráficos Interactivos Avanzados** con Plotly
- 🔄 **Actualizaciones en Tiempo Real** vía WebSocket
- 🎨 **Tema Dark/Light** intercambiable
- 📱 **Diseño Responsive** para móvil
- 🚨 **Sistema de Alertas** inteligente
- 📊 **Análisis de Riesgo** completo (VaR, CVaR, Sortino, Calmar)
- 🎯 **Atribución de Performance** por estrategia
- 🔥 **Mapa de Calor** de correlaciones
- 💾 **Exportación de Reportes**
- ⚡ **Performance Optimizado** con caché

---

## 🚀 Inicio Rápido

### Opción 1: Con Docker (Recomendado)

```bash
# El docker-compose ya incluye el dashboard
docker compose up -d

# Acceder
http://localhost:8050
```

### Opción 2: Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar (opcional)
export DASHBOARD_HOST="0.0.0.0"
export DASHBOARD_PORT="8050"

# 3. Ejecutar dashboard
python src/dashboard/app.py

# 4. Abrir navegador
http://localhost:8050
```

---

## 📊 Componentes del Dashboard

### 1. Barra de Navegación

**Elementos**:
- **Logo y Nombre**: BotV2 v2.0
- **Indicador de Conexión**: Estado WebSocket en tiempo real
- **Toggle de Tema**: Cambiar entre Dark/Light
- **Botón de Exportación**: Descargar reportes
- **Pantalla Completa**: Modo full-screen

### 2. Tarjetas de Métricas Overview

Seis tarjetas con métricas clave:

#### Equity Total
- Valor actual del portfolio
- Cambio del día (EUR y %)
- Indicador visual positivo/negativo

#### P&L Total
- Ganancia/Pérdida total
- Retorno total en %
- Color dinámico

#### Win Rate
- Porcentaje de trades ganadores
- Total de trades ejecutados

#### Sharpe Ratio
- Ratio de Sharpe actual
- Calificación (Malo/Aceptable/Bueno/Muy Bueno/Excelente)

#### Max Drawdown
- Máximo drawdown histórico
- Drawdown actual

#### Volatilidad
- Volatilidad anualizada
- Calificación de riesgo

### 3. Curva de Equity

**Gráfico Principal**:
- Curva de equity en tiempo real
- SMAs (20 y 50 periodos)
- Filtros de periodo (1D, 1W, 1M, TODO)
- Hover interactivo
- Fill gradient para visualización

**Interactividad**:
- Zoom con mouse wheel
- Pan arrastrando
- Reset con doble-click

### 4. Retornos Diarios

**Gráfico de Barras**:
- Retornos diarios en %
- Colores dinámicos (verde/rojo)
- Identificación visual rápida de performance

### 5. Gráfico de Drawdown

**Visualización del Drawdown**:
- Drawdown histórico
- Identificación de periodos difíciles
- Zoom en periodos específicos

### 6. Rendimiento por Estrategia

**Gráfico de Barras**:
- Performance de cada estrategia
- Selector de métrica:
  - Retorno total
  - Sharpe Ratio
  - Win Rate
  - Total de trades
- Ordenación automática

### 7. Mapa de Calor de Correlaciones

**Heatmap Interactivo**:
- Correlaciones entre estrategias
- Escala de color (-1 a +1)
- Identificación de redundancias
- Optimización de portfolio

### 8. Atribución de Performance

**Gráfico Circular (Donut)**:
- Contribución de cada estrategia al P&L total
- Porcentajes visuales
- Identificación de estrategias top

### 9. Métricas de Riesgo

**Grid de Métricas**:

| Métrica | Descripción |
|---------|-------------|
| **Sharpe Ratio** | Retorno ajustado por riesgo |
| **Sortino Ratio** | Similar a Sharpe, solo considera downside |
| **Calmar Ratio** | Retorno / Max Drawdown |
| **Max Drawdown** | Máxima caída desde peak |
| **Current DD** | Drawdown actual |
| **Volatilidad** | Volatilidad anualizada |
| **VaR 95%** | Value at Risk al 95% |
| **CVaR 95%** | Conditional VaR (Expected Shortfall) |

### 10. Tabla de Trades Recientes

**Tabla Interactiva**:
- Últimos 20 trades
- Columnas:
  - Timestamp
  - Estrategia
  - Símbolo
  - Acción (BUY/SELL)
  - Tamaño
  - Precio de entrada
  - P&L (EUR)
  - P&L (%)
  - Confianza
- Scroll infinito
- Colores dinámicos
- Botón de refresh

---

## 🎨 Temas (Dark/Light)

### Dark Theme (Default)

**Paleta de Colores**:
```css
Background Primary:   #0a0e1a
Background Secondary: #131824
Cards:                #1e2536
Text Primary:         #e0e6ed
Accent Primary:       #00d4aa (Verde Cyan)
Accent Danger:        #ff4757 (Rojo)
Accent Success:       #26de81 (Verde)
```

**Inspiración**: Bloomberg Terminal, trading platforms profesionales

### Light Theme

**Paleta de Colores**:
```css
Background Primary:   #f5f7fa
Background Secondary: #ffffff
Cards:                #ffffff
Text Primary:         #1a202c
Accent Primary:       #00b894 (Verde)
```

**Cambiar Tema**:
- Click en el botón de luna/sol en la navbar
- Preferencia guardada en localStorage
- Recarga automática de gráficos

---

## 🔌 WebSocket - Actualizaciones en Tiempo Real

### Cómo Funciona

1. **Conexión**: Cliente conecta vía Socket.IO al iniciar
2. **Eventos**: Bot emite eventos cuando hay cambios
3. **Actualización**: Dashboard actualiza gráficos automáticamente
4. **Fallback**: Polling cada 30 segundos si WebSocket falla

### Eventos WebSocket

```javascript
// Cliente recibe updates
socket.on('update', (data) => {
    // Actualiza overview, equity, strategies, etc.
});

// Cliente recibe alertas
socket.on('alert', (alert) => {
    // Muestra alerta visual
});

// Estado de conexión
socket.on('connect', () => {
    // Indicador verde
});

socket.on('disconnect', () => {
    // Indicador rojo
});
```

### Desde el Bot

```python
# En tu sistema de trading
from src.dashboard.app import ProfessionalDashboard

dashboard = ProfessionalDashboard(config)

# Actualizar datos
dashboard.update_data(
    portfolio={'equity': 10000, 'cash': 5000, 'positions': {}},
    trades=trades_list,
    strategies=strategies_performance,
    risk=risk_metrics
)

# Enviar alerta
dashboard.add_alert(
    level='warning',
    message='Circuit breaker nivel 1 activado',
    category='risk'
)

# Ejecutar servidor
dashboard.run()
```

---

## 📡 API REST

### Endpoints Disponibles

#### GET /api/overview
**Descripción**: Métricas generales del portfolio

**Response**:
```json
{
    "equity": 10500.50,
    "cash": 5000.00,
    "positions_count": 3,
    "total_return": 5.00,
    "daily_change": 250.00,
    "daily_change_pct": 2.43,
    "win_rate": 62.5,
    "total_trades": 48,
    "sharpe_ratio": 2.85,
    "max_drawdown": -8.2,
    "timestamp": "2026-01-21T01:00:00"
}
```

#### GET /api/equity
**Descripción**: Datos de curva de equity

**Response**:
```json
{
    "timestamps": ["2026-01-20T00:00:00", ...],
    "equity": [10000, 10050, 10100, ...],
    "sma_20": [10000, 10025, 10050, ...],
    "sma_50": [10000, 10010, 10020, ...],
    "drawdown": [0, -0.005, -0.01, ...]
}
```

#### GET /api/trades?limit=50
**Descripción**: Trades recientes

**Parámetros**:
- `limit`: Número de trades (default: 50)

**Response**:
```json
{
    "trades": [
        {
            "timestamp": "2026-01-21T00:30:00",
            "strategy": "MomentumStrategy",
            "symbol": "BTC-USD",
            "action": "BUY",
            "size": 0.025,
            "entry_price": 42500.00,
            "pnl": 125.50,
            "pnl_pct": 2.35,
            "confidence": 0.75
        }
    ],
    "summary": {
        "total_trades": 48,
        "winning_trades": 30,
        "losing_trades": 18,
        "win_rate": 62.5,
        "avg_win": 85.20,
        "avg_loss": -45.30,
        "profit_factor": 1.88,
        "total_pnl": 1250.50
    }
}
```

#### GET /api/strategies
**Descripción**: Performance de estrategias

**Response**:
```json
{
    "strategies": [
        {
            "name": "CrossExchangeArb",
            "total_return": 15.2,
            "sharpe_ratio": 3.5,
            "win_rate": 75.0,
            "total_trades": 120,
            "avg_win": 95.50,
            "avg_loss": -35.20,
            "profit_factor": 2.71,
            "weight": 0.25,
            "status": "active"
        }
    ]
}
```

#### GET /api/risk
**Descripción**: Métricas de riesgo completas

**Response**:
```json
{
    "sharpe_ratio": 2.85,
    "sortino_ratio": 3.42,
    "calmar_ratio": 0.61,
    "max_drawdown": -8.2,
    "current_drawdown": -2.5,
    "volatility": 15.3,
    "var_95": -2.1,
    "cvar_95": -3.8,
    "beta": 0.95,
    "alpha": 0.05,
    "information_ratio": 1.25
}
```

#### GET /api/correlation
**Descripción**: Matriz de correlación entre estrategias

**Response**:
```json
{
    "strategies": ["Strategy1", "Strategy2", "Strategy3"],
    "matrix": [
        [1.0, 0.25, -0.15],
        [0.25, 1.0, 0.35],
        [-0.15, 0.35, 1.0]
    ]
}
```

#### GET /api/attribution
**Descripción**: Atribución de performance

**Response**:
```json
{
    "attribution": [
        {
            "strategy": "CrossExchangeArb",
            "pnl": 450.25,
            "contribution_pct": 36.0
        },
        {
            "strategy": "StatArb",
            "pnl": 320.50,
            "contribution_pct": 25.6
        }
    ]
}
```

#### GET /api/alerts
**Descripción**: Alertas activas

**Response**:
```json
{
    "alerts": [
        {
            "id": 1,
            "timestamp": "2026-01-21T00:30:00",
            "level": "warning",
            "message": "Circuit breaker nivel 1 activado",
            "category": "risk"
        }
    ]
}
```

#### GET /health
**Descripción**: Health check del dashboard

**Response**:
```json
{
    "status": "healthy",
    "version": "2.0",
    "uptime": "Running",
    "last_update": "2026-01-21T01:00:00"
}
```

---

## 💾 Exportación de Reportes

### Formatos Soportados

- **PDF**: Reporte completo con gráficos
- **Excel**: Datos raw para análisis
- **JSON**: Datos estructurados

### Cómo Exportar

```bash
# Desde el dashboard
# Click en botón de exportación (💾)

# O vía API
curl http://localhost:8050/api/export/report?format=pdf -o report.pdf
```

### Contenido del Reporte

1. **Resumen Ejecutivo**
   - Métricas clave
   - Performance overview
   
2. **Análisis de Performance**
   - Curva de equity
   - Retornos por periodo
   - Comparación vs benchmark
   
3. **Análisis de Riesgo**
   - Métricas de riesgo
   - Drawdowns históricos
   - VaR y CVaR
   
4. **Estrategias**
   - Performance individual
   - Contribución al portfolio
   - Correlaciones
   
5. **Trades**
   - Trades recientes
   - Estadísticas
   - Win/Loss analysis

---

## 🚨 Sistema de Alertas

### Tipos de Alertas

#### Info ℹ️
- Actualizaciones generales
- Nuevas estrategias activadas
- Cambios de configuración

#### Warning ⚠️
- Circuit breaker nivel 1 activado
- Correlación alta detectada
- Volatilidad elevada

#### Danger 🚨
- Circuit breaker nivel 2 o 3
- Pérdidas significativas
- Errores críticos

#### Success ✅
- Objetivos alcanzados
- Hitos de performance
- Recuperación de drawdown

### Configuración de Alertas

```python
# En tu bot
dashboard.add_alert(
    level='danger',  # info, warning, danger, success
    message='Max drawdown excedido: -15.2%',
    category='risk'  # risk, performance, system, strategy
)
```

### Visualización

- **Barra de alertas** en la parte superior
- **Animación de entrada** suave
- **Auto-dismiss** después de 10 segundos
- **Timestamp** de la alerta
- **Color e icono** según nivel

---

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Host y Puerto
export DASHBOARD_HOST="0.0.0.0"  # Default: 0.0.0.0
export DASHBOARD_PORT="8050"     # Default: 8050

# Secret Key (para Flask)
export SECRET_KEY="your-secret-key-here"

# Autenticación (opcional)
export DASHBOARD_USERNAME="admin"
export DASHBOARD_PASSWORD="your-password"

# Redis (para caching)
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

### settings.yaml

```yaml
dashboard:
  host: "0.0.0.0"
  port: 8050
  debug: false
  refresh_rate: 5  # segundos
  
  # Caché
  cache:
    enabled: true
    ttl: 60  # segundos
  
  # Historial
  history:
    max_points: 10000  # Máximo de puntos en equity curve
    max_trades: 1000   # Máximo de trades en memoria
  
  # Alertas
  alerts:
    max_alerts: 100
    auto_dismiss: 10  # segundos
```

---

## 📊 Optimización de Performance

### Mejores Prácticas

1. **Limitar Puntos en Gráficos**
   - Máximo 10,000 puntos en equity curve
   - Downsampling automático para periodos largos

2. **Caché de Cálculos**
   - Métricas pre-calculadas
   - TTL de 60 segundos
   - Invalidación inteligente

3. **WebSocket Eficiente**
   - Solo envía cambios (delta updates)
   - Throttling de actualizaciones
   - Compresión de datos

4. **Lazy Loading**
   - Gráficos se renderizan bajo demanda
   - Trades con paginación
   - Imágenes optimizadas

### Benchmarks

```
Tiempo de carga inicial:  < 2s
Update WebSocket:         < 100ms
Renderizado de gráfico:  < 500ms
Consumo de memoria:       < 150MB
Conexiones simultáneas:  > 100
```

---

## 🐛 Troubleshooting

### Dashboard no carga

```bash
# Verificar que el servidor está corriendo
ps aux | grep dashboard

# Verificar puerto
sudo netstat -tlnp | grep 8050

# Ver logs
tail -f logs/dashboard.log

# Verificar dependencias
pip list | grep -E "flask|socketio|plotly"
```

### WebSocket no conecta

```javascript
// En consola del navegador
console.log(io);

// Verificar que Socket.IO se cargó
if (typeof io === 'undefined') {
    console.error('Socket.IO no cargado');
}
```

**Soluciones**:
1. Verificar firewall permite puerto 8050
2. Revisar CORS config
3. Probar con polling fallback

### Gráficos no se muestran

```javascript
// Verificar Plotly
if (typeof Plotly === 'undefined') {
    console.error('Plotly no cargado');
}

// Ver errores de renderizado
Plotly.validate(data, layout);
```

**Soluciones**:
1. Limpiar caché del navegador
2. Verificar datos válidos en API
3. Comprobar tema aplicado correctamente

### Performance lento

**Diagnóstico**:
```python
# Ver cantidad de datos en memoria
print(f"Portfolio points: {len(dashboard.portfolio_history)}")
print(f"Trades: {len(dashboard.trades_history)}")
```

**Soluciones**:
1. Reducir `max_points` en config
2. Habilitar caché
3. Usar Redis para datos históricos

---

## 📱 Mobile Responsive

### Breakpoints

- **Desktop**: > 1200px
- **Tablet**: 768px - 1200px
- **Mobile**: < 768px

### Adaptaciones Mobile

1. **Navbar**: Se compacta, botones en dropdown
2. **Métricas**: Grid de 1 columna
3. **Gráficos**: Full width, altura reducida
4. **Tabla**: Scroll horizontal
5. **Fuentes**: Tamaños reducidos

---

## 🎓 Ejemplos de Uso

### Integración Básica

```python
from src.dashboard.app import ProfessionalDashboard
from src.config.config_manager import ConfigManager

# Inicializar
config = ConfigManager()
dashboard = ProfessionalDashboard(config)

# En tu loop de trading
while True:
    # ... ejecutar trading logic ...
    
    # Actualizar dashboard
    dashboard.update_data(
        portfolio={
            'equity': current_equity,
            'cash': available_cash,
            'positions': active_positions
        },
        trades=recent_trades,
        strategies=strategy_performance,
        risk=risk_metrics
    )
    
    await asyncio.sleep(60)

# Ejecutar dashboard (en thread separado)
import threading
dashboard_thread = threading.Thread(target=dashboard.run)
dashboard_thread.start()
```

### Alertas Personalizadas

```python
# Circuit breaker activado
if drawdown < -5.0:
    dashboard.add_alert(
        level='warning',
        message=f'Circuit breaker nivel 1: Drawdown {drawdown:.2f}%',
        category='risk'
    )

# Objetivo alcanzado
if total_return > 20.0:
    dashboard.add_alert(
        level='success',
        message=f'¡Objetivo del 20% alcanzado! Return: {total_return:.2f}%',
        category='performance'
    )

# Error de sistema
try:
    execute_trade()
except Exception as e:
    dashboard.add_alert(
        level='danger',
        message=f'Error ejecutando trade: {str(e)}',
        category='system'
    )
```

---

## 🚀 Roadmap Futuro

### v2.1 (Próximo)
- [ ] Autenticación con JWT
- [ ] Multi-usuario con roles
- [ ] Notificaciones push (Telegram/Email)
- [ ] Comparación con benchmarks
- [ ] Backtesting visual interactivo

### v2.2
- [ ] Machine Learning insights
- [ ] Predicciones en tiempo real
- [ ] Optimización automática de parámetros
- [ ] A/B testing de estrategias
- [ ] Dashboard público (read-only)

### v3.0
- [ ] Mobile app nativa
- [ ] Voz con comandos
- [ ] IA conversacional
- [ ] AR/VR visualization
- [ ] Integración con brokers

---

## 📚 Recursos

### Documentación
- [Flask](https://flask.palletsprojects.com/)
- [Socket.IO](https://socket.io/)
- [Plotly](https://plotly.com/python/)
- [Chart.js](https://www.chartjs.org/)

### Tutoriales
- [Real-time Dashboards with Flask](https://example.com)
- [Bloomberg Terminal UI Design](https://example.com)
- [WebSocket Best Practices](https://example.com)

---

## ⭐ Contribuciones

Si tienes ideas para mejorar el dashboard:

1. Abre un Issue describiendo la mejora
2. Fork el repositorio
3. Implementa la feature
4. Abre un Pull Request

---

**Versión**: 2.0  
**Última Actualización**: Enero 2026  
**Autor**: Juan Carlos Garcia Arriero  
**Licencia**: Uso Personal

---

<div align="center">

**📊 Happy Trading! 📊**

</div>
