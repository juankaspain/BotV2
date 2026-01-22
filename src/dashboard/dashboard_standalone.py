#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BotV2 Dashboard - Standalone Entry Point with Demo Data
Runs dashboard with automatically generated demo data for testing and demos

Usage:
    python src/dashboard/dashboard_standalone.py
    
Access:
    http://localhost:8050/login
    Credentials: admin / [see console output for password]
"""

import sys
import os
import io
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np

# Force UTF-8 encoding for stdout in Docker containers
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockConfig:
    """Mock config object for standalone dashboard"""
    
    def __init__(self):
        self.data = {
            'dashboard': {
                'host': os.getenv('DASHBOARD_HOST', '0.0.0.0'),
                'port': int(os.getenv('DASHBOARD_PORT', 8050)),
                'debug': os.getenv('DEBUG', 'false').lower() == 'true'
            },
            'trading': {
                'initial_capital': 3000.0
            }
        }
    
    def get(self, key, default=None):
        """Get config value by key"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


def generate_demo_data():
    """
    Generate realistic demo trading data
    
    Returns:
        Tuple of (portfolio_history, trades_history, strategy_performance, risk_metrics)
    """
    logger.info("[DEMO] Generating demo trading data...")
    
    # ===== PORTFOLIO HISTORY (90 days) =====
    days = 90
    initial_capital = 3000.0
    current_equity = initial_capital
    
    portfolio_history = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=(days - i))
        
        # Random walk with positive drift
        daily_return = np.random.normal(0.001, 0.02)  # 0.1% daily return, 2% volatility
        current_equity = current_equity * (1 + daily_return)
        
        portfolio_history.append({
            'timestamp': date,
            'equity': max(2000, current_equity),  # Floor at 2000
            'cash': max(500, current_equity * 0.3),
            'positions': {
                'BTC/USD': {'size': 0.05, 'value': current_equity * 0.3},
                'ETH/USD': {'size': 1.2, 'value': current_equity * 0.25},
                'AAPL': {'size': 15, 'value': current_equity * 0.15}
            } if i > 10 else {}
        })
    
    logger.info(f"  [OK] Generated {len(portfolio_history)} portfolio snapshots")
    
    # ===== TRADES HISTORY (125 trades) =====
    trades_count = 125
    trades_history = []
    
    strategies = ['Momentum', 'Mean Reversion', 'Breakout', 'Pairs Trading', 'ML Model']
    symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL', 'TSLA', 'NVDA']
    actions = ['BUY', 'SELL']
    
    for i in range(trades_count):
        # Generate realistic P&L (68.5% win rate)
        is_win = np.random.rand() < 0.685
        
        if is_win:
            pnl = np.random.uniform(5, 50)  # Winning trade
            pnl_pct = np.random.uniform(0.5, 5.0)
        else:
            pnl = -np.random.uniform(3, 30)  # Losing trade (smaller losses)
            pnl_pct = -np.random.uniform(0.3, 3.0)
        
        trade_date = datetime.now() - timedelta(days=np.random.randint(0, 90))
        
        trades_history.append({
            'timestamp': trade_date,
            'strategy': np.random.choice(strategies),
            'symbol': np.random.choice(symbols),
            'action': np.random.choice(actions),
            'size': np.random.uniform(0.01, 0.1),
            'entry_price': np.random.uniform(100, 50000),
            'exit_price': np.random.uniform(100, 50000),
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'confidence': np.random.uniform(0.5, 0.95)
        })
    
    # Sort by date
    trades_history.sort(key=lambda x: x['timestamp'])
    
    logger.info(f"  [OK] Generated {len(trades_history)} trades (68.5% win rate)")
    
    # ===== STRATEGY PERFORMANCE =====
    strategy_performance = {
        'Momentum': {
            'total_return': 0.125,  # 12.5%
            'sharpe_ratio': 2.1,
            'win_rate': 0.72,
            'total_trades': 35,
            'avg_win': 28.5,
            'avg_loss': -15.2,
            'profit_factor': 1.87,
            'total_pnl': 245.80,
            'weight': 0.25,
            'status': 'active'
        },
        'Mean Reversion': {
            'total_return': 0.083,  # 8.3%
            'sharpe_ratio': 1.8,
            'win_rate': 0.65,
            'total_trades': 42,
            'avg_win': 22.1,
            'avg_loss': -12.8,
            'profit_factor': 1.45,
            'total_pnl': 168.90,
            'weight': 0.20,
            'status': 'active'
        },
        'Breakout': {
            'total_return': 0.157,  # 15.7%
            'sharpe_ratio': 2.5,
            'win_rate': 0.68,
            'total_trades': 28,
            'avg_win': 42.3,
            'avg_loss': -18.5,
            'profit_factor': 2.12,
            'total_pnl': 312.60,
            'weight': 0.30,
            'status': 'active'
        },
        'Pairs Trading': {
            'total_return': 0.062,  # 6.2%
            'sharpe_ratio': 1.5,
            'win_rate': 0.71,
            'total_trades': 15,
            'avg_win': 18.2,
            'avg_loss': -9.5,
            'profit_factor': 1.38,
            'total_pnl': 124.50,
            'weight': 0.15,
            'status': 'active'
        },
        'ML Model': {
            'total_return': 0.098,  # 9.8%
            'sharpe_ratio': 1.9,
            'win_rate': 0.66,
            'total_trades': 5,
            'avg_win': 35.7,
            'avg_loss': -16.8,
            'profit_factor': 1.62,
            'total_pnl': 198.20,
            'weight': 0.10,
            'status': 'active'
        }
    }
    
    logger.info(f"  [OK] Generated {len(strategy_performance)} strategy profiles")
    
    # ===== RISK METRICS =====
    risk_metrics = {
        'sharpe_ratio': 2.34,
        'sortino_ratio': 3.12,
        'calmar_ratio': 1.87,
        'max_drawdown': -8.2,
        'volatility': 12.5,
        'var_95': -2.5,
        'cvar_95': -3.8,
        'beta': 0.85,
        'alpha': 5.2,
        'information_ratio': 1.45
    }
    
    logger.info(f"  [OK] Generated risk metrics (Sharpe: {risk_metrics['sharpe_ratio']})")
    
    logger.info("[OK] Demo data generation complete!")
    
    return portfolio_history, trades_history, strategy_performance, risk_metrics


def main():
    """
    Main entry point for standalone dashboard with demo data
    """
    
    print("")
    print("=" * 70)
    print("     BotV2 Dashboard - Standalone Mode with Demo Data")
    print("                      v3.2")
    print("=" * 70)
    print("")
    
    logger.info("[START] Starting dashboard in standalone mode...")
    
    # Check environment
    env = os.getenv('FLASK_ENV', 'development')
    logger.info(f"[ENV] Environment: {env.upper()}")
    
    # Import dashboard
    try:
        from src.dashboard.web_app import ProfessionalDashboard
    except ImportError as e:
        logger.error(f"[ERROR] Failed to import dashboard: {e}")
        logger.error("Make sure you're running from project root: python src/dashboard/dashboard_standalone.py")
        sys.exit(1)
    
    # Create mock config
    config = MockConfig()
    
    # Create dashboard instance
    try:
        dashboard = ProfessionalDashboard(config)
        logger.info("[OK] Dashboard instance created successfully")
    except Exception as e:
        logger.error(f"[ERROR] Failed to create dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generate and load demo data
    try:
        portfolio_history, trades_history, strategy_performance, risk_metrics = generate_demo_data()
        
        # Load data into dashboard
        dashboard.portfolio_history = portfolio_history
        dashboard.trades_history = trades_history
        dashboard.strategy_performance = strategy_performance
        dashboard.risk_metrics = risk_metrics
        
        logger.info("[OK] Demo data loaded into dashboard")
    except Exception as e:
        logger.error(f"[ERROR] Failed to generate demo data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display access information
    host = config.get('dashboard.host', '0.0.0.0')
    port = config.get('dashboard.port', 8050)
    username = os.getenv('DASHBOARD_USERNAME', 'admin')
    password = os.getenv('DASHBOARD_PASSWORD')
    
    print("")
    print("=" * 70)
    print("                    ACCESS INFORMATION")
    print("-" * 70)
    print(f"  URL:      http://localhost:{port}/login")
    print(f"  Username: {username}")
    
    if password:
        # Mask password
        masked = password[:4] + '*' * (len(password) - 4) if len(password) > 4 else '****'
        print(f"  Password: {masked} (from DASHBOARD_PASSWORD)")
    else:
        print(f"  Password: [Check console output above]")
    
    print("=" * 70)
    print("")
    
    logger.info("")
    logger.info("[FEATURES] Dashboard Features:")
    logger.info("  - 13 Interactive Charts (Equity, P&L, Correlation, etc.)")
    logger.info("  - Real-time WebSocket Updates")
    logger.info("  - Dark/Light/Bloomberg Themes")
    logger.info("  - Time Filters (24h, 7d, 30d, 90d, YTD, All)")
    logger.info("  - Export Capabilities (PNG, SVG)")
    logger.info("  - Mobile Responsive Design")
    logger.info("")
    
    logger.info("[SECURITY] Security Features:")
    logger.info("  - Session-Based Authentication")
    logger.info("  - Rate Limiting (10 req/min per IP)")
    logger.info("  - Brute Force Protection (5 attempts lockout)")
    logger.info("  - Security Audit Logging (JSON)")
    
    if env == 'production':
        logger.info("  - HTTPS Enforcement ENABLED")
    else:
        logger.info("  - HTTPS Enforcement DISABLED (dev mode)")
    
    logger.info("")
    
    # Start dashboard server
    try:
        logger.info("=" * 70)
        logger.info("[START] Starting Flask server...")
        logger.info("=" * 70)
        logger.info("")
        
        dashboard.run()
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("[INTERRUPT] Keyboard interrupt received")
        logger.info("[SHUTDOWN] Shutting down dashboard...")
    
    except Exception as e:
        logger.error(f"[ERROR] Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    logger.info("")
    logger.info("[OK] Dashboard shutdown complete")
    logger.info("[BYE] Goodbye!")
    logger.info("")


if __name__ == "__main__":
    main()
