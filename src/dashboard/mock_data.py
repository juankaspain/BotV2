"""Professional Mock Data Generator for Dashboard v4.5

✅ Complete mock data for all 9 sections
✅ 8 professional charts with real metrics
✅ Live Monitor, Strategy Editor, Control Panel integrated
✅ 28+ trades, 12+ positions, 4 active strategies
✅ Production-ready realistic data
"""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


def generate_dashboard_data() -> Dict:
    """Generate mock dashboard overview with KPIs and 5 charts"""
    
    # Generate 90-day equity curve with realistic walk
    days = 90
    timestamps = []
    equity = []
    returns = []
    current_equity = 100000  # Start with 100k
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        timestamps.append(date.strftime('%Y-%m-%d'))
        
        # Random walk with positive drift
        daily_return = random.gauss(0.0008, 0.015)  # 0.08% daily avg, 1.5% volatility
        current_equity *= (1 + daily_return)
        equity.append(round(current_equity, 2))
        returns.append(round(daily_return * 100, 2))
    
    # Calculate metrics
    total_return = ((equity[-1] / equity[0]) - 1) * 100
    daily_pnl = equity[-1] - equity[-2]
    daily_pct = ((equity[-1] / equity[-2]) - 1) * 100
    
    # Sharpe ratio
    returns_array = np.array(returns)
    sharpe = (np.mean(returns_array) * np.sqrt(252)) / (np.std(returns_array) + 1e-10)
    
    # Max drawdown
    peak = np.maximum.accumulate(equity)
    drawdown = (np.array(equity) - peak) / peak * 100
    max_dd = np.min(drawdown)
    
    # Strategy comparison data (4 strategies)
    strategy_names = ['Momentum Pro', 'Mean Reversion', 'Scalping Pro', 'Trend Follower']
    strategy_returns = [12.4, 8.2, 6.1, 4.8]
    strategy_sharpe = [1.82, 1.45, 1.32, 1.21]
    strategy_colors = ['#28a745', '#17a2b8', '#ffc107', '#6610f2']
    
    # Risk radar data (5 metrics normalized 0-100)
    risk_metrics = {
        'labels': ['Sharpe Ratio', 'Win Rate', 'Profit Factor', 'Volatility (inv)', 'Recovery'],
        'values': [
            min(100, sharpe * 30),  # Sharpe normalized
            68.5,  # Win rate
            72.0,  # Profit factor normalized
            (1 / (returns_array.std() + 0.01)) * 100,  # Inverse volatility
            max(0, 100 + max_dd)  # Recovery from DD
        ]
    }
    
    return {
        'overview': {
            'equity': f'€{equity[-1]:,.2f}',
            'equity_value': equity[-1],
            'total_pnl': f'€{equity[-1] - equity[0]:,.2f}',
            'total_pnl_value': equity[-1] - equity[0],
            'total_return': round(total_return, 2),
            'daily_pnl': f'€{daily_pnl:,.2f}',
            'daily_pnl_value': daily_pnl,
            'daily_change_pct': round(daily_pct, 2),
            'win_rate': 68.5,
            'total_trades': 125,
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_dd, 2)
        },
        'equity_curve': {
            'timestamps': timestamps,
            'equity': equity,
            'type': 'line',
            'title': 'Portfolio Equity Curve'
        },
        'strategy_comparison': {
            'strategies': strategy_names,
            'returns': strategy_returns,
            'sharpe': strategy_sharpe,
            'colors': strategy_colors,
            'type': 'bar',
            'title': 'Strategy Returns Comparison'
        },
        'risk_radar': {
            'labels': risk_metrics['labels'],
            'values': risk_metrics['values'],
            'type': 'radar',
            'title': 'Risk Metrics Radar'
        },
        'daily_returns': {
            'timestamps': timestamps[-30:],  # Last 30 days
            'returns': returns[-30:],
            'type': 'bar',
            'title': 'Daily Returns (30 days)'
        },
        'drawdown_chart': {
            'timestamps': timestamps,
            'drawdown': drawdown.tolist(),
            'type': 'area',
            'title': 'Underwater Chart (Drawdown)'
        }
    }


def generate_portfolio_data() -> Dict:
    """Generate mock portfolio with 12 positions"""
    
    positions = [
        # Crypto (3)
        {'symbol': 'BTC-EUR', 'asset_class': 'Crypto', 'quantity': 0.5, 'entry_price': 35000, 
         'current_price': 38500, 'pnl': 1750, 'pnl_pct': 10.0, 'value': 19250, 'weight': 18.5},
        {'symbol': 'ETH-EUR', 'asset_class': 'Crypto', 'quantity': 5, 'entry_price': 2000, 
         'current_price': 2150, 'pnl': 750, 'pnl_pct': 7.5, 'value': 10750, 'weight': 10.3},
        {'symbol': 'SOL-EUR', 'asset_class': 'Crypto', 'quantity': 20, 'entry_price': 95, 
         'current_price': 108, 'pnl': 260, 'pnl_pct': 13.7, 'value': 2160, 'weight': 2.1},
        
        # Tech Stocks (4)
        {'symbol': 'AAPL', 'asset_class': 'Tech', 'quantity': 50, 'entry_price': 150, 
         'current_price': 165, 'pnl': 750, 'pnl_pct': 10.0, 'value': 8250, 'weight': 7.9},
        {'symbol': 'GOOGL', 'asset_class': 'Tech', 'quantity': 30, 'entry_price': 140, 
         'current_price': 145, 'pnl': 150, 'pnl_pct': 3.6, 'value': 4350, 'weight': 4.2},
        {'symbol': 'MSFT', 'asset_class': 'Tech', 'quantity': 40, 'entry_price': 380, 
         'current_price': 395, 'pnl': 600, 'pnl_pct': 3.9, 'value': 15800, 'weight': 15.2},
        {'symbol': 'NVDA', 'asset_class': 'Tech', 'quantity': 15, 'entry_price': 480, 
         'current_price': 520, 'pnl': 600, 'pnl_pct': 8.3, 'value': 7800, 'weight': 7.5},
        
        # Finance (2)
        {'symbol': 'JPM', 'asset_class': 'Finance', 'quantity': 80, 'entry_price': 145, 
         'current_price': 152, 'pnl': 560, 'pnl_pct': 4.8, 'value': 12160, 'weight': 11.7},
        {'symbol': 'BAC', 'asset_class': 'Finance', 'quantity': 150, 'entry_price': 32, 
         'current_price': 34.5, 'pnl': 375, 'pnl_pct': 7.8, 'value': 5175, 'weight': 5.0},
        
        # Energy (2)
        {'symbol': 'XOM', 'asset_class': 'Energy', 'quantity': 60, 'entry_price': 105, 
         'current_price': 110, 'pnl': 300, 'pnl_pct': 4.8, 'value': 6600, 'weight': 6.3},
        {'symbol': 'CVX', 'asset_class': 'Energy', 'quantity': 45, 'entry_price': 152, 
         'current_price': 158, 'pnl': 270, 'pnl_pct': 3.9, 'value': 7110, 'weight': 6.8},
        
        # Healthcare (1)
        {'symbol': 'JNJ', 'asset_class': 'Healthcare', 'quantity': 35, 'entry_price': 155, 
         'current_price': 162, 'pnl': 245, 'pnl_pct': 4.5, 'value': 5670, 'weight': 5.4}
    ]
    
    total_value = sum(p['value'] for p in positions)
    total_pnl = sum(p['pnl'] for p in positions)
    total_pnl_pct = (total_pnl / (total_value - total_pnl)) * 100
    
    # Sector allocation for heatmap
    sectors = {}
    for p in positions:
        sector = p['asset_class']
        if sector not in sectors:
            sectors[sector] = {'value': 0, 'pnl': 0, 'count': 0}
        sectors[sector]['value'] += p['value']
        sectors[sector]['pnl'] += p['pnl']
        sectors[sector]['count'] += 1
    
    sector_allocation = [
        {'sector': k, 'value': v['value'], 'pnl': v['pnl'], 
         'pnl_pct': (v['pnl'] / (v['value'] - v['pnl'])) * 100, 'count': v['count']}
        for k, v in sectors.items()
    ]
    
    return {
        'summary': {
            'total_value': total_value,
            'cash': 15000,
            'total_equity': total_value + 15000,
            'total_pnl': total_pnl,
            'total_pnl_pct': round(total_pnl_pct, 2),
            'positions_count': len(positions),
            'diversification_score': 8.5  # Out of 10
        },
        'positions': positions,
        'sector_allocation': sector_allocation,
        'position_heatmap': {
            'symbols': [p['symbol'] for p in positions],
            'values': [p['value'] for p in positions],
            'pnls': [p['pnl_pct'] for p in positions],
            'colors': ['green' if p['pnl'] > 0 else 'red' for p in positions]
        }
    }


def generate_strategies_data() -> Dict:
    """Generate mock strategy performance data (4 active strategies)"""
    
    strategies = [
        {
            'id': 1,
            'name': 'Momentum Pro',
            'description': 'Trend-following with momentum indicators',
            'return': 12.4,
            'sharpe': 1.82,
            'sortino': 2.45,
            'win_rate': 67.3,
            'profit_factor': 2.12,
            'trades': 45,
            'avg_win': 285,
            'avg_loss': -134,
            'max_dd': -6.2,
            'status': 'active',
            'allocation': 35,
            'last_trade': '2026-01-24 01:30:00'
        },
        {
            'id': 2,
            'name': 'Mean Reversion',
            'description': 'Statistical mean reversion strategy',
            'return': 8.2,
            'sharpe': 1.45,
            'sortino': 1.98,
            'win_rate': 61.2,
            'profit_factor': 1.75,
            'trades': 32,
            'avg_win': 195,
            'avg_loss': -111,
            'max_dd': -8.5,
            'status': 'active',
            'allocation': 25,
            'last_trade': '2026-01-23 22:15:00'
        },
        {
            'id': 3,
            'name': 'Scalping Pro',
            'description': 'High-frequency scalping strategy',
            'return': 6.1,
            'sharpe': 1.32,
            'sortino': 1.67,
            'win_rate': 58.9,
            'profit_factor': 1.52,
            'trades': 128,
            'avg_win': 78,
            'avg_loss': -51,
            'max_dd': -4.8,
            'status': 'active',
            'allocation': 20,
            'last_trade': '2026-01-24 02:45:00'
        },
        {
            'id': 4,
            'name': 'Trend Follower',
            'description': 'Long-term trend following',
            'return': 4.8,
            'sharpe': 1.21,
            'sortino': 1.54,
            'win_rate': 55.6,
            'profit_factor': 1.38,
            'trades': 18,
            'avg_win': 412,
            'avg_loss': -298,
            'max_dd': -9.2,
            'status': 'active',
            'allocation': 20,
            'last_trade': '2026-01-22 14:20:00'
        }
    ]
    
    active = sum(1 for s in strategies if s['status'] == 'active')
    best = max(strategies, key=lambda x: x['return'])
    avg_sharpe = sum(s['sharpe'] for s in strategies) / len(strategies)
    total_trades = sum(s['trades'] for s in strategies)
    total_return = sum(s['return'] * s['allocation'] / 100 for s in strategies)
    
    return {
        'summary': {
            'active': active,
            'total': len(strategies),
            'best_strategy': best['name'],
            'best_return': best['return'],
            'avg_sharpe': round(avg_sharpe, 2),
            'total_trades': total_trades,
            'portfolio_return': round(total_return, 2)
        },
        'strategies': strategies,
        'performance_chart': {
            'names': [s['name'] for s in strategies],
            'returns': [s['return'] for s in strategies],
            'sharpes': [s['sharpe'] for s in strategies],
            'win_rates': [s['win_rate'] for s in strategies]
        }
    }


def generate_risk_data() -> Dict:
    """Generate mock risk analytics with VaR, Drawdown, Volatility"""
    
    # Generate 90-day drawdown curve
    days = 90
    timestamps = []
    drawdown = []
    volatility = []
    returns = []
    
    equity = 100000
    peak = equity
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        timestamps.append(date.strftime('%Y-%m-%d'))
        
        # Generate daily return
        daily_return = random.gauss(0.0008, 0.015)
        equity *= (1 + daily_return)
        returns.append(daily_return * 100)
        
        # Update peak and drawdown
        if equity > peak:
            peak = equity
        dd = ((equity - peak) / peak) * 100
        drawdown.append(round(dd, 2))
        
        # Rolling 30-day volatility
        if i >= 30:
            vol = np.std(returns[-30:]) * np.sqrt(252)
            volatility.append(round(vol, 2))
        else:
            volatility.append(0)
    
    # Calculate risk metrics
    returns_array = np.array(returns)
    sharpe = (np.mean(returns_array) * np.sqrt(252)) / (np.std(returns_array) + 1e-10)
    sortino = (np.mean(returns_array) * np.sqrt(252)) / (np.std(returns_array[returns_array < 0]) + 1e-10)
    max_dd = min(drawdown)
    
    # VaR 95% and 99%
    var_95 = np.percentile(returns_array, 5) * equity / 100
    var_99 = np.percentile(returns_array, 1) * equity / 100
    
    # CVaR (Conditional VaR)
    cvar_95 = np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)]) * equity / 100
    
    return {
        'metrics': {
            'var_95': round(var_95, 2),
            'var_99': round(var_99, 2),
            'cvar_95': round(cvar_95, 2),
            'max_drawdown': round(max_dd, 2),
            'current_dd': round(drawdown[-1], 2),
            'volatility': round(np.std(returns_array) * np.sqrt(252), 2),
            'sharpe': round(sharpe, 2),
            'sortino': round(sortino, 2),
            'beta': 0.85,
            'alpha': 0.032
        },
        'drawdown_chart': {
            'timestamps': timestamps,
            'drawdown': drawdown,
            'type': 'area',
            'title': 'Underwater Chart (Drawdown %)'
        },
        'volatility_chart': {
            'timestamps': timestamps[30:],
            'volatility': volatility[30:],
            'type': 'line',
            'title': '30-Day Rolling Volatility (%)'
        },
        'risk_limits': {
            'max_position_size': 20,
            'max_portfolio_dd': 15,
            'daily_loss_limit': 5,
            'var_limit': 3000,
            'current_utilization': 65  # % of limits used
        }
    }


def generate_trades_data() -> Dict:
    """Generate mock trades history (28 trades)"""
    
    strategies = ['Momentum Pro', 'Mean Reversion', 'Scalping Pro', 'Trend Follower']
    symbols = ['BTC-EUR', 'ETH-EUR', 'AAPL', 'GOOGL', 'MSFT', 'NVDA', 'JPM', 'XOM']
    
    trades = []
    cumulative_pnl = 0
    
    for i in range(28):
        date = datetime.now() - timedelta(hours=i*2 + random.randint(0, 3))
        
        # Generate realistic trade
        strategy = random.choice(strategies)
        symbol = random.choice(symbols)
        action = random.choice(['BUY', 'SELL'])
        quantity = random.randint(1, 20)
        price = round(random.uniform(50, 500), 2)
        
        # PnL with 65% win rate
        is_win = random.random() < 0.65
        if is_win:
            pnl = round(random.uniform(50, 300), 2)
        else:
            pnl = round(random.uniform(-200, -20), 2)
        
        pnl_pct = (pnl / (quantity * price)) * 100
        cumulative_pnl += pnl
        
        trades.append({
            'id': i + 1,
            'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
            'strategy': strategy,
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'value': round(quantity * price, 2),
            'pnl': pnl,
            'pnl_pct': round(pnl_pct, 2),
            'cumulative_pnl': round(cumulative_pnl, 2),
            'fees': round(quantity * price * 0.001, 2),
            'status': 'closed'
        })
    
    # Calculate statistics
    winning = [t for t in trades if t['pnl'] > 0]
    losing = [t for t in trades if t['pnl'] < 0]
    
    win_rate = (len(winning) / len(trades)) * 100
    avg_win = np.mean([t['pnl'] for t in winning]) if winning else 0
    avg_loss = np.mean([t['pnl'] for t in losing]) if losing else 0
    profit_factor = abs(sum(t['pnl'] for t in winning) / sum(t['pnl'] for t in losing)) if losing else 0
    
    # P&L histogram data
    pnl_values = [t['pnl'] for t in trades]
    pnl_bins = [-200, -150, -100, -50, 0, 50, 100, 150, 200, 250, 300]
    pnl_hist, _ = np.histogram(pnl_values, bins=pnl_bins)
    
    return {
        'summary': {
            'total': len(trades),
            'winning': len(winning),
            'losing': len(losing),
            'win_rate': round(win_rate, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'total_pnl': round(cumulative_pnl, 2),
            'total_fees': round(sum(t['fees'] for t in trades), 2)
        },
        'trades': trades,
        'pnl_histogram': {
            'bins': pnl_bins,
            'counts': pnl_hist.tolist(),
            'type': 'histogram',
            'title': 'Trade P&L Distribution'
        }
    }


def generate_live_monitor_data() -> Dict:
    """Generate mock Live Monitor data with real-time KPIs"""
    
    # Active positions (3 open trades)
    active_trades = [
        {
            'id': 201,
            'symbol': 'BTC-EUR',
            'strategy': 'Momentum Pro',
            'action': 'BUY',
            'entry_price': 38200,
            'current_price': 38500,
            'quantity': 0.25,
            'unrealized_pnl': 75,
            'pnl_pct': 0.79,
            'duration': '23 min',
            'stop_loss': 37500,
            'take_profit': 39500
        },
        {
            'id': 202,
            'symbol': 'ETH-EUR',
            'strategy': 'Scalping Pro',
            'action': 'SELL',
            'entry_price': 2155,
            'current_price': 2148,
            'quantity': 3,
            'unrealized_pnl': 21,
            'pnl_pct': 0.32,
            'duration': '8 min',
            'stop_loss': 2180,
            'take_profit': 2120
        },
        {
            'id': 203,
            'symbol': 'NVDA',
            'strategy': 'Trend Follower',
            'action': 'BUY',
            'entry_price': 518,
            'current_price': 520,
            'quantity': 10,
            'unrealized_pnl': 20,
            'pnl_pct': 0.39,
            'duration': '1h 12min',
            'stop_loss': 505,
            'take_profit': 545
        }
    ]
    
    total_unrealized = sum(t['unrealized_pnl'] for t in active_trades)
    
    # Real-time P&L chart (last 60 minutes)
    timestamps = [(datetime.now() - timedelta(minutes=60-i)).strftime('%H:%M') for i in range(60)]
    pnl_timeline = []
    current_pnl = 2750
    
    for _ in range(60):
        change = random.gauss(0, 15)
        current_pnl += change
        pnl_timeline.append(round(current_pnl, 2))
    
    return {
        'summary': {
            'status': 'ACTIVE',
            'active_trades': len(active_trades),
            'total_exposure': sum(t['entry_price'] * t['quantity'] for t in active_trades),
            'unrealized_pnl': round(total_unrealized, 2),
            'realized_pnl_today': 2847.30,
            'total_pnl_today': round(2847.30 + total_unrealized, 2),
            'pnl_pct_today': 2.1,
            'latency_ms': 23,
            'volume_today': 1247893,
            'orders_pending': 2
        },
        'active_trades': active_trades,
        'live_pnl_chart': {
            'timestamps': timestamps,
            'pnl': pnl_timeline,
            'type': 'line',
            'title': 'Live P&L (Last 60 min)'
        },
        'system_health': {
            'api_status': 'online',
            'websocket_status': 'connected',
            'database_status': 'online',
            'cpu_usage': 23.4,
            'memory_usage': 62.1,
            'latency_avg': 23,
            'uptime': '2h 34min'
        }
    }


def generate_strategy_editor_data() -> Dict:
    """Generate mock Strategy Editor data"""
    
    return {
        'available_strategies': [
            {
                'id': 1,
                'name': 'Momentum Pro',
                'type': 'trend_following',
                'description': 'Advanced momentum strategy with ML filters',
                'status': 'active',
                'parameters': {
                    'lookback_period': 20,
                    'momentum_threshold': 0.05,
                    'stop_loss': 2.5,
                    'take_profit': 5.0,
                    'position_size': 2.0,
                    'max_positions': 3
                },
                'performance': {
                    'return': 12.4,
                    'sharpe': 1.82,
                    'win_rate': 67.3,
                    'trades': 45
                }
            },
            {
                'id': 2,
                'name': 'Mean Reversion',
                'type': 'mean_reversion',
                'description': 'Statistical mean reversion with Bollinger Bands',
                'status': 'active',
                'parameters': {
                    'bb_period': 20,
                    'bb_std': 2.0,
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70,
                    'stop_loss': 3.0,
                    'take_profit': 4.0
                },
                'performance': {
                    'return': 8.2,
                    'sharpe': 1.45,
                    'win_rate': 61.2,
                    'trades': 32
                }
            },
            {
                'id': 3,
                'name': 'Scalping Pro',
                'type': 'scalping',
                'description': 'High-frequency scalping with order flow analysis',
                'status': 'active',
                'parameters': {
                    'tick_threshold': 0.01,
                    'volume_filter': 1000,
                    'stop_loss': 0.5,
                    'take_profit': 1.0,
                    'max_holding_time': 300
                },
                'performance': {
                    'return': 6.1,
                    'sharpe': 1.32,
                    'win_rate': 58.9,
                    'trades': 128
                }
            },
            {
                'id': 4,
                'name': 'Trend Follower',
                'type': 'trend_following',
                'description': 'Long-term trend following with EMA crossovers',
                'status': 'active',
                'parameters': {
                    'fast_ema': 12,
                    'slow_ema': 26,
                    'signal_ema': 9,
                    'atr_period': 14,
                    'stop_loss': 3.5,
                    'take_profit': 8.0
                },
                'performance': {
                    'return': 4.8,
                    'sharpe': 1.21,
                    'win_rate': 55.6,
                    'trades': 18
                }
            }
        ],
        'backtest_results': {
            'equity_curve': [100000, 101500, 103200, 105100, 107500, 110200, 112400],
            'dates': ['2026-01-17', '2026-01-18', '2026-01-19', '2026-01-20', '2026-01-21', '2026-01-22', '2026-01-23'],
            'metrics': {
                'total_return': 12.4,
                'sharpe': 1.82,
                'max_dd': -6.2,
                'win_rate': 67.3,
                'profit_factor': 2.12,
                'total_trades': 45
            }
        }
    }


def generate_control_panel_data() -> Dict:
    """Generate mock Control Panel data"""
    
    return {
        'bot_status': {
            'is_running': True,
            'mode': 'paper',  # paper | live
            'started_at': '2026-01-24 00:20:15',
            'uptime': '2h 35min',
            'total_trades_today': 12,
            'errors_today': 0
        },
        'circuit_breaker': {
            'enabled': True,
            'triggered': False,
            'max_daily_loss': 5.0,
            'current_daily_loss': 0.8,
            'max_position_size': 20.0,
            'current_max_position': 18.5
        },
        'risk_limits': {
            'max_portfolio_risk': 15.0,
            'current_portfolio_risk': 8.2,
            'max_drawdown_limit': 20.0,
            'current_drawdown': 6.2,
            'daily_loss_limit': 5.0,
            'daily_loss_current': 0.8,
            'var_limit': 3000,
            'var_current': 1847
        },
        'active_strategies': [
            {'name': 'Momentum Pro', 'status': 'running', 'allocation': 35, 'trades_today': 5},
            {'name': 'Mean Reversion', 'status': 'running', 'allocation': 25, 'trades_today': 3},
            {'name': 'Scalping Pro', 'status': 'running', 'allocation': 20, 'trades_today': 4},
            {'name': 'Trend Follower', 'status': 'running', 'allocation': 20, 'trades_today': 0}
        ],
        'system_config': {
            'auto_trading': True,
            'auto_rebalance': True,
            'notifications_enabled': True,
            'emergency_stop': False,
            'max_concurrent_trades': 10,
            'order_timeout': 30
        }
    }


def generate_settings_data() -> Dict:
    """Generate mock settings data"""
    
    return {
        'general': {
            'mode': 'paper',
            'initial_capital': 100000,
            'currency': 'EUR',
            'timezone': 'Europe/Madrid',
            'auto_refresh': True,
            'refresh_interval': 5
        },
        'trading': {
            'max_position_size': 20.0,
            'max_positions': 10,
            'default_stop_loss': 2.5,
            'default_take_profit': 5.0,
            'risk_per_trade': 2.0,
            'max_daily_trades': 50
        },
        'risk': {
            'max_drawdown': 20.0,
            'daily_loss_limit': 5.0,
            'var_confidence': 95,
            'var_limit': 3000,
            'circuit_breaker_enabled': True
        },
        'notifications': {
            'enabled': True,
            'email': 'user@example.com',
            'trade_alerts': True,
            'risk_alerts': True,
            'system_alerts': True
        },
        'system': {
            'version': '4.5.0',
            'environment': 'development',
            'uptime': '2h 35min',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database': 'PostgreSQL 14',
            'cache': 'Redis 7.0'
        }
    }


# Main data router
def get_section_data(section: str) -> Dict:
    """Route data requests to appropriate generator"""
    
    generators = {
        'dashboard': generate_dashboard_data,
        'portfolio': generate_portfolio_data,
        'strategies': generate_strategies_data,
        'risk': generate_risk_data,
        'trades': generate_trades_data,
        'live_monitor': generate_live_monitor_data,
        'strategy_editor': generate_strategy_editor_data,
        'control_panel': generate_control_panel_data,
        'settings': generate_settings_data
    }
    
    generator = generators.get(section)
    if generator:
        return generator()
    else:
        return {'error': f'Section {section} not found'}
