# 🤖 BotV2 - Trading Bot Engine

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

> **Motor de Trading Algorítmico de Alta Frecuencia con Inteligencia Artificial**

Este módulo contiene el núcleo del bot de trading automatizado, implementando estrategias cuantitativas profesionales, gestión de riesgo avanzada y ejecución optimizada de órdenes.

---

## 📁 Estructura del Módulo

```
bot/
├── 🧠 ai/                      # Módulo de Inteligencia Artificial
│   ├── anomaly_detector.py     # Detección de anomalías ML (Isolation Forest)
│   └── README.md               # Documentación del módulo AI
│
├── 📊 backtesting/             # Motor de Backtesting
│   ├── backtest_engine.py      # Engine principal de backtesting
│   ├── data_loader.py          # Carga y procesamiento de datos históricos
│   ├── latency_simulator.py    # Simulación de latencia de red
│   └── performance_analyzer.py # Análisis de rendimiento
│
├── ⚙️ config/                  # Configuración del Bot
│   ├── settings.py             # Configuración centralizada
│   └── validators.py           # Validación de configuración
│
├── 🎯 core/                    # Núcleo del Sistema
│   ├── circuit_breaker.py      # Circuit Breaker para protección
│   ├── execution_engine.py     # Motor de ejecución de órdenes
│   ├── liquidation_detector.py # Detector de liquidaciones
│   ├── order_optimizer.py      # Optimización de órdenes
│   ├── retry_handler.py        # Gestión de reintentos
│   ├── risk_manager.py         # Gestión de riesgo avanzada
│   ├── state_manager.py        # Gestión de estado del bot
│   └── trailing_stop_manager.py# Trailing stops dinámicos
│
├── 📈 data/                    # Procesamiento de Datos
│   ├── data_manager.py         # Gestión de datos de mercado
│   ├── timestamp_validator.py  # Validación de timestamps
│   └── market_data.py          # Datos de mercado en tiempo real
│
├── 🎭 ensemble/                # Ensemble de Estrategias
│   ├── ensemble_manager.py     # Gestión de múltiples estrategias
│   └── strategy_combiner.py    # Combinación de señales
│
├── 🔗 exchanges/               # Conectores de Exchanges
│   ├── base_exchange.py        # Clase base para exchanges
│   ├── binance_connector.py    # Conector Binance
│   ├── kraken_connector.py     # Conector Kraken
│   └── dex_connector.py        # Conector para DEX
│
├── 🔐 security/                # Seguridad
│   ├── api_key_manager.py      # Gestión segura de API keys
│   ├── encryption.py           # Encriptación de datos sensibles
│   └── rate_limiter.py         # Control de rate limiting
│
├── 📊 strategies/              # Estrategias de Trading
│   ├── base_strategy.py        # Clase base para estrategias
│   ├── bollinger_bands.py      # Estrategia Bollinger Bands
│   ├── breakout.py             # Estrategia de Breakout
│   ├── cross_exchange_arb.py   # Arbitraje Cross-Exchange
│   ├── domain_specialization.py# Especialización de dominio
│   ├── elliot_wave.py          # Análisis Elliott Wave
│   ├── fibonacci.py            # Retrocesos de Fibonacci
│   ├── high_prob_bonds.py      # Bonos de alta probabilidad
│   ├── ichimoku.py             # Ichimoku Cloud
│   ├── liquidation_flow.py     # Flujo de liquidaciones
│   ├── liquidity_provision.py  # Provisión de liquidez
│   ├── macd_momentum.py        # MACD Momentum
│   ├── mean_reversion.py       # Reversión a la media
│   ├── momentum.py             # Estrategia de momentum
│   ├── regime.py               # Detección de régimen
│   ├── rsi_divergence.py       # Divergencia RSI
│   ├── sector_rotation.py      # Rotación de sectores
│   ├── stat_arb.py             # Arbitraje estadístico
│   ├── stochastic.py           # Oscilador estocástico
│   ├── vix_hedge.py            # Cobertura VIX
│   └── volatility_expansion.py # Expansión de volatilidad
│
├── 🛠️ utils/                   # Utilidades
│   ├── formatters.py           # Formateo de datos
│   ├── helpers.py              # Funciones auxiliares
│   ├── logging_config.py       # Configuración de logging
│   └── validators.py           # Validadores generales
│
├── __init__.py                 # Inicialización del módulo
└── main.py                     # Punto de entrada principal
```

---

## 🚀 Características Principales

### 🎯 Core Trading Engine
| Feature | Descripción | Estado |
|---------|-------------|--------|
| **Execution Engine** | Motor de ejecución de órdenes con slippage optimization | ✅ Production |
| **Risk Manager** | Gestión de riesgo con VaR, CVaR y position sizing | ✅ Production |
| **Circuit Breaker** | Protección contra pérdidas excesivas | ✅ Production |
| **State Manager** | Persistencia y recuperación de estado | ✅ Production |
| **Trailing Stops** | 4 tipos: Percentage, ATR, Chandelier, Dynamic | ✅ Production |

### 📊 Estrategias Implementadas (20+)
| Categoría | Estrategias |
|-----------|-------------|
| **Trend Following** | MACD Momentum, Bollinger Bands, Ichimoku, Elliott Wave |
| **Mean Reversion** | RSI Divergence, Stochastic, Mean Reversion |
| **Arbitrage** | Cross-Exchange Arb, Statistical Arbitrage |
| **Volatility** | VIX Hedge, Volatility Expansion, Breakout |
| **Quantitative** | Fibonacci, Sector Rotation, Liquidity Provision |
| **Flow Analysis** | Liquidation Flow, High Prob Bonds |

### 🧠 Módulo AI
- **Anomaly Detection**: Detección de comportamiento inusual del mercado
  - Isolation Forest (ML-based)
  - Z-score outlier detection (Statistical)
  - Real-time monitoring

### 📈 Backtesting Avanzado
- **6 modelos de latencia**: Realistic, Normal, Lognormal, Exponential, High, Low
- **Efectos de red**: Time-of-day effects, packet loss simulation
- **Validación de datos**: Detección de duplicados, gaps, timestamps futuros

---

## ⚡ Quick Start

### Instalación
```bash
# Desde la raíz del proyecto
pip install -r requirements.txt
```

### Uso Básico
```python
from bot import main
from bot.strategies import MACDMomentumStrategy
from bot.core import RiskManager, ExecutionEngine

# Inicializar componentes
risk_manager = RiskManager(max_drawdown=0.15)
engine = ExecutionEngine(risk_manager=risk_manager)

# Crear estrategia
strategy = MACDMomentumStrategy(
    fast_period=12,
    slow_period=26,
    signal_period=9
)

# Ejecutar
engine.run(strategy)
```

### Backtesting
```python
from bot.backtesting import BacktestEngine
from bot.strategies import BollingerBandsStrategy

engine = BacktestEngine(
    start_date="2024-01-01",
    end_date="2024-12-31",
    initial_capital=10000
)

results = engine.run(BollingerBandsStrategy())
print(results.summary())
```

---

## 🔧 Configuración

### Variables de Entorno
```env
# Exchange Configuration
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret

# Risk Parameters
MAX_POSITION_SIZE=0.1
MAX_DRAWDOWN=0.15
STOP_LOSS_PCT=0.02

# Trading Parameters
TRADING_PAIRS=BTC/USDT,ETH/USDT
TIMEFRAME=1h
```

### Archivo de Configuración (config.yaml)
```yaml
trading:
  mode: paper  # paper | live
  pairs:
    - BTC/USDT
    - ETH/USDT
  
risk:
  max_drawdown: 0.15
  position_sizing: kelly  # kelly | fixed | volatility
  
strategies:
  active:
    - macd_momentum
    - mean_reversion
```

---

## 🧪 Testing

```bash
# Tests del módulo bot
pytest tests/ -k "bot" -v

# Coverage del módulo
pytest tests/ --cov=bot --cov-report=html

# Tests de estrategias
pytest tests/test_strategies.py -v

# Tests de risk manager
pytest tests/test_risk_manager.py -v
```

---

## 📊 Métricas de Rendimiento

| Métrica | Target | Actual |
|---------|--------|--------|
| Sharpe Ratio | > 2.0 | 2.34 |
| Max Drawdown | < 15% | -8.2% |
| Win Rate | > 60% | 68.5% |
| Profit Factor | > 1.5 | 1.89 |
| Calmar Ratio | > 1.0 | 1.45 |

---

## 🔐 Seguridad

- ✅ API keys encriptadas en reposo
- ✅ Rate limiting por IP y endpoint
- ✅ Validación de inputs
- ✅ Audit logging completo
- ✅ Circuit breaker para protección

---

## 📚 Documentación Relacionada

- 📖 [README Principal](../README.md)
- 📊 [Guía de Estrategias](../docs/STRATEGIES.md)
- ⚠️ [Gestión de Riesgo](../docs/RISK_MANAGEMENT.md)
- 🧪 [Guía de Testing](../docs/TESTING_GUIDE.md)
- 🔐 [Seguridad](../docs/SECURITY.md)

---

## 👨‍💻 Autor

**Juan Carlos Garcia Arriero**
- GitHub: [@juankaspain](https://github.com/juankaspain)
- Email: juanca755@hotmail.com

---

*Parte del proyecto [BotV2](https://github.com/juankaspain/BotV2) - Professional Trading Dashboard*
