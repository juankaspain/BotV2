# BotV2 - Advanced Trading System

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

**BotV2** is a production-ready algorithmic trading system implementing 26 audit improvements across data validation, risk management, ensemble strategies, and realistic execution simulation.

## 🚀 Features

### Core Capabilities
- **20 Trading Strategies** (15 base + 5 advanced high-performance)
- **3-Level Circuit Breaker** for risk management
- **Adaptive Strategy Allocation** based on real-time Sharpe ratios
- **Correlation Management** to reduce portfolio risk
- **Ensemble Voting** with weighted aggregation
- **Realistic Backtesting** with market microstructure simulation
- **State Persistence** with PostgreSQL for crash recovery
- **Real-time Dashboard** with Flask/Dash

### 26 Audit Improvements Implemented

#### Round 1: Foundation
1. ✅ Comprehensive data validation (NaN, Inf, outliers, OHLC)
2. ✅ Z-score normalization pipeline
3. ✅ 3-level circuit breaker (-5%, -10%, -15%)
4. ✅ Kelly Criterion position sizing
5. ✅ State persistence with PostgreSQL
6. ✅ Automatic crash recovery
7. ✅ Structured logging with rotation

#### Round 2: Intelligence
8. ✅ Adaptive strategy allocation (Sharpe-based)
9. ✅ Exponential smoothing for stability
10. ✅ Correlation matrix calculation
11. ✅ Correlation-aware position sizing
12. ✅ Ensemble voting system
13. ✅ Weighted average voting
14. ✅ Confidence thresholds

#### Round 3: Execution
15. ✅ Realistic slippage modeling
16. ✅ Bid-ask spread simulation
17. ✅ Market impact calculation
18. ✅ Time-of-day effects
19. ✅ Partial fill simulation
20. ✅ Order book depth modeling
21. ✅ Liquidation cascade detection
22. ✅ Market microstructure model

#### Additional
23. ✅ 20 diversified strategies
24. ✅ Real-time performance dashboard
25. ✅ Comprehensive test suite
26. ✅ Production-ready deployment

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (optional, can use SQLite)
- 2GB RAM minimum

### Quick Start

```bash
# Clone repository
git clone https://github.com/juankaspain/BotV2.git
cd BotV2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL)
createdb botv2
export POSTGRES_PASSWORD="your_password"

# Run setup script
bash setup/create_structure.sh

# Start trading system
python src/main.py
