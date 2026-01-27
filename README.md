<div align="center">

# 🤖 BotV2 - Advanced Algorithmic Trading System

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/juankaspain/BotV2/releases)
[![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-70%2B%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](tests/)

**Enterprise-grade algorithmic trading bot with 20 strategies, real-time dashboard, and multi-exchange support**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Strategies](#-trading-strategies) • [Dashboard](#-dashboard) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Trading Strategies](#-trading-strategies)
- [Risk Management](#-risk-management)
- [Dashboard](#-dashboard)
- [Configuration](#-configuration)
- [Exchanges](#-exchanges)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

BotV2 is a **professional-grade algorithmic trading system** designed for cryptocurrency and prediction markets. Built with Python 3.11+, it combines sophisticated trading strategies with enterprise-level risk management and real-time monitoring capabilities.

### Key Highlights

| Feature | Description |
|---------|-------------|
| **20 Trading Strategies** | From momentum to statistical arbitrage |
| **Multi-Exchange Support** | Binance, Coinbase, Kraken, Polymarket |
| **Real-Time Dashboard** | Live monitoring with Dash/Plotly |
| **Advanced Risk Management** | Circuit breakers, trailing stops, Kelly criterion |
| **Enterprise Security** | JWT auth, rate limiting, HTTPS support |
| **Backtesting Engine** | Realistic simulation with slippage & latency |

---

## ✨ Features

### 🎯 Trading Engine
- **20 Unique Strategies** with ensemble voting
- **Adaptive Position Sizing** using Kelly Criterion
- **Order Optimization** (market, limit, hybrid, VWAP/TWAP)
- **Multi-Timeframe Analysis**

### 🛡️ Risk Management
- **3-Level Circuit Breaker** (5%, 10%, 15% drawdown)
- **Dynamic Trailing Stops** (percentage, ATR, Chandelier)
- **Correlation Management** to avoid concentrated risk
- **Liquidation Detection** for cascade protection

### 📊 Dashboard & Monitoring
- **Real-Time Portfolio Tracking**
- **Strategy Performance Analytics**
- **Interactive Charts** (equity curve, drawdown, heatmaps)
- **Secure Access** with JWT authentication

### ⚡ Technical Features
- **State Persistence** (PostgreSQL/SQLite/Redis)
- **Latency Simulation** for realistic backtesting
- **Data Validation** with drift detection
- **Docker Support** for easy deployment

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, SQLite by default)
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/juankaspain/BotV2.git
cd BotV2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `config.yaml` to customize:

```yaml
trading:
  initial_capital: 3000  # EUR
  max_position_size: 0.15  # 15% max per position
  max_open_positions: 10

risk:
  circuit_breaker:
    level_1_drawdown: -5.0  # Stop at -5% daily
    level_2_drawdown: -10.0  # Reduce size 50%
    level_3_drawdown: -15.0  # Emergency liquidation
```

### Running the Bot

```bash
# Start trading bot
python -m bot.main

# Start dashboard (separate terminal)
python -m dashboard.web_app

# Access dashboard at http://localhost:8050
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f botv2
```

---

## 🏗️ Architecture

```
BotV2/
├── bot/                    # Core trading engine
│   ├── ai/                 # AI/ML components
│   ├── backtesting/        # Backtesting engine
│   ├── config/             # Configuration management
│   ├── core/               # Core modules
│   │   ├── circuit_breaker.py
│   │   ├── execution_engine.py
│   │   ├── order_optimizer.py
│   │   ├── risk_manager.py
│   │   ├── state_manager.py
│   │   └── trailing_stop_manager.py
│   ├── data/               # Data processing
│   ├── ensemble/           # Strategy ensemble
│   ├── exchanges/          # Exchange adapters
│   ├── security/           # Security modules
│   ├── strategies/         # 20 trading strategies
│   └── utils/              # Utilities
├── dashboard/              # Web dashboard
│   ├── api/                # REST API
│   ├── components/         # UI components
│   ├── pages/              # Dashboard pages
│   └── templates/          # HTML templates
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── tests/                  # Test suite (70+ tests)
├── config.yaml             # Main configuration
├── docker-compose.yml      # Docker setup
└── requirements.txt        # Dependencies
```

---

## 📈 Trading Strategies

BotV2 implements **20 sophisticated trading strategies**:

### Base Strategies (15)

| Strategy | Type | Description |
|----------|------|-------------|
| `momentum` | Trend | Follows price momentum with RSI/MACD |
| `mean_reversion` | Counter-Trend | Exploits price mean reversion |
| `breakout` | Volatility | Captures breakout from consolidation |
| `stat_arb` | Arbitrage | Statistical arbitrage pairs trading |
| `regime` | Adaptive | Adapts to market regime changes |
| `volatility_expansion` | Volatility | Trades volatility expansions |
| `fibonacci` | Technical | Fibonacci retracements & extensions |
| `macd_momentum` | Trend | MACD-based momentum signals |
| `rsi_divergence` | Technical | RSI divergence patterns |
| `bollinger_bands` | Mean Reversion | Bollinger Bands strategies |
| `stochastic` | Oscillator | Stochastic oscillator signals |
| `ichimoku` | Trend | Ichimoku cloud analysis |
| `elliot_wave` | Pattern | Elliott Wave pattern recognition |
| `vix_hedge` | Hedging | VIX-based hedging strategy |
| `sector_rotation` | Rotation | Sector/asset rotation |

### Advanced Strategies (5)

| Strategy | Type | Description |
|----------|------|-------------|
| `cross_exchange_arb` | Arbitrage | Cross-exchange price arbitrage |
| `liquidation_flow` | Flow | Exploits liquidation cascades |
| `high_prob_bonds` | Fixed Income | High probability bond strategies |
| `liquidity_provision` | Market Making | Liquidity provision strategies |
| `domain_specialization` | ML | Domain-specific ML models |

### Ensemble System

- **Weighted Voting**: Strategies vote with confidence weights
- **Adaptive Allocation**: Sharpe-based weight adjustment
- **Correlation Management**: Reduces correlated positions
- **Minimum Agreement**: Requires 3+ strategies to agree

---

## 🛡️ Risk Management

### Circuit Breaker System

```
Level 1 (-5% DD)  →  Stop new trades, alert
Level 2 (-10% DD) →  Reduce positions 50%
Level 3 (-15% DD) →  Emergency liquidation
```

### Trailing Stops

| Type | Description |
|------|-------------|
| **Percentage** | Fixed % from highest price |
| **ATR-Based** | Volatility-adjusted stops |
| **Chandelier** | Chandelier Exit method |
| **Dynamic** | Adapts to market conditions |

### Position Sizing

- **Kelly Criterion**: Optimal bet sizing (25% Kelly)
- **Correlation Limits**: Max 0.7 correlation threshold
- **Portfolio Limits**: Max 15% per position

---

## 📊 Dashboard

Access the real-time dashboard at `http://localhost:8050`

### Features

- **Portfolio Overview**: Current value, P&L, metrics
- **Equity Curve**: Historical performance chart
- **Strategy Performance**: Individual strategy analytics
- **Risk Metrics**: Drawdown, Sharpe, Sortino ratios
- **Position Monitor**: Active positions and trailing stops
- **Correlation Heatmap**: Strategy correlation visualization

### Security

- JWT Authentication
- Rate Limiting (60 req/min)
- HTTPS Support
- IP Whitelisting (optional)
- Access Logging

---

## ⚙️ Configuration

### Main Config (`config.yaml`)

```yaml
system:
  name: "BotV2"
  version: "1.1.0"
  environment: "production"

trading:
  initial_capital: 3000
  trading_interval: 60  # seconds
  max_position_size: 0.15
  max_open_positions: 10

risk:
  circuit_breaker:
    level_1_drawdown: -5.0
    level_2_drawdown: -10.0
    level_3_drawdown: -15.0
  trailing_stops:
    enabled: true
    default_type: "percentage"
    activation_profit: 2.0
```

### Environment Variables (`.env`)

```bash
# Exchange API Keys
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret

# Dashboard Security
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=secure_password
DASHBOARD_JWT_SECRET=your_jwt_secret

# Database
POSTGRES_PASSWORD=your_db_password
```

---

## 🏦 Exchanges

| Exchange | Status | Description |
|----------|--------|-------------|
| **Binance** | ✅ Active | Full support, BTC/ETH/BNB pairs |
| **Coinbase Pro** | ✅ Ready | Optional, EUR pairs |
| **Kraken** | ✅ Ready | Optional, EUR pairs |
| **Polymarket** | ✅ Active | Prediction markets |
| **Finst** | 🔄 Preparatory | Awaiting API release |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System architecture details |
| [Configuration Guide](docs/CONFIG_GUIDE.md) | Complete config reference |
| [Order Optimization](docs/ORDER_OPTIMIZATION.md) | Order execution strategies |
| [Control Panel](docs/CONTROL_PANEL_V4.2.md) | Dashboard user guide |
| [Deployment](docs/deployment/) | Deployment guides |
| [API Reference](docs/reference/) | API documentation |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=bot --cov-report=html

# Run specific test module
pytest tests/test_strategies.py -v
```

**Test Coverage**: 95%+ target | 70+ test cases

---

## 🤝 Contributing

Contributions are welcome! Please read the contribution guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Juan Carlos García Arriero**

- GitHub: [@juankaspain](https://github.com/juankaspain)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

*Built with ❤️ for algorithmic trading*

</div>
