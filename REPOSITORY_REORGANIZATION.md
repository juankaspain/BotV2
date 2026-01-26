# BotV2 Repository Reorganization Plan

This document outlines the strategy for separating the **Trading Bot** and the **Dashboard** into distinct modules for better maintainability and independent deployment.

## 🏗️ New Architecture Overview

```text
BotV2/
├── bot/                # Trading Bot Module
├── dashboard/          # Dashboard Module
├── shared/             # Shared code (config, utils, models)
├── tests/              # Organized tests
├── docs/               # Module-specific documentation
├── scripts/            # Utility scripts
└── docker/             # Docker configurations
```

## 🤖 Bot Module (`/bot`)
Contains everything related to the trading logic and engine.
- **Entry point:** `bot/main.py`
- **Logic:** Core trading, strategies, exchange adapters, backtesting, AI/ML models.

## 📊 Dashboard Module (`/dashboard`)
Contains the web interface and API endpoints.
- **Entry point:** `dashboard/web_app.py`
- **Logic:** Flask/Dash app, routes, models, mock data, monitors.

## 📦 Shared Module (`/shared`)
Code reused by both applications to avoid duplication.
- `shared/config/`: Secret validation and environment config.
- `shared/utils/`: Logging, validators, shared helper functions.
- `shared/models/`: Shared data structures.

---

## 🔄 Migration Plan (Git Commands)

### 1. Create Base Directories
```bash
mkdir -p bot dashboard shared/config shared/utils shared/models tests/bot tests/dashboard tests/shared
```

### 2. Move Bot Files
```bash
git mv src/main.py bot/
git mv src/core/ bot/
git mv src/strategies/ bot/
git mv src/exchanges/ bot/
git mv src/ai/ bot/
git mv src/backtesting/ bot/
git mv src/ensemble/ bot/
git mv src/data/ bot/
git mv src/security/ bot/
git mv src/notifications/ bot/
git mv src/utils/ bot/
```

### 3. Move Dashboard Files
```bash
git mv src/dashboard/* dashboard/
# Move specific dashboard files from src/ if any
```

### 4. Extract Shared Code
```bash
git mv src/config/secrets_validator.py shared/config/
# Extract other shared logic as needed
```

### 5. Update Imports
A search-and-replace for imports will be required:
- `from src.core...` -> `from bot.core...`
- `from src.dashboard...` -> `from dashboard...`
- `from config.secrets_validator...` -> `from shared.config.secrets_validator...`

---

## 🐳 Docker Integration

Each module will have its own optimized Dockerfile.

### Bot Dockerfile (`docker/Dockerfile.bot`)
- Focused on minimal size for background processes.
- No web server dependencies.

### Dashboard Dockerfile (`docker/Dockerfile.dashboard`)
- Includes web assets and static files.
- Optimized for Flask/Dash performance.

---

## 🧪 Verification Steps
1. Run `pip install -r requirements.txt`
2. Execute bot: `python bot/main.py`
3. Execute dashboard: `python dashboard/web_app.py`
4. Run all tests: `pytest tests/`
5. Build and run via Docker Compose.

---
*Created on: 26-01-2026*
