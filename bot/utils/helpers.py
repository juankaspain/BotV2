"""
Helper Utilities
Common utility functions used across the system
"""

import pandas as pd
import numpy as np
from typing import Union, List
from datetime import datetime, timedelta


def calculate_sharpe_ratio(returns: Union[pd.Series, np.ndarray],
                           risk_free_rate: float = 0.02,
                           periods: int = 252) -> float:
    """
    Calculate annualized Sharpe ratio
    
    Args:
        returns: Array of returns
        risk_free_rate: Annual risk-free rate
        periods: Trading periods per year (252 for daily)
        
    Returns:
        Annualized Sharpe ratio
    """
    
    returns_array = np.array(returns)
    
    if len(returns_array) < 2:
        return 0.0
    
    mean_return = np.mean(returns_array)
    std_return = np.std(returns_array)
    
    if std_return == 0:
        return 0.0
    
    daily_rf = risk_free_rate / periods
    sharpe = (mean_return - daily_rf) / std_return * np.sqrt(periods)
    
    return sharpe


def calculate_max_drawdown(equity_curve: Union[pd.Series, np.ndarray]) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        equity_curve: Portfolio equity over time
        
    Returns:
        Maximum drawdown (negative value)
    """
    
    cumulative = np.array(equity_curve)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    
    return np.min(drawdown)


def calculate_sortino_ratio(returns: Union[pd.Series, np.ndarray],
                            risk_free_rate: float = 0.02,
                            periods: int = 252) -> float:
    """
    Calculate Sortino ratio (downside deviation)
    
    Args:
        returns: Array of returns
        risk_free_rate: Annual risk-free rate
        periods: Trading periods per year
        
    Returns:
        Sortino ratio
    """
    
    returns_array = np.array(returns)
    
    if len(returns_array) < 2:
        return 0.0
    
    mean_return = np.mean(returns_array)
    
    # Downside deviation (only negative returns)
    negative_returns = returns_array[returns_array < 0]
    
    if len(negative_returns) == 0:
        return np.inf
    
    downside_std = np.std(negative_returns)
    
    if downside_std == 0:
        return 0.0
    
    daily_rf = risk_free_rate / periods
    sortino = (mean_return - daily_rf) / downside_std * np.sqrt(periods)
    
    return sortino


def format_currency(value: float, currency: str = 'EUR') -> str:
    """Format value as currency"""
    symbol = '€' if currency == 'EUR' else '$'
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value * 100:.{decimals}f}%"


def time_ago(dt: datetime) -> str:
    """Convert datetime to human-readable 'time ago' string"""
    
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return f"{int(diff.total_seconds())}s ago"
    elif diff < timedelta(hours=1):
        return f"{int(diff.total_seconds() / 60)}m ago"
    elif diff < timedelta(days=1):
        return f"{int(diff.total_seconds() / 3600)}h ago"
    else:
        return f"{diff.days}d ago"
