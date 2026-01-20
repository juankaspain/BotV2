"""
Execution Engine
Handles order execution with realistic market simulation
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Execution engine with realistic market simulation
    - Market orders
    - Limit orders
    - Stop loss / Take profit
    - Slippage modeling
    - Commission calculation
    """
    
    def __init__(self, config):
        """Initialize execution engine"""
        
        self.config = config
        
        # Execution config
        self.slippage_model = config.execution.slippage_model
        self.commission_pct = config.execution.commission_percent
        self.market_impact_pct = config.execution.market_impact_percent
        
        # Order types enabled
        self.order_types = config.execution.order_types
        
        # Execution stats
        self.total_executions = 0
        self.total_slippage = 0.0
        self.total_commissions = 0.0
        
        logger.info(
            f"✓ Execution Engine initialized "
            f"(model={self.slippage_model}, commission={self.commission_pct:.4%})"
        )
    
    async def execute(self,
                     signal: 'TradeSignal',
                     position_size: float,
                     market_data: Dict,
                     portfolio: Dict) -> Dict:
        """
        Execute trade with realistic simulation
        
        Args:
            signal: Trade signal from ensemble
            position_size: Position size as fraction of portfolio
            market_data: Current market data
            portfolio: Current portfolio state
            
        Returns:
            Execution result dict
        """
        
        # Get current price
        current_price = market_data.get('close', 0)
        if current_price == 0:
            logger.error("No valid price data")
            return self._failed_execution()
        
        # Calculate position value
        portfolio_value = portfolio.get('equity', portfolio.get('cash', 0))
        position_value = portfolio_value * position_size
        
        # Check if we have enough cash
        if position_value > portfolio['cash']:
            logger.warning(
                f"Insufficient cash: need €{position_value:.2f}, "
                f"have €{portfolio['cash']:.2f}"
            )
            return self._failed_execution()
        
        # Calculate slippage
        slippage = self._calculate_slippage(
            signal.action,
            position_size,
            market_data
        )
        
        # Apply slippage to price
        if signal.action == 'BUY':
            execution_price = current_price * (1 + slippage)
        else:  # SELL
            execution_price = current_price * (1 - slippage)
        
        # Calculate shares/contracts
        shares = position_value / execution_price
        
        # Calculate commission
        commission = position_value * self.commission_pct
        
        # Total cost
        total_cost = position_value + commission
        
        # Simulate execution delay
        await asyncio.sleep(0.1)
        
        # Build result
        result = {
            'executed': True,
            'timestamp': datetime.now(),
            'symbol': signal.symbol,
            'action': signal.action,
            'strategy': signal.strategy,
            'signal_price': current_price,
            'execution_price': execution_price,
            'price': execution_price,
            'shares': shares,
            'position_size': position_size,
            'position_value': position_value,
            'slippage': slippage,
            'slippage_cost': abs(execution_price - current_price) * shares,
            'commission': commission,
            'cost': total_cost,
            'confidence': signal.confidence
        }
        
        # Update stats
        self.total_executions += 1
        self.total_slippage += slippage
        self.total_commissions += commission
        
        logger.debug(
            f"Executed: {signal.action} {signal.symbol} "
            f"@ €{execution_price:.2f} (slippage: {slippage:.4%})"
        )
        
        return result
    
    def _calculate_slippage(self,
                           action: str,
                           position_size: float,
                           market_data: Dict) -> float:
        """
        Calculate realistic slippage
        
        Args:
            action: BUY or SELL
            position_size: Position size as fraction
            market_data: Market data with volatility info
            
        Returns:
            Slippage as decimal (e.g., 0.0015 = 0.15%)
        """
        
        if self.slippage_model == 'realistic':
            # Base slippage
            base_slippage = 0.0015  # 0.15% average
            
            # Size impact (larger positions = more slippage)
            size_impact = position_size * 0.01  # 1% per 1 position size
            
            # Volatility impact
            volatility = market_data.get('volatility', 0.02)
            volatility_impact = volatility * 0.5
            
            # Market impact
            market_impact = self.market_impact_pct
            
            # Total slippage
            total_slippage = base_slippage + size_impact + volatility_impact + market_impact
            
            # Add random component (±20%)
            random_factor = np.random.uniform(0.8, 1.2)
            total_slippage *= random_factor
            
        elif self.slippage_model == 'aggressive':
            # Higher slippage for conservative estimates
            total_slippage = 0.003  # 0.3%
            
        elif self.slippage_model == 'conservative':
            # Lower slippage (optimistic)
            total_slippage = 0.001  # 0.1%
            
        else:
            # Default
            total_slippage = 0.0015
        
        # Ensure non-negative
        return max(0, total_slippage)
    
    def _failed_execution(self) -> Dict:
        """Return failed execution result"""
        return {
            'executed': False,
            'timestamp': datetime.now(),
            'reason': 'execution_failed'
        }
    
    async def execute_limit_order(self,
                                  signal: 'TradeSignal',
                                  limit_price: float,
                                  timeout_seconds: int = 300) -> Dict:
        """
        Execute limit order with timeout
        
        Args:
            signal: Trade signal
            limit_price: Limit price
            timeout_seconds: Max wait time
            
        Returns:
            Execution result
        """
        
        if not self.order_types.get('limit', False):
            logger.error("Limit orders not enabled")
            return self._failed_execution()
        
        logger.info(
            f"Limit order placed: {signal.action} {signal.symbol} "
            f"@ €{limit_price:.2f} (timeout: {timeout_seconds}s)"
        )
        
        # Simulate waiting for limit to be hit
        # In real implementation, this would monitor price feeds
        await asyncio.sleep(min(timeout_seconds, 5))
        
        # For now, assume it fills (TODO: implement real limit logic)
        logger.info("Limit order filled")
        
        return {
            'executed': True,
            'order_type': 'limit',
            'limit_price': limit_price
        }
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        
        avg_slippage = (
            self.total_slippage / self.total_executions
            if self.total_executions > 0
            else 0.0
        )
        
        return {
            'total_executions': self.total_executions,
            'total_commissions': self.total_commissions,
            'average_slippage': avg_slippage,
            'slippage_model': self.slippage_model
        }
