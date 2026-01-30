#!/usr/bin/env python3
"""
Strategy Editor - Parameter management for trading strategies

Provides:
- Strategy parameter CRUD operations
- Preset configurations
- Change history tracking
- Impact estimation
- Quick backtesting
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import deque
import random
import copy

logger = logging.getLogger(__name__)

# Singleton instance
_editor_instance = None


class PresetType(Enum):
    """Strategy preset types"""
    CONSERVATIVE = 'conservative'
    BALANCED = 'balanced'
    AGGRESSIVE = 'aggressive'


@dataclass
class ParameterChange:
    """Parameter change record"""
    timestamp: datetime
    strategy_name: str
    parameter: str
    old_value: Any
    new_value: Any
    user: str
    change_type: str  # 'manual', 'preset', 'rollback'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'strategy_name': self.strategy_name,
            'parameter': self.parameter,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'user': self.user,
            'change_type': self.change_type
        }


@dataclass
class StrategyParameter:
    """Strategy parameter definition"""
    name: str
    value: Any
    param_type: str  # 'int', 'float', 'bool', 'str'
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'type': self.param_type,
            'min': self.min_value,
            'max': self.max_value,
            'description': self.description
        }


class StrategyEditor:
    """
    Editor for managing strategy parameters.
    
    Tracks changes, supports presets, and provides impact estimation.
    In demo mode, uses simulated strategies.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Storage
        self.strategies: Dict[str, Dict[str, StrategyParameter]] = {}
        self._change_history: deque = deque(maxlen=max_history)
        
        # Statistics
        self._total_changes = 0
        self._last_change = None
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Initialize demo strategies
        self._initialize_strategies()
        
        logger.info(f"StrategyEditor initialized (demo={self.demo_mode})")
    
    def _initialize_strategies(self):
        """Initialize default strategies"""
        # RSI Strategy
        self.strategies['RSI'] = {
            'oversold': StrategyParameter('oversold', 30.0, 'float', 10, 40, 'RSI oversold threshold'),
            'overbought': StrategyParameter('overbought', 70.0, 'float', 60, 90, 'RSI overbought threshold'),
            'period': StrategyParameter('period', 14, 'int', 5, 50, 'RSI calculation period'),
            'enabled': StrategyParameter('enabled', True, 'bool', None, None, 'Strategy enabled')
        }
        
        # MACD Strategy
        self.strategies['MACD'] = {
            'fast_period': StrategyParameter('fast_period', 12, 'int', 5, 20, 'Fast EMA period'),
            'slow_period': StrategyParameter('slow_period', 26, 'int', 15, 40, 'Slow EMA period'),
            'signal_period': StrategyParameter('signal_period', 9, 'int', 5, 15, 'Signal line period'),
            'enabled': StrategyParameter('enabled', True, 'bool', None, None, 'Strategy enabled')
        }
        
        # Bollinger Bands
        self.strategies['BollingerBands'] = {
            'period': StrategyParameter('period', 20, 'int', 10, 50, 'Moving average period'),
            'std_dev': StrategyParameter('std_dev', 2.0, 'float', 1.0, 3.0, 'Standard deviation multiplier'),
            'enabled': StrategyParameter('enabled', True, 'bool', None, None, 'Strategy enabled')
        }
        
        # MA Crossover
        self.strategies['MA_Crossover'] = {
            'fast_ma': StrategyParameter('fast_ma', 10, 'int', 5, 50, 'Fast MA period'),
            'slow_ma': StrategyParameter('slow_ma', 20, 'int', 15, 100, 'Slow MA period'),
            'ma_type': StrategyParameter('ma_type', 'EMA', 'str', None, None, 'Moving average type'),
            'enabled': StrategyParameter('enabled', True, 'bool', None, None, 'Strategy enabled')
        }
        
        # Momentum Strategy
        self.strategies['Momentum'] = {
            'lookback': StrategyParameter('lookback', 10, 'int', 5, 30, 'Lookback period'),
            'threshold': StrategyParameter('threshold', 0.02, 'float', 0.005, 0.1, 'Momentum threshold'),
            'enabled': StrategyParameter('enabled', True, 'bool', None, None, 'Strategy enabled')
        }
    
    # ==================== STRATEGY OPERATIONS ====================
    
    def get_strategy_list(self) -> List[Dict[str, Any]]:
        """Get list of all strategies with basic info"""
        with self._lock:
            strategies = []
            for name, params in self.strategies.items():
                enabled = params.get('enabled', StrategyParameter('enabled', True, 'bool')).value
                strategies.append({
                    'name': name,
                    'enabled': enabled,
                    'parameter_count': len(params),
                    'category': self._get_strategy_category(name)
                })
            return strategies
    
    def _get_strategy_category(self, name: str) -> str:
        """Get category for a strategy"""
        if any(x in name.lower() for x in ['rsi', 'macd', 'momentum']):
            return 'momentum'
        elif any(x in name.lower() for x in ['bollinger', 'ma', 'crossover']):
            return 'trend'
        else:
            return 'other'
    
    def get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get all parameters for a strategy"""
        with self._lock:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy not found: {strategy_name}")
            
            params = self.strategies[strategy_name]
            return {
                'name': strategy_name,
                'parameters': {k: v.to_dict() for k, v in params.items()},
                'category': self._get_strategy_category(strategy_name)
            }
    
    def update_parameter(self, strategy_name: str, parameter: str, value: Any, user: str = 'user') -> Dict[str, Any]:
        """Update a strategy parameter"""
        with self._lock:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy not found: {strategy_name}")
            
            if parameter not in self.strategies[strategy_name]:
                raise ValueError(f"Parameter not found: {parameter}")
            
            param = self.strategies[strategy_name][parameter]
            old_value = param.value
            
            # Validate value
            self._validate_value(param, value)
            
            # Update value
            param.value = value
            
            # Record change
            change = ParameterChange(
                timestamp=datetime.now(),
                strategy_name=strategy_name,
                parameter=parameter,
                old_value=old_value,
                new_value=value,
                user=user,
                change_type='manual'
            )
            self._change_history.append(change)
            self._total_changes += 1
            self._last_change = datetime.now()
            
            logger.info(f"Parameter updated: {strategy_name}.{parameter} = {value} (by {user})")
            
            return self.get_strategy_parameters(strategy_name)
    
    def _validate_value(self, param: StrategyParameter, value: Any):
        """Validate parameter value"""
        if param.param_type == 'int':
            if not isinstance(value, (int, float)):
                raise ValueError(f"Expected numeric value for {param.name}")
            value = int(value)
        elif param.param_type == 'float':
            if not isinstance(value, (int, float)):
                raise ValueError(f"Expected numeric value for {param.name}")
        elif param.param_type == 'bool':
            if not isinstance(value, bool):
                raise ValueError(f"Expected boolean value for {param.name}")
        
        # Check bounds
        if param.min_value is not None and value < param.min_value:
            raise ValueError(f"{param.name} must be >= {param.min_value}")
        if param.max_value is not None and value > param.max_value:
            raise ValueError(f"{param.name} must be <= {param.max_value}")
    
    # ==================== PRESETS ====================
    
    def apply_preset(self, strategy_name: str, preset: PresetType, user: str = 'user') -> Dict[str, Any]:
        """Apply a preset to a strategy or all strategies"""
        with self._lock:
            if strategy_name == 'all':
                return self._apply_preset_all(preset, user)
            
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy not found: {strategy_name}")
            
            preset_values = self._get_preset_values(strategy_name, preset)
            
            for param_name, value in preset_values.items():
                if param_name in self.strategies[strategy_name]:
                    param = self.strategies[strategy_name][param_name]
                    old_value = param.value
                    param.value = value
                    
                    # Record change
                    change = ParameterChange(
                        timestamp=datetime.now(),
                        strategy_name=strategy_name,
                        parameter=param_name,
                        old_value=old_value,
                        new_value=value,
                        user=user,
                        change_type='preset'
                    )
                    self._change_history.append(change)
            
            self._total_changes += 1
            self._last_change = datetime.now()
            
            logger.info(f"Preset {preset.value} applied to {strategy_name} (by {user})")
            
            return self.get_strategy_parameters(strategy_name)
    
    def _apply_preset_all(self, preset: PresetType, user: str) -> Dict[str, Any]:
        """Apply preset to all strategies"""
        results = {'strategies': []}
        
        for strategy_name in self.strategies.keys():
            result = self.apply_preset(strategy_name, preset, user)
            results['strategies'].append(result)
        
        return results
    
    def _get_preset_values(self, strategy_name: str, preset: PresetType) -> Dict[str, Any]:
        """Get preset values for a strategy"""
        # Define preset modifications
        presets = {
            PresetType.CONSERVATIVE: {
                'RSI': {'oversold': 25.0, 'overbought': 75.0},
                'MACD': {'fast_period': 14, 'slow_period': 30},
                'BollingerBands': {'std_dev': 2.5},
                'MA_Crossover': {'fast_ma': 15, 'slow_ma': 30},
                'Momentum': {'threshold': 0.03}
            },
            PresetType.BALANCED: {
                'RSI': {'oversold': 30.0, 'overbought': 70.0},
                'MACD': {'fast_period': 12, 'slow_period': 26},
                'BollingerBands': {'std_dev': 2.0},
                'MA_Crossover': {'fast_ma': 10, 'slow_ma': 20},
                'Momentum': {'threshold': 0.02}
            },
            PresetType.AGGRESSIVE: {
                'RSI': {'oversold': 35.0, 'overbought': 65.0},
                'MACD': {'fast_period': 10, 'slow_period': 22},
                'BollingerBands': {'std_dev': 1.5},
                'MA_Crossover': {'fast_ma': 8, 'slow_ma': 15},
                'Momentum': {'threshold': 0.015}
            }
        }
        
        return presets.get(preset, {}).get(strategy_name, {})
    
    # ==================== HISTORY & ROLLBACK ====================
    
    def get_change_history(self, strategy_name: str = None, limit: int = 50) -> List[Dict]:
        """Get change history"""
        with self._lock:
            history = list(self._change_history)
            
            if strategy_name:
                history = [c for c in history if c.strategy_name == strategy_name]
            
            # Sort by timestamp descending
            history.sort(key=lambda x: x.timestamp, reverse=True)
            history = history[:limit]
            
            return [c.to_dict() for c in history]
    
    def rollback_change(self, strategy_name: str, timestamp: str, user: str = 'user') -> Dict[str, Any]:
        """Rollback to a previous configuration"""
        with self._lock:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy not found: {strategy_name}")
            
            # Find the change at the given timestamp
            target_time = datetime.fromisoformat(timestamp)
            target_change = None
            
            for change in self._change_history:
                if change.strategy_name == strategy_name and change.timestamp <= target_time:
                    target_change = change
                    break
            
            if not target_change:
                raise ValueError(f"No change found at timestamp: {timestamp}")
            
            # Rollback to old value
            param = self.strategies[strategy_name].get(target_change.parameter)
            if param:
                old_value = param.value
                param.value = target_change.old_value
                
                # Record rollback
                rollback = ParameterChange(
                    timestamp=datetime.now(),
                    strategy_name=strategy_name,
                    parameter=target_change.parameter,
                    old_value=old_value,
                    new_value=target_change.old_value,
                    user=user,
                    change_type='rollback'
                )
                self._change_history.append(rollback)
            
            return self.get_strategy_parameters(strategy_name)
    
    # ==================== ANALYSIS ====================
    
    def estimate_impact(self, strategy_name: str, parameter: str, value: Any) -> Dict[str, Any]:
        """Estimate impact of a parameter change"""
        with self._lock:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy not found: {strategy_name}")
            
            if parameter not in self.strategies[strategy_name]:
                raise ValueError(f"Parameter not found: {parameter}")
            
            current_value = self.strategies[strategy_name][parameter].value
            
            # Calculate change percentage
            if isinstance(current_value, (int, float)) and current_value != 0:
                change_pct = ((value - current_value) / current_value) * 100
            else:
                change_pct = 0
            
            # Estimate impact (simulated)
            impact = {
                'strategy': strategy_name,
                'parameter': parameter,
                'current_value': current_value,
                'proposed_value': value,
                'change_percentage': round(change_pct, 2),
                'estimated_signal_change': round(random.uniform(-15, 15), 1),
                'estimated_risk_change': round(random.uniform(-10, 10), 1),
                'confidence': round(random.uniform(0.7, 0.95), 2),
                'warnings': []
            }
            
            # Add warnings
            if abs(change_pct) > 20:
                impact['warnings'].append('Large parameter change may significantly affect performance')
            
            return impact
    
    def quick_backtest(self, strategy_name: str, days: int = 7) -> Dict[str, Any]:
        """Run quick backtest with current parameters"""
        with self._lock:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy not found: {strategy_name}")
            
            # Simulated backtest results
            return {
                'strategy': strategy_name,
                'period_days': days,
                'total_trades': random.randint(10, 50),
                'winning_trades': random.randint(5, 30),
                'losing_trades': random.randint(5, 20),
                'win_rate': round(random.uniform(0.45, 0.65), 2),
                'total_return_pct': round(random.uniform(-5, 15), 2),
                'max_drawdown_pct': round(random.uniform(2, 10), 2),
                'sharpe_ratio': round(random.uniform(0.5, 2.5), 2),
                'timestamp': datetime.now().isoformat()
            }
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get editor statistics"""
        with self._lock:
            return {
                'total_strategies': len(self.strategies),
                'total_parameters': sum(len(p) for p in self.strategies.values()),
                'total_changes': self._total_changes,
                'last_change': self._last_change.isoformat() if self._last_change else None,
                'history_size': len(self._change_history),
                'demo_mode': self.demo_mode
            }


def get_strategy_editor() -> StrategyEditor:
    """
    Get the singleton StrategyEditor instance.
    
    Returns:
        StrategyEditor instance
    """
    global _editor_instance
    
    if _editor_instance is None:
        _editor_instance = StrategyEditor()
    
    return _editor_instance
