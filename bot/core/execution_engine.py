"""
Execution Engine - Integrated with Order Optimizer

Handles order execution with:
- Realistic market simulation
- Intelligent order type selection (market vs limit)
- Commission minimization via OrderOptimizer
- Crypto trading (Binance, Kraken, Coinbase, Finst)
- Separate logic for Polymarket (prediction markets)

Author: Juan Carlos Garcia Arriero
Date: January 2026
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from enum import Enum
import numpy as np
from bot.core.order_optimizer import OrderOptimizer, OrderOptimizationStrategy

from bot.core.order_optimizer_config import get_optimizer_for_exchange

logger = logging.getLogger(__name__)


class MarketType(Enum):
    """Type of market for execution"""
    CRYPTO_SPOT = "crypto_spot"      # Binance, Kraken, Coinbase, Finst
    PREDICTION_MARKET = "prediction"  # Polymarket, Kalshi, etc.


class ExecutionEngine:
    """
    Unified execution engine with market-aware routing
    
    Handles:
    - Crypto spot trading with commission optimization
    - Prediction markets with binary outcomes
    - Realistic market simulation
    - Comprehensive execution tracking
    """
    
    def __init__(self, config):
        """
        Initialize execution engine
        
        Args:
            config: Configuration object with execution settings
        """
        
        self.config = config
        
        # Execution config
        self.slippage_model = config.execution.slippage_model
        self.market_impact_pct = config.execution.market_impact_percent
        self.order_types = config.execution.order_types
        
        # Execution stats
        self.total_executions = 0
        self.total_slippage = 0.0
        self.total_commissions = 0.0
        
        # CRYPTO TRADING: Initialize order optimizer
        self.order_optimizer = None
        self._initialize_order_optimizer(config)
        
        logger.info(
            f"✓ Execution Engine initialized "
            f"(model={self.slippage_model}, "
            f"optimizer={self.order_optimizer is not None})"
        )
    
    def _initialize_order_optimizer(self, config):
        """
        Initialize order optimizer for crypto trading
        
        Args:
            config: Configuration object
        """
        try:
            # Get exchange from config
            exchange = config.exchanges.get('primary', 'binance')
            
            # Check if optimizer is enabled in config
            exchange_config = config.exchanges.get(exchange, {})
            if not exchange_config.get('enabled', False):
                logger.warning(f"Exchange {exchange} not enabled - optimizer skipped")
                return
            
            # Initialize optimizer
            self.order_optimizer = get_optimizer_for_exchange(
                exchange_name=exchange,
                optimization_strategy=OrderOptimizationStrategy.HYBRID,
                volume_30d=0.0,  # Will be updated as trading happens
                has_bnb=(exchange.lower() == 'binance'),  # BNB only for Binance
                max_execution_time=300
            )
            
            logger.info(f"✓ Order Optimizer initialized for {exchange}")
            
        except Exception as e:
            logger.warning(f"Could not initialize order optimizer: {e}")
            self.order_optimizer = None
    
    async def execute(
        self,
        signal: 'TradeSignal',
        position_size: float,
        market_data: Dict,
        portfolio: Dict,
        market_type: MarketType = MarketType.CRYPTO_SPOT
    ) -> Dict:
        """
        Execute trade with market-aware routing
        
        Args:
            signal: Trade signal from ensemble
            position_size: Position size as fraction of portfolio
            market_data: Current market data
            portfolio: Current portfolio state
            market_type: Type of market (CRYPTO_SPOT or PREDICTION_MARKET)
            
        Returns:
            Execution result dict with full details
        """
        
        # Route to appropriate execution method
        if market_type == MarketType.CRYPTO_SPOT:
            return await self._execute_crypto_spot(
                signal, position_size, market_data, portfolio
            )
        elif market_type == MarketType.PREDICTION_MARKET:
            return await self._execute_prediction_market(
                signal, position_size, market_data, portfolio
            )
        else:
            logger.error(f"Unknown market type: {market_type}")
            return self._failed_execution()
    
    async def _execute_crypto_spot(
        self,
        signal: 'TradeSignal',
        position_size: float,
        market_data: Dict,
        portfolio: Dict
    ) -> Dict:
        """
        Execute crypto spot trade with order optimization
        
        This is where OrderOptimizer is used:
        - Analyzes signal confidence, order size, liquidity, volatility
        - Decides: market order? limit? split execution?
        - Minimizes commissions while maintaining fill probability
        
        Args:
            signal: Trade signal
            position_size: Position size fraction
            market_data: Market data
            portfolio: Portfolio state
            
        Returns:
            Execution result
        """
        
        # Validate inputs
        current_price = market_data.get('close', 0)
        if current_price == 0:
            logger.error("No valid price data for crypto execution")
            return self._failed_execution()
        
        # Calculate position value
        portfolio_value = portfolio.get('equity', portfolio.get('cash', 0))
        position_value = portfolio_value * position_size
        
        # Check cash
        if position_value > portfolio['cash']:
            logger.warning(
                f"Insufficient cash: need €{position_value:.2f}, "
                f"have €{portfolio['cash']:.2f}"
            )
            return self._failed_execution()
        
        # Use OrderOptimizer if available
        execution_plan = None
        if self.order_optimizer:
            try:
                execution_plan = self.order_optimizer.create_execution_plan(
                    symbol=signal.symbol,
                    side=signal.action,
                    amount=position_value,
                    current_price=current_price,
                    market_volatility=market_data.get('volatility', 0.02),
                    market_spread=market_data.get('spread', 0.0005),
                    strategy_name=signal.strategy,
                    confidence=signal.confidence,
                    liquidity_rank=self._get_liquidity_rank(signal.symbol)
                )
                
                logger.debug(
                    f"Optimization: {signal.symbol} {signal.action} "
                    f"→ {execution_plan.order_type.value} "
                    f"(fee: {execution_plan.estimated_commission_percent:.4%})"
                )
                
            except Exception as e:
                logger.warning(f"Order optimizer failed: {e}, using fallback")
                execution_plan = None
        
        # If optimizer not available, use fallback
        if execution_plan is None:
            execution_plan = self._create_fallback_plan(
                signal.symbol,
                signal.action,
                position_value,
                current_price
            )
        
        # Execute the optimized plan
        result = await self._execute_plan(
            execution_plan,
            signal,
            position_value,
            current_price,
            portfolio_value,
            market_data
        )
        
        return result
    
    async def _execute_prediction_market(
        self,
        signal: 'TradeSignal',
        position_size: float,
        market_data: Dict,
        portfolio: Dict
    ) -> Dict:
        """
        Execute prediction market trade (Polymarket, Kalshi, etc.)
        
        Note: Prediction markets use different logic:
        - Binary outcomes (YES/NO)
        - Fixed fees per contract
        - No order type selection needed
        - Not applicable for OrderOptimizer
        
        Args:
            signal: Trade signal
            position_size: Position size fraction
            market_data: Market data
            portfolio: Portfolio state
            
        Returns:
            Execution result
        """
        
        logger.info(
            f"Executing prediction market trade: {signal.symbol} "
            f"{signal.action}"
        )
        
        # Calculate position value
        portfolio_value = portfolio.get('equity', portfolio.get('cash', 0))
        position_value = portfolio_value * position_size
        
        # Check cash
        if position_value > portfolio['cash']:
            logger.warning(
                f"Insufficient cash for prediction: "
                f"need €{position_value:.2f}, have €{portfolio['cash']:.2f}"
            )
            return self._failed_execution()
        
        # Get market probability
        market_prob = market_data.get('probability', 0.5)
        
        # Calculate expected value
        if signal.action == 'BUY':
            expected_value = (1 - market_prob) * 1.0  # Win if prob realized
            fee = market_data.get('fee', 0.02)  # Polymarket ~2% fee
        else:  # SELL / NO
            expected_value = market_prob * 1.0
            fee = market_data.get('fee', 0.02)
        
        # Calculate fee cost
        fee_cost = position_value * fee
        
        # Build result
        result = {
            'executed': True,
            'timestamp': datetime.now(),
            'market_type': MarketType.PREDICTION_MARKET.value,
            'symbol': signal.symbol,
            'action': signal.action,
            'strategy': signal.strategy,
            'position_value': position_value,
            'market_probability': market_prob,
            'expected_value': expected_value,
            'fee': fee,
            'fee_cost': fee_cost,
            'net_position': position_value - fee_cost,
            'confidence': signal.confidence,
            'note': 'Prediction market - binary outcome, fixed fee'
        }
        
        self.total_executions += 1
        self.total_commissions += fee_cost
        
        logger.debug(
            f"Prediction market executed: {signal.symbol} "
            f"@ prob {market_prob:.1%}, cost: €{fee_cost:.2f}"
        )
        
        return result
    
    async def _execute_plan(
        self,
        execution_plan,
        signal,
        position_value: float,
        current_price: float,
        portfolio_value: float,
        market_data: Dict
    ) -> Dict:
        """
        Execute the optimized plan orders
        
        Args:
            execution_plan: OrderExecutionPlan from optimizer
            signal: Original trade signal
            position_value: Total position value
            current_price: Current market price
            portfolio_value: Total portfolio value
            market_data: Market data
            
        Returns:
            Execution result
        """
        
        total_shares = 0.0
        total_cost = 0.0
        execution_prices = []
        
        # Execute each order in the plan
        for order in execution_plan.orders:
            order_size = order.get('size', position_value)
            order_type = order.get('type', 'market')
            
            # Calculate slippage
            slippage = self._calculate_slippage(
                signal.action,
                order_size / portfolio_value if portfolio_value > 0 else 0,
                market_data
            )
            
            # Apply slippage
            if signal.action == 'BUY':
                execution_price = current_price * (1 + slippage)
            else:
                execution_price = current_price * (1 - slippage)
            
            execution_prices.append(execution_price)
            
            # Calculate shares
            shares = order_size / execution_price
            total_shares += shares
            
            # Add to cost
            total_cost += order_size
            
            # Simulate execution delay for split orders
            if 'delay_seconds' in order:
                await asyncio.sleep(order['delay_seconds'])
        
        # Calculate average execution price
        avg_execution_price = total_cost / total_shares if total_shares > 0 else current_price
        
        # Commission
        commission = execution_plan.estimated_total_commission
        
        # Build final result
        result = {
            'executed': True,
            'timestamp': datetime.now(),
            'market_type': MarketType.CRYPTO_SPOT.value,
            'symbol': signal.symbol,
            'action': signal.action,
            'strategy': signal.strategy,
            'signal_price': current_price,
            'execution_price': avg_execution_price,
            'price': avg_execution_price,
            'shares': total_shares,
            'position_size': position_value,
            'position_value': position_value,
            'slippage': np.mean(execution_prices) - current_price if execution_prices else 0,
            'slippage_pct': (np.mean(execution_prices) - current_price) / current_price if execution_prices else 0,
            'commission': commission,
            'commission_pct': execution_plan.estimated_commission_percent,
            'total_cost': position_value + commission,
            'num_orders': execution_plan.number_of_orders,
            'order_type': execution_plan.order_type.value,
            'optimization_strategy': execution_plan.optimization_strategy.value,
            'confidence': signal.confidence,
            'savings_vs_market': max(0, (0.001 - execution_plan.estimated_commission_percent) * position_value)
        }
        
        # Update stats
        self.total_executions += 1
        self.total_commissions += commission
        self.total_slippage += result['slippage_pct']
        
        logger.debug(
            f"Executed: {signal.action} {signal.symbol} "
            f"@ €{avg_execution_price:.2f} "
            f"(commission: {execution_plan.estimated_commission_percent:.4%}, "
            f"orders: {execution_plan.number_of_orders})"
        )
        
        return result
    
    def _create_fallback_plan(self, symbol: str, side: str, amount: float, price: float):
        """
        Create fallback execution plan if optimizer unavailable
        
        Uses conservative market order approach
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            amount: Amount in EUR
            price: Current price
            
        Returns:
            Mock execution plan
        """
        
        # Fallback: single market order with standard commission
        commission_pct = 0.001  # 0.10% - Binance standard taker
        
        return type('ExecutionPlan', (), {
            'symbol': symbol,
            'side': side,
            'total_amount': amount,
            'order_type': type('OrderType', (), {'value': 'market'}),
            'optimization_strategy': type('Strategy', (), {'value': 'fallback'}),
            'number_of_orders': 1,
            'orders': [{'type': 'market', 'size': amount}],
            'estimated_commission_percent': commission_pct,
            'estimated_total_commission': amount * commission_pct,
            'estimated_slippage_percent': 0.0015,
            'estimated_total_cost': amount * (1 + commission_pct + 0.0015)
        })()
    
    def _get_liquidity_rank(self, symbol: str) -> int:
        """
        Get liquidity rank for a trading pair
        
        Args:
            symbol: Trading pair (e.g., 'BTC/EUR')
            
        Returns:
            Liquidity rank (1=most liquid, 5=least liquid)
        """
        
        # Liquidity ranking (can be updated with real data)
        liquidity_tiers = {
            'BTC/EUR': 1,  # Most liquid
            'ETH/EUR': 1,
            'BNB/EUR': 2,
            'ADA/EUR': 3,
            'SOL/EUR': 2,
            'XRP/EUR': 3,
            'USDT/EUR': 1,
            'USDC/EUR': 2,
        }
        
        return liquidity_tiers.get(symbol, 3)  # Default: medium liquidity
    
    def _calculate_slippage(
        self,
        action: str,
        position_size: float,
        market_data: Dict
    ) -> float:
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
            total_slippage = 0.003  # 0.3%
            
        elif self.slippage_model == 'conservative':
            total_slippage = 0.001  # 0.1%
            
        else:
            total_slippage = 0.0015
        
        return max(0, total_slippage)
    
    def _failed_execution(self) -> Dict:
        """Return failed execution result"""
        return {
            'executed': False,
            'timestamp': datetime.now(),
            'reason': 'execution_failed'
        }
    
    def get_execution_stats(self) -> Dict:
        """
        Get execution statistics
        
        Returns:
            Dict with statistics
        """
        
        avg_slippage = (
            self.total_slippage / self.total_executions
            if self.total_executions > 0
            else 0.0
        )
        
        avg_commission = (
            self.total_commissions / self.total_executions
            if self.total_executions > 0
            else 0.0
        )
        
        stats = {
            'total_executions': self.total_executions,
            'total_commissions': self.total_commissions,
            'average_commission': avg_commission,
            'average_slippage': avg_slippage,
            'slippage_model': self.slippage_model,
            'optimizer_active': self.order_optimizer is not None
        }
        
        # Add optimizer stats if available
        if self.order_optimizer:
            optimizer_stats = self.order_optimizer.get_optimizer_stats()
            stats['optimizer_stats'] = optimizer_stats
        
        return stats
    
    def update_volume_tracking(self, volume_30d: float):
        """
        Update 30-day volume for fee tier adjustments
        
        Args:
            volume_30d: 30-day trading volume
        """
        
        if self.order_optimizer:
            self.order_optimizer.update_volume_30d(volume_30d)
            logger.info(f"Volume tracking updated: €{volume_30d:,.0f}")
