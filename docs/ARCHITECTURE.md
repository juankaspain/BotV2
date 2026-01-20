BotV2/
├── src/
│   ├── main.py                 # Main entry point
│   ├── config/
│   │   ├── settings.yaml       # Configuration
│   │   └── config_manager.py   # Config loader
│   ├── core/
│   │   ├── risk_manager.py     # Risk management
│   │   ├── execution_engine.py # Order execution
│   │   ├── state_manager.py    # State persistence
│   │   └── liquidation_detector.py
│   ├── data/
│   │   ├── data_validator.py   # Data validation
│   │   └── normalization_pipeline.py
│   ├── ensemble/
│   │   ├── adaptive_allocation.py
│   │   ├── correlation_manager.py
│   │   └── ensemble_voting.py
│   ├── strategies/             # 20 strategies
│   │   ├── momentum.py
│   │   ├── stat_arb.py
│   │   ├── cross_exchange_arb.py
│   │   └── ...
│   ├── backtesting/
│   │   ├── realistic_simulator.py
│   │   └── market_microstructure.py
│   └── dashboard/
│       └── web_app.py          # Real-time dashboard
├── tests/                      # Test suite
├── docs/                       # Documentation
└── logs/                       # Log files
