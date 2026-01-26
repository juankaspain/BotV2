# BotV2 Comprehensive Restructuring Plan

## Objective
Reorganize the BotV2 project to separate bot-specific code from dashboard-specific code while maintaining shared utilities. The structure will be professional and scalable.

## Directory Structure After Reorganization

### BOT Module (`bot/`)
Trading bot specific code

```
bot/
├── __init__.py                 # Bot module initialization
├── main.py                     # Entry point (existing)
├── strategies/                 # Trading strategies
│   ├── __init__.py
│   ├── base.py                # Base strategy class
│   ├── momentum.py            # Momentum strategy (from src/strategies/)
│   ├── mean_reversion.py      # Mean reversion strategy
│   ├── breakout.py            # Breakout strategy
│   ├── stat_arb.py            # Statistical arbitrage
│   ├── regime.py              # Regime detection
│   ├── volatility_expansion.py# Volatility expansion
│   └── ... (other strategies)
├── exchanges/                  # Exchange integrations
│   ├── __init__.py
│   ├── base.py                # Base exchange adapter
│   ├── binance.py             # Binance integration
│   ├── coinbase.py            # Coinbase integration
│   ├── kraken.py              # Kraken integration
│   └── polymarket.py          # Polymarket integration
├── execution/                  # Order execution logic
│   ├── __init__.py
│   ├── executor.py            # Main execution engine
│   ├── order_manager.py       # Order management
│   └── slippage.py            # Slippage calculation
├── risk/                       # Risk management
│   ├── __init__.py
│   ├── circuit_breaker.py     # Circuit breaker logic
│   ├── position_sizing.py     # Position sizing calculator
│   └── correlation_manager.py # Correlation management
├── engine/                     # Trading engine
│   ├── __init__.py
│   └── trading_engine.py      # Main trading engine (from src/core/)
└── utils/                      # Bot-specific utilities
    ├── __init__.py
    └── trade_logger.py        # Trade logging utilities
```

### DASHBOARD Module (`dashboard/`)
Web dashboard specific code

```
dashboard/
├── __init__.py                # Dashboard module initialization
├── web_app.py                 # Entry point (existing)
├── api/                        # REST API endpoints
│   ├── __init__.py
│   ├── routes.py              # API routes
│   ├── handlers.py            # Request handlers
│   └── middleware.py          # API middleware
├── components/                 # UI components
│   ├── __init__.py
│   ├── charts.py              # Chart components
│   ├── metrics.py             # Metrics display components
│   └── widgets.py             # Other UI widgets
├── pages/                      # Dashboard pages
│   ├── __init__.py
│   ├── overview.py            # Overview page
│   ├── strategies.py          # Strategies page
│   ├── positions.py           # Positions page
│   └── performance.py         # Performance page
├── static/                     # Static files (CSS, JS, images)
│   └── ...
├── templates/                  # HTML templates
│   └── ...
└── utils/                      # Dashboard-specific utilities
    ├── __init__.py
    └── formatters.py          # Data formatters
```

### SHARED Module (`shared/`)
Common code used by both bot and dashboard

```
shared/
├── config/                     # Configuration management (existing)
│   ├── __init__.py
│   ├── config_manager.py      # ConfigManager singleton
│   └── secrets_validator.py   # Secrets validation
├── data/                       # Data processing (from src/data/)
│   ├── __init__.py
│   ├── validators.py          # Data validation
│   ├── processors.py          # Data processors
│   └── gap_detection.py       # Gap detection logic
├── utils/                      # General utilities
│   ├── __init__.py
│   ├── logging.py             # Logging configuration
│   ├── helpers.py             # General helper functions
│   └── decorators.py          # Useful decorators
├── security/                   # Security utilities (from src/security/)
│   ├── __init__.py
│   ├── rate_limiter.py        # Rate limiting
│   ├── encryption.py          # Encryption utilities
│   └── validators.py          # Security validators
├── models/                     # Data models/schemas
│   ├── __init__.py
│   ├── trade.py               # Trade model
│   ├── position.py            # Position model
│   └── order.py               # Order model
└── notifications/             # Alert system (from src/notifications/)
    ├── __init__.py
    ├── alerts.py              # Alert system
    └── dispatchers.py         # Notification dispatchers
```

### SRC Module (`src/`)
Keep only supporting modules that don't fit elsewhere

```
src/
├── ai/                        # AI/ML modules (used by both)
│   ├── __init__.py
│   └── ...
├── ensemble/                  # Ensemble methods (from src/ensemble/)
│   ├── __init__.py
│   └── ...
├── backtesting/              # Backtesting engine (bot-specific)
│   ├── __init__.py
│   └── ... (OPTIONAL: can move to bot/ if bot-exclusive)
├── core/                      # Core utilities
│   ├── __init__.py
│   └── ...
└── main.py                   # Keep for backward compatibility (deprecated)
```

## Migration Steps

### Phase 1: Create Directory Structure
- [ ] Create `bot/` subdirectories: strategies, exchanges, execution, risk, engine, utils
- [ ] Create `dashboard/` subdirectories: api, components, pages, static, templates, utils
- [ ] Create `shared/` subdirectories: data, utils, security, models, notifications

### Phase 2: Move Bot-Specific Files
- [ ] Move `src/strategies/*` → `bot/strategies/`
- [ ] Move `src/exchanges/*` → `bot/exchanges/`
- [ ] Create `bot/execution/` with execution logic from `src/core/`
- [ ] Create `bot/risk/` with risk management logic
- [ ] Move `src/core/trading_engine.py` → `bot/engine/`

### Phase 3: Move Dashboard-Specific Files
- [ ] Move `src/dashboard/*` → `dashboard/`
- [ ] Create `dashboard/api/` for REST endpoints
- [ ] Create `dashboard/components/` for UI components
- [ ] Create `dashboard/pages/` for dashboard pages

### Phase 4: Move Shared Files
- [ ] Move `src/data/*` → `shared/data/`
- [ ] Move `src/security/*` → `shared/security/`
- [ ] Move `src/notifications/*` → `shared/notifications/`
- [ ] Create `shared/models/` with common data models
- [ ] Create `shared/utils/` with common utilities

### Phase 5: Update Imports
- [ ] Update imports in `bot/main.py`
- [ ] Update imports in `dashboard/web_app.py`
- [ ] Update imports in all bot modules
- [ ] Update imports in all dashboard modules
- [ ] Update imports in all shared modules

### Phase 6: Update Entry Points
- [ ] Update `bot/main.py` to use new import paths
- [ ] Update `dashboard/web_app.py` to use new import paths
- [ ] Update Docker configuration if needed
- [ ] Update documentation

### Phase 7: Verification
- [ ] Run import tests
- [ ] Run bot functionality tests
- [ ] Run dashboard functionality tests
- [ ] Verify all configurations load correctly

## Import Patterns After Reorganization

### In Bot Code
```python
# Strategies
from bot.strategies import BaseStrategy, MomentumStrategy
from bot.exchanges import BinanceExchange, PolymarketExchange
from bot.execution import OrderExecutor
from bot.risk import CircuitBreaker, PositionSizer
from bot.engine import TradingEngine

# Shared
from shared.config import ConfigManager
from shared.data import DataValidator, DataProcessor
from shared.security import RateLimiter
from shared.models import Trade, Position
from shared.notifications import AlertSystem
from shared.utils import Logger
```

### In Dashboard Code
```python
# Dashboard components
from dashboard.api import APIRoutes
from dashboard.components import Charts, Metrics
from dashboard.pages import OverviewPage, StrategiesPage

# Shared
from shared.config import ConfigManager
from shared.models import Trade, Position
from shared.notifications import AlertSystem
from shared.utils import Logger
```

## Benefits of This Structure

1. **Clear Separation of Concerns**
   - Bot logic is isolated from dashboard logic
   - Easy to understand what each module does

2. **Improved Maintainability**
   - Bot developers don't need to understand dashboard code
   - Dashboard developers don't need to understand trading strategies

3. **Easier Testing**
   - Can test bot independently
   - Can test dashboard independently
   - Can test shared modules independently

4. **Better Scalability**
   - Easy to add new strategies
   - Easy to add new exchange integrations
   - Easy to add new dashboard pages

5. **Cleaner Imports**
   - No circular dependencies
   - Clear import paths
   - Easy to identify dependencies

## Timeline

Expected completion: Single session
- Phase 1-2: 20-30 minutes
- Phase 3-4: 20-30 minutes
- Phase 5: 20-30 minutes
- Phase 6: 10-15 minutes
- Phase 7: 5-10 minutes

## Validation Checklist

- [ ] All imports resolve correctly
- [ ] No circular dependencies
- [ ] Bot starts without errors
- [ ] Dashboard starts without errors
- [ ] Configuration loads correctly
- [ ] All modules can be imported individually
- [ ] No missing __init__.py files
- [ ] All relative imports work correctly
- [ ] Docker containers build successfully
- [ ] Tests pass

## Notes

- Keep `src/` for backward compatibility, but make it a transition layer
- Consider creating adapter modules in `src/` that import from new locations
- Update documentation to reflect new structure
- Update ARCHITECTURE.md to document new structure
