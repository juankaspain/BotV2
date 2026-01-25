# BotV2 Dashboard - Guía de Funcionalidades y Métricas

## 📊 Versión: 7.2.1
**Última actualización:** 25 Enero 2026

---

## 🎯 Tabla de Contenidos

1. [Funcionalidades Principales](#funcionalidades-principales)
2. [Métricas y KPIs](#métricas-y-kpis)
3. [Atajos de Teclado](#atajos-de-teclado)
4. [Temas y Personalización](#temas-y-personalización)
5. [Visual Excellence](#visual-excellence)
6. [Command Palette](#command-palette)
7. [AI Insights Panel](#ai-insights-panel)
8. [Gráficos y Visualizaciones](#gráficos-y-visualizaciones)
9. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Funcionalidades Principales

### 1. **Dashboard Principal**
- **Vista General del Portfolio**
  - Valor total del portfolio en tiempo real
  - P&L diario, semanal, mensual y total
  - Win Rate y métricas de rendimiento
  - Sharpe Ratio y métricas de riesgo-rendimiento

- **Equity Curve (Curva de Capital)**
  - Visualización histórica del capital
  - Zoom interactivo y navegación temporal
  - Comparación con benchmark
  - Exportación a PNG/CSV

### 2. **Portfolio**
- **Asignación de Activos**
  - Gráfico de pastel interactivo
  - Desglose por símbolo y valor
  - P&L por posición (absoluto y porcentual)
  - Estado de cada posición (OPEN/CLOSED)

- **Tabla de Posiciones**
  - Filtrado por símbolo, estado
  - Ordenación por columna
  - Búsqueda instantánea

### 3. **Trades (Historial)**
- **Registro Completo de Operaciones**
  - Timestamp preciso de cada trade
  - Acción (BUY/SELL) con badges visuales
  - Precio de ejecución
  - P&L por trade
  - Volumen operado

- **Estadísticas Agregadas**
  - Total de trades ejecutados
  - Número de trades ganadores/perdedores
  - Win Rate calculado
  - Filtrado por rango de fechas

### 4. **Performance**
- **Retornos Mensuales**
  - Gráfico de barras con colores semánticos
  - Retorno promedio mensual
  - Mejor y peor mes
  - Consistencia de retornos

- **Métricas de Rendimiento**
  - Retorno total acumulado
  - Retorno anualizado
  - Sharpe Ratio
  - Sortino Ratio
  - Calmar Ratio

### 5. **Risk Analysis**
- **Métricas de Riesgo**
  - **VaR 95%** (Value at Risk): Máxima pérdida esperada con 95% de confianza
  - **Max Drawdown**: Mayor caída desde un máximo histórico
  - **Volatilidad Anualizada**: Desviación estándar de retornos
  - **Beta**: Sensibilidad respecto al mercado

- **Gráfico de Drawdown**
  - Visualización temporal de las caídas
  - Identificación de periodos de recuperación
  - Duración de drawdowns

### 6. **Market Overview**
- **Índices Principales**
  - S&P 500, Nasdaq, Dow Jones
  - DAX, FTSE, Nikkei
  - Cambio diario en valor y porcentaje

- **Top Movers**
  - Mayores ganadores del día
  - Mayores perdedores
  - Volumen de operaciones
  - Tendencia de mercado

- **Crypto Markets**
  - Bitcoin, Ethereum, principales altcoins
  - Precios en tiempo real
  - Cambios porcentuales

### 7. **Strategies**
- **Gestión de Estrategias**
  - Lista de estrategias configuradas
  - Estado (ACTIVE/INACTIVE)
  - Retorno por estrategia
  - Sharpe Ratio por estrategia
  - Número de trades ejecutados
  - Win Rate individual

- **Configuración**
  - Activar/Desactivar estrategias
  - Parámetros configurables
  - Alertas y notificaciones

### 8. **Backtesting**
- **Simulación Histórica**
  - Comparación Estrategia vs Benchmark
  - Retorno total de backtesting
  - Outperformance calculado
  - Métricas de riesgo simuladas

- **Análisis de Resultados**
  - Gráficos comparativos
  - Tabla de trades simulados
  - Métricas de rendimiento ajustadas

### 9. **Live Monitor**
- **Monitoreo en Tiempo Real**
  - Estado del bot (RUNNING/STOPPED)
  - Uptime del sistema
  - Órdenes activas
  - Trades del día

- **Órdenes Activas**
  - Tipo de orden (MARKET/LIMIT/STOP)
  - Lado (BUY/SELL)
  - Cantidad y precio
  - Estado (PENDING/FILLED/CANCELLED)

### 10. **Control Panel**
- **Control del Bot**
  - Iniciar/Detener bot
  - Configuración de trading automático
  - Ajuste de tamaño de posición máximo
  - Nivel de riesgo (LOW/MEDIUM/HIGH)

- **Configuración de Estrategia**
  - Modo de trading (LIVE/PAPER/BACKTEST)
  - Estrategia activa
  - Stop Loss porcentual
  - Take Profit porcentual

---

## 📊 Métricas y KPIs

### **Portfolio Value**
- **Definición:** Valor total del portfolio incluyendo cash y posiciones abiertas
- **Cálculo:** `Cash + ∑(Precio_Actual × Cantidad)`
- **Interpretación:** Mayor valor indica crecimiento del capital

### **Total P&L (Profit & Loss)**
- **Definición:** Beneficio o pérdida total acumulada
- **Cálculo:** `Capital_Actual - Capital_Inicial`
- **Interpretación:** 
  - Positivo (🟢): Beneficios
  - Negativo (🔴): Pérdidas

### **Win Rate**
- **Definición:** Porcentaje de trades ganadores
- **Cálculo:** `(Trades_Ganadores / Total_Trades) × 100`
- **Interpretación:**
  - ≥ 60%: Excelente (🟢)
  - 40-59%: Bueno (🟡)
  - < 40%: Mejorable (🔴)

### **Sharpe Ratio**
- **Definición:** Retorno ajustado por riesgo
- **Cálculo:** `(Retorno_Promedio - Risk_Free_Rate) / Volatilidad`
- **Interpretación:**
  - > 2.0: Excelente
  - 1.0 - 2.0: Bueno
  - < 1.0: Suboptimal

### **Max Drawdown**
- **Definición:** Mayor caída porcentual desde un pico
- **Cálculo:** `((Valor_Mínimo - Valor_Pico) / Valor_Pico) × 100`
- **Interpretación:**
  - < 10%: Excelente control de riesgo
  - 10-20%: Aceptable
  - > 20%: Alto riesgo

### **Value at Risk (VaR 95%)**
- **Definición:** Máxima pérdida esperada con 95% de confianza
- **Cálculo:** Percentil 5 de distribuc
 de retornos
- **Interpretación:** Mayor VaR = Mayor riesgo potencial

### **Sortino Ratio**
- **Definición:** Retorno ajustado por riesgo a la baja
- **Cálculo:** `(Retorno - Risk_Free) / Downside_Deviation`
- **Interpretación:** Similar a Sharpe pero penaliza solo volatilidad negativa

### **Calmar Ratio**
- **Definición:** Retorno anualizado / Max Drawdown
- **Cálculo:** `Retorno_Anualizado / |Max_Drawdown|`
- **Interpretación:**
  - > 3.0: Excelente
  - 1.0 - 3.0: Bueno
  - < 1.0: Revisar estrategia

---

## ⌨️ Atajos de Teclado

### **Navegación**
- **Ctrl + K** (o Cmd + K): Abrir Command Palette
- **Ctrl + /** : Toggle AI Insights Panel
- **Ctrl + R**: Refrescar vista actual
- **Esc**: Cerrar overlays/paneles

### **Command Palette**
- **↑ ↓**: Navegar por comandos
- **Enter**: Ejecutar comando seleccionado
- **Esc**: Cerrar palette
- **Typing**: Búsqueda fuzzy instantánea

### **Insights Panel**
- **Ctrl + /**: Abrir/Cerrar panel
- **×** (botón): Cerrar panel

---

## 🎨 Temas y Personalización

### **Temas Disponibles**

#### **1. Dark Theme (Por defecto)**
- Background: #0d1117
- Colores inspirados en GitHub Dark
- Optimizado para uso nocturno
- Reduce fatiga visual

#### **2. Light Theme**
- Background: #ffffff
- Alto contraste para entornos iluminados
- Colores vibrantes y claros
- Ideal para día/oficina

#### **3. Bloomberg Terminal**
- Background: #000000
- Estilo terminal profesional
- Color primario: Orange (#ff9900)
- Experiencia Bloomberg authentic

### **Cambiar Tema**
- **Vía UI:** Topbar → Theme Switcher
- **Vía Command Palette:** Ctrl+K → "Switch to [theme]"
- **Vía JavaScript:** `setTheme('dark' | 'light' | 'bloomberg')`

---

## ✨ Visual Excellence

### **Animaciones**
- **Fade In**: Entrada suave de elementos
- **Slide Up**: Deslizamiento vertical
- **Pulse**: Indicadores de estado activo
- **Float**: Iconos flotantes en estados vacíos

### **Skeleton Loaders**
- Placeholders animados durante carga
- Mejora percepción de velocidad
- Evita saltos de layout (CLS)

### **Empty States**
- Estados vacíos con iconos descriptivos
- Mensajes claros y orientados a acción
- Botones CTA cuando aplica

### **Micro-interactions**
- Hover effects en botones y cards
- Transform elevations
- Color transitions
- Shadow dynamics

---

## 🚀 Command Palette

### **¿Qué es?**
Interfaz de comandos estilo Spotlight/VSCode para navegación rápida y ejecución de acciones.

### **Características**
- **Fuzzy Search**: Búsqueda inteligente difusa
- **Keyboard Navigation**: 100% navegable con teclado
- **Categorization**: Comandos organizados por categoría
- **Badges**: Indicadores visuales (Pro, Beta, etc.)
- **Shortcuts Display**: Atajos mostrados inline

### **Categorías de Comandos**

#### **Navigation**
- Go to Dashboard
- Go to Portfolio
- Go to Trades
- Go to Performance
- Go to Risk Analysis
- Go to Market Overview
- Go to Strategies
- Go to Backtesting

#### **Actions**
- Start Trading Bot
- Stop Trading Bot
- Refresh Data
- Export Data
- Toggle AI Insights

#### **Settings**
- Switch to Dark Theme
- Switch to Light Theme
- Switch to Bloomberg Terminal

#### **Help**
- View Keyboard Shortcuts
- Open Documentation

### **Uso**
1. Presionar **Ctrl + K**
2. Escribir nombre del comando o keywords
3. Usar **↑↓** para navegar
4. Presionar **Enter** para ejecutar

---

## 💡 AI Insights Panel

### **¿Qué es?**
Panel lateral con recomendaciones inteligentes basadas en análisis de tu portfolio.

### **Tipos de Insights**

#### **Performance Insights**
- Detección de momentum
- Alertas de rendimiento
- Comparación con benchmarks
- Identificación de tendencias

#### **Risk Alerts**
- Drawdown elevado
- Concentración excesiva
- Volatilidad inusual
- Pérdidas consecutivas

#### **Opportunities**
- Capital disponible para deployment
- Condiciones de mercado favorables
- Activos subvalorados
- Timing de entrada/salida

### **Severidad de Insights**
- **Success** (🟢): Oportunidades positivas
- **Warning** (🟡): Precauciones y alertas
- **Info** (🔵): Información general
- **Danger** (🔴): Riesgos críticos

### **Confidence Score**
- Cada insight incluye nivel de confianza (0-100%)
- **High** (≥ 85%): Alta certeza
- **Medium** (70-84%): Confianza moderada
- **Low** (< 70%): Revisión sugerida

### **Acciones Disponibles**
- View Details: Navegar a sección relacionada
- Share: Compartir insight
- Adjust Settings: Modificar configuración
- Deploy Capital: Wizard de deployment

---

## 📊 Gráficos y Visualizaciones

### **Tipos de Gráficos**

#### **Line Charts**
- Equity Curve
- Drawdown Chart
- Price evolution

**Características:**
- Zoom interactivo
- Hover tooltips
- Fill gradients
- Multiple series support

#### **Bar Charts**
- Monthly Returns
- Trade distribution
- Volume analysis

**Características:**
- Color coding semántico
- Grouped bars
- Stacked option

#### **Pie/Donut Charts**
- Portfolio allocation
- Sector distribution
- Strategy breakdown

**Características:**
- Hover details
- Percentage display
- Hole customization (donut)

### **Controles de Gráficos**
Todos los gráficos incluyen:
- **🔄 Refresh**: Actualizar datos
- **📊 Compare**: Modo comparación
- **⛶ Fullscreen**: Pantalla completa
- **📥 Export PNG**: Exportar imagen 2K
- **📊 Export CSV**: Exportar datos

### **Interactividad Plotly**
- **Zoom**: Box select o scroll wheel
- **Pan**: Arrastr y soltar
- **Reset**: Double click
- **Hover**: Tooltips detallados
- **Legend**: Click para toggle series

---

## 🔧 Solución de Problemas

### **Error: InsightsPanel.toggle is not a function**
**Solución:**
1. Verificar que advanced-features-v7.2.js está cargado
2. Revisar consola para errores de carga
3. Refrescar página (Ctrl+R)
4. Limpiar caché del navegador

**Código correcto:**
```javascript
// El botón debe llamar:
onclick="typeof InsightsPanel !== 'undefined' ? InsightsPanel.toggle() : alert('Insights loading...')"
```

### **Gráficos no se renderizan**
**Causas comunes:**
- Plotly.js no cargado
- Datos inválidos o vacíos
- Contenedor no existe en DOM

**Solución:**
1. Verificar en consola: `typeof Plotly`
2. Revisar datos: `console.log(data)`
3. Verificar ID del contenedor

### **Reload constante al cambiar sección**
**Causa:** `loadSection()` re-renderiza todo el contenido

**Optimización:**
- Implementar cache de secciones
- Usar `requestAnimationFrame` para renders
- Cleanup de charts antes de reload
- Skeleton loaders durante carga

### **Temas no persisten**
**Solución:**
```javascript
// El tema se guarda en localStorage
localStorage.setItem('dashboard-theme', theme);

// Cargar al inicio
const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
setTheme(savedTheme);
```

### **WebSocket no conecta**
**Verificar:**
1. Socket.io cargado: `typeof io`
2. Servidor corriendo en puerto correcto
3. CORS configurado
4. Firewall/proxy no bloqueando

**Logs:**
```javascript
socket.on('connect', () => console.log('Connected'));
socket.on('disconnect', () => console.log('Disconnected'));
socket.on('error', (err) => console.error('Socket error:', err));
```

### **Performance lenta**
**Optimizaciones:**
- Reducir frecuencia de updates en tiempo real
- Implementar virtualización en tablas grandes
- Lazy loading de gráficos offscreen
- Debounce en inputs de búsqueda
- Comprimir datos del servidor

---

## 📚 Recursos Adicionales

### **Enlaces Útiles**
- [Plotly.js Documentation](https://plotly.com/javascript/)
- [Socket.io Client API](https://socket.io/docs/v4/client-api/)
- [GitHub Repository](https://github.com/juankaspain/BotV2)

### **Soporte**
Para issues y preguntas:
- GitHub Issues: [BotV2/issues](https://github.com/juankaspain/BotV2/issues)
- Email: juanca755@hotmail.com

---

**© 2026 BotV2 - Dashboard v7.2.1**  
*Desarrollado por Juan Carlos Garcia Arriero*
