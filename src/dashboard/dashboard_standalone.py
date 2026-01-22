#!/usr/bin/env python3
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
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np

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
    logger.info("\ud83d\udd04 Generating demo trading data...")
    
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
    
    logger.info(f"  \u2705 Generated {len(portfolio_history)} portfolio snapshots")
    
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
    
    logger.info(f"  \u2705 Generated {len(trades_history)} trades (68.5% win rate)")
    
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
    
    logger.info(f"  \u2705 Generated {len(strategy_performance)} strategy profiles")
    
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
    
    logger.info(f"  \u2705 Generated risk metrics (Sharpe: {risk_metrics['sharpe_ratio']})")
    
    logger.info("\u2705 Demo data generation complete!")
    
    return portfolio_history, trades_history, strategy_performance, risk_metrics


def main():
    """
    Main entry point for standalone dashboard with demo data
    """
    
    print("")
    print("\u2554" + "="*68 + "\u2557")
    print("\u2551" + " "*14 + "BotV2 Dashboard - Standalone Mode" + " "*20 + "\u2551")
    print("\u2551" + " "*20 + "v3.2 with Demo Data" + " "*27 + "\u2551")
    print("\u255a" + "="*68 + "\u255d")
    print("")
    
    logger.info("\ud83d\ude80 Starting dashboard in standalone mode...")
    
    # Check environment
    env = os.getenv('FLASK_ENV', 'development')
    logger.info(f"\ud83c\udf0d Environment: {env.upper()}")
    
    # Import dashboard
    try:
        from src.dashboard.web_app import ProfessionalDashboard
    except ImportError as e:
        logger.error(f"\u274c Failed to import dashboard: {e}")
        logger.error("Make sure you're running from project root: python src/dashboard/dashboard_standalone.py")
        sys.exit(1)
    
    # Create mock config
    config = MockConfig()
    
    # Create dashboard instance
    try:
        dashboard = ProfessionalDashboard(config)
        logger.info("\u2705 Dashboard instance created successfully")
    except Exception as e:
        logger.error(f"\u274c Failed to create dashboard: {e}")
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
        
        logger.info("\u2705 Demo data loaded into dashboard")
    except Exception as e:
        logger.error(f"\u274c Failed to generate demo data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display access information
    host = config.get('dashboard.host', '0.0.0.0')
    port = config.get('dashboard.port', 8050)
    username = os.getenv('DASHBOARD_USERNAME', 'admin')
    password = os.getenv('DASHBOARD_PASSWORD')
    
    print("")
    print("\u2554" + "="*68 + "\u2557")
    print("\u2551" + " "*23 + "\ud83d\udd10 Access Information" + " "*23 + "\u2551")
    print("\u2560" + "\u2500"*68 + "\u2563")
    print(f"\u2551  \ud83c\udf0d URL:      http://localhost:{port}/login" + " "*(68-40-len(str(port))) + "\u2551")
    print(f"\u2551  \ud83d\udc64 Username: {username}" + " "*(68-15-len(username)) + "\u2551")
    
    if password:
        # Mask password
        masked = password[:4] + '*' * (len(password) - 4) if len(password) > 4 else '****'
        print(f"\u2551  \ud83d\udd11 Password: {masked} (from DASHBOARD_PASSWORD)" + " "*(68-48-len(masked)) + "\u2551")
    else:
        print(f"\u2551  \ud83d\udd11 Password: [Check console output above]" + " "*19 + "\u2551")
    
    print("\u255a" + "="*68 + "\u255d")
    print("")
    
    logger.info("")
    logger.info("\ud83d\udcca Dashboard Features:")
    logger.info("  \u2705 13 Interactive Charts (Equity, P&L, Correlation, etc.)")
    logger.info("  \u2705 Real-time WebSocket Updates")
    logger.info("  \u2705 Dark/Light/Bloomberg Themes")
    logger.info("  \u2705 Time Filters (24h, 7d, 30d, 90d, YTD, All)")
    logger.info("  \u2705 Export Capabilities (PNG, SVG)")
    logger.info("  \u2705 Mobile Responsive Design")
    logger.info("")
    
    logger.info("\ud83d\udd12 Security Features:")
    logger.info("  \u2705 Session-Based Authentication")
    logger.info("  \u2705 Rate Limiting (10 req/min per IP)")
    logger.info("  \u2705 Brute Force Protection (5 attempts lockout)")
    logger.info("  \u2705 Security Audit Logging (JSON)")
    
    if env == 'production':
        logger.info("  \u2705 HTTPS Enforcement ENABLED")
    else:
        logger.info("  \u26a0\ufe0f  HTTPS Enforcement DISABLED (dev mode)")
    
    logger.info("")
    
    # Start dashboard server
    try:
        logger.info("="*70)
        logger.info("\ud83d\ude80 Starting Flask server...")
        logger.info("="*70)
        logger.info("")
        
        dashboard.run()
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("\u26a0\ufe0f  Keyboard interrupt received")
        logger.info("\ud83d\udc4b Shutting down dashboard...")
    
    except Exception as e:
        logger.error(f"\u274c Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    logger.info("")
    logger.info("\u2705 Dashboard shutdown complete")
    logger.info("\ud83d\udc4b Goodbye!")
    logger.info("")


if __name__ == "__main__":
    main()
