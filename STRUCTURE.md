# BotV2 - Repository Structure

This document describes the reorganized structure of the BotV2 project.

## Overview

BotV2 has been reorganized into a clean, modular structure with clear separation of concerns:

```
BotV2/
├── bot/                      # Main trading bot implementation
│   ├── __init__.py
│   ├── main.py              # Bot entry point
│   ├── engine/              # Trading engine core logic
│   ├── exchanges/           # Exchange integrations (Binance, KuCoin, etc.)
│   ├── execution/           # Trade execution module
│   ├── risk/                # Risk management module
│   ├── strategies/          # Trading strategies
│   └── utils/               # Bot-specific utilities
│
├── dashboard/               # Web-based trading dashboard
│   ├── __init__.py
│   ├── app.py              # Dashboard main app
│   ├── routes/             # API routes
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
│
├── shared/                  # Shared components across modules
│   ├── __init__.py
│   ├── config/             # Configuration management
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   └── secrets_validator.py
│   ├── data/               # Data models and utilities
│   │   └── __init__.py
│   └── utils/              # Shared utilities
│       ├── __init__.py
│       ├── logging.py
│       └── helpers.py
│
├── scripts/                 # Utility and deployment scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── maintenance/
│
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── docs/                    # Documentation
│   ├── api/
│   ├── deployment/
│   └── trading_strategies/
│
├── config.yaml              # Unified configuration file
├── requirements.txt         # Unified dependencies for all environments
├── docker-compose.yml       # Docker composition
├── Dockerfile               # Production container
├── .env.example             # Environment variables template
├── pytest.ini               # Pytest configuration
└── README.md                # Project overview
```

## Module Descriptions

### bot/
The core trading bot implementation. This is where all bot logic resides.

**Subdirectories:**
- `engine/`: Core trading logic, market analysis, and decision making
- `exchanges/`: Exchange API connectors and market data fetching
- `execution/`: Order placement and execution management
- `risk/`: Position sizing, stop loss, take profit logic
- `strategies/`: Individual trading strategy implementations
- `utils/`: Bot-specific utility functions

### dashboard/
Web-based interface for monitoring and controlling the bot.

**Features:**
- Real-time portfolio monitoring
- Trading history and statistics
- Strategy performance analytics
- Manual trade execution controls
- Alerts and notifications configuration

### shared/
Reusable components shared across bot and dashboard.

**Subdirectories:**
- `config/`: Configuration management and secrets validation
- `data/`: Shared data models and database utilities
- `utils/`: Common logging, helpers, and utilities

### scripts/
Utility scripts for setup, deployment, and maintenance.

### tests/
Comprehensive test suite with unit and integration tests.

### docs/
Project documentation including API docs and deployment guides.

## Configuration Management

All configuration is centralized in `config.yaml` at the root of the project.

**Configuration Sections:**
- `app`: General application settings
- `bot`: Bot core settings and modules
- `strategies`: Strategy configuration
- `exchanges`: Exchange API credentials
- `database`: Database connection settings
- `cache`: Caching backend configuration
- `notifications`: Alert and notification settings
- `logging`: Logging configuration
- `api`: REST API server settings

**Environment Variables:**
Sensitive data (API keys, passwords) should be provided via environment variables:
- `${BINANCE_API_KEY}` and `${BINANCE_API_SECRET}`
- `${DB_USER}` and `${DB_PASSWORD}`
- And others as needed (see `.env.example`)

## Dependencies

All project dependencies are listed in `requirements.txt` with sections for:
- Core configuration and processing (PyYAML, numpy, pandas)
- Trading & exchange APIs (requests, websockets, ccxt, backtrader)
- Web framework (Flask and extensions)
- Monitoring and metrics (prometheus-client)
- Testing (pytest and plugins)
- Security (cryptography)

**Installation:**
```bash
pip install -r requirements.txt
```

## Running the Project

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot/main.py

# Run the dashboard
python -m flask --app dashboard.app run
```

### Docker Deployment
```bash
# Build the image
docker build -t botv2:latest .

# Run with docker-compose
docker-compose up -d
```

## Package Initialization

Each directory with Python modules includes an `__init__.py` file, making them proper Python packages. This enables:
- Absolute and relative imports within packages
- Namespace management
- Package-level initialization

## Best Practices

1. **Import Style**: Use absolute imports from the root (e.g., `from bot.engine import Trading`)
2. **Configuration**: Always read from the unified `config.yaml` through the config manager
3. **Logging**: Use the shared logging utilities from `shared.utils.logging`
4. **Secrets**: Never hardcode credentials; use environment variables
5. **Testing**: Write tests for new features in the appropriate `tests/` subdirectory

## Migration Notes

This reorganization consolidates the previous scattered structure:
- Code previously in `src/` has been reorganized into `bot/` and `shared/`
- `src/config/` settings are now managed through the unified `config.yaml`
- Multiple requirements files have been unified into a single `requirements.txt`
- All modules now have proper `__init__.py` files for package initialization

## Future Improvements

- Microservices architecture for scalability
- Additional exchange integrations
- Enhanced monitoring and alerting
- Machine learning model integration
