"""Mock data generator for dashboard demo mode"""
import random
from datetime import datetime, timedelta
from typing import Dict, List


def generate_dashboard_data() -> Dict:
    """Generate mock dashboard overview data"""
    
    # Generate 90-day equity curve
    days = 90
    timestamps = []
    equity = []
    current_equity = 3000
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        timestamps.append(date.isoformat())
        change = (random.random() - 0.45) * 50
        current_equity = max(2500, current_equity + change)
        equity.append(round(current_equity, 2))
    
    return {
        'overview': {
            'equity': f'€{equity[-1]:,.2f}',
            'total_pnl': f'€{equity[-1] - 3000:,.2f}',
            'total_return': round((equity[-1] / 3000 - 1) * 100, 2),
            'daily_change': round(equity[-1] - equity[-2], 2),
            'daily_change_pct': round((equity[-1] / equity[-2] - 1) * 100, 2),
            'win_rate': 68.5,
            'total_trades': 125,
            'sharpe_ratio': 2.34,
            'max_drawdown': -8.2
        },
        'equity': {
            'timestamps': timestamps,
            'equity': equity
        },
        'strategies': {
            'names': ['Momentum', 'Mean Reversion', 'Breakout', 'Pairs Trading', 'ML Model'],
            'returns': [12.5, 8.3, 15.7, 6.2, 9.8]
        },
        'risk': {
            'metrics': ['Sharpe', 'Sortino', 'Calmar', 'Max DD', 'Volatility'],
            'values': [2.34, 3.12, 1.87, 8.2, 12.5]
        }
    }


def generate_portfolio_data() -> Dict:
    """Generate mock portfolio positions data"""
    
    positions = [
        {
            'symbol': 'BTC-EUR',
            'quantity': 0.5,
            'entry_price': 35000,
            'current_price': 38500,
            'pnl': 1750,
            'pnl_pct': 10.0,
            'value': 19250
        },
        {
            'symbol': 'ETH-EUR',
            'quantity': 5,
            'entry_price': 2000,
            'current_price': 2150,
            'pnl': 750,
            'pnl_pct': 7.5,
            'value': 10750
        },
        {
            'symbol': 'AAPL',
            'quantity': 10,
            'entry_price': 150,
            'current_price': 165,
            'pnl': 150,
            'pnl_pct': 10.0,
            'value': 1650
        },
        {
            'symbol': 'GOOGL',
            'quantity': 5,
            'entry_price': 140,
            'current_price': 145,
            'pnl': 25,
            'pnl_pct': 3.57,
            'value': 725
        },
    ]
    
    total_value = sum(p['value'] for p in positions)
    total_pnl = sum(p['pnl'] for p in positions)
    
    return {
        'summary': {
            'total_value': total_value,
            'cash': 5000,
            'total_pnl': total_pnl,
            'positions_count': len(positions)
        },
        'positions': positions
    }


def generate_strategies_data() -> Dict:
    """Generate mock strategy performance data"""
    
    strategies = [
        {
            'name': 'Momentum',
            'return': 12.5,
            'sharpe': 2.1,
            'win_rate': 72,
            'trades': 45,
            'status': 'active'
        },
        {
            'name': 'Mean Reversion',
            'return': 8.3,
            'sharpe': 1.8,
            'win_rate': 65,
            'trades': 32,
            'status': 'active'
        },
        {
            'name': 'Breakout',
            'return': 15.7,
            'sharpe': 2.5,
            'win_rate': 68,
            'trades': 28,
            'status': 'active'
        },
        {
            'name': 'Pairs Trading',
            'return': 6.2,
            'sharpe': 1.5,
            'win_rate': 60,
            'trades': 15,
            'status': 'paused'
        },
        {
            'name': 'ML Model',
            'return': 9.8,
            'sharpe': 2.0,
            'win_rate': 70,
            'trades': 5,
            'status': 'active'
        },
    ]
    
    active = sum(1 for s in strategies if s['status'] == 'active')
    best = max(strategies, key=lambda x: x['return'])
    avg_sharpe = sum(s['sharpe'] for s in strategies) / len(strategies)
    total_trades = sum(s['trades'] for s in strategies)
    
    return {
        'summary': {
            'active': active,
            'best_strategy': best['name'],
            'best_return': best['return'],
            'avg_sharpe': avg_sharpe,
            'total_trades': total_trades
        },
        'strategies': strategies
    }


def generate_risk_data() -> Dict:
    """Generate mock risk analytics data"""
    
    # Generate drawdown and volatility data
    days = 90
    timestamps = []
    drawdown = []
    volatility = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        timestamps.append(date.isoformat())
        drawdown.append(round(random.uniform(-15, 0), 2))
        volatility.append(round(random.uniform(8, 18), 2))
    
    return {
        'metrics': {
            'var_95': -250.50,
            'max_drawdown': -8.2,
            'volatility': 12.5,
            'sharpe': 2.34
        },
        'drawdown': {
            'timestamps': timestamps,
            'drawdown': drawdown
        },
        'volatility': {
            'timestamps': timestamps,
            'volatility': volatility
        }
    }


def generate_trades_data() -> Dict:
    """Generate mock trades history data"""
    
    trades = []
    for i in range(20):
        date = datetime.now() - timedelta(hours=i*3)
        trades.append({
            'timestamp': date.isoformat(),
            'strategy': random.choice(['Momentum', 'Mean Reversion', 'Breakout']),
            'symbol': random.choice(['BTC-EUR', 'ETH-EUR', 'AAPL', 'GOOGL']),
            'action': random.choice(['BUY', 'SELL']),
            'quantity': random.randint(1, 10),
            'price': round(random.uniform(50, 500), 2),
            'pnl': round(random.uniform(-50, 150), 2)
        })
    
    winning = sum(1 for t in trades if t['pnl'] > 0)
    win_rate = (winning / len(trades)) * 100
    total_wins = sum(t['pnl'] for t in trades if t['pnl'] > 0)
    total_losses = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    return {
        'summary': {
            'total': len(trades),
            'winning': winning,
            'win_rate': win_rate,
            'profit_factor': profit_factor
        },
        'trades': trades
    }


def generate_settings_data() -> Dict:
    """Generate mock settings data"""
    
    return {
        'settings': {
            'mode': 'paper',
            'initial_capital': 3000,
            'max_position_size': 20,
            'stop_loss': 5,
            'risk_per_trade': 2,
            'auto_refresh': True
        },
        'system': {
            'version': '3.3',
            'environment': 'development',
            'uptime': '2 hours',
            'last_update': datetime.now().isoformat()
        }
    }
