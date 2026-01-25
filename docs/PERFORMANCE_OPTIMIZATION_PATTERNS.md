# Performance Optimization Patterns - Guía Completa

## ⚡ Versión: 1.0
**Fecha:** 25 Enero 2026  
**Autor:** Juan Carlos Garcia

---

## 📚 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Debounce vs Throttle](#debounce-vs-throttle)
3. [Mutex Lock Pattern](#mutex-lock-pattern)
4. [Section Cache con LRU](#section-cache-con-lru)
5. [Request Deduplication](#request-deduplication)
6. [AbortController Manager](#abortcontroller-manager)
7. [Prefetch Manager](#prefetch-manager)
8. [Lazy Component Loading](#lazy-component-loading)
9. [Performance Monitoring](#performance-monitoring)
10. [Patrones de Integración](#patrones-de-integración)
11. [Best Practices](#best-practices)

---

## 🚀 Introducción

### ¿Por qué necesitamos optimización?

Las aplicaciones web modernas enfrentan desafíos significativos de rendimiento:

- **Event Flooding**: Los usuarios pueden disparar eventos (clicks, typing, scroll) muchísimas más veces de lo necesario
- **Concurrent Loading**: Múltiples cargas simultáneas de la misma sección causan flickering y desperdicio de recursos
- **Redundant Requests**: Peticiones idénticas duplicadas saturan el servidor y la red
- **Memory Leaks**: Secciones no limpiadas correctamente consumen memoria indefinidamente
- **Network Latency**: Cargas secuenciales lentas degradan la UX

### Impacto en UX

Según estudios recientes:
- **53%** de usuarios abandonan sitios que tardan más de **3 segundos** en cargar[web:10]
- Cada **100ms** de mejora en rendimiento puede incrementar conversión en **1%**[web:10]
- El **70%** de usuarios consideran la velocidad como factor decisivo en su experiencia[web:13]

### Módulo Performance Optimizer

El módulo `performance-optimizer.js` proporciona:

✅ **8 patrones de optimización** probados en producción  
✅ **API simple y consistente** fácil de integrar  
✅ **Zero dependencies** - puro JavaScript vanilla  
✅ **Type-safe** con JSDoc completo  
✅ **Production-ready** con manejo robusto de errores

---

## 🔄 Debounce vs Throttle

### ¿Qué es Debounce?

**Debounce** retrasa la ejecución de una función hasta que pasa un tiempo determinado **sin nuevos eventos**[web:11].

#### Cómo funciona

```
User types: J-a-v-a-S-c-r-i-p-t
            │ │ │ │ │ │ │ │ │ │
            └───────────────────┘
                    Wait 500ms
                        ↓
                   API CALL (1x)
```

Sin debounce: **10 llamadas**  
Con debounce: **1 llamada**  
**Ahorro: 90%**

### Implementación

```javascript
const debouncedSearch = PerformanceOptimizer.debounce(
    async (query) => {
        const results = await fetch(`/api/search?q=${query}`);
        displayResults(results);
    },
    500,  // Wait 500ms
    {
        leading: false,   // Don't execute on first call
        trailing: true,   // Execute after delay
        maxWait: 2000    // Force execution after 2s max
    }
);

input.addEventListener('input', (e) => {
    debouncedSearch(e.target.value);
});

// Cancel pending execution
debouncedSearch.cancel();

// Execute immediately
debouncedSearch.flush();
```

### Opciones Avanzadas

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `leading` | boolean | `false` | Ejecutar en el primer evento |
| `trailing` | boolean | `true` | Ejecutar después del delay |
| `maxWait` | number | `null` | Máximo tiempo de espera forzado |

### ¿Qué es Throttle?

**Throttle** limita la ejecución a **una vez por período de tiempo**, sin importar cuántos eventos ocurran[web:11].

#### Cómo funciona

```
User scrolls continuously
  │     │     │     │     │
  ↓     │     ↓     │     ↓
 EXEC   wait   EXEC  wait   EXEC
      (100ms)      (100ms)

API CALL every 100ms
```

Sin throttle: **100+ llamadas/segundo**  
Con throttle (100ms): **10 llamadas/segundo**  
**Ahorro: 90%**

### Implementación

```javascript
const throttledScroll = PerformanceOptimizer.throttle(
    () => {
        const scrollY = window.scrollY;
        updateScrollIndicator(scrollY);
    },
    100,  // Execute max once per 100ms
    {
        leading: true,    // Execute immediately on first scroll
        trailing: false   // Don't execute after scrolling stops
    }
);

window.addEventListener('scroll', throttledScroll);

// Cancel throttled execution
throttledScroll.cancel();
```

### Debounce vs Throttle: ¿Cuándo usar cada uno?

| Escenario | Usar | Razón |
|-----------|------|--------|
| **Search autocomplete** | Debounce | Solo buscar cuando usuario terminó de escribir[web:11] |
| **Form validation** | Debounce | Validar cuando usuario para de escribir |
| **Button clicks** | Debounce | Prevenir double-clicks accidentales |
| **Scroll events** | Throttle | Actualizar UI a intervalos regulares[web:11] |
| **Resize events** | Throttle | Recalcular layout periódicamente |
| **Mousemove tracking** | Throttle | Limitar frecuencia de tracking |
| **API rate limiting** | Throttle | Respetar límites del servidor |

### Comparación Visual

```
EVENTS:    ││││││││││││││││││││  (20 events)
              0s    0.5s    1.0s    1.5s    2.0s

DEBOUNCE:                                   X   (1 execution - at end)
THROTTLE:     X           X           X     X   (4 executions - regular intervals)
NO LIMIT:     XXXXXXXXXXXXXXXXXXXX            (20 executions - every event)
```

---

## 🔒 Mutex Lock Pattern

### Problema: Race Conditions

Cuando un usuario hace click rápido en diferentes secciones:

```javascript
// SIN Mutex Lock - PROBLEMA
function loadSection(section) {
    // User clicks "Portfolio"
    fetchData(section);  // Request 1 starts
    
    // User clicks "Trades" before Portfolio finishes
    fetchData(section);  // Request 2 starts
    
    // Both requests compete, causing:
    // - Flickering UI
    // - Wrong data displayed
    // - Memory leaks
    // - Race conditions
}
```

### Solución: Mutual Exclusion

**Mutex Lock** garantiza que solo **una instancia** de una función se ejecute a la vez[web:5].

### Implementación

```javascript
const loadSectionLock = new PerformanceOptimizer.MutexLock();

async function loadSection(section) {
    // Try to acquire lock (non-blocking)
    const acquired = await loadSectionLock.acquire();
    
    if (!acquired) {
        console.log('⚠️ Section load already in progress');
        return; // Skip this call
    }
    
    try {
        // Only one execution reaches here
        await fetchSectionData(section);
        renderSection(section);
    } catch (error) {
        console.error('Error loading section:', error);
    } finally {
        // ALWAYS release the lock
        loadSectionLock.release();
    }
}
```

### Métodos Disponibles

#### `acquire()` - Non-blocking

```javascript
const acquired = await lock.acquire();
if (acquired) {
    // Lock obtained, proceed
} else {
    // Lock held by another, skip or queue
}
```

#### `waitForLock()` - Blocking

```javascript
// Wait until lock becomes available
await lock.waitForLock();
try {
    // Guaranteed exclusive access
} finally {
    lock.release();
}
```

#### `isLocked()`

```javascript
if (lock.isLocked()) {
    console.log('Operation in progress');
}
```

### Caso de Uso Real: Dashboard

```javascript
// Global lock instance
const sectionLock = PerformanceOptimizer.loadSectionLock;

// Nav link click handler
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', async (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        
        if (!await sectionLock.acquire()) {
            // Show toast: "Please wait..."
            return;
        }
        
        try {
            showLoadingSpinner();
            await loadSection(section);
        } finally {
            hideLoadingSpinner();
            sectionLock.release();
        }
    });
});
```

---

## 💾 Section Cache con LRU

### Problema: Reload Innecesario

Sin caché, cada cambio de sección recarga todo:

```
User: Dashboard → Portfolio → Dashboard → Portfolio
      ↓            ↓            ↓            ↓
    LOAD         LOAD         LOAD         LOAD
   (500ms)      (500ms)      (500ms)      (500ms)
   
Total: 2 seconds wasted!
```

### Solución: LRU Cache

**LRU (Least Recently Used)** mantiene en memoria las secciones más usadas, evitando reloads innecesarios[web:13].

```
User: Dashboard → Portfolio → Dashboard → Portfolio
      ↓            ↓            ↓            ↓
    LOAD         LOAD       CACHE        CACHE
   (500ms)      (500ms)     (10ms)       (10ms)
   
Total: 1.02 seconds (49% faster!)
```

### Características

✅ **Capacity Limit**: Máximo 10 secciones en memoria  
✅ **TTL (Time To Live)**: Expiración automática a los 5 minutos  
✅ **LRU Eviction**: Elimina la sección menos usada cuando el cache está lleno  
✅ **Automatic Refresh**: Actualiza timestamp en cada acceso

### Implementación

```javascript
const cache = PerformanceOptimizer.sectionCache;

async function loadSection(section) {
    // 1. Try cache first
    const cached = cache.get(section);
    if (cached) {
        console.log('💾 Loading from cache:', section);
        renderSection(cached);
        return cached;
    }
    
    // 2. Cache miss - load from server
    console.log('🌐 Loading from server:', section);
    const data = await fetchSectionData(section);
    
    // 3. Store in cache for next time
    cache.set(section, data);
    
    renderSection(data);
    return data;
}
```

### LRU Eviction en Acción

```javascript
const cache = new PerformanceOptimizer.SectionCache(3); // Capacity: 3

cache.set('dashboard', dataDashboard);   // [dashboard]
cache.set('portfolio', dataPortfolio);   // [dashboard, portfolio]
cache.set('trades', dataTrades);         // [dashboard, portfolio, trades]

// Cache is full (3/3)

cache.get('dashboard');  // Access dashboard (moves to end)
                         // [portfolio, trades, dashboard]

cache.set('performance', dataPerformance);
// Evicts least recently used: 'portfolio'
// [trades, dashboard, performance]

cache.get('portfolio');  // Returns null (evicted)
```

### Métodos

#### `get(key)`

```javascript
const data = cache.get('dashboard');
if (data) {
    // Cache HIT - data is fresh
} else {
    // Cache MISS - load from server
}
```

#### `set(key, value)`

```javascript
cache.set('dashboard', {
    metrics: {...},
    charts: {...},
    timestamp: Date.now()
});
```

#### `delete(key)`

```javascript
// Manual invalidation
cache.delete('dashboard');
```

#### `clear()`

```javascript
// Clear entire cache (e.g., on logout)
cache.clear();
```

#### `stats()`

```javascript
const stats = cache.stats();
console.log(stats);
// {
//   size: 7,
//   capacity: 10,
//   keys: ['dashboard', 'portfolio', 'trades', ...]
// }
```

### Cache Invalidation Strategies

#### 1. TTL-based (Automatic)

```javascript
// Cache expires after 5 minutes (default)
const cache = new SectionCache(10, 300000);
```

#### 2. Manual Invalidation

```javascript
// When data changes (e.g., new trade)
function onNewTrade(trade) {
    cache.delete('trades');  // Force reload next time
    cache.delete('dashboard'); // May show stale data
}
```

#### 3. Selective Refresh

```javascript
// Refresh specific sections
async function refreshSection(section) {
    cache.delete(section);
    return await loadSection(section);
}
```

---

## 🔄 Request Deduplication

### Problema: Duplicate Requests

Usuarios impacientes hacen múltiples clicks:

```javascript
// User clicks "Refresh" button 3 times rapidly
button.addEventListener('click', () => {
    fetch('/api/data');  // Request 1
    fetch('/api/data');  // Request 2 (duplicate!)
    fetch('/api/data');  // Request 3 (duplicate!)
});

// Server receives 3 identical requests
// Network congestion
// Wasted bandwidth
// Race conditions on response
```

### Solución: Deduplication

**Request Deduplicator** detecta peticiones idénticas en progreso y las fusiona en una sola[web:7].

### Implementación

```javascript
const deduplicator = PerformanceOptimizer.requestDeduplicator;

async function fetchDashboardData() {
    return deduplicator.execute(
        'dashboard-data',  // Unique key
        async () => {
            // This function runs only once
            // even if called multiple times
            const response = await fetch('/api/dashboard');
            return response.json();
        }
    );
}

// All 3 calls share the same Promise
const promise1 = fetchDashboardData();
const promise2 = fetchDashboardData();  // Deduplicated!
const promise3 = fetchDashboardData();  // Deduplicated!

// All receive the same result
const [data1, data2, data3] = await Promise.all([promise1, promise2, promise3]);
// data1 === data2 === data3  ✅
```

### Logs

```
🚀 Request STARTED: dashboard-data
🔄 Request DEDUPLICATED: dashboard-data
🔄 Request DEDUPLICATED: dashboard-data
✅ Request COMPLETED: dashboard-data
```

**Resultado:** 3 llamadas → 1 request  
**Ahorro:** 67% de requests

### Métodos

#### `execute(key, requestFn)`

```javascript
await deduplicator.execute('users-list', async () => {
    return await fetch('/api/users');
});
```

#### `cancel(key)`

```javascript
// Cancel pending request
deduplicator.cancel('users-list');
```

#### `cancelAll()`

```javascript
// Cancel all pending requests (e.g., on logout)
deduplicator.cancelAll();
```

---

## ❌ AbortController Manager

### Problema: Orphaned Requests

Usuario cambia de sección antes de que termine la carga:

```javascript
// User: Dashboard → waits 100ms → clicks Portfolio

// Request for Dashboard still pending
fetch('/api/dashboard').then(data => {
    // User already left!
    // But we still render Dashboard data
    // Memory leak + wrong UI state
});
```

### Solución: AbortController

**AbortController** cancela requests obsoletos automáticamente[web:7].

### Implementación

```javascript
const abortManager = PerformanceOptimizer.abortManager;

async function loadSection(section) {
    // Create AbortController for this section
    // (automatically aborts previous request for same section)
    const controller = abortManager.create(`section-${section}`);
    
    try {
        const response = await fetch(`/api/sections/${section}`, {
            signal: controller.signal  // Pass signal to fetch
        });
        
        const data = await response.json();
        renderSection(data);
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('❌ Request aborted:', section);
        } else {
            console.error('Fetch error:', error);
        }
    }
}

// User clicks rapidly
loadSection('dashboard');  // Request 1 starts
loadSection('portfolio');  // Request 1 ABORTED, Request 2 starts
loadSection('trades');     // Request 2 ABORTED, Request 3 starts
```

### Logs

```
🚀 Fetch STARTED: section-dashboard
❌ Fetch ABORTED: section-dashboard
🚀 Fetch STARTED: section-portfolio
❌ Fetch ABORTED: section-portfolio
🚀 Fetch STARTED: section-trades
✅ Fetch COMPLETED: section-trades
```

### Métodos

#### `create(key)`

```javascript
const controller = abortManager.create('my-request');
fetch(url, { signal: controller.signal });
```

#### `abort(key)`

```javascript
abortManager.abort('my-request');
```

#### `abortAll()`

```javascript
// Cancel all pending requests
abortManager.abortAll();
```

---

## 🔍 Prefetch Manager

### Predictive Loading

**Prefetch** carga datos en segundo plano durante idle time, anticipándose a las acciones del usuario[web:13].

### Estrategia: Hover Intent

```javascript
const prefetchManager = PerformanceOptimizer.prefetchManager;

// Prefetch on hover (user likely to click)
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('mouseenter', () => {
        const section = link.dataset.section;
        
        // Start prefetching (silent, background)
        prefetchManager.prefetch(
            `section-${section}`,
            () => fetch(`/api/sections/${section}`).then(r => r.json())
        );
    });
    
    link.addEventListener('click', async () => {
        const section = link.dataset.section;
        
        // Check if already prefetched
        const prefetched = prefetchManager.get(`section-${section}`);
        
        if (prefetched) {
            console.log('⚡ Instant load from prefetch!');
            renderSection(prefetched);
        } else {
            // Fallback to normal load
            const data = await fetchSection(section);
            renderSection(data);
        }
    });
});
```

### Resultado

```
Without Prefetch:
  Hover → Click → Fetch (500ms) → Render
                    ^
                    Perceived load time: 500ms

With Prefetch:
  Hover → Prefetch starts (background)
       → Click → Get from cache (10ms) → Render
                  ^
                  Perceived load time: 10ms
  
98% faster!
```

### Métodos

#### `prefetch(key, fetchFn)`

```javascript
await prefetchManager.prefetch('portfolio', async () => {
    return await fetch('/api/portfolio').then(r => r.json());
});
```

#### `get(key, maxAge)`

```javascript
// Get if fresh (default: 5 minutes)
const data = prefetchManager.get('portfolio', 300000);
```

#### `clear()`

```javascript
prefetchManager.clear();
```

---

## 👁️ Lazy Component Loading

### Intersection Observer Pattern

**Lazy Loading** carga componentes solo cuando son visibles en viewport[web:13].

### Implementación

```javascript
const lazyLoader = new PerformanceOptimizer.LazyComponentLoader({
    rootMargin: '100px',  // Load 100px before visible
    threshold: 0.01       // Trigger at 1% visibility
});

// Register heavy components
const chartContainer = document.getElementById('equity-chart');
lazyLoader.observe(chartContainer, () => {
    console.log('👁️ Chart visible, loading Plotly...');
    loadPlotlyChart(chartContainer);
});

const tableContainer = document.getElementById('trades-table');
lazyLoader.observe(tableContainer, () => {
    console.log('👁️ Table visible, loading data...');
    loadTradesTable(tableContainer);
});
```

### Beneficios

- **Faster Initial Load**: Solo carga componentes visibles
- **Reduced Memory**: Componentes offscreen no consumen memoria
- **Better Mobile**: Crucial para conexiones lentas
- **Improved Metrics**: Mejor LCP (Largest Contentful Paint)

---

## 📊 Performance Monitoring

### Tracking Metrics

```javascript
const perfMonitor = PerformanceOptimizer.perfMonitor;

// Measure section load time
perfMonitor.start('load-dashboard');

await loadDashboardSection();

const duration = perfMonitor.end('load-dashboard');
// ⚡ PERF load-dashboard: 342.50ms

// Get statistics
const stats = perfMonitor.getStats('load-dashboard');
console.log(stats);
// {
//   count: 15,
//   avg: 380.5,
//   min: 234.2,
//   max: 892.1
// }
```

---

## 🔗 Patrones de Integración

### Pattern 1: Optimized Section Loader

```javascript
const optimizedLoadSection = PerformanceOptimizer.createOptimizedSectionLoader(
    async (section) => {
        // Your existing load logic
        const data = await fetch(`/api/${section}`);
        return data.json();
    }
);

// Use it
await optimizedLoadSection('dashboard');
// ✅ Auto mutex lock
// ✅ Auto caching
// ✅ Auto performance tracking
```

### Pattern 2: Smart Search

```javascript
const searchAPI = PerformanceOptimizer.debounce(
    async (query) => {
        return PerformanceOptimizer.requestDeduplicator.execute(
            `search-${query}`,
            async () => {
                const controller = PerformanceOptimizer.abortManager.create('search');
                return fetch(`/api/search?q=${query}`, {
                    signal: controller.signal
                });
            }
        );
    },
    300
);
```

---

## ✅ Best Practices

### 1. Always Release Locks

```javascript
// ❌ BAD
if (await lock.acquire()) {
    doWork();
    lock.release();  // Might not execute if doWork() throws
}

// ✅ GOOD
if (await lock.acquire()) {
    try {
        await doWork();
    } finally {
        lock.release();  // Always executes
    }
}
```

### 2. Appropriate Delays

```javascript
// ❌ TOO SHORT
const debounced = debounce(fn, 50);  // Still too many calls

// ❌ TOO LONG
const debounced = debounce(fn, 5000);  // Feels laggy

// ✅ JUST RIGHT
const debounced = debounce(fn, 300);  // Sweet spot
```

### 3. Cache Invalidation

```javascript
// Invalidate on mutations
function createTrade(trade) {
    await api.createTrade(trade);
    
    // Invalidate affected caches
    cache.delete('trades');
    cache.delete('dashboard');
    cache.delete('portfolio');
}
```

### 4. Monitor Performance

```javascript
// Log slow operations
const duration = perfMonitor.end('operation');
if (duration > 1000) {
    console.warn('⚠️ Slow operation detected:', duration);
    // Send to analytics
}
```

---

## 📚 Referencias

- [JavaScript Debounce vs. Throttle](https://www.syncfusion.com/blogs/post/javascript-debounce-vs-throttle) - Syncfusion[web:11]
- [Five Data-Loading Patterns](https://www.smashingmagazine.com/2022/09/data-loading-patterns-improve-frontend-performance/) - Smashing Magazine[web:13]
- [JavaScript Concurrency](https://www.honeybadger.io/blog/javascript-concurrency/) - Honeybadger[web:12]
- [Prevent Concurrent Execution](https://stackoverflow.com/questions/2497930/) - Stack Overflow[web:5]

---

**© 2026 BotV2 - Performance Optimizer v1.0**  
*Juan Carlos Garcia Arriero*
