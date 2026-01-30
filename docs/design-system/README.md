# 🎨 BotV2 Design System

> Guía completa de estilos y componentes para el Dashboard de Trading BotV2

## 📋 Tabla de Contenidos

- [Tokens de Diseño](#tokens-de-diseño)
- [Colores](#colores)
- [Tipografía](#tipografía)
- [Espaciado](#espaciado)
- [Componentes](#componentes)
- [Microinteracciones](#microinteracciones)
- [Accesibilidad](#accesibilidad)

---

## 🎯 Tokens de Diseño

### Colores Semánticos

| Token | Light Mode | Dark Mode | Uso |
|-------|------------|-----------|-----|
| `--color-primary` | `#3b82f6` | `#60a5fa` | Acciones principales, links |
| `--color-success` | `#10b981` | `#34d399` | Profit, operaciones exitosas |
| `--color-danger` | `#ef4444` | `#f87171` | Loss, errores, alertas críticas |
| `--color-warning` | `#f59e0b` | `#fbbf24` | Advertencias, precaución |
| `--color-info` | `#06b6d4` | `#22d3ee` | Información neutral |

### Escala de Colores (50-950)

```css
/* Primary Scale */
--primary-50: #eff6ff;
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;
--primary-600: #2563eb;
--primary-700: #1d4ed8;
--primary-800: #1e40af;
--primary-900: #1e3a8a;
--primary-950: #172554;
```

---

## 📝 Tipografía

### Font Family

```css
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### Escala Tipográfica (Fluid)

| Token | Min | Max | Uso |
|-------|-----|-----|-----|
| `--text-xs` | 0.75rem | 0.75rem | Labels pequeños |
| `--text-sm` | 0.875rem | 0.875rem | Texto secundario |
| `--text-base` | 1rem | 1rem | Texto body |
| `--text-lg` | 1.125rem | 1.25rem | Subtítulos |
| `--text-xl` | 1.25rem | 1.5rem | Títulos sección |
| `--text-2xl` | 1.5rem | 2rem | Títulos página |
| `--text-3xl` | 1.875rem | 2.5rem | Headers grandes |

### Line Heights

```css
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

---

## 📏 Espaciado

### Sistema de 4px Base

| Token | Valor | Uso |
|-------|-------|-----|
| `--space-1` | 0.25rem (4px) | Micro espaciado |
| `--space-2` | 0.5rem (8px) | Padding interno |
| `--space-3` | 0.75rem (12px) | Gap pequeño |
| `--space-4` | 1rem (16px) | Padding estándar |
| `--space-6` | 1.5rem (24px) | Secciones |
| `--space-8` | 2rem (32px) | Cards |
| `--space-12` | 3rem (48px) | Layouts |
| `--space-16` | 4rem (64px) | Separadores grandes |

---

## 🧩 Componentes

Ver documentación detallada en:
- [StatCard](./components/stat-card.md)
- [DataTable](./components/data-table.md)
- [Toast](./components/toast.md)
- [Modal](./components/modal.md)
- [Button](./components/button.md)

---

## ✨ Microinteracciones

### Hover States

```css
/* Card Lift */
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Button Scale */
.btn:hover {
  transform: scale(1.02);
}

/* Link Underline */
.link:hover {
  text-decoration-color: currentColor;
}
```

### Animaciones de Carga

```css
/* Skeleton Shimmer */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

### Transiciones

```css
--transition-fast: 150ms ease;
--transition-base: 200ms ease;
--transition-slow: 300ms ease;
--transition-bounce: 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

---

## ♿ Accesibilidad

### Focus States

```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Contraste Mínimo

- Texto normal: ratio 4.5:1
- Texto grande: ratio 3:1
- Componentes UI: ratio 3:1

---

## 🌐 Internacionalización

### Soporte RTL

```css
[dir="rtl"] {
  --direction: rtl;
}

.text-start { text-align: start; }
.text-end { text-align: end; }
.ms-auto { margin-inline-start: auto; }
.me-auto { margin-inline-end: auto; }
```

### Text Overflow

```css
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

---

## 📦 Instalación

```bash
# Los estilos están incluidos en dashboard/static/css/main.css
# No requiere instalación adicional
```

## 🔗 Referencias

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Logical Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Logical_Properties)
- [Reduced Motion](https://web.dev/prefers-reduced-motion/)

---

*Design System v1.0 - BotV2 Dashboard*
*Última actualización: Enero 2026*
