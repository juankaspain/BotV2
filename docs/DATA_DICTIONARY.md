# 📚 Diccionario de Datos - BotV2

## Introducción

Este documento explica todos los conceptos, términos y métricas utilizados en BotV2 de forma clara y accesible. Está diseñado para personas sin experiencia previa en trading algorítmico o programación financiera.

---

## 🎯 Conceptos Fundamentales

### Trading (Comercio)

**Definición**: Compra y venta de activos financieros (criptomonedas, acciones, etc.) con el objetivo de obtener beneficios.

**Ejemplo**: Compras Bitcoin a 40.000€ y lo vendes a 42.000€. Tu beneficio es 2.000€ (menos comisiones).

### Bot de Trading

**Definición**: Un programa informático que realiza operaciones de compra/venta automáticamente siguiendo reglas predefinidas, sin necesidad de intervención humana constante.

**Ventajas**:
- Opera 24/7 sin descanso
- Elimina emociones (miedo, codicia)
- Ejecuta operaciones en milisegundos
- Puede gestionar múltiples estrategias simultáneamente

### Capital

**Definición**: La cantidad de dinero que tienes disponible para invertir.

**En BotV2**: Por defecto 3.000€. Es el dinero inicial con el que el bot comienza a operar.

### Posición

**Definición**: Una inversión activa en un activo específico.

**Tipos**:
- **Posición Larga (Long)**: Compras esperando que el precio suba
- **Posición Corta (Short)**: Vendes esperando que el precio baje

**Ejemplo**: Si compras 0.5 Bitcoin a 40.000€, tienes una posición larga de 0.5 BTC valorada en 20.000€.

### Portfolio (Cartera)

**Definición**: Conjunto de todas tus inversiones activas más el efectivo disponible.

**Composición**:
```
Portfolio = Efectivo + Valor de Posiciones Abiertas
```

**Ejemplo**:
- Efectivo: 10.000€
- Posición en BTC: 5.000€
- Posición en ETH: 3.000€
- **Portfolio Total**: 18.000€

---

## 📊 Métricas de Rendimiento

### ROI (Return on Investment / Retorno de Inversión)

**Definición**: Porcentaje de ganancia o pérdida sobre tu inversión inicial.

**Fórmula**:
```
ROI = ((Valor Final - Valor Inicial) / Valor Inicial) × 100
```

**Ejemplo**:
- Inversión inicial: 3.000€
- Valor final: 3.600€
- ROI = ((3.600 - 3.000) / 3.000) × 100 = **20%**

**Interpretación**:
- ROI positivo (+20%): Has ganado dinero
- ROI negativo (-10%): Has perdido dinero
- ROI = 0%: Estás igual que al inicio

### Sharpe Ratio (Ratio de Sharpe)

**Definición**: Mide cuánto rendimiento obtienes por cada unidad de riesgo que asumes. Es la métrica más importante para evaluar estrategias.

**Fórmula Simplificada**:
```
Sharpe Ratio = (Retorno Promedio - Tasa Libre de Riesgo) / Volatilidad
```

**Interpretación**:
- **< 1.0**: Mal - El riesgo no compensa
- **1.0 - 2.0**: Bueno - Riesgo razonable
- **2.0 - 3.0**: Muy bueno - Excelente balance
- **> 3.0**: Excepcional - Difícil de mantener

**Ejemplo**:
- Estrategia A: 30% retorno, 20% volatilidad → Sharpe = 1.5
- Estrategia B: 20% retorno, 5% volatilidad → Sharpe = 4.0
- **Estrategia B es mejor** (menos riesgo para retorno similar)

### Drawdown (Caída)

**Definición**: La caída máxima desde un pico hasta un valle en el valor de tu portfolio.

**Fórmula**:
```
Drawdown = ((Pico - Valle) / Pico) × 100
```

**Ejemplo Timeline**:
```
Día 1: 10.000€ (pico)
Día 2: 9.500€
Día 3: 8.500€ (valle)
Día 4: 9.000€

Drawdown Máximo = ((10.000 - 8.500) / 10.000) × 100 = 15%
```

**Importancia**: Indica cuánto puedes llegar a perder en el peor escenario. Un drawdown del 50% significa que necesitas un 100% de ganancia para recuperarte.

### Win Rate (Tasa de Acierto)

**Definición**: Porcentaje de operaciones que terminan en ganancia.

**Fórmula**:
```
Win Rate = (Operaciones Ganadoras / Total Operaciones) × 100
```

**Ejemplo**:
- 100 operaciones realizadas
- 65 ganadoras, 35 perdedoras
- Win Rate = 65%

**Nota Importante**: Un Win Rate alto no garantiza rentabilidad. Puedes tener 90% de aciertos pero si las pérdidas son muy grandes, pierdes dinero igualmente.

### Profit Factor (Factor de Beneficio)

**Definición**: Relación entre ganancias brutas y pérdidas brutas.

**Fórmula**:
```
Profit Factor = Ganancias Totales / Pérdidas Totales
```

**Interpretación**:
- **< 1.0**: Pierdes más de lo que ganas (malo)
- **1.0 - 1.5**: Apenas rentable
- **1.5 - 2.0**: Bueno
- **> 2.0**: Excelente

**Ejemplo**:
- Ganancias totales: 15.000€
- Pérdidas totales: 6.000€
- Profit Factor = 15.000 / 6.000 = **2.5** (Excelente)

### Volatilidad

**Definición**: Medida de cuánto varía el precio de un activo. Alta volatilidad = cambios bruscos de precio.

**Indicador Común**: Desviación estándar de los retornos.

**Analogía**: Como un coche en una carretera:
- **Baja volatilidad**: Carretera recta y suave
- **Alta volatilidad**: Carretera con muchas curvas y baches

**Impacto en Trading**:
- Alta volatilidad = Mayor riesgo pero mayor oportunidad
- Baja volatilidad = Menor riesgo pero menores ganancias

---

## 🎲 Gestión de Riesgo

### Stop Loss (Límite de Pérdida)

**Definición**: Orden automática para vender una posición si el precio cae a un nivel predeterminado, limitando tus pérdidas.

**Ejemplo**:
```
Compras Bitcoin a 40.000€
Stop Loss al -5% = 38.000€

Si BTC baja a 38.000€ → Venta automática
Pérdida controlada: -2.000€ (5%)
```

**Beneficio**: Evita pérdidas catastróficas si el mercado se desploma.

### Take Profit (Toma de Beneficios)

**Definición**: Orden automática para vender una posición cuando alcanza un objetivo de ganancia.

**Ejemplo**:
```
Compras Bitcoin a 40.000€
Take Profit al +10% = 44.000€

Si BTC sube a 44.000€ → Venta automática
Ganancia asegurada: +4.000€ (10%)
```

### Position Sizing (Tamaño de Posición)

**Definición**: Cuánto dinero arriesgas en cada operación.

**Regla General**:
- **Mínimo**: 1% del capital (30€ si tienes 3.000€)
- **Máximo**: 15% del capital (450€ si tienes 3.000€)

**Por qué es importante**: Si arriesgas todo en una operación y pierdes, quedas fuera del juego.

### Kelly Criterion (Criterio de Kelly)

**Definición**: Fórmula matemática para calcular el tamaño óptimo de cada posición basándose en probabilidades de ganar.

**Fórmula**:
```
Kelly% = (Probabilidad de Ganar × Ganancia Media - Probabilidad de Perder) / Ganancia Media
```

**En BotV2**: Usamos "Kelly Conservador" = 25% del Kelly completo para reducir riesgo.

**Ejemplo**:
- Probabilidad de ganar: 60%
- Ganancia media: 2x (ganas el doble de lo que arriesgas)
- Kelly = (0.6 × 2 - 0.4) / 2 = 0.4 o 40% del capital
- Kelly conservador = 40% × 0.25 = **10% del capital**

### Circuit Breaker (Disyuntor de Seguridad)

**Definición**: Sistema automático que detiene el trading cuando las pérdidas alcanzan ciertos niveles.

**Niveles en BotV2**:

1. **Nivel 1 (-5% diario)**:
   - Estado: Precaución ⚠️
   - Acción: Reduce tamaño de posiciones al 50%

2. **Nivel 2 (-10% diario)**:
   - Estado: Alerta ⚠️⚠️
   - Acción: Reduce posiciones al 25%

3. **Nivel 3 (-15% diario)**:
   - Estado: STOP 🛑
   - Acción: Cierra todas las posiciones, pausa el bot por 30 minutos

**Beneficio**: Protege tu capital en días muy malos.

---

## 📈 Indicadores Técnicos

### Moving Average / MA (Media Móvil)

**Definición**: Promedio del precio de un activo durante un periodo específico.

**Cálculo MA(20)**:
```
MA = Suma de últimos 20 precios de cierre / 20
```

**Uso**:
- Precio > MA → Tendencia alcista (señal de compra)
- Precio < MA → Tendencia bajista (señal de venta)

**Tipos**:
- **SMA**: Simple (todos los precios con igual peso)
- **EMA**: Exponencial (da más peso a precios recientes)

### RSI (Relative Strength Index / Índice de Fuerza Relativa)

**Definición**: Oscilador que mide la velocidad y magnitud de los cambios de precio. Va de 0 a 100.

**Zonas**:
- **RSI > 70**: Sobrecomprado (posible corrección a la baja)
- **RSI 30-70**: Zona neutral
- **RSI < 30**: Sobrevendido (posible rebote al alza)

**Uso en BotV2**:
```
Señal de COMPRA: RSI < 30 (activo muy barato)
Señal de VENTA: RSI > 70 (activo muy caro)
```

**Analogía**: Como un resorte:
- RSI alto = resorte muy comprimido (puede rebotar hacia arriba)
- RSI bajo = resorte muy estirado (puede volver hacia abajo)

### Bollinger Bands (Bandas de Bollinger)

**Definición**: Tres líneas que forman un canal alrededor del precio basándose en la volatilidad.

**Componentes**:
```
Banda Superior = MA(20) + 2 × Desviación Estándar
Banda Media    = MA(20)
Banda Inferior = MA(20) - 2 × Desviación Estándar
```

**Interpretación**:
- Precio toca banda superior → Posible venta (sobrevalorado)
- Precio toca banda inferior → Posible compra (infravalorado)
- Bandas estrechas → Baja volatilidad (posible explosión de precio)
- Bandas anchas → Alta volatilidad

### MACD (Moving Average Convergence Divergence)

**Definición**: Indicador de momentum que muestra la relación entre dos medias móviles.

**Componentes**:
```
MACD Línea  = EMA(12) - EMA(26)
Señal Línea = EMA(9) del MACD
Histograma  = MACD - Señal
```

**Señales**:
- **Cruce Alcista**: MACD cruza por encima de Señal → COMPRA
- **Cruce Bajista**: MACD cruza por debajo de Señal → VENTA

### ATR (Average True Range / Rango Verdadero Promedio)

**Definición**: Mide la volatilidad mostrando el rango promedio de movimiento del precio.

**Uso**:
- ATR alto → Mercado volátil (grandes movimientos)
- ATR bajo → Mercado tranquilo (pequeños movimientos)

**Aplicación en Stop Loss**:
```
Stop Loss = Precio de Entrada - (2 × ATR)
```
Esto ajusta el stop loss según la volatilidad actual.

### ADX (Average Directional Index / Índice Direccional Promedio)

**Definición**: Mide la fuerza de una tendencia (no su dirección).

**Valores**:
- **ADX < 25**: Sin tendencia (mercado lateral)
- **ADX 25-50**: Tendencia moderada
- **ADX > 50**: Tendencia fuerte

**Uso**:
- ADX alto + Precio subiendo → Fuerte tendencia alcista
- ADX alto + Precio bajando → Fuerte tendencia bajista
- ADX bajo → Evitar estrategias de tendencia

---

## 🤖 Estrategias de Trading

### Momentum Strategy (Estrategia de Momento)

**Concepto**: "Lo que sube, tiende a seguir subiendo"

**Lógica**: Compra activos que están en tendencia alcista fuerte, esperando que continúe.

**Señal de Entrada**:
```
COMPRA cuando:
- Precio > MA(20)
- RSI > 50
- ROC > 2%
```

**Mejor Entorno**: Mercados en tendencia clara.

**Riesgo**: Puede comprar en máximos antes de una corrección.

### Mean Reversion (Reversión a la Media)

**Concepto**: "Lo que sube mucho, eventualmente baja. Lo que baja mucho, eventualmente sube"

**Lógica**: Los precios tienden a volver a su promedio histórico.

**Señal de Entrada**:
```
COMPRA cuando:
- Precio toca Banda de Bollinger inferior
- RSI < 30
```

**Mejor Entorno**: Mercados laterales o con rango definido.

**Riesgo**: Puede perder en tendencias fuertes.

### Statistical Arbitrage (Arbitraje Estadístico)

**Concepto**: Explotar relaciones matemáticas entre activos correlacionados.

**Ejemplo**:
```
Bitcoin y Ethereum suelen moverse juntos.
Si BTC sube 10% pero ETH solo 2%:
→ Compra ETH (esperando que alcance a BTC)
→ O vende BTC (esperando que baje hacia ETH)
```

**Ventaja**: Estrategia "market-neutral" (no depende de si el mercado sube o baja).

**Complejidad**: Alta, requiere análisis estadístico avanzado.

### Breakout Strategy (Estrategia de Ruptura)

**Concepto**: Compra cuando el precio rompe niveles de resistencia importantes.

**Señal**:
```
COMPRA cuando:
- Precio > Resistencia + 1%
- Volumen > 1.5× promedio
- ATR creciente
```

**Analogía**: Como una olla a presión que finalmente explota.

**Riesgo**: Falsas rupturas (el precio vuelve rápidamente al rango).

### Cross-Exchange Arbitrage (Arbitraje Entre Exchanges)

**Concepto**: Compra en un exchange barato, vende en otro más caro.

**Ejemplo Real**:
```
Binance: Bitcoin a 40.000€
Kraken:  Bitcoin a 40.300€

1. Compra en Binance: -40.000€
2. Vende en Kraken: +40.300€
3. Ganancia bruta: 300€ (0.75%)
4. Costes (fees + transfer): -150€
5. Ganancia neta: 150€ (0.375%)
```

**Ventaja**: Bajo riesgo, alta frecuencia.

**Desafíos**:
- Requiere tener fondos en múltiples exchanges
- Transferencias toman tiempo (riesgo de cambio de precio)
- Oportunidades desaparecen rápido (segundos)

### Liquidation Flow (Flujo de Liquidaciones)

**Concepto**: Aprovecha cascadas de liquidaciones forzadas en mercados de futuros.

**¿Qué es una liquidación?**: Cuando un trader con apalancamiento pierde todo y el exchange cierra su posición automáticamente.

**Señal**:
```
Detecta liquidación masiva:
- Volumen spike > 3× normal
- Caída de precio > 2% en 1 minuto

Acción: Compra el "dip" (caída brusca)
Objetivo: Rebote del 1-2%
```

**ROI en BotV2**: +950% (estrategia muy agresiva)

**Riesgo**: Alto - requiere timing perfecto.

---

## 🔧 Componentes del Sistema

### Data Validation (Validación de Datos)

**Propósito**: Asegurar que los datos de mercado son correctos antes de usarlos.

**Verificaciones**:
1. **NaN Check**: No hay valores vacíos
2. **Infinity Check**: No hay valores infinitos
3. **OHLC Consistency**: High ≥ Low, Open/Close dentro del rango
4. **Outlier Detection**: Detecta valores anómalos (fuera de 5σ)
5. **Time Gaps**: No hay huecos temporales grandes

**Beneficio**: Evita decisiones basadas en datos erróneos.

### Normalization (Normalización)

**Propósito**: Hacer que datos de diferentes mercados sean comparables.

**Método Z-Score**:
```
Z = (Valor - Media) / Desviación Estándar
```

**Ejemplo**:
```
Bitcoin:   40.000€ → Z-score: +1.5
Ethereum:  2.000€ → Z-score: +1.4
Dogecoin:  0.10€ → Z-score: -0.8

Aunque los precios son muy diferentes, los Z-scores
son comparables y muestran que BTC y ETH están
igualmente "caros" relativamente.
```

**Rango**: Se limita entre -3 y +3 para evitar extremos.

### Ensemble Voting (Votación de Conjunto)

**Propósito**: Combinar señales de múltiples estrategias para tomar una decisión final.

**Método "Weighted Average"** (usado en BotV2):
```
Señal Final = Σ (Señal_i × Peso_i)

donde:
- Señal_i: Señal de estrategia i (-1 a +1)
- Peso_i: Peso de estrategia i (basado en Sharpe Ratio)
```

**Ejemplo**:
```
Estrategia A (peso 0.3): COMPRA (señal = +1.0)
Estrategia B (peso 0.5): COMPRA (señal = +0.6)
Estrategia C (peso 0.2): VENTA (señal = -0.4)

Señal Final = (1.0 × 0.3) + (0.6 × 0.5) + (-0.4 × 0.2)
            = 0.3 + 0.3 - 0.08
            = 0.52 → COMPRA con 52% confianza
```

**Ventaja**: Reduce falsas señales, más robusto que usar una sola estrategia.

### Adaptive Allocation (Asignación Adaptativa)

**Propósito**: Dar más peso a estrategias que están funcionando mejor actualmente.

**Proceso**:
1. Calcula Sharpe Ratio de cada estrategia (últimos 20 días)
2. Aplica suavizado exponencial (evita cambios bruscos)
3. Convierte Sharpe a pesos proporcionales
4. Aplica límites (min 1%, max 25% por estrategia)

**Ejemplo**:
```
Día 1:
- Estrategia A: Sharpe 2.5 → Peso 25%
- Estrategia B: Sharpe 1.0 → Peso 10%

Día 30 (A funciona mal, B mejora):
- Estrategia A: Sharpe 0.8 → Peso 8%
- Estrategia B: Sharpe 2.2 → Peso 22%

El sistema automáticamente reduce A y aumenta B.
```

**Beneficio**: Se adapta a condiciones cambiantes del mercado.

### Correlation Management (Gestión de Correlación)

**Propósito**: Evitar tener múltiples posiciones que se muevan igual (reducir riesgo).

**Correlación**:
- **+1.0**: Movimiento idéntico (muy peligroso si tienes ambos)
- **0.0**: Sin relación
- **-1.0**: Movimiento opuesto (bueno para diversificación)

**Ejemplo Problema**:
```
Tienes:
- Posición en Bitcoin
- Posición en Ethereum
- Correlación BTC-ETH = 0.85

Si BTC cae 10%, ETH probablemente caerá ~8.5%
→ Pierdes en AMBAS posiciones simultáneamente
```

**Solución BotV2**:
```
Si correlación_portfolio > 0.7:
  penalty = 1 - (correlación - 0.7) / 0.3
  tamaño_posición_ajustado = tamaño_base × penalty
```

Reduce automáticamente el tamaño de posiciones correlacionadas.

### State Persistence (Persistencia de Estado)

**Propósito**: Guardar el estado del bot regularmente para recuperarse de crashes.

**Qué se guarda**:
- Posiciones abiertas
- Capital disponible
- Historial de trades
- Métricas de rendimiento
- Estado de cada estrategia

**Frecuencia**: Cada 5 minutos (configurable)

**Beneficio**: Si el bot se cae (corte de luz, error, etc.), puede continuar desde donde lo dejó sin perder información.

**Tecnología**: PostgreSQL (base de datos robusta y confiable)

---

## 📉 Conceptos de Mercado

### Slippage (Deslizamiento)

**Definición**: Diferencia entre el precio esperado de una orden y el precio real al ejecutarse.

**Causas**:
- Volatilidad alta
- Baja liquidez
- Órdenes grandes
- Latencia (retraso en la ejecución)

**Ejemplo**:
```
Quieres comprar Bitcoin a 40.000€
En el momento que tu orden llega al exchange:
- Precio subió a 40.050€
- Slippage = 50€ (0.125%)
```

**En BotV2**: Se simula slippage realista (0.05% - 0.2%) para backtesting preciso.

### Bid-Ask Spread (Diferencial Compra-Venta)

**Definición**: Diferencia entre el precio al que puedes comprar (Ask) y vender (Bid).

**Ejemplo**:
```
Bitcoin:
- Bid (puedes vender): 40.000€
- Ask (puedes comprar): 40.100€
- Spread: 100€ (0.25%)
```

**Impacto**: Pagas el spread en cada operación (coste oculto).

**En BotV2**: Incorporado en el modelo de ejecución realista.

### Liquidity (Liquidez)

**Definición**: Facilidad para comprar/vender un activo sin afectar su precio.

**Alta Liquidez** (Bitcoin, Ethereum):
- Puedes comprar/vender millones rápidamente
- Spread bajo (0.01% - 0.05%)
- Slippage mínimo

**Baja Liquidez** (tokens pequeños):
- Órdenes grandes mueven el precio significativamente
- Spread alto (1% - 5%)
- Difícil salir de posiciones

**Analogía**: Como vender una casa vs. vender un coche:
- Casa (baja liquidez): Tarda meses, precio negociable
- Coche (mayor liquidez): Tarda días/semanas
- Bitcoin (altísima liquidez): Segundos, precio casi fijo

### Market Impact (Impacto de Mercado)

**Definición**: Cuánto afecta tu orden al precio del mercado.

**Fórmula Aproximada**:
```
Market Impact = Tamaño_Orden / Liquidez_Disponible
```

**Ejemplo**:
```
Libro de órdenes de BTC tiene 10 BTC disponibles a 40.000€
Tu orden: 2 BTC

Impact = 2 / 10 = 20%
→ Tu orden consumirá 20% de la liquidez
→ Precio final podría ser 40.050€ (slippage)
```

**En BotV2**: Se modela el impacto para órdenes realistas.

### Volume (Volumen)

**Definición**: Cantidad de activo negociado en un periodo (generalmente 24h).

**Importancia**:
- Volumen alto → Mercado activo, fácil entrar/salir
- Volumen bajo → Mercado dormido, riesgo de manipulación

**Uso en Señales**:
```
Ruptura de resistencia con volumen alto → Señal fuerte
Ruptura de resistencia con volumen bajo → Señal débil (posible falsa ruptura)
```

---

## 🧮 Matemáticas Simplificadas

### Retorno Logarítmico

**Definición**: Forma matemática de calcular retornos que permite sumarlos a lo largo del tiempo.

**Fórmula**:
```
Retorno_log = ln(Precio_Final / Precio_Inicial)
```

**Por qué es útil**:
```
Retornos normales: No se pueden sumar
  +10% luego +10% ≠ +20% (es +21%)

Retornos logarítmicos: Se pueden sumar
  0.0953 + 0.0953 = 0.1906 ✓
```

### Desviación Estándar (σ)

**Definición**: Medida de cuánto se dispersan los datos respecto a su promedio.

**Interpretación**:
- σ pequeña → Datos concentrados (baja volatilidad)
- σ grande → Datos dispersos (alta volatilidad)

**Regla 68-95-99.7**:
- 68% de datos están dentro de ±1σ
- 95% de datos están dentro de ±2σ
- 99.7% de datos están dentro de ±3σ

**Ejemplo**:
```
Retornos diarios de Bitcoin:
Media = 0.1% al día
σ = 3%

Interpretación:
- 68% de los días: entre -2.9% y +3.1%
- 95% de los días: entre -5.9% y +6.1%
- Días fuera de ±3σ son eventos raros
```

### Correlación (ρ)

**Definición**: Medida de cómo se mueven dos activos entre sí.

**Valores**:
```
ρ = +1.0: Movimiento idéntico
ρ = +0.5: Tendencia similar pero no idéntica
ρ = 0.0:  Sin relación
ρ = -0.5: Tendencia opuesta moderada
ρ = -1.0: Movimiento perfectamente opuesto
```

**Ejemplo Visual**:
```
Alta Correlación (+0.9):
Bitcoin:   ↗↗↗↘↘↗↗
Ethereum:  ↗↗↗↘↘↗↗

Baja Correlación (0.1):
Bitcoin:   ↗↗↗↘↘↗↗
Litecoin:  ↘↗↘↗↗↘↗

Correlación Negativa (-0.8):
Bitcoin:  ↗↗↗↘↘↗↗
VIX:      ↘↘↘↗↗↘↘
```

**Uso**: Busca activos con baja correlación para diversificar.

### Compounding (Capitalización)

**Definición**: Reinvertir las ganancias para generar más ganancias sobre las ganancias.

**Ejemplo sin compounding**:
```
Capital: 1.000€
Retorno: 10% mensual sin reinvertir

Mes 1: 1.000 + 100 = 1.100 (guardar los 100)
Mes 2: 1.000 + 100 = 1.100 (guardar otros 100)
Mes 12: 1.000 + (100 × 12) = 2.200€
```

**Ejemplo con compounding**:
```
Capital: 1.000€
Retorno: 10% mensual reinvirtiendo

Mes 1: 1.000 × 1.10 = 1.100€
Mes 2: 1.100 × 1.10 = 1.210€
Mes 3: 1.210 × 1.10 = 1.331€
...
Mes 12: 3.138€
```

**Diferencia**: 3.138€ vs 2.200€ → 938€ extra por el poder del compounding.

**Fórmula**:
```
Valor Final = Valor Inicial × (1 + r)^n

donde:
r = retorno por periodo
n = número de periodos
```

---

## ⚙️ Configuración del Sistema

### Trading Interval (Intervalo de Trading)

**Definición**: Frecuencia con la que el bot busca oportunidades.

**En BotV2**: 60 segundos (cada minuto)

**Impacto**:
- Intervalo corto (30s): Más operaciones, más comisiones
- Intervalo largo (5min): Menos operaciones, puede perder oportunidades

### Max Position Size (Tamaño Máximo de Posición)

**Definición**: Porcentaje máximo del capital que puedes invertir en una sola posición.

**En BotV2**: 15% (450€ si tienes 3.000€)

**Razón**: Diversificación - no poner todos los huevos en la misma cesta.

### Confidence Threshold (Umbral de Confianza)

**Definición**: Nivel mínimo de confianza que debe tener una señal para ejecutarse.

**En BotV2**: 50% (0.5)

**Ejemplo**:
```
Ensemble genera señal de COMPRA con 45% confianza → RECHAZADA
Ensemble genera señal de COMPRA con 62% confianza → ACEPTADA y ejecutada
```

**Ajuste**:
- Threshold alto (70%): Menos trades pero mayor calidad
- Threshold bajo (30%): Más trades pero menor calidad

---

## 🚨 Alertas y Eventos

### Liquidation Cascade (Cascada de Liquidaciones)

**Definición**: Efecto dominó de liquidaciones forzadas que amplifica movimientos de precio.

**Secuencia**:
```
1. BTC cae 2% rápidamente
2. Traders con apalancamiento son liquidados
3. Sus posiciones se cierran automáticamente (más ventas)
4. Esto hace que el precio caiga más
5. Provoca más liquidaciones
6. Ciclo se repite (cascada)
```

**Detección en BotV2**:
```
Cascade Risk = Volume_Spike × Price_Drop_Speed × Recent_Liquidations

Si Cascade Risk > 60% → Reduce posiciones (evita quedar atrapado)
```

### Regime Change (Cambio de Régimen)

**Definición**: Cambio fundamental en el comportamiento del mercado.

**Ejemplos**:
- De mercado alcista a bajista
- De baja a alta volatilidad
- De trending a lateral

**Impacto**: Estrategias que funcionaban bien pueden dejar de funcionar.

**BotV2 Response**: Ajusta pesos de estrategias automáticamente vía Adaptive Allocation.

---

## 📚 Glosario Rápido

| Término | Definición Corta |
|---------|------------------|
| **Apalancamiento** | Pedir prestado para amplificar ganancias (y pérdidas) |
| **Backtest** | Probar una estrategia con datos históricos |
| **Bull Market** | Mercado alcista (precios subiendo) |
| **Bear Market** | Mercado bajista (precios bajando) |
| **Candle** | Representación gráfica del precio en un periodo |
| **Exchange** | Plataforma donde se compran/venden criptomonedas |
| **Fee** | Comisión que cobra el exchange por cada operación |
| **FOMO** | Fear Of Missing Out (miedo a perderse ganancias) |
| **FUD** | Fear, Uncertainty, Doubt (información negativa) |
| **Hedge** | Posición para protegerse de pérdidas |
| **Leverage** | Ver Apalancamiento |
| **Long** | Comprar esperando que suba |
| **Order Book** | Lista de todas las órdenes de compra/venta |
| **P&L** | Profit & Loss (ganancias y pérdidas) |
| **Paper Trading** | Trading simulado (sin dinero real) |
| **Pump and Dump** | Manipulación: subir precio artificialmente y vender |
| **Resistance** | Nivel de precio difícil de superar al alza |
| **Short** | Vender esperando que baje |
| **Support** | Nivel de precio que sostiene caídas |
| **Ticker** | Símbolo del activo (BTC, ETH, etc.) |
| **Whale** | Inversor con mucho capital (puede mover mercados) |

---

## 🎓 Recursos de Aprendizaje

### Para Principiantes
1. **Conceptos básicos**: Capital, Posición, ROI, Win Rate
2. **Indicadores simples**: MA, RSI, Bollinger Bands
3. **Gestión de riesgo**: Stop Loss, Position Sizing, Circuit Breaker

### Para Intermedios
1. **Métricas avanzadas**: Sharpe Ratio, Drawdown, Profit Factor
2. **Indicadores complejos**: MACD, ATR, ADX
3. **Estrategias**: Momentum, Mean Reversion, Breakout

### Para Avanzados
1. **Matemáticas**: Correlación, Z-scores, Kelly Criterion
2. **Arbitraje**: Cross-exchange, Statistical
3. **Arquitectura del sistema**: Ensemble, Adaptive Allocation, State Management

---

## ❓ FAQs

### ¿Qué significa un Sharpe Ratio de 2.5?
Por cada unidad de riesgo que asumes, obtienes 2.5 unidades de retorno. Es excelente (la mayoría de fondos profesionales tienen < 2.0).

### ¿Por qué el bot no opera a veces?
Puede ser porque:
1. No hay señales con suficiente confianza (< 50%)
2. Circuit breaker activado (pérdidas del día superaron límites)
3. Datos de mercado no válidos
4. Correlation muy alta entre estrategias

### ¿Cuánto puedo ganar/perder?
**Expectativa realista**:
- Retorno anual objetivo: 50-100%
- Drawdown máximo tolerado: -20%
- Días perdedores: 30-40%

**Recuerda**: Resultados pasados no garantizan resultados futuros.

### ¿El bot garantiza ganancias?
**NO**. Ningún sistema de trading garantiza ganancias. BotV2 implementa las mejores prácticas de gestión de riesgo, pero siempre hay riesgo de pérdida.

### ¿Necesito conocimientos técnicos para usar el bot?
Para **usar** el bot: No, solo configurar parámetros básicos.
Para **entender** lo que hace: Este documento es suficiente.
Para **modificar** el bot: Sí, se requiere programación en Python.

---

## 📞 Soporte

Para dudas sobre conceptos específicos:
1. Revisa este diccionario
2. Consulta la documentación técnica en `/docs`
3. Revisa el código fuente (está comentado)

---

**Versión**: 1.0.0  
**Última Actualización**: Enero 2026  
**Autor**: Juan Carlos Garcia Arriero  
**Propósito**: Educativo - Uso Personal

---

## 📊 Tabla de Referencia Rápida

| Métrica | Malo | Regular | Bueno | Excelente |
|---------|------|---------|-------|-----------|
| Sharpe Ratio | < 1.0 | 1.0-1.5 | 1.5-2.5 | > 2.5 |
| Win Rate | < 45% | 45-55% | 55-65% | > 65% |
| Profit Factor | < 1.0 | 1.0-1.5 | 1.5-2.0 | > 2.0 |
| Max Drawdown | > -30% | -20% a -30% | -10% a -20% | < -10% |
| Recovery Factor | < 2.0 | 2.0-3.0 | 3.0-5.0 | > 5.0 |

---

**¡Este diccionario es un documento vivo! Se actualiza conforme el sistema evoluciona.**
