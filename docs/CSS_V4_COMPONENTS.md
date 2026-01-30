# 🎨 CSS v4.0 Components - Guía Completa

**Dashboard BotV2** | Autor: Juan Carlos Garcia Arriero | Fecha: 30 Enero 2026

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Componente: Metric Cards](#componente-metric-cards)
3. [Componente: Empty States](#componente-empty-states)
4. [Componente: Chart Containers](#componente-chart-containers)
5. [Migración desde Bootstrap](#migración-desde-bootstrap)
6. [Best Practices](#best-practices)
7. [Integración con ThemeManager](#integración-con-thememanager)

---

## 🎯 Introducción

CSS v4.0 introduce **componentes reutilizables y profesionales** siguiendo metodología BEM (Block Element Modifier) para construir interfaces consistentes y mantenibles.

### Por Qué Usar CSS v4.0

| Antes (Bootstrap Only) | Ahora (CSS v4.0) |
|------------------------|------------------|
| ❌ Estilos genéricos | ✅ Componentes semánticos |
| ❌ Markup repetitivo | ✅ Estructura limpia |
| ❌ Difícil de mantener | ✅ BEM + CSS vars |
| ❌ No theme-aware | ✅ Se adapta a Dark/Light |

### Componentes Disponibles

1. **`.metric-card`** - Tarjetas de métricas con icono
2. **`.empty-state`** - Estados vacíos para tablas/listas
3. **`.chart-container`** - Contenedores para gráficos Chart.js
4. **`.card-grid`** - Grid responsivo para cards

---

## 📏 Componente: Metric Cards

### Estructura BEM

```html
<div class="metric-card">
    <div class="metric-card__icon bg-primary">
        <i class="fas fa-wallet"></i>
    </div>
    <div class="metric-card__content">
        <span class="metric-card__label">Total Balance</span>
        <span class="metric-card__value">$125,450.00</span>
        <small style="font-size: 0.75rem; margin-top: 4px; display: block;">
            +12.5% from last month
        </small>
    </div>
</div>
```

### Elementos del Componente

| Clase | Descripción | Uso |
|-------|-------------|-----|
| `.metric-card` | Contenedor principal | Block |
| `.metric-card__icon` | Icono decorativo | Element |
| `.metric-card__content` | Contenedor de texto | Element |
| `.metric-card__label` | Etiqueta descriptiva | Element |
| `.metric-card__value` | Valor principal | Element |

### Modificadores de Icono

Usa clases utility para el color del icono:

```html
<!-- Azul (Primary) -->
<div class="metric-card__icon bg-primary">
    <i class="fas fa-wallet"></i>
</div>

<!-- Verde (Success) -->
<div class="metric-card__icon bg-success">
    <i class="fas fa-chart-line"></i>
</div>

<!-- Celeste (Info) -->
<div class="metric-card__icon bg-info">
    <i class="fas fa-trophy"></i>
</div>

<!-- Amarillo (Warning) -->
<div class="metric-card__icon bg-warning">
    <i class="fas fa-exclamation-triangle"></i>
</div>

<!-- Rojo (Danger) -->
<div class="metric-card__icon bg-danger">
    <i class="fas fa-times-circle"></i>
</div>
```

### Ejemplo Completo: Dashboard con 4 Métricas

```html
<div class="card-grid mb-4">
    <!-- Metric 1: Total Balance -->
    <div class="metric-card">
        <div class="metric-card__icon bg-primary">
            <i class="fas fa-wallet"></i>
        </div>
        <div class="metric-card__content">
            <span class="metric-card__label">Total Balance</span>
            <span class="metric-card__value" id="total-balance">€0.00</span>
            <small class="text-success" style="font-size: 0.75rem; margin-top: 4px; display: block;">
                +15.3%
            </small>
        </div>
    </div>

    <!-- Metric 2: Daily P&L -->
    <div class="metric-card">
        <div class="metric-card__icon bg-success">
            <i class="fas fa-chart-line"></i>
        </div>
        <div class="metric-card__content">
            <span class="metric-card__label">Daily P&L</span>
            <span class="metric-card__value" id="daily-pnl">€1,234.56</span>
            <small style="font-size: 0.75rem; margin-top: 4px; display: block;">
                12 trades today
            </small>
        </div>
    </div>

    <!-- Metric 3: Win Rate -->
    <div class="metric-card">
        <div class="metric-card__icon bg-info">
            <i class="fas fa-trophy"></i>
        </div>
        <div class="metric-card__content">
            <span class="metric-card__label">Win Rate</span>
            <span class="metric-card__value">72.5%</span>
            <small class="text-muted" style="font-size: 0.75rem; margin-top: 4px; display: block;">
                248 total trades
            </small>
        </div>
    </div>

    <!-- Metric 4: Active Positions -->
    <div class="metric-card">
        <div class="metric-card__icon bg-warning">
            <i class="fas fa-layer-group"></i>
        </div>
        <div class="metric-card__content">
            <span class="metric-card__label">Open Positions</span>
            <span class="metric-card__value">5</span>
            <small style="font-size: 0.75rem; margin-top: 4px; display: block;">
                3 profitable
            </small>
        </div>
    </div>
</div>
```

### CSS Interno del Componente

```css
/* Definido en main.css */
.metric-card {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    padding: var(--spacing-lg);
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    transition: all var(--transition-fast);
}

.metric-card:hover {
    background: var(--bg-card-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.metric-card__icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-md);
    font-size: 1.25rem;
    flex-shrink: 0;
}

.metric-card__content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    flex: 1;
}

.metric-card__label {
    font-size: var(--font-size-sm);
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-card__value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-heading);
    line-height: 1;
}
```

---

## 📋 Componente: Empty States

### Estructura BEM

```html
<div class="empty-state">
    <i class="empty-state__icon fas fa-inbox"></i>
    <div class="empty-state__title">No Data Available</div>
    <div class="empty-state__description">
        Your data will appear here once it's available
    </div>
</div>
```

### Elementos del Componente

| Clase | Descripción | Uso |
|-------|-------------|-----|
| `.empty-state` | Contenedor principal | Block |
| `.empty-state__icon` | Icono grande | Element |
| `.empty-state__title` | Título principal | Element |
| `.empty-state__description` | Descripción secundaria | Element |

### Ejemplo: Tabla Sin Datos

```html
<div class="card">
    <div class="card-header">
        <div class="card-header__title">
            <h5>Open Positions</h5>
        </div>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover" id="positions-table" style="display: none;">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Side</th>
                        <th>P&L</th>
                    </tr>
                </thead>
                <tbody id="positions-body"></tbody>
            </table>
        </div>
        
        <!-- Empty State (visible cuando no hay datos) -->
        <div id="no-positions" class="empty-state">
            <i class="empty-state__icon fas fa-layer-group"></i>
            <div class="empty-state__title">No Open Positions</div>
            <div class="empty-state__description">
                Your active trades will appear here
            </div>
        </div>
    </div>
</div>
```

### JavaScript para Toggle

```javascript
function updatePositionsTable(positions) {
    const tbody = document.getElementById('positions-body');
    const noPositions = document.getElementById('no-positions');
    const table = document.getElementById('positions-table');
    
    if (positions.length === 0) {
        // Mostrar empty state
        table.style.display = 'none';
        noPositions.style.display = 'flex';
    } else {
        // Mostrar tabla con datos
        table.style.display = 'table';
        noPositions.style.display = 'none';
        
        tbody.innerHTML = positions.map(pos => `
            <tr>
                <td>${pos.symbol}</td>
                <td>${pos.side}</td>
                <td>${pos.pnl}</td>
            </tr>
        `).join('');
    }
}
```

### Variaciones de Iconos

```html
<!-- Sin posiciones -->
<i class="empty-state__icon fas fa-layer-group"></i>

<!-- Sin trades -->
<i class="empty-state__icon fas fa-history"></i>

<!-- Sin datos -->
<i class="empty-state__icon fas fa-inbox"></i>

<!-- Sin resultados de búsqueda -->
<i class="empty-state__icon fas fa-search"></i>

<!-- Sin archivos -->
<i class="empty-state__icon fas fa-folder-open"></i>
```

### CSS Interno del Componente

```css
/* Definido en main.css */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-3xl) var(--spacing-xl);
    min-height: 240px;
    text-align: center;
}

.empty-state__icon {
    font-size: 4rem;
    color: var(--text-muted);
    opacity: 0.4;
    margin-bottom: var(--spacing-lg);
}

.empty-state__title {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-sm);
}

.empty-state__description {
    font-size: var(--font-size-sm);
    color: var(--text-muted);
    max-width: 400px;
}
```

---

## 📊 Componente: Chart Containers

### Estructura BEM

```html
<div class="card">
    <div class="card-header">
        <div class="card-header__title">
            <h5>Portfolio Performance</h5>
        </div>
    </div>
    <div class="card-body">
        <div class="chart-container">
            <canvas id="my-chart"></canvas>
        </div>
    </div>
</div>
```

### Con Altura Personalizada

```html
<!-- Altura fija de 300px -->
<div class="chart-container" style="height: 300px;">
    <canvas id="performance-chart"></canvas>
</div>

<!-- Altura fija de 400px -->
<div class="chart-container" style="height: 400px;">
    <canvas id="large-chart"></canvas>
</div>
```

### Ejemplo: Gráfico de Líneas con ThemeManager

```html
<div class="card">
    <div class="card-header">
        <div class="card-header__title">
            <h5>Revenue Trend</h5>
        </div>
    </div>
    <div class="card-body">
        <div class="chart-container" style="height: 350px;">
            <canvas id="revenue-chart"></canvas>
        </div>
    </div>
</div>

<script>
const colors = ThemeManager.getChartColors();
const config = ThemeManager.getChartDefaults('line');

config.data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
        label: 'Revenue',
        data: [1200, 1900, 1500, 2200, 2500],
        borderColor: colors.primary,
        backgroundColor: `${colors.primary}20`,
        fill: true
    }]
};

const revenueChart = new Chart(
    document.getElementById('revenue-chart'),
    config
);
</script>
```

### CSS Interno del Componente

```css
/* Definido en main.css */
.chart-container {
    position: relative;
    width: 100%;
    height: auto;
    min-height: 200px;
}

.chart-container canvas {
    max-width: 100%;
    height: auto !important;
}
```

---

## 🔄 Migración desde Bootstrap

### Caso 1: Cards de Métricas

**❌ ANTES (Bootstrap Only):**
```html
<div class="col-md-3">
    <div class="card">
        <div class="card-body">
            <h6 class="text-muted mb-2">Total Balance</h6>
            <h3 class="mb-1" id="total-balance">$0.00</h3>
            <small class="text-success">+12.5%</small>
        </div>
    </div>
</div>
```

**Problemas:**
- ❌ No hay separación visual clara
- ❌ Sin icono semántico
- ❌ Estilos genéricos
- ❌ No sigue BEM

**✅ AHORA (CSS v4.0):**
```html
<div class="metric-card">
    <div class="metric-card__icon bg-primary">
        <i class="fas fa-wallet"></i>
    </div>
    <div class="metric-card__content">
        <span class="metric-card__label">Total Balance</span>
        <span class="metric-card__value" id="total-balance">$0.00</span>
        <small class="text-success" style="font-size: 0.75rem; margin-top: 4px; display: block;">+12.5%</small>
    </div>
</div>
```

**Beneficios:**
- ✅ Icono decorativo con color semántico
- ✅ Estructura BEM clara
- ✅ Hover effect profesional
- ✅ Se adapta a Dark/Light mode

---

### Caso 2: Tablas Vacías

**❌ ANTES (Bootstrap Only):**
```html
<tbody id="positions-body">
    <tr>
        <td colspan="6" class="text-center text-muted">
            No open positions
        </td>
    </tr>
</tbody>
```

**Problemas:**
- ❌ Solo texto, sin visual impact
- ❌ No hay jerarquía visual
- ❌ Poco profesional

**✅ AHORA (CSS v4.0):**
```html
<div id="no-positions" class="empty-state">
    <i class="empty-state__icon fas fa-inbox"></i>
    <div class="empty-state__title">No Open Positions</div>
    <div class="empty-state__description">
        Your active trades will appear here
    </div>
</div>
```

**Beneficios:**
- ✅ Icono grande para impacto visual
- ✅ Título + descripción para claridad
- ✅ Centro visual bien definido
- ✅ Profesional y moderno

---

### Caso 3: Gráficos

**❌ ANTES:**
```html
<div class="card-body">
    <canvas id="my-chart" height="300"></canvas>
</div>
```

**Problemas:**
- ❌ Sin contenedor semántico
- ❌ Altura hardcodeada en canvas
- ❌ No responsivo

**✅ AHORA (CSS v4.0):**
```html
<div class="card-body">
    <div class="chart-container" style="height: 300px;">
        <canvas id="my-chart"></canvas>
    </div>
</div>
```

**Beneficios:**
- ✅ Contenedor semántico `.chart-container`
- ✅ Altura controlada por CSS
- ✅ Totalmente responsivo

---

## ✅ Best Practices

### 1. **Usar `.card-grid` para Métricas**

✅ **BIEN:**
```html
<div class="card-grid mb-4">
    <div class="metric-card">...</div>
    <div class="metric-card">...</div>
    <div class="metric-card">...</div>
    <div class="metric-card">...</div>
</div>
```

❌ **MAL:**
```html
<div class="row mb-4 g-3">
    <div class="col-md-3">
        <div class="metric-card">...</div>
    </div>
    <!-- Repetir col-md-3 es verboso -->
</div>
```

**Por qué:** `.card-grid` usa CSS Grid con auto-fit responsivo. No necesitas columnas Bootstrap.

---

### 2. **Siempre Usar Iconos Semánticos**

✅ **BIEN:**
```html
<!-- Balance = Wallet -->
<div class="metric-card__icon bg-primary">
    <i class="fas fa-wallet"></i>
</div>

<!-- P&L = Chart Line -->
<div class="metric-card__icon bg-success">
    <i class="fas fa-chart-line"></i>
</div>

<!-- Win Rate = Trophy -->
<div class="metric-card__icon bg-info">
    <i class="fas fa-trophy"></i>
</div>
```

❌ **MAL:**
```html
<!-- Todos con el mismo icono genérico -->
<div class="metric-card__icon bg-primary">
    <i class="fas fa-circle"></i>
</div>
```

---

### 3. **Toggle Entre Tabla y Empty State**

Siempre incluir lógica JavaScript para mostrar/ocultar:

```javascript
function updateTable(data) {
    const table = document.getElementById('my-table');
    const emptyState = document.getElementById('empty-state');
    
    if (data.length === 0) {
        table.style.display = 'none';
        emptyState.style.display = 'flex'; // flexbox para centrado
    } else {
        table.style.display = 'table';
        emptyState.style.display = 'none';
        // Renderizar datos...
    }
}
```

---

### 4. **Combinar con ThemeManager para Charts**

Siempre usar `ThemeManager` en gráficos dentro de `.chart-container`:

```html
<div class="chart-container">
    <canvas id="my-chart"></canvas>
</div>

<script>
const colors = ThemeManager.getChartColors();
const config = ThemeManager.getChartDefaults('line');

config.data = { /* tus datos */ };

new Chart(document.getElementById('my-chart'), config);
</script>
```

**Ver documentación completa:** [`docs/THEME_SYSTEM.md`](./THEME_SYSTEM.md)

---

## 🔗 Integración con ThemeManager

### Componentes que Responden a Tema

Todos los componentes CSS v4.0 usan variables CSS que se adaptan automáticamente:

```css
/* En main.css */
.metric-card {
    background: var(--bg-card);      /* Cambia con tema */
    border: 1px solid var(--border-color); /* Cambia con tema */
}

.metric-card__label {
    color: var(--text-muted);        /* Cambia con tema */
}

.metric-card__value {
    color: var(--text-heading);      /* Cambia con tema */
}

.empty-state__icon {
    color: var(--text-muted);        /* Cambia con tema */
}
```

### Evento `themechange`

Si necesitas re-renderizar componentes al cambiar tema:

```javascript
window.addEventListener('themechange', function(e) {
    console.log('New theme:', e.detail.theme);
    
    // Re-renderizar charts con nuevos colores
    updateAllCharts();
});
```

---

## 📞 Soporte y Contacto

**Autor:** Juan Carlos Garcia Arriero  
**Email:** juanca755@hotmail.com  
**Repositorio:** [BotV2 GitHub](https://github.com/juankaspain/BotV2)

**Documentación Relacionada:**
- [ThemeManager API](./THEME_SYSTEM.md)
- [CSS Variables Reference](./THEME_SYSTEM.md#variables-css-disponibles)

---

## 📄 Licencia

Este código es parte del proyecto BotV2 - Dashboard de Trading Personal.
© 2026 Juan Carlos Garcia Arriero. Todos los derechos reservados.
