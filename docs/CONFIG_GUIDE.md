# 📋 Guía Completa de Configuración - BotV2

## Introducción

Este documento explica **cada propiedad** del archivo de configuración `src/config/settings.yaml` de forma clara y comprensible, incluso para personas sin experiencia técnica en trading.

El archivo de configuración es el **centro de control** del bot, donde defines cómo debe comportarse, qué riesgos asumir, y cómo gestionar tu capital.

---

## 🎯 Estructura General

El archivo está organizado en **11 secciones principales**:

1. **System** - Configuración del sistema
2. **Trading** - Parámetros de trading
3. **Risk** - Gestión de riesgo
4. **Execution** - Ejecución de órdenes
5. **Data** - Validación y normalización de datos
6. **Ensemble** - Sistema de votación de estrategias
7. **Strategies** - Estrategias habilitadas
8. **Liquidation Detection** - Detección de cascadas
9. **Monitoring** - Monitoreo y alertas
10. **State Persistence** - Persistencia de estado
11. **Markets** - Mercados y exchanges
12. **Backtesting** - Pruebas históricas
13. **Dashboard** - Panel de control web

---

## 1. System - Configuración del Sistema

### `system.name`
**Valor**: `"BotV2"`  
**Tipo**: Texto  
**Qué hace**: Nombre del sistema para identificación en logs y reportes.

**Cuándo cambiar**: Solo si quieres personalizar el nombre del bot.

---

### `system.version`
**Valor**: `"1.0.0"`  
**Tipo**: Texto  
**Qué hace**: Versión actual del sistema.

**Cuándo cambiar**: Actualiza cuando hagas cambios significativos al código.

**Formato**: `MAJOR.MINOR.PATCH`
- MAJOR: Cambios incompatibles
- MINOR: Nuevas funcionalidades compatibles
- PATCH: Correcciones de bugs

---

### `system.environment`
**Valor**: `"production"` | `"staging"` | `"development"`  
**Tipo**: Texto  
**Qué hace**: Define el entorno de ejecución.

**Opciones**:
- **`production`**: Trading real con dinero real
- **`staging`**: Pruebas finales antes de producción
- **`development`**: Desarrollo y pruebas locales

**Impacto**:
- En `production`: Logs mínimos, máxima eficiencia
- En `development`: Logs detallados (DEBUG), más información

**⚠️ Importante**: Asegúrate de estar en `development` cuando pruebes cambios.

---

### `system.log_level`
**Valor**: `"DEBUG"` | `"INFO"` | `"WARNING"` | `"ERROR"` | `"CRITICAL"`  
**Tipo**: Texto  
**Qué hace**: Controla cuánta información se registra en los logs.

**Niveles de detalle** (de más a menos):

| Nivel | Qué registra | Cuándo usar |
|-------|-------------|-------------|
| **DEBUG** | Todo (cada paso del bot) | Depuración, desarrollo |
| **INFO** | Eventos importantes (trades, señales) | Producción normal |
| **WARNING** | Advertencias (circuit breaker, etc.) | Producción conservadora |
| **ERROR** | Solo errores | No recomendado |
| **CRITICAL** | Solo fallos críticos | No recomendado |

**Recomendado**:
- Desarrollo: `DEBUG`
- Producción: `INFO`
- Trading agresivo: `WARNING`

---

## 2. Trading - Parámetros de Trading

### `trading.initial_capital`
**Valor**: `3000` (EUR)  
**Tipo**: Número  
**Qué hace**: Capital inicial con el que el bot comienza a operar.

**Ejemplo**:
```
initial_capital: 3000  → El bot gestiona 3.000€
initial_capital: 10000 → El bot gestiona 10.000€
```

**⚠️ Importante**: 
- No pongas más de lo que puedes permitirte perder
- El bot operará con este capital + ganancias acumuladas
- Mínimo recomendado: 1.000€ para diversificación

---

### `trading.trading_interval`
**Valor**: `60` (segundos)  
**Tipo**: Número  
**Qué hace**: Cada cuántos segundos el bot busca nuevas oportunidades de trading.

**Ejemplos**:
```
trading_interval: 30  → Revisa cada 30 segundos (más operaciones)
trading_interval: 60  → Revisa cada minuto (recomendado)
trading_interval: 300 → Revisa cada 5 minutos (menos operaciones)
```

**Impacto**:
- **Menor intervalo** (30s):
  - ✅ Más oportunidades
  - ❌ Más comisiones
  - ❌ Mayor carga del sistema
  
- **Mayor intervalo** (300s):
  - ✅ Menos comisiones
  - ✅ Menor carga
  - ❌ Puede perder oportunidades rápidas

**Recomendado**: `60` segundos (balance óptimo)

---

### `trading.max_position_size`
**Valor**: `0.15` (15%)  
**Tipo**: Decimal (0.0 a 1.0)  
**Qué hace**: Máximo porcentaje de tu capital que puedes invertir en una sola operación.

**Ejemplo con capital de 3.000€**:
```
max_position_size: 0.15 → Máximo 450€ por operación
max_position_size: 0.10 → Máximo 300€ por operación
max_position_size: 0.25 → Máximo 750€ por operación
```

**Recomendaciones por perfil**:

| Perfil | Valor | Explicación |
|--------|-------|-------------|
| **Conservador** | 0.05 - 0.10 | Máxima diversificación |
| **Moderado** | 0.10 - 0.15 | Balance (recomendado) |
| **Agresivo** | 0.15 - 0.25 | Más concentración, más riesgo |

**⚠️ Nunca excedas 0.25** (25%) - Es demasiado arriesgado.

---

### `trading.min_position_size`
**Valor**: `0.01` (1%)  
**Tipo**: Decimal  
**Qué hace**: Mínimo porcentaje para una operación. Evita operaciones demasiado pequeñas.

**Razón**: Operaciones muy pequeñas no son rentables por las comisiones.

**Ejemplo con capital de 3.000€**:
```
min_position_size: 0.01 → Mínimo 30€ por operación
```

**No cambies este valor** a menos que tengas un capital muy grande (>50.000€).

---

### `trading.max_open_positions`
**Valor**: `10`  
**Tipo**: Número entero  
**Qué hace**: Número máximo de posiciones abiertas simultáneamente.

**Impacto**:
```
max_open_positions: 5  → Muy concentrado, menos diversificación
max_open_positions: 10 → Balance óptimo (recomendado)
max_open_positions: 20 → Muy diversificado, requiere más capital
```

**Cálculo de capital necesario**:
```
Capital mínimo = max_open_positions × min_position_size × initial_capital

Ejemplo con 10 posiciones y 1% mínimo:
3.000€ × 10 × 0.01 = 300€ por posición mínima
Funciona correctamente ✓
```

**Recomendación**: 
- Capital < 5.000€: `max_open_positions: 5-7`
- Capital 5.000-10.000€: `max_open_positions: 8-10`
- Capital > 10.000€: `max_open_positions: 10-15`

---

## 3. Risk - Gestión de Riesgo

Esta es la sección **MÁS IMPORTANTE**. Protege tu capital de pérdidas catastróficas.

### Circuit Breaker (Disyuntor de Seguridad)

El circuit breaker detiene el trading automáticamente si las pérdidas diarias alcanzan ciertos niveles.

---

#### `risk.circuit_breaker.level_1_drawdown`
**Valor**: `-5.0` (%)  
**Tipo**: Número negativo  
**Qué hace**: Si pierdes 5% en un día, se activa el **Nivel 1** de precaución.

**Acción al activarse**:
- 🟡 Estado: AMARILLO (Precaución)
- Reduce el tamaño de nuevas posiciones al 50%
- Sigue operando pero más conservador

**Ejemplo**:
```
Capital inicial hoy: 3.000€
Pérdida del día: -150€ (-5%)
→ Se activa Nivel 1
→ Nuevas posiciones: máximo 225€ (en vez de 450€)
```

**Cuándo ajustar**:
- Más agresivo: `-7.0` (tolera más pérdidas antes de reducir)
- Más conservador: `-3.0` (reacciona antes)

---

#### `risk.circuit_breaker.level_2_drawdown`
**Valor**: `-10.0` (%)  
**Tipo**: Número negativo  
**Qué hace**: Si pierdes 10% en un día, se activa el **Nivel 2** de alerta.

**Acción al activarse**:
- 🟠 Estado: NARANJA (Alerta)
- Reduce posiciones al 25% del tamaño normal
- Cierra posiciones poco prometedoras

**Ejemplo**:
```
Capital inicial hoy: 3.000€
Pérdida del día: -300€ (-10%)
→ Se activa Nivel 2
→ Nuevas posiciones: máximo 112€ (en vez de 450€)
→ Se consideran cierres anticipados
```

---

#### `risk.circuit_breaker.level_3_drawdown`
**Valor**: `-15.0` (%)  
**Tipo**: Número negativo  
**Qué hace**: Si pierdes 15% en un día, se activa el **Nivel 3** de STOP total.

**Acción al activarse**:
- 🔴 Estado: ROJO (STOP)
- **Detiene TODO el trading inmediatamente**
- Cierra todas las posiciones abiertas
- Pausa el bot durante el tiempo de cooldown

**Ejemplo**:
```
Capital inicial hoy: 3.000€
Pérdida del día: -450€ (-15%)
→ Se activa Nivel 3
→ ⛔ STOP TOTAL
→ Cierre de todas las posiciones
→ Espera 30 minutos antes de reanudar
```

**⚠️ CRÍTICO**: Este es tu último mecanismo de defensa. **No lo pongas más bajo que -20%**.

---

#### `risk.circuit_breaker.cooldown_minutes`
**Valor**: `30` (minutos)  
**Tipo**: Número entero  
**Qué hace**: Tiempo de espera después de activar el Nivel 3 antes de volver a operar.

**Por qué es importante**: 
- Evita que el bot vuelva a entrar inmediatamente después de un mal momento
- Da tiempo para que el mercado se estabilice
- Previene pérdidas emocionales/automáticas en cascada

**Recomendaciones**:
- Mercado volátil (crypto): `30-60` minutos
- Mercado estable (stocks): `15-30` minutos

---

### Gestión de Correlación

#### `risk.correlation_threshold`
**Valor**: `0.7`  
**Tipo**: Decimal (0.0 a 1.0)  
**Qué hace**: Si la correlación de tu portfolio supera este valor, reduce el tamaño de las posiciones.

**¿Qué es correlación?**:
- **0.0**: Activos se mueven independientemente (👍 bueno)
- **0.5**: Se mueven en la misma dirección a veces
- **0.7**: Se mueven juntos frecuentemente (⚠️ riesgo)
- **1.0**: Se mueven idénticamente (❌ muy arriesgado)

**Ejemplo**:
```
Tienes posiciones en:
- Bitcoin
- Ethereum
- Litecoin

Correlación entre ellas: 0.85 (muy alta)
→ Se aplica penalización: reduce tamaños de posición
```

**Por qué importa**: Si todos tus activos caen juntos, pierdes en todos simultáneamente.

**Ajuste**:
- Más estricto: `0.6` (penaliza antes)
- Más relajado: `0.8` (permite más correlación)

**Recomendado**: Dejar en `0.7`

---

#### `risk.max_portfolio_correlation`
**Valor**: `0.4`  
**Tipo**: Decimal  
**Qué hace**: Correlación promedio máxima deseada para todo el portfolio.

**Interpretación**:
- `0.4` significa que, en promedio, tus activos se mueven juntos solo 40% del tiempo
- Esto es **bueno** - significa diversificación

**Objetivo**: Mantener portfolio diversificado con baja correlación.

**No cambiar** a menos que entiendas completamente las implicaciones.

---

### Kelly Criterion (Tamaño Óptimo de Posición)

El Kelly Criterion es una fórmula matemática para calcular cuánto apostar en cada operación basándose en probabilidades.

#### `risk.kelly.fraction`
**Valor**: `0.25` (25%)  
**Tipo**: Decimal  
**Qué hace**: Usa el 25% del "Kelly completo" para calcular tamaños de posición.

**Kelly Completo**:
```
Si Kelly dice "invierte 40% del capital":
Kelly completo: 40%
Kelly conservador (25%): 10% del capital
```

**¿Por qué no usar Kelly completo?**:
- Kelly completo es **muy agresivo**
- Puede llevar a grandes drawdowns
- 25% es el estándar profesional (balance óptimo)

**Ajuste por perfil**:

| Perfil | Valor | Resultado |
|--------|-------|-----------|
| **Muy conservador** | 0.10 | 10% del Kelly |
| **Conservador** | 0.20 | 20% del Kelly |
| **Moderado** | 0.25 | 25% del Kelly (recomendado) |
| **Agresivo** | 0.35 | 35% del Kelly |

**⚠️ Nunca uses más de 0.50** (50%).

---

#### `risk.kelly.min_probability`
**Valor**: `0.55` (55%)  
**Tipo**: Decimal (0.0 a 1.0)  
**Qué hace**: Solo opera si la probabilidad de ganar es al menos 55%.

**Razón**: Evita operaciones con baja probabilidad de éxito.

**Ejemplo**:
```
Estrategia A: 60% probabilidad de ganar → ✓ Opera
Estrategia B: 52% probabilidad de ganar → ✗ No opera
```

**Ajuste**:
- Más selectivo: `0.60` (solo opera con alta confianza)
- Menos selectivo: `0.50` (opera con probabilidad 50/50)

**Recomendado**: Mantener en `0.55` (ligero edge positivo).

---

### Objetivos de Rendimiento

#### `risk.sharpe_target`
**Valor**: `2.5`  
**Tipo**: Decimal  
**Qué hace**: Objetivo de Sharpe Ratio (retorno ajustado por riesgo).

**Interpretación**:
- **< 1.0**: Mal - riesgo no compensa
- **1.0-2.0**: Bueno
- **2.0-3.0**: Muy bueno (nuestro objetivo)
- **> 3.0**: Excepcional (difícil mantener)

**Uso**: Métrica para evaluar si el bot está funcionando bien.

**No es un límite** - es un objetivo aspiracional.

---

#### `risk.max_drawdown_tolerance`
**Valor**: `-20.0` (%)  
**Tipo**: Número negativo  
**Qué hace**: Máxima caída aceptable desde un pico.

**Ejemplo**:
```
Pico de capital: 4.000€
Drawdown de -20%: Cae a 3.200€
→ Esto es el MÁXIMO tolerable
→ El circuit breaker debe evitar llegar aquí
```

**⚠️ IMPORTANTE**: 
- Este es el drawdown **acumulado** (no diario)
- Los circuit breakers diarios (-5%, -10%, -15%) previenen llegar a -20%
- Si llegas a -20%, **detén el bot y revisa la configuración**

**Nota**: Para recuperarte de un drawdown del 20%, necesitas un 25% de ganancia.

---

## 4. Execution - Ejecución de Órdenes

Esta sección controla cómo se ejecutan las órdenes (compra/venta).

### `execution.slippage_model`
**Valor**: `"realistic"` | `"aggressive"` | `"conservative"`  
**Tipo**: Texto  
**Qué hace**: Modelo de slippage (diferencia entre precio esperado y precio real).

**Opciones**:

| Modelo | Slippage | Cuándo usar |
|--------|----------|-------------|
| **`realistic`** | 0.10-0.20% | Producción (recomendado) |
| **`aggressive`** | 0.05-0.10% | Backtesting optimista |
| **`conservative`** | 0.20-0.50% | Backtesting pesimista |

**Recomendado**: `"realistic"` - Simula condiciones reales de mercado.

---

### `execution.commission_percent`
**Valor**: `0.0005` (0.05%)  
**Tipo**: Decimal  
**Qué hace**: Comisión que cobra el exchange por cada operación.

**Ejemplos de exchanges**:
```
Binance:       0.10% (0.001)
Coinbase Pro:  0.05% (0.0005) ← Nuestro valor por defecto
Kraken:        0.16% (0.0016)
```

**Ajustar** según el exchange que uses. La comisión se cobra en **ambos lados** (compra Y venta):

```
Operación completa:
Compra:  Comisión 0.05%
Venta:   Comisión 0.05%
Total:   0.10%
```

**Impacto en rentabilidad**:
```
100 trades al año
Comisión 0.05% × 2 × 100 = 10% del capital en comisiones
```

---

### `execution.market_impact_percent`
**Valor**: `0.001` (0.1%)  
**Tipo**: Decimal  
**Qué hace**: Cuánto mueve el mercado tu orden.

**Explicación**:
- Cuando compras, tu orden puede empujar el precio hacia arriba
- Cuando vendes, tu orden puede empujar el precio hacia abajo
- Esto es el "market impact"

**Valor típico**: 0.1% para órdenes de tamaño normal.

**Ajustar si**:
- Operas con mucho capital: Aumentar (0.002-0.005)
- Operas con poco capital: Disminuir (0.0005)

---

### Order Types (Tipos de Órdenes)

#### `execution.order_types.market`
**Valor**: `true` | `false`  
**Qué hace**: Permite órdenes de mercado (compra/vende al precio actual inmediatamente).

**Recomendado**: `true` - Necesario para trading rápido.

---

#### `execution.order_types.limit`
**Valor**: `true` | `false`  
**Qué hace**: Permite órdenes limitadas (compra/vende solo a un precio específico o mejor).

**Recomendado**: `true` - Útil para mejor control de precios.

---

#### `execution.order_types.stop_loss`
**Valor**: `true` | `false`  
**Qué hace**: Permite stop loss automático (vende si el precio cae a cierto nivel).

**Recomendado**: `true` - **CRÍTICO** para gestión de riesgo.

---

#### `execution.order_types.take_profit`
**Valor**: `true` | `false`  
**Qué hace**: Permite take profit automático (vende cuando alcanza objetivo de ganancia).

**Recomendado**: `true` - Asegura ganancias automáticamente.

---

### Simulation (Simulación Realista)

#### `execution.simulation.model`
**Valor**: `"microstructure"` | `"simple"`  
**Qué hace**: Modelo de simulación de mercado para backtesting.

**Opciones**:
- **`microstructure`**: Simula libro de órdenes, liquidez, spreads (muy realista)
- **`simple`**: Simulación básica

**Recomendado**: `"microstructure"` - Más preciso.

---

#### `execution.simulation.include_bid_ask_spread`
**Valor**: `true` | `false`  
**Qué hace**: Incluye el spread bid-ask en la simulación.

**Qué es bid-ask spread**: Diferencia entre precio de compra y venta.

**Recomendado**: `true` - Esencial para realismo.

---

#### `execution.simulation.include_order_book_depth`
**Valor**: `true` | `false`  
**Qué hace**: Simula profundidad del libro de órdenes (liquidez disponible).

**Recomendado**: `true` - Evita asumir liquidez infinita.

---

#### `execution.simulation.include_time_of_day_effects`
**Valor**: `true` | `false`  
**Qué hace**: Simula diferentes comportamientos según hora del día.

**Ejemplo**:
- Apertura de mercado: Mayor volatilidad
- Cierre de mercado: Mayor volatilidad
- Madrugada: Menor volatilidad

**Recomendado**: `true` - Más realista.

---

#### `execution.simulation.realistic_fills`
**Valor**: `true` | `false`  
**Qué hace**: Simula llenado parcial de órdenes (no siempre se llena 100%).

**Recomendado**: `true` - En mercados reales, órdenes grandes pueden llenarse parcialmente.

---

## 5. Data - Validación y Normalización de Datos

### Validation (Validación)

#### `data.validation.check_nan`
**Valor**: `true` | `false`  
**Qué hace**: Verifica que no haya valores NaN (vacíos) en los datos.

**Recomendado**: `true` - **CRÍTICO**. NaN corrompe todas las señales.

---

#### `data.validation.check_infinity`
**Valor**: `true` | `false`  
**Qué hace**: Verifica que no haya valores infinitos.

**Recomendado**: `true` - Valores infinitos rompen cálculos.

---

#### `data.validation.check_outliers`
**Valor**: `true` | `false`  
**Qué hace**: Detecta valores extremos que pueden ser errores de datos.

**Recomendado**: `true` - Evita operar con datos erróneos.

---

#### `data.validation.check_ohlc_consistency`
**Valor**: `true` | `false`  
**Qué hace**: Verifica que High ≥ Low, Open/Close dentro del rango, etc.

**Recomendado**: `true` - Datos inconsistentes indican error de API.

---

#### `data.validation.check_volume`
**Valor**: `true` | `false`  
**Qué hace**: Verifica que el volumen sea positivo y realista.

**Recomendado**: `true` - Volumen 0 o negativo es imposible.

---

#### `data.validation.outlier_std_threshold`
**Valor**: `5` (desviaciones estándar)  
**Tipo**: Número entero  
**Qué hace**: Un valor es outlier si está a más de 5σ de la media.

**Explicación**:
- σ (sigma) = desviación estándar
- 5σ captura 99.9999% de datos normales
- Valores fuera de 5σ son probablemente errores

**Ajuste**:
- Más estricto: `3` (capta más outliers, puede rechazar datos válidos)
- Más relajado: `7` (permite más variación)

**Recomendado**: Dejar en `5`.

---

### Normalization (Normalización)

#### `data.normalization.method`
**Valor**: `"zscore"` | `"minmax"` | `"robust"`  
**Tipo**: Texto  
**Qué hace**: Método de normalización de datos.

**Opciones**:

| Método | Fórmula | Ventajas | Desventajas |
|--------|---------|----------|-------------|
| **`zscore`** | (x-μ)/σ | Estándar estadístico | Sensible a outliers |
| **`minmax`** | (x-min)/(max-min) | Escala [0,1] | Muy sensible a outliers |
| **`robust`** | (x-median)/IQR | Robusto a outliers | Menos estándar |

**Recomendado**: `"zscore"` - Más común en trading cuantitativo.

---

#### `data.normalization.lookback_period`
**Valor**: `252` (días)  
**Tipo**: Número entero  
**Qué hace**: Ventana de tiempo para calcular media y desviación estándar.

**252 días** = 1 año de trading (número de días hábiles).

**Ajuste**:
- Corto plazo: `60-120` días
- Largo plazo: `500+` días

**Recomendado**: `252` (estándar de la industria).

---

#### `data.normalization.clip_range`
**Valor**: `[-3, 3]`  
**Tipo**: Lista de 2 números  
**Qué hace**: Limita los valores normalizados a este rango.

**Por qué**: Valores extremos (>3σ) son outliers que pueden distorsionar modelos.

**No cambiar** a menos que tengas una razón específica.

---

### Drift Detection (Detección de Cambios)

#### `data.drift_detection.enabled`
**Valor**: `true` | `false`  
**Qué hace**: Detecta cuando las características de los datos cambian (market regime change).

**Recomendado**: `true` - Alerta cuando el mercado cambia fundamentalmente.

---

#### `data.drift_detection.method`
**Valor**: `"adwin"`  
**Tipo**: Texto  
**Qué hace**: Algoritmo de detección (ADWIN = Adaptive Windowing).

**No cambiar** - ADWIN es el algoritmo más efectivo para esto.

---

#### `data.drift_detection.delta`
**Valor**: `0.002`  
**Tipo**: Decimal  
**Qué hace**: Sensibilidad de detección (más bajo = más sensible).

**Ajuste**:
- Más sensible: `0.001` (detecta cambios pequeños)
- Menos sensible: `0.005` (solo cambios grandes)

**Recomendado**: `0.002` (balance).

---

## 6. Ensemble - Sistema de Votación de Estrategias

### `ensemble.voting_method`
**Valor**: `"weighted_average"` | `"majority"` | `"blend"`  
**Tipo**: Texto  
**Qué hace**: Método para combinar señales de múltiples estrategias.

**Opciones**:

| Método | Cómo funciona | Cuándo usar |
|--------|---------------|-------------|
| **`weighted_average`** | Voto ponderado por Sharpe Ratio | Producción (recomendado) |
| **`majority`** | La mayoría gana | Todas las estrategias iguales |
| **`blend`** | Mezcla ponderada por confianza | Experimental |

**Recomendado**: `"weighted_average"` - Da más peso a estrategias que funcionan mejor.

---

### `ensemble.confidence_threshold`
**Valor**: `0.5` (50%)  
**Tipo**: Decimal (0.0 a 1.0)  
**Qué hace**: Confianza mínima para ejecutar una operación.

**Ejemplo**:
```
Señal con 45% confianza → ✗ Rechazada
Señal con 62% confianza → ✓ Ejecutada
```

**Ajuste por perfil**:

| Perfil | Valor | Resultado |
|--------|-------|-----------|
| **Conservador** | 0.70 | Menos trades, mayor calidad |
| **Moderado** | 0.50 | Balance (recomendado) |
| **Agresivo** | 0.30 | Más trades, menor calidad |

---

### `ensemble.min_strategies_agree`
**Valor**: `3`  
**Tipo**: Número entero  
**Qué hace**: Número mínimo de estrategias que deben estar de acuerdo para ejecutar.

**Ejemplo con 20 estrategias**:
```
min_strategies_agree: 3
→ Al menos 3 estrategias deben dar la misma señal (BUY o SELL)
```

**Ajuste**:
- Más conservador: `5-7` (requiere más consenso)
- Más agresivo: `2-3` (menos consenso necesario)

**Recomendado**: `3` (balance).

---

### Adaptive Allocation (Asignación Adaptativa)

#### `ensemble.adaptive_allocation.method`
**Valor**: `"sharpe_based"` | `"equal"` | `"returns_based"`  
**Tipo**: Texto  
**Qué hace**: Cómo calcular el peso de cada estrategia.

**Opciones**:
- **`sharpe_based`**: Peso según Sharpe Ratio (riesgo-ajustado) ← Recomendado
- **`equal`**: Todas las estrategias con mismo peso
- **`returns_based`**: Peso según retornos absolutos (ignora riesgo)

**Recomendado**: `"sharpe_based"` - Considera riesgo, no solo retorno.

---

#### `ensemble.adaptive_allocation.rebalance_frequency`
**Valor**: `"daily"` | `"hourly"` | `"weekly"`  
**Tipo**: Texto  
**Qué hace**: Cada cuánto se recalculan los pesos de estrategias.

**Opciones**:
- **`hourly`**: Muy reactivo (puede sobre-adaptarse)
- **`daily`**: Balance óptimo (recomendado)
- **`weekly`**: Muy estable (puede ser lento para adaptarse)

**Recomendado**: `"daily"` - Responde a cambios sin sobre-reaccionar.

---

#### `ensemble.adaptive_allocation.smoothing_alpha`
**Valor**: `0.7`  
**Tipo**: Decimal (0.0 a 1.0)  
**Qué hace**: Suavizado exponencial (evita cambios bruscos de pesos).

**Fórmula**:
```
nuevo_peso = α × peso_anterior + (1-α) × peso_calculado
```

**Interpretación**:
- **0.9**: Muy suave (cambia lentamente)
- **0.7**: Balance (recomendado)
- **0.3**: Muy reactivo (cambia rápido)

**Recomendado**: `0.7` - Buena estabilidad sin perder adaptabilidad.

---

#### `ensemble.adaptive_allocation.lookback_days`
**Valor**: `20` (días)  
**Tipo**: Número entero  
**Qué hace**: Ventana de tiempo para calcular rendimiento de estrategias.

**Explicación**: Usa los últimos 20 días para calcular Sharpe Ratio.

**Ajuste**:
- Corto plazo: `10-15` días (más reactivo)
- Largo plazo: `30-60` días (más estable)

**Recomendado**: `20` días (aproximadamente 1 mes de trading).

---

### Correlation Management (Gestión de Correlación)

#### `ensemble.correlation_management.recalculate_frequency`
**Valor**: `"hourly"` | `"daily"`  
**Tipo**: Texto  
**Qué hace**: Cada cuánto recalcular matriz de correlación.

**Recomendado**: `"hourly"` - La correlación puede cambiar rápidamente.

---

#### `ensemble.correlation_management.correlation_lookback`
**Valor**: `60` (minutos)  
**Tipo**: Número entero  
**Qué hace**: Ventana de tiempo para calcular correlación.

**Recomendado**: `60` minutos (1 hora) - Captura correlación reciente.

---

#### `ensemble.correlation_management.method`
**Valor**: `"pearson"` | `"spearman"`  
**Tipo**: Texto  
**Qué hace**: Método de cálculo de correlación.

**Opciones**:
- **`pearson`**: Correlación lineal (estándar)
- **`spearman`**: Correlación de rangos (robusto a outliers)

**Recomendado**: `"pearson"` - Más estándar en finanzas.

---

## 7. Strategies - Estrategias Habilitadas

### `strategies.enabled_count`
**Valor**: `20`  
**Tipo**: Número entero  
**Qué hace**: Número total de estrategias activas.

**Informativo** - Se actualiza automáticamente según las estrategias habilitadas.

---

### `strategies.base`
**Tipo**: Lista  
**Qué hace**: Lista de estrategias base (técnicas tradicionales).

**Estrategias incluidas**:
1. `momentum` - Sigue tendencias
2. `stat_arb` - Arbitraje estadístico
3. `regime` - Detecta régimen de mercado
4. `mean_reversion` - Reversión a la media
5. `volatility_expansion` - Expansión de volatilidad
6. `breakout` - Rupturas de niveles
7. `fibonacci` - Niveles de Fibonacci
8. `macd_momentum` - Momentum MACD
9. `rsi_divergence` - Divergencias RSI
10. `bollinger_bands` - Bandas de Bollinger
11. `stochastic` - Oscilador Estocástico
12. `ichimoku` - Ichimoku Kinko Hyo
13. `elliot_wave` - Ondas de Elliott
14. `vix_hedge` - Cobertura con VIX
15. `sector_rotation` - Rotación sectorial

**Para deshabilitar una estrategia**: Comenta la línea con `#`
```yaml
base:
  - momentum
  # - stat_arb  ← Esta estrategia está deshabilitada
  - regime
```

---

### `strategies.advanced`
**Tipo**: Lista  
**Qué hace**: Lista de estrategias avanzadas (alto rendimiento).

**Estrategias incluidas**:
1. `cross_exchange_arb` - Arbitraje entre exchanges (+4,820% ROI)
2. `liquidation_flow` - Cascadas de liquidación (+950% ROI)
3. `high_prob_bonds` - Contratos de alta probabilidad (+1,800% ROI)
4. `liquidity_provision` - Provisión de liquidez (+180% ROI)
5. `domain_specialization` - Especialización de dominio (+720% ROI)

**⚠️ Importante**: Estas estrategias son más complejas y requieren:
- APIs específicas (Polymarket, etc.)
- Más capital para ser efectivas
- Mayor supervisión

---

## 8. Liquidation Detection - Detección de Cascadas

### `liquidation_detection.enabled`
**Valor**: `true` | `false`  
**Qué hace**: Activa detección de cascadas de liquidación.

**Qué es una cascada de liquidación**: Efecto dominó cuando muchos traders con apalancamiento son liquidados simultáneamente.

**Recomendado**: `true` - Protege de caídas repentinas.

---

### `liquidation_detection.cascade_threshold`
**Valor**: `0.6` (60%)  
**Tipo**: Decimal (0.0 a 1.0)  
**Qué hace**: Probabilidad mínima de cascada para tomar acción.

**Ejemplo**:
```
Cascada detectada con 70% probabilidad
→ Threshold es 60%
→ Se activa acción protectora
```

**Ajuste**:
- Más conservador: `0.5` (actúa antes)
- Más agresivo: `0.8` (actúa solo en cascadas muy probables)

---

### `liquidation_detection.lookback_window`
**Valor**: `300` (segundos = 5 minutos)  
**Tipo**: Número entero  
**Qué hace**: Ventana de tiempo para detectar liquidaciones recientes.

**No cambiar** - 5 minutos es óptimo para detectar cascadas en formación.

---

### `liquidation_detection.recent_liquidation_count`
**Valor**: `50`  
**Tipo**: Número entero  
**Qué hace**: Número de liquidaciones recientes que constituye una "cascada".

**Ejemplo**:
```
Últimos 5 minutos: 65 liquidaciones
→ Supera threshold de 50
→ Se considera cascada
```

---

### `liquidation_detection.action_on_cascade`
**Valor**: `"reduce_positions"` | `"close_all"` | `"hedge"`  
**Tipo**: Texto  
**Qué hace**: Acción a tomar cuando se detecta cascada.

**Opciones**:

| Acción | Qué hace | Cuándo usar |
|--------|----------|-------------|
| **`reduce_positions`** | Reduce tamaño 50% | Recomendado (balance) |
| **`close_all`** | Cierra todas las posiciones | Muy conservador |
| **`hedge`** | Abre posiciones de cobertura | Avanzado |

**Recomendado**: `"reduce_positions"` - Protege sin salir completamente.

---

## 9. Monitoring - Monitoreo y Alertas

### `monitoring.real_time`
**Valor**: `true` | `false`  
**Qué hace**: Activa monitoreo en tiempo real.

**Recomendado**: `true` - Esencial para ver qué está haciendo el bot.

---

### `monitoring.update_frequency`
**Valor**: `5` (segundos)  
**Tipo**: Número entero  
**Qué hace**: Cada cuántos segundos actualizar métricas.

**Recomendado**: `5` segundos - Balance entre frescura y carga del sistema.

---

### `monitoring.metrics`
**Tipo**: Lista  
**Qué hace**: Métricas que se rastrean.

**Métricas incluidas**:
- `daily_returns` - Retornos diarios
- `sharpe_ratio` - Ratio de Sharpe
- `max_drawdown` - Drawdown máximo
- `win_rate` - Tasa de acierto
- `profit_factor` - Factor de beneficio
- `recovery_factor` - Factor de recuperación
- `sortino_ratio` - Ratio de Sortino (solo downside risk)
- `calmar_ratio` - Ratio de Calmar (retorno/drawdown)

**Para deshabilitar una métrica**: Comenta con `#`

---

### Alerts (Alertas)

#### `monitoring.alerts.email`
**Valor**: `true` | `false`  
**Qué hace**: Envía alertas por email.

**Requiere configuración adicional** de SMTP.

---

#### `monitoring.alerts.slack`
**Valor**: `true` | `false`  
**Qué hace**: Envía alertas a Slack.

**Requiere configuración adicional** de webhook de Slack.

---

#### `monitoring.alerts.telegram`
**Valor**: `true` | `false`  
**Qué hace**: Envía alertas a Telegram.

**Requiere configuración adicional** de bot de Telegram.

**Por defecto todas en `false`** - Activa solo las que vayas a usar.

---

## 10. State Persistence - Persistencia de Estado

### `state_persistence.enabled`
**Valor**: `true` | `false`  
**Qué hace**: Guarda el estado del bot en base de datos.

**Recomendado**: `true` - **CRÍTICO** para recuperación tras crashes.

---

### `state_persistence.checkpoint_frequency`
**Valor**: `300` (segundos = 5 minutos)  
**Tipo**: Número entero  
**Qué hace**: Cada cuánto guardar snapshot del portfolio.

**Ajuste**:
- Más frecuente: `60` segundos (más seguro pero más carga)
- Menos frecuente: `600` segundos (menos carga pero más riesgo)

**Recomendado**: `300` segundos (5 minutos) - Balance óptimo.

---

### `state_persistence.backup_frequency`
**Valor**: `3600` (segundos = 1 hora)  
**Tipo**: Número entero  
**Qué hace**: Cada cuánto hacer backup completo.

**Recomendado**: `3600` (1 hora) - Backups regulares sin saturar.

---

### Storage (Almacenamiento)

#### `state_persistence.storage.type`
**Valor**: `"postgresql"` | `"sqlite"` | `"redis"`  
**Tipo**: Texto  
**Qué hace**: Tipo de base de datos.

**Opciones**:

| Tipo | Ventajas | Desventajas | Cuándo usar |
|------|----------|-------------|-------------|
| **`postgresql`** | Robusto, escalable | Requiere instalación | Producción |
| **`sqlite`** | Simple, archivo local | Menos robusto | Desarrollo |
| **`redis`** | Muy rápido | Solo en memoria | Cache |

**Recomendado**: 
- Producción: `"postgresql"`
- Desarrollo: `"sqlite"`

---

#### `state_persistence.storage.host`
**Valor**: `"localhost"` | IP  
**Tipo**: Texto  
**Qué hace**: Dirección del servidor de base de datos.

**Valores comunes**:
- `"localhost"`: Base de datos local
- `"192.168.1.100"`: Servidor en red local
- `"db.example.com"`: Servidor remoto

---

#### `state_persistence.storage.port`
**Valor**: `5432`  
**Tipo**: Número entero  
**Qué hace**: Puerto de PostgreSQL.

**Por defecto PostgreSQL**: `5432`  
**No cambiar** a menos que uses configuración personalizada.

---

#### `state_persistence.storage.database`
**Valor**: `"botv2"`  
**Tipo**: Texto  
**Qué hace**: Nombre de la base de datos.

**Puedes cambiarlo** si quieres usar un nombre diferente.

---

#### `state_persistence.storage.user`
**Valor**: `"botv2_user"`  
**Tipo**: Texto  
**Qué hace**: Usuario de la base de datos.

**Debe coincidir** con el usuario que creaste en PostgreSQL.

---

### Backup (Respaldo)

#### `state_persistence.backup.path`
**Valor**: `"./backups"`  
**Tipo**: Ruta  
**Qué hace**: Directorio donde guardar backups.

**Puedes cambiarlo** a cualquier ruta, por ejemplo:
- `"/home/usuario/botv2-backups"`
- `"./data/backups"`

---

#### `state_persistence.backup.retention_days`
**Valor**: `30` (días)  
**Tipo**: Número entero  
**Qué hace**: Cuántos días conservar backups antiguos.

**Ejemplo**:
```
retention_days: 30
→ Backups de hace más de 30 días se eliminan automáticamente
```

**Ajuste**:
- Más backups: `60-90` días
- Menos backups: `7-14` días

---

#### `state_persistence.backup.compress`
**Valor**: `true` | `false`  
**Qué hace**: Comprime backups para ahorrar espacio.

**Recomendado**: `true` - Ahorra mucho espacio en disco.

---

## 11. Markets - Mercados y Exchanges

### `markets.primary`
**Valor**: `"polymarket"` | `"binance"` | etc.  
**Tipo**: Texto  
**Qué hace**: Exchange o plataforma principal para operar.

**Cambiar** según donde quieras operar.

---

### Polymarket (ejemplo)

#### `markets.polymarket.base_url`
**Valor**: URL  
**Qué hace**: URL base de la API de Polymarket.

**No cambiar** - Es la URL oficial.

---

#### `markets.polymarket.api_key_env`
**Valor**: `"POLYMARKET_API_KEY"`  
**Tipo**: Texto  
**Qué hace**: Nombre de la variable de entorno que contiene tu API key.

**Configuración**:
```bash
export POLYMARKET_API_KEY="tu_clave_api_aqui"
```

**⚠️ NUNCA** pongas la API key directamente en el archivo YAML.

---

#### `markets.polymarket.markets`
**Tipo**: Lista  
**Qué hace**: Mercados específicos de Polymarket a operar.

**Puedes agregar/quitar** mercados según tus intereses.

---

### `markets.fallback`
**Tipo**: Lista  
**Qué hace**: Exchanges de respaldo si el primario falla.

**Ejemplo**:
```yaml
fallback:
  - "kalshi"
  - "predictit"
```

---

## 12. Backtesting - Pruebas Históricas

### `backtesting.enabled`
**Valor**: `true` | `false`  
**Qué hace**: Activa modo backtesting.

**Para trading real**: `false`  
**Para pruebas**: `true`

---

### `backtesting.start_date`
**Valor**: Fecha (`"YYYY-MM-DD"`)  
**Qué hace**: Fecha de inicio para backtest.

**Ejemplo**: `"2023-01-01"` - Comienza desde 1 de enero 2023.

---

### `backtesting.end_date`
**Valor**: Fecha (`"YYYY-MM-DD"`)  
**Qué hace**: Fecha final para backtest.

**Ejemplo**: `"2025-12-31"` - Termina el 31 de diciembre 2025.

---

### `backtesting.initial_capital`
**Valor**: Número  
**Qué hace**: Capital inicial para el backtest.

**Puede ser diferente** del capital real de trading.

---

### Simulation (Simulación en Backtest)

Estas opciones controlan cuán realista es el backtest.

**Recomendado: TODAS EN `true`** para máxima precisión.

---

### Output (Salida del Backtest)

#### `backtesting.output.save_trades`
**Valor**: `true` | `false`  
**Qué hace**: Guarda todas las operaciones del backtest.

**Recomendado**: `true` - Útil para análisis detallado.

---

#### `backtesting.output.save_equity_curve`
**Valor**: `true` | `false`  
**Qué hace**: Guarda curva de equity (evolución del capital).

**Recomendado**: `true` - Visualiza rendimiento.

---

#### `backtesting.output.save_metrics`
**Valor**: `true` | `false`  
**Qué hace**: Guarda métricas de rendimiento.

**Recomendado**: `true` - Para evaluación.

---

#### `backtesting.output.generate_report`
**Valor**: `true` | `false`  
**Qué hace**: Genera reporte HTML completo del backtest.

**Recomendado**: `true` - Reporte visual muy útil.

---

## 13. Dashboard - Panel de Control Web

### `dashboard.enabled`
**Valor**: `true` | `false`  
**Qué hace**: Activa el dashboard web.

**Recomendado**: `true` - Visualización en tiempo real.

---

### `dashboard.host`
**Valor**: `"0.0.0.0"` | `"localhost"` | IP  
**Tipo**: Texto  
**Qué hace**: En qué interfaz escuchar.

**Opciones**:
- `"0.0.0.0"`: Accesible desde cualquier dispositivo en la red
- `"localhost"` o `"127.0.0.1"`: Solo accesible desde el mismo ordenador

**Seguridad**:
- Desarrollo: `"localhost"`
- Red local confiable: `"0.0.0.0"`

---

### `dashboard.port`
**Valor**: `8050`  
**Tipo**: Número entero  
**Qué hace**: Puerto donde escucha el dashboard.

**Acceso**: `http://localhost:8050` (o tu IP + puerto)

**Cambiar** si el puerto 8050 está ocupado.

---

### `dashboard.debug`
**Valor**: `true` | `false`  
**Qué hace**: Modo debug del dashboard (muestra errores detallados).

**Recomendado**:
- Desarrollo: `true`
- Producción: `false`

---

### `dashboard.refresh_rate`
**Valor**: `5` (segundos)  
**Tipo**: Número entero  
**Qué hace**: Cada cuántos segundos actualizar gráficos.

**Ajuste**:
- Más rápido: `2-3` segundos (consume más recursos)
- Más lento: `10-30` segundos (menos carga)

**Recomendado**: `5` segundos.

---

### `dashboard.charts`
**Tipo**: Lista  
**Qué hace**: Qué gráficos mostrar en el dashboard.

**Gráficos disponibles**:
- `equity_curve` - Curva de equity
- `daily_returns` - Retornos diarios
- `drawdown` - Drawdown
- `strategy_performance` - Rendimiento por estrategia
- `correlation_heatmap` - Mapa de correlación
- `position_sizes` - Tamaños de posición

**Para ocultar un gráfico**: Comenta la línea con `#`

---

## 📚 Resumen de Perfiles Recomendados

### Perfil Conservador

```yaml
trading:
  initial_capital: 3000
  max_position_size: 0.10  # 10% máximo
  
risk:
  circuit_breaker:
    level_1_drawdown: -3.0   # Más restrictivo
    level_2_drawdown: -7.0
    level_3_drawdown: -12.0
  kelly:
    fraction: 0.20  # Más conservador
    
ensemble:
  confidence_threshold: 0.70  # Solo señales muy confiables
```

### Perfil Moderado (Recomendado)

```yaml
trading:
  initial_capital: 3000
  max_position_size: 0.15  # 15% máximo
  
risk:
  circuit_breaker:
    level_1_drawdown: -5.0
    level_2_drawdown: -10.0
    level_3_drawdown: -15.0
  kelly:
    fraction: 0.25
    
ensemble:
  confidence_threshold: 0.50  # Balance
```

### Perfil Agresivo

```yaml
trading:
  initial_capital: 3000
  max_position_size: 0.20  # 20% máximo
  
risk:
  circuit_breaker:
    level_1_drawdown: -7.0   # Más tolerante
    level_2_drawdown: -12.0
    level_3_drawdown: -18.0
  kelly:
    fraction: 0.35  # Más agresivo
    
ensemble:
  confidence_threshold: 0.35  # Más operaciones
```

---

## ⚠️ Advertencias Importantes

### NO Cambiar Sin Entender

Estas propiedades son **CRÍTICAS** y cambiarlas sin conocimiento puede causar pérdidas:

1. `risk.circuit_breaker.*` - Protección contra pérdidas
2. `risk.max_drawdown_tolerance` - Límite de pérdidas
3. `risk.kelly.fraction` - Tamaño de posiciones
4. `data.validation.*` - Validación de datos
5. `execution.commission_percent` - Debe coincidir con tu exchange
6. `state_persistence.enabled` - Debe estar en `true`

### Seguridad

**NUNCA** pongas información sensible en `settings.yaml`:
- ❌ API keys
- ❌ Contraseñas
- ❌ Claves privadas

**Usa variables de entorno**:
```bash
export POLYMARKET_API_KEY="tu_clave"
export POSTGRES_PASSWORD="tu_password"
```

### Backup

**Antes de cambiar configuración**:
1. Haz backup del archivo `settings.yaml`
2. Anota los valores originales
3. Haz cambios graduales
4. Monitorea resultados
5. Revierte si es necesario

---

## 🧪 Testing de Configuración

### Validar Configuración

```bash
# Comprobar que el archivo es válido
python -c "import yaml; yaml.safe_load(open('src/config/settings.yaml'))"
```

### Probar en Desarrollo

Antes de usar una configuración en producción:

1. Pon `system.environment: "development"`
2. Habilita `backtesting.enabled: true`
3. Ejecuta backtest con 1-2 meses de datos
4. Revisa métricas:
   - Sharpe Ratio > 1.5
   - Max Drawdown < -20%
   - Win Rate > 50%
5. Si pasa las pruebas, usa en producción

---

## 📞 Soporte

### Si tienes dudas sobre una propiedad:

1. **Busca en este documento** usando Ctrl+F
2. **Revisa el valor por defecto** - generalmente es óptimo
3. **Consulta la documentación técnica** en `/docs`
4. **Haz pruebas en modo desarrollo** antes de cambiar

### Si algo falla:

1. **Revierte a valores por defecto**
2. **Revisa logs** en `logs/`
3. **Verifica variables de entorno** (API keys, passwords)
4. **Comprueba conexión a base de datos**

---

**Versión**: 1.0.0  
**Última Actualización**: Enero 2026  
**Autor**: Juan Carlos Garcia Arriero  
**Propósito**: Guía completa de configuración

---

## ✅ Checklist Pre-Producción

Antes de ejecutar el bot con dinero real, verifica:

- [ ] `system.environment: "production"`
- [ ] `trading.initial_capital` es correcto
- [ ] `execution.commission_percent` coincide con tu exchange
- [ ] Variables de entorno configuradas (API keys)
- [ ] Base de datos funcionando
- [ ] Circuit breakers configurados
- [ ] Backup automático habilitado
- [ ] Dashboard accesible
- [ ] Logs escribiendo correctamente
- [ ] Backtest exitoso con configuración actual

---

**¡Configuración completa! Ahora estás listo para usar BotV2 de forma segura e informada.**
