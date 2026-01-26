"""
Core Engine Modules

Includes:
- ExecutionEngine: Order execution with realistic simulation
- RiskManager: Portfolio risk management
- LiquidationDetector: Liquidation cascade detection
- StateManager: Persistent state management
- OrderOptimizer: Commission and slippage minimization
"""

from .execution_engine import ExecutionEngine
from .risk_manager import RiskManager
from .liquidation_detector import LiquidationDetector
from .state_manager import StateManager
from .order_optimizer import (
    OrderOptimizer,
    OrderType,
    OrderOptimizationStrategy,
    OrderExecutionPlan,
    ExchangeCommissionConfig
)
from .order_optimizer_config import (
    ExchangeConfigs,
    get_optimizer_for_exchange
)

__all__ = [
    'ExecutionEngine',
    'RiskManager',
    'LiquidationDetector',
    'StateManager',
    'OrderOptimizer',
    'OrderType',
    'OrderOptimizationStrategy',
    'OrderExecutionPlan',
    'ExchangeCommissionConfig',
    'ExchangeConfigs',
    'get_optimizer_for_exchange'
]
