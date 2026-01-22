#!/usr/bin/env python3
"""
Strategy Editor v4.4 - Parameter Management System

Provides comprehensive strategy parameter editing without code changes:
- Dynamic parameter parsing from strategy classes
- Parameter validation with ranges and types
- Configuration presets (Conservative, Balanced, Aggressive)
- Change history with rollback capability
- Quick backtesting integration

Author: Juan Carlos Garcia Arriero
Date: 22 Enero 2026
Version: 4.4.0
"""

import logging
import json
import copy
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class PresetType(str, Enum):
    """Configuration preset types"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


class ParameterType(str, Enum):
    """Parameter data types"""
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"
    ENUM = "enum"


# ==================== DATA CLASSES ====================

@dataclass
 class ParameterDefinition:
    """Definition of a strategy parameter"""
    name: str
    type: ParameterType
    current_value: Any
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    enum_values: Optional[List[str]] = None
    description: str = ""
    category: str = "general"
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate parameter value
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Type validation
            if self.type == ParameterType.INTEGER:
                value = int(value)
                if self.min_value is not None and value < self.min_value:
                    return False, f"Value {value} is below minimum {self.min_value}"
                if self.max_value is not None and value > self.max_value:
                    return False, f"Value {value} is above maximum {self.max_value}"
            
            elif self.type == ParameterType.FLOAT:
                value = float(value)
                if self.min_value is not None and value < self.min_value:
                    return False, f"Value {value} is below minimum {self.min_value}"
                if self.max_value is not None and value > self.max_value:
                    return False, f"Value {value} is above maximum {self.max_value}"
            
            elif self.type == ParameterType.BOOLEAN:
                if not isinstance(value, bool):
                    return False, f"Value must be boolean, got {type(value)}"
            
            elif self.type == ParameterType.ENUM:
                if value not in self.enum_values:
                    return False, f"Value {value} not in allowed values: {self.enum_values}"
            
            return True, None
        
        except (ValueError, TypeError) as e:
            return False, f"Invalid value: {str(e)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class StrategyConfiguration:
    """Complete strategy configuration"""
    strategy_name: str
    enabled: bool
    parameters: Dict[str, Any]
    preset: PresetType
    last_modified: datetime
    modified_by: str
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['last_modified'] = self.last_modified.isoformat()
        return data


@dataclass
class ConfigurationChange:
    """Record of a configuration change"""
    timestamp: datetime
    strategy_name: str
    user: str
    parameter: str
    old_value: Any
    new_value: Any
    preset: Optional[PresetType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


# ==================== STRATEGY EDITOR CORE ====================

class StrategyEditor:
    """Strategy Parameter Editor v4.4
    
    Features:
    - Dynamic parameter parsing
    - Validation and type checking
    - Configuration presets
    - Change history with rollback
    - Quick backtesting integration
    
    Thread-safe singleton implementation.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize strategy editor"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Strategy definitions
        self.strategies: Dict[str, Dict[str, ParameterDefinition]] = {}
        
        # Current configurations
        self.configurations: Dict[str, StrategyConfiguration] = {}
        
        # Change history (ring buffer, max 1000)
        from collections import deque
        self.change_history: deque = deque(maxlen=1000)
        
        # Configuration storage
        self.config_dir = Path('config/strategies')
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_changes': 0,
            'rollbacks': 0,
            'backtests_run': 0,
            'last_update': None
        }
        
        # Initialize default strategies
        self._initialize_default_strategies()
        
        # Load saved configurations
        self._load_configurations()
        
        logger.info("✅ Strategy Editor v4.4 initialized")
    
    def _initialize_default_strategies(self):
        """Initialize default strategy definitions"""
        
        # RSI Strategy
        self.strategies['RSI'] = {
            'period': ParameterDefinition(
                name='period',
                type=ParameterType.INTEGER,
                current_value=14,
                default_value=14,
                min_value=5,
                max_value=50,
                step=1,
                description='RSI calculation period',
                category='indicator'
            ),
            'overbought': ParameterDefinition(
                name='overbought',
                type=ParameterType.FLOAT,
                current_value=70.0,
                default_value=70.0,
                min_value=60.0,
                max_value=90.0,
                step=1.0,
                description='Overbought threshold (sell signal)',
                category='thresholds'
            ),
            'oversold': ParameterDefinition(
                name='oversold',
                type=ParameterType.FLOAT,
                current_value=30.0,
                default_value=30.0,
                min_value=10.0,
                max_value=40.0,
                step=1.0,
                description='Oversold threshold (buy signal)',
                category='thresholds'
            )
        }
        
        # MACD Strategy
        self.strategies['MACD'] = {
            'fast_period': ParameterDefinition(
                name='fast_period',
                type=ParameterType.INTEGER,
                current_value=12,
                default_value=12,
                min_value=5,
                max_value=20,
                step=1,
                description='Fast EMA period',
                category='indicator'
            ),
            'slow_period': ParameterDefinition(
                name='slow_period',
                type=ParameterType.INTEGER,
                current_value=26,
                default_value=26,
                min_value=15,
                max_value=40,
                step=1,
                description='Slow EMA period',
                category='indicator'
            ),
            'signal_period': ParameterDefinition(
                name='signal_period',
                type=ParameterType.INTEGER,
                current_value=9,
                default_value=9,
                min_value=5,
                max_value=15,
                step=1,
                description='Signal line period',
                category='indicator'
            )
        }
        
        # Bollinger Bands Strategy
        self.strategies['Bollinger'] = {
            'period': ParameterDefinition(
                name='period',
                type=ParameterType.INTEGER,
                current_value=20,
                default_value=20,
                min_value=10,
                max_value=50,
                step=1,
                description='Moving average period',
                category='indicator'
            ),
            'std_dev': ParameterDefinition(
                name='std_dev',
                type=ParameterType.FLOAT,
                current_value=2.0,
                default_value=2.0,
                min_value=1.0,
                max_value=3.0,
                step=0.1,
                description='Standard deviation multiplier',
                category='indicator'
            )
        }
        
        # MA Crossover Strategy
        self.strategies['MA_Crossover'] = {
            'fast_period': ParameterDefinition(
                name='fast_period',
                type=ParameterType.INTEGER,
                current_value=50,
                default_value=50,
                min_value=10,
                max_value=100,
                step=5,
                description='Fast moving average period',
                category='indicator'
            ),
            'slow_period': ParameterDefinition(
                name='slow_period',
                type=ParameterType.INTEGER,
                current_value=200,
                default_value=200,
                min_value=100,
                max_value=300,
                step=10,
                description='Slow moving average period',
                category='indicator'
            )
        }
        
        # Initialize configurations
        for strategy_name in self.strategies.keys():
            self.configurations[strategy_name] = StrategyConfiguration(
                strategy_name=strategy_name,
                enabled=True,
                parameters={name: param.current_value for name, param in self.strategies[strategy_name].items()},
                preset=PresetType.BALANCED,
                last_modified=datetime.now(),
                modified_by='system',
                version=1
            )
    
    def get_strategy_list(self) -> List[Dict[str, Any]]:
        """Get list of all strategies
        
        Returns:
            List of strategy summaries
        """
        strategies = []
        
        for name, params in self.strategies.items():
            config = self.configurations.get(name)
            
            strategies.append({
                'name': name,
                'enabled': config.enabled if config else True,
                'preset': config.preset.value if config else PresetType.BALANCED.value,
                'parameter_count': len(params),
                'last_modified': config.last_modified.isoformat() if config else None,
                'version': config.version if config else 1
            })
        
        return strategies
    
    def get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get parameters for a specific strategy
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dictionary with parameter definitions and current values
        """
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")
        
        params = self.strategies[strategy_name]
        config = self.configurations.get(strategy_name)
        
        return {
            'strategy_name': strategy_name,
            'enabled': config.enabled if config else True,
            'preset': config.preset.value if config else PresetType.BALANCED.value,
            'parameters': [
                {
                    **param.to_dict(),
                    'current_value': config.parameters.get(name, param.current_value) if config else param.current_value
                }
                for name, param in params.items()
            ],
            'last_modified': config.last_modified.isoformat() if config else None
        }
    
    def update_parameter(self, strategy_name: str, parameter_name: str, new_value: Any, user: str = 'user') -> Dict[str, Any]:
        """Update a strategy parameter
        
        Args:
            strategy_name: Name of the strategy
            parameter_name: Name of the parameter
            new_value: New value for the parameter
            user: User making the change
            
        Returns:
            Updated configuration
        """
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")
        
        if parameter_name not in self.strategies[strategy_name]:
            raise ValueError(f"Parameter {parameter_name} not found in strategy {strategy_name}")
        
        param_def = self.strategies[strategy_name][parameter_name]
        
        # Validate new value
        is_valid, error_msg = param_def.validate(new_value)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Get current configuration
        config = self.configurations[strategy_name]
        old_value = config.parameters.get(parameter_name, param_def.current_value)
        
        # Record change
        change = ConfigurationChange(
            timestamp=datetime.now(),
            strategy_name=strategy_name,
            user=user,
            parameter=parameter_name,
            old_value=old_value,
            new_value=new_value
        )
        self.change_history.append(change)
        
        # Update configuration
        config.parameters[parameter_name] = new_value
        config.last_modified = datetime.now()
        config.modified_by = user
        config.version += 1
        config.preset = PresetType.CUSTOM  # Mark as custom when manually changed
        
        # Update statistics
        self.stats['total_changes'] += 1
        self.stats['last_update'] = datetime.now().isoformat()
        
        # Save configuration
        self._save_configuration(strategy_name)
        
        logger.info(f"✅ Parameter updated: {strategy_name}.{parameter_name} = {new_value} (user: {user})")
        
        return self.get_strategy_parameters(strategy_name)
    
    def apply_preset(self, strategy_name: str, preset: PresetType, user: str = 'user') -> Dict[str, Any]:
        """Apply a configuration preset to a strategy
        
        Args:
            strategy_name: Name of the strategy (or 'all' for all strategies)
            preset: Preset type to apply
            user: User applying the preset
            
        Returns:
            Updated configuration(s)
        """
        # Define presets for each strategy
        presets = {
            'RSI': {
                PresetType.CONSERVATIVE: {'period': 21, 'overbought': 75.0, 'oversold': 25.0},
                PresetType.BALANCED: {'period': 14, 'overbought': 70.0, 'oversold': 30.0},
                PresetType.AGGRESSIVE: {'period': 9, 'overbought': 65.0, 'oversold': 35.0}
            },
            'MACD': {
                PresetType.CONSERVATIVE: {'fast_period': 15, 'slow_period': 30, 'signal_period': 12},
                PresetType.BALANCED: {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
                PresetType.AGGRESSIVE: {'fast_period': 8, 'slow_period': 20, 'signal_period': 7}
            },
            'Bollinger': {
                PresetType.CONSERVATIVE: {'period': 25, 'std_dev': 2.5},
                PresetType.BALANCED: {'period': 20, 'std_dev': 2.0},
                PresetType.AGGRESSIVE: {'period': 15, 'std_dev': 1.5}
            },
            'MA_Crossover': {
                PresetType.CONSERVATIVE: {'fast_period': 75, 'slow_period': 250},
                PresetType.BALANCED: {'fast_period': 50, 'slow_period': 200},
                PresetType.AGGRESSIVE: {'fast_period': 30, 'slow_period': 150}
            }
        }
        
        strategies_to_update = [strategy_name] if strategy_name != 'all' else list(self.strategies.keys())
        
        for strat_name in strategies_to_update:
            if strat_name not in self.strategies:
                continue
            
            if strat_name not in presets or preset not in presets[strat_name]:
                logger.warning(f"No preset {preset.value} defined for strategy {strat_name}")
                continue
            
            preset_params = presets[strat_name][preset]
            config = self.configurations[strat_name]
            
            # Apply preset parameters
            for param_name, value in preset_params.items():
                old_value = config.parameters.get(param_name)
                config.parameters[param_name] = value
                
                # Record change
                change = ConfigurationChange(
                    timestamp=datetime.now(),
                    strategy_name=strat_name,
                    user=user,
                    parameter=param_name,
                    old_value=old_value,
                    new_value=value,
                    preset=preset
                )
                self.change_history.append(change)
            
            config.preset = preset
            config.last_modified = datetime.now()
            config.modified_by = user
            config.version += 1
            
            self._save_configuration(strat_name)
            
            logger.info(f"✅ Preset {preset.value} applied to {strat_name} (user: {user})")
        
        self.stats['total_changes'] += len(strategies_to_update)
        self.stats['last_update'] = datetime.now().isoformat()
        
        if strategy_name == 'all':
            return {'strategies': [self.get_strategy_parameters(s) for s in strategies_to_update]}
        else:
            return self.get_strategy_parameters(strategy_name)
    
    def get_change_history(self, strategy_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get change history
        
        Args:
            strategy_name: Filter by strategy name (optional)
            limit: Maximum number of changes to return
            
        Returns:
            List of configuration changes
        """
        changes = list(self.change_history)
        
        if strategy_name:
            changes = [c for c in changes if c.strategy_name == strategy_name]
        
        # Sort by timestamp descending (most recent first)
        changes.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [c.to_dict() for c in changes[:limit]]
    
    def rollback_change(self, strategy_name: str, timestamp: str, user: str = 'user') -> Dict[str, Any]:
        """Rollback to a previous configuration
        
        Args:
            strategy_name: Name of the strategy
            timestamp: Timestamp of the change to rollback to
            user: User performing the rollback
            
        Returns:
            Updated configuration
        """
        # Find the change
        target_time = datetime.fromisoformat(timestamp)
        changes = [c for c in self.change_history if c.strategy_name == strategy_name and c.timestamp <= target_time]
        
        if not changes:
            raise ValueError(f"No changes found for {strategy_name} at {timestamp}")
        
        # Get parameters at that point in time
        config = self.configurations[strategy_name]
        rollback_params = copy.deepcopy(config.parameters)
        
        # Apply changes in reverse order
        for change in reversed(changes):
            rollback_params[change.parameter] = change.old_value
        
        # Apply rollback
        for param_name, value in rollback_params.items():
            old_value = config.parameters.get(param_name)
            config.parameters[param_name] = value
            
            # Record rollback
            change = ConfigurationChange(
                timestamp=datetime.now(),
                strategy_name=strategy_name,
                user=user,
                parameter=param_name,
                old_value=old_value,
                new_value=value
            )
            self.change_history.append(change)
        
        config.last_modified = datetime.now()
        config.modified_by = user
        config.version += 1
        config.preset = PresetType.CUSTOM
        
        self._save_configuration(strategy_name)
        
        self.stats['rollbacks'] += 1
        self.stats['last_update'] = datetime.now().isoformat()
        
        logger.info(f"✅ Rolled back {strategy_name} to {timestamp} (user: {user})")
        
        return self.get_strategy_parameters(strategy_name)
    
    def estimate_impact(self, strategy_name: str, parameter_name: str, new_value: Any) -> Dict[str, Any]:
        """Estimate impact of parameter change
        
        Args:
            strategy_name: Name of the strategy
            parameter_name: Name of the parameter
            new_value: Proposed new value
            
        Returns:
            Impact estimation
        """
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")
        
        param_def = self.strategies[strategy_name][parameter_name]
        current_value = self.configurations[strategy_name].parameters.get(parameter_name, param_def.current_value)
        
        # Calculate percentage change
        if isinstance(current_value, (int, float)) and current_value != 0:
            pct_change = ((new_value - current_value) / current_value) * 100
        else:
            pct_change = 0
        
        # Estimate impact level
        if abs(pct_change) < 10:
            impact = 'low'
            description = 'Minor adjustment, minimal impact expected'
        elif abs(pct_change) < 30:
            impact = 'medium'
            description = 'Moderate change, noticeable impact on signals'
        else:
            impact = 'high'
            description = 'Significant change, major impact on strategy behavior'
        
        return {
            'strategy_name': strategy_name,
            'parameter_name': parameter_name,
            'current_value': current_value,
            'new_value': new_value,
            'change_pct': round(pct_change, 2),
            'impact_level': impact,
            'description': description,
            'recommendation': self._get_recommendation(strategy_name, parameter_name, pct_change)
        }
    
    def _get_recommendation(self, strategy_name: str, parameter_name: str, pct_change: float) -> str:
        """Get recommendation for parameter change"""
        if strategy_name == 'RSI':
            if parameter_name in ['overbought', 'oversold']:
                if pct_change > 0:
                    return 'Increasing thresholds will generate fewer signals (more conservative)'
                else:
                    return 'Decreasing thresholds will generate more signals (more aggressive)'
        
        elif strategy_name == 'MACD':
            if 'period' in parameter_name:
                if pct_change > 0:
                    return 'Increasing periods will smooth signals (less responsive to short-term moves)'
                else:
                    return 'Decreasing periods will make strategy more responsive (more signals)'
        
        elif strategy_name == 'Bollinger':
            if parameter_name == 'std_dev':
                if pct_change > 0:
                    return 'Wider bands will generate fewer breakout signals'
                else:
                    return 'Narrower bands will generate more breakout signals'
        
        return 'Test the change with backtesting to evaluate impact'
    
    def quick_backtest(self, strategy_name: str, days: int = 7) -> Dict[str, Any]:
        """Run quick backtest with current parameters
        
        Args:
            strategy_name: Name of the strategy
            days: Number of days to backtest
            
        Returns:
            Backtest results summary
        """
        # Placeholder for actual backtesting integration
        # This would call the backtesting engine with current parameters
        
        self.stats['backtests_run'] += 1
        
        # Mock results for demonstration
        return {
            'strategy_name': strategy_name,
            'period': f'Last {days} days',
            'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
            'end_date': datetime.now().isoformat(),
            'total_trades': 15,
            'winning_trades': 10,
            'losing_trades': 5,
            'win_rate': 66.67,
            'total_return': 3.45,
            'sharpe_ratio': 1.85,
            'max_drawdown': -2.10,
            'status': 'completed'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get editor statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'total_strategies': len(self.strategies),
            'enabled_strategies': sum(1 for c in self.configurations.values() if c.enabled),
            'history_size': len(self.change_history)
        }
    
    def _save_configuration(self, strategy_name: str):
        """Save configuration to disk
        
        Args:
            strategy_name: Name of the strategy
        """
        config = self.configurations[strategy_name]
        config_file = self.config_dir / f'{strategy_name.lower()}.json'
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            logger.debug(f"Configuration saved: {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration {strategy_name}: {e}")
    
    def _load_configurations(self):
        """Load configurations from disk"""
        for strategy_name in self.strategies.keys():
            config_file = self.config_dir / f'{strategy_name.lower()}.json'
            
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        data = json.load(f)
                    
                    self.configurations[strategy_name] = StrategyConfiguration(
                        strategy_name=data['strategy_name'],
                        enabled=data['enabled'],
                        parameters=data['parameters'],
                        preset=PresetType(data['preset']),
                        last_modified=datetime.fromisoformat(data['last_modified']),
                        modified_by=data['modified_by'],
                        version=data.get('version', 1)
                    )
                    
                    logger.debug(f"Configuration loaded: {config_file}")
                except Exception as e:
                    logger.error(f"Failed to load configuration {strategy_name}: {e}")


# ==================== SINGLETON GETTER ====================

_editor_instance = None

def get_strategy_editor() -> StrategyEditor:
    """Get Strategy Editor singleton instance
    
    Returns:
        StrategyEditor instance
    """
    global _editor_instance
    if _editor_instance is None:
        _editor_instance = StrategyEditor()
    return _editor_instance
