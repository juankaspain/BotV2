# 🎨 ThemeManager v2.0 - Guía de Uso Completa

**Dashboard BotV2** | Autor: Juan Carlos Garcia Arriero | Fecha: 30 Enero 2026

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [API Completa](#api-completa)
3. [Uso en Charts (Chart.js)](#uso-en-charts-chartjs)
4. [Variables CSS Disponibles](#variables-css-disponibles)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Best Practices](#best-practices)
7. [Migración desde Colores Hardcodeados](#migración-desde-colores-hardcodeados)

---

## 🎯 Introducción

`ThemeManager` es el sistema centralizado para gestionar temas (Dark/Light) y colores dinámicos en el dashboard. **Versión 2.0** añade soporte completo para obtener variables CSS dinámicamente, ideal para integrar con Chart.js y otros componentes visuales.

### Características Principales

- ✅ **Gestión de temas Dark/Light** con persistencia en localStorage
- ✅ **Detección automática** de preferencias del sistema
- ✅ **Colores dinámicos** para Chart.js que se adaptan al tema
- ✅ **Configuración predeterminada** de Chart.js reutilizable
- ✅ **Eventos de cambio de tema** para componentes reactivos
- ✅ **Acceso a todas las CSS custom properties**

### Carga Automática

`ThemeManager` se carga automáticamente en `base.html` y está disponible globalmente:

```html
<!-- En base.html -->
<script src="{{ url_for('static', filename='js/theme.js') }}"></script>
```

---

## 📚 API Completa

### Métodos Originales (v1.0)

#### `ThemeManager.getTheme()`
Obtiene el tema actual.

```javascript
const currentTheme = ThemeManager.getTheme();
console.log(currentTheme); // 'dark' o 'light'
```

#### `ThemeManager.setTheme(theme)`
Establece un tema específico.

```javascript
ThemeManager.setTheme('light'); // Cambia a Light mode
ThemeManager.setTheme('dark');  // Cambia a Dark mode
```

#### `ThemeManager.toggle()`
Alterna entre Dark y Light mode.

```javascript
const newTheme = ThemeManager.toggle();
console.log(newTheme); // 'light' o 'dark'
```

---

### Nuevos Métodos (v2.0)

#### `ThemeManager.getCSSVariable(varName)`
Obtiene el valor de una variable CSS.

**Parámetros:**
- `varName` (string): Nombre de la variable CSS (con o sin `--`)

**Retorna:** `string` - Valor computado de la variable

**Ejemplo:**
```javascript
const primaryColor = ThemeManager.getCSSVariable('--color-primary');
console.log(primaryColor); // '#5b8def' (dark) o '#4e73df' (light)

// También funciona sin '--'
const textColor = ThemeManager.getCSSVariable('text-primary');
```

---

#### `ThemeManager.getChartColors()`
Obtiene un objeto con todos los colores del tema actual, optimizado para Chart.js.

**Retorna:** `Object` con las siguientes propiedades:

```javascript
const colors = ThemeManager.getChartColors();

// Colores semánticos principales
colors.primary        // Color primario
colors.primaryDark    // Variante oscura
colors.primaryLight   // Variante clara

colors.success        // Verde (éxito)
colors.warning        // Amarillo/Naranja (advertencia)
colors.danger         // Rojo (error/peligro)
colors.info           // Azul claro (información)

// Colores de texto
colors.textPrimary    // Texto principal
colors.textSecondary  // Texto secundario
colors.textMuted      // Texto atenuado

// Colores de fondo
colors.bgCard         // Fondo de tarjetas
colors.bgCardHover    // Fondo hover

// Colores de borde
colors.borderColor    // Borde estándar
colors.borderColorLight // Borde claro

// Paleta para gráficos circulares/barras
colors.palette        // Array de 7 colores principales
```

**Ejemplo de uso:**
```javascript
const colors = ThemeManager.getChartColors();

// Para gráfico de dona/pie
backgroundColor: colors.palette,

// Para líneas individuales
borderColor: colors.primary,
backgroundColor: colors.primaryLight,

// Para texto en gráficos
color: colors.textPrimary
```

---

#### `ThemeManager.getChartDefaults(type)`
Obtiene una configuración base de Chart.js con estilos del tema actual.

**Parámetros:**
- `type` (string): Tipo de gráfico - `'line'`, `'bar'`, `'doughnut'`, `'pie'`, etc.

**Retorna:** `Object` - Configuración completa de Chart.js

**Ejemplo:**
```javascript
const ctx = document.getElementById('myChart');
const config = ThemeManager.getChartDefaults('line');

// Añade tus datos
config.data = {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
        label: 'Ventas',
        data: [12, 19, 3],
        borderColor: ThemeManager.getChartColors().primary
    }]
};

new Chart(ctx, config);
```

**La configuración incluye:**
- ✅ Responsive y aspect ratio configurado
- ✅ Leyenda con estilos del tema
- ✅ Tooltips con colores del tema
- ✅ Ejes X/Y con colores de grid/texto del tema (para line/bar)
- ✅ Fuente Inter para consistencia

---

## 📊 Uso en Charts (Chart.js)

### Ejemplo 1: Gráfico de Dona (Doughnut) - Portfolio

**❌ ANTES (Colores Hardcodeados):**
```javascript
new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['BTC', 'ETH', 'SOL'],
        datasets: [{
            data: [45, 30, 25],
            backgroundColor: [
                '#5865f2', // ❌ No cambia con el tema
                '#57f287',
                '#fee75c'
            ]
        }]
    },
    options: {
        plugins: {
            legend: {
                labels: {
                    color: '#e4e6eb' // ❌ Solo funciona en dark
                }
            }
        }
    }
});
```

**✅ AHORA (Theme-Aware):**
```javascript
const colors = ThemeManager.getChartColors();
const config = ThemeManager.getChartDefaults('doughnut');

config.data = {
    labels: ['BTC', 'ETH', 'SOL'],
    datasets: [{
        data: [45, 30, 25],
        backgroundColor: colors.palette // ✅ Se adapta al tema
    }]
};

new Chart(ctx, config);
```

**Resultado:**
- 🌙 **Dark mode**: Colores vibrantes optimizados
- ☀️ **Light mode**: Colores ajustados automáticamente
- 🎨 **Sin código duplicado**: Reutiliza `getChartDefaults()`

---

### Ejemplo 2: Gráfico de Línea - Performance

```javascript
const colors = ThemeManager.getChartColors();
const config = ThemeManager.getChartDefaults('line');

config.data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [{
        label: 'Revenue',
        data: [120, 190, 150, 200],
        borderColor: colors.primary,
        backgroundColor: `${colors.primary}20`, // 20 = 12.5% opacity
        fill: true,
        tension: 0.4
    }, {
        label: 'Costs',
        data: [80, 100, 90, 110],
        borderColor: colors.danger,
        backgroundColor: `${colors.danger}20`,
        fill: true,
        tension: 0.4
    }]
};

// Personalizar tooltip
config.options.plugins.tooltip.callbacks = {
    label: function(context) {
        return `${context.dataset.label}: $${context.parsed.y}`;
    }
};

const myChart = new Chart(ctx, config);
```

---

### Ejemplo 3: Actualizar Chart al Cambiar Tema

```javascript
let myChart = null;

function renderChart(data) {
    const colors = ThemeManager.getChartColors();
    const config = ThemeManager.getChartDefaults('bar');
    
    config.data = {
        labels: data.labels,
        datasets: [{
            label: 'Trades',
            data: data.values,
            backgroundColor: colors.palette
        }]
    };
    
    // Destruir chart anterior si existe
    if (myChart) {
        myChart.destroy();
    }
    
    myChart = new Chart(ctx, config);
}

// Renderizar al cargar
renderChart(myData);

// Re-renderizar al cambiar tema
window.addEventListener('themechange', function(e) {
    console.log('Theme changed to:', e.detail.theme);
    renderChart(myData); // Re-crea con nuevos colores
});
```

---

## 🎨 Variables CSS Disponibles

### Colores Semánticos

| Variable CSS | Descripción | Dark | Light |
|--------------|-------------|------|-------|
| `--color-primary` | Azul primario | `#5b8def` | `#4e73df` |
| `--color-success` | Verde éxito | `#3dd68c` | `#17a770` |
| `--color-warning` | Amarillo advertencia | `#ffb020` | `#f5a623` |
| `--color-danger` | Rojo peligro | `#ff5757` | `#e63946` |
| `--color-info` | Azul información | `#4fc3f7` | `#2ba3d4` |

### Colores de Texto

| Variable CSS | Descripción | Dark | Light |
|--------------|-------------|------|-------|
| `--text-primary` | Texto principal | `#e6edf3` | `#1a202c` |
| `--text-secondary` | Texto secundario | `#c9d1d9` | `#475569` |
| `--text-muted` | Texto atenuado | `#a8b1bd` | `#64748b` |
| `--text-heading` | Encabezados | `#f0f6fc` | `#0f172a` |

### Colores de Fondo

| Variable CSS | Descripción | Dark | Light |
|--------------|-------------|------|-------|
| `--bg-body` | Fondo body | `#0d1117` | `#f8fafc` |
| `--bg-sidebar` | Fondo sidebar | `#161b22` | `#ffffff` |
| `--bg-card` | Fondo cards | `#1c2128` | `#ffffff` |
| `--bg-card-hover` | Hover cards | `#22272e` | `#f1f5f9` |

### Colores de Borde

| Variable CSS | Descripción | Dark | Light |
|--------------|-------------|------|-------|
| `--border-color` | Borde estándar | `#30363d` | `#e2e8f0` |
| `--border-color-light` | Borde claro | `#424a53` | `#cbd5e1` |

---

## 💡 Ejemplos Prácticos

### Caso 1: Badge con Color Dinámico

```javascript
const colors = ThemeManager.getChartColors();

function createBadge(status) {
    const badge = document.createElement('span');
    badge.className = 'badge';
    
    switch(status) {
        case 'active':
            badge.style.backgroundColor = colors.success;
            badge.textContent = 'Active';
            break;
        case 'pending':
            badge.style.backgroundColor = colors.warning;
            badge.textContent = 'Pending';
            break;
        case 'error':
            badge.style.backgroundColor = colors.danger;
            badge.textContent = 'Error';
            break;
    }
    
    return badge;
}
```

### Caso 2: Progress Bar con Color Dinámico

```javascript
const colors = ThemeManager.getChartColors();
const progressBar = document.querySelector('.progress-bar');

const percentage = 75;
progressBar.style.width = `${percentage}%`;

if (percentage >= 80) {
    progressBar.style.backgroundColor = colors.success;
} else if (percentage >= 50) {
    progressBar.style.backgroundColor = colors.warning;
} else {
    progressBar.style.backgroundColor = colors.danger;
}
```

### Caso 3: Custom Chart Plugin con Tema

```javascript
const gradientPlugin = {
    id: 'gradientBackground',
    beforeDraw: (chart) => {
        const colors = ThemeManager.getChartColors();
        const ctx = chart.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, chart.height);
        
        gradient.addColorStop(0, `${colors.primary}40`);
        gradient.addColorStop(1, `${colors.primary}00`);
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, chart.width, chart.height);
    }
};

Chart.register(gradientPlugin);
```

---

## ✅ Best Practices

### 1. **NUNCA Hardcodear Colores**

❌ **MAL:**
```javascript
backgroundColor: '#5865f2'
color: '#e4e6eb'
```

✅ **BIEN:**
```javascript
const colors = ThemeManager.getChartColors();
backgroundColor: colors.primary
color: colors.textPrimary
```

### 2. **Usar `getChartDefaults()` Siempre que Sea Posible**

Evita repetir configuración de Chart.js. Usa la base y personaliza solo lo necesario.

✅ **BIEN:**
```javascript
const config = ThemeManager.getChartDefaults('line');
config.data = { /* tus datos */ };
config.options.scales.y.beginAtZero = true; // Solo personaliza lo específico
```

### 3. **Escuchar Evento `themechange`**

Para componentes que deben actualizarse al cambiar tema:

```javascript
window.addEventListener('themechange', function(event) {
    console.log('New theme:', event.detail.theme);
    updateMyComponent();
});
```

### 4. **Usar Opacidad con Colores Hex**

Para transparencias, añade sufijo hex:

```javascript
const colors = ThemeManager.getChartColors();

// 50% opacity
backgroundColor: `${colors.primary}80` // 80 en hex = 50%

// 25% opacity
backgroundColor: `${colors.primary}40` // 40 en hex = 25%

// 10% opacity
backgroundColor: `${colors.primary}1A` // 1A en hex = 10%
```

---

## 🔄 Migración desde Colores Hardcodeados

### Paso 1: Identificar Colores Hardcodeados

Busca en tu código:
- `'#XXXXXX'` (hex colors)
- `'rgb(X, Y, Z)'`
- `'rgba(X, Y, Z, A)'`

### Paso 2: Mapear a Variables CSS

| Color Hardcoded | Variable CSS |
|-----------------|-------------|
| `#5865f2`, `#4e73df` | `colors.primary` |
| `#57f287`, `#3dd68c` | `colors.success` |
| `#fee75c`, `#ffb020` | `colors.warning` |
| `#ff5757`, `#ed4245` | `colors.danger` |
| `#e4e6eb`, `#c9d1d9` | `colors.textPrimary` |
| `#0d1117`, `#1c2128` | `colors.bgCard` |

### Paso 3: Actualizar Código

**ANTES:**
```javascript
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        datasets: [{
            backgroundColor: ['#5865f2', '#57f287', '#fee75c']
        }]
    },
    options: {
        plugins: {
            legend: {
                labels: { color: '#e4e6eb' }
            }
        }
    }
});
```

**DESPUÉS:**
```javascript
const colors = ThemeManager.getChartColors();
const config = ThemeManager.getChartDefaults('bar');

config.data = {
    datasets: [{
        backgroundColor: colors.palette
    }]
};

const myChart = new Chart(ctx, config);
```

### Paso 4: Añadir Listener de Tema (Opcional)

Si el componente debe actualizarse al cambiar tema:

```javascript
window.addEventListener('themechange', () => {
    myChart.destroy();
    renderChart(); // Re-crea con nuevos colores
});
```

---

## 📞 Soporte y Contacto

**Autor:** Juan Carlos Garcia Arriero  
**Email:** juanca755@hotmail.com  
**Repositorio:** [BotV2 GitHub](https://github.com/juankaspain/BotV2)

**Issues relacionados:**
- [CSS Inconsistency Audit](https://github.com/juankaspain/BotV2/issues/XX)
- [Theme-aware Charts Implementation](https://github.com/juankaspain/BotV2/issues/YY)

---

## 📄 Licencia

Este código es parte del proyecto BotV2 - Dashboard de Trading Personal.
© 2026 Juan Carlos Garcia Arriero. Todos los derechos reservados.
