"""
Order Optimization Engine

Minimizes trading commissions and slippage across ALL strategies.
Implements intelligent order type selection (market vs limit), position sizing,
and batch execution strategies.

Author: Juan Carlos Garcia Arriero
Company: Santander Digital
Date: January 2026
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import time
import numpy as np

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order execution types"""
    MARKET = "market"  # Taker (0.10% on Binance)
    LIMIT = "limit"    # Maker (0.075% on Binance with rebate)
    ICEBERG = "iceberg"  # Large orders split into smaller chunks
    VWAP = "vwap"  # Volume-weighted average price execution
    TWAP = "twap"  # Time-weighted average price execution


class OrderOptimizationStrategy(Enum):
    """Strategies for minimizing commissions"""
    AGGRESSIVE_MARKET = "aggressive_market"  # Always market, prioritize fill
    PATIENT_MAKER = "patient_maker"  # Always limit orders (maker)
    HYBRID = "hybrid"  # Mix based on market conditions
    INTELLIGENT = "intelligent"  # ML-based decision (future)
    SIZE_AWARE = "size_aware"  # Split large orders


@dataclass
class OrderExecutionPlan:
    """
    Optimized execution plan for a trade signal
    """
    # Basic info
    symbol: str
    side: str  # BUY or SELL
    total_amount: float  # Total EUR/amount to execute
    
    # Execution method
    order_type: OrderType
    optimization_strategy: OrderOptimizationStrategy
    
    # Order details
    number_of_orders: int = 1
    orders: List[Dict] = None  # List of individual orders
    
    # Estimates
    estimated_commission_percent: float = 0.0
    estimated_total_commission: float = 0.0
    estimated_slippage_percent: float = 0.0
    estimated_total_cost: float = 0.0
    
    # Execution params
    time_limit_seconds: int = 300  # Max execution time
    max_slippage_tolerance: float = 0.005  # 0.5% max slippage
    
    # Metadata
    strategy_name: str = "unknown"
    confidence: float = 0.5
    priority: int = 1  # 1=low, 5=high
    
    def __post_init__(self):
        if self.orders is None:
            self.orders = []


class ExchangeCommissionConfig:
    """
    Exchange-specific commission configuration
    """
    def __init__(
        self,
        exchange_name: str,
        maker_fee: float,
        taker_fee: float,
        volume_tier_discounts: Optional[Dict] = None,
        flat_fee: Optional[float] = None,
        supports_bnb_discount: bool = False,
        bnb_discount_percent: float = 0.0,
        min_order_size: float = 10.0  # EUR
    ):
        """
        Args:
            exchange_name: Name of exchange (Binance, Coinbase, Kraken, Finst)
            maker_fee: Maker fee as decimal (0.001 = 0.1%)
            taker_fee: Taker fee as decimal
            volume_tier_discounts: Dict mapping volume to discount {50000: 0.0025, ...}
            flat_fee: Fixed fee regardless of type (used by Finst)
            supports_bnb_discount: Whether BNB discount is available
            bnb_discount_percent: BNB discount amount (0.25 = 25% off)
            min_order_size: Minimum order size in EUR
        """
        self.exchange_name = exchange_name
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.volume_tier_discounts = volume_tier_discounts or {}
        self.flat_fee = flat_fee
        self.supports_bnb_discount = supports_bnb_discount
        self.bnb_discount_percent = bnb_discount_percent
        self.min_order_size = min_order_size
    
    def get_effective_fee(
        self,
        order_type: OrderType,
        volume_30d: float = 0.0,
        has_bnb: bool = False
    ) -> float:
        """
        Calculate effective commission rate
        
        Args:
            order_type: Type of order (market/limit)
            volume_30d: 30-day trading volume
            has_bnb: Whether user has BNB balance for discount
            
        Returns:
            Effective fee as decimal
        """
        # If flat fee (like Finst), return it
        if self.flat_fee is not None:
            return self.flat_fee
        
        # Select base fee
        if order_type == OrderType.LIMIT:
            base_fee = self.maker_fee
        else:
            base_fee = self.taker_fee
        
        # Apply volume tiers
        for tier_volume, tier_fee in sorted(
            self.volume_tier_discounts.items(), reverse=True
        ):
            if volume_30d >= tier_volume:
                base_fee = tier_fee
                break
        
        # Apply BNB discount
        if has_bnb and self.supports_bnb_discount:
            base_fee *= (1 - self.bnb_discount_percent)
        
        return base_fee


class OrderOptimizer:
    """
    Main Order Optimization Engine
    
    Analyzes trade signals and creates optimized execution plans
    that minimize total cost (commissions + slippage).
    
    Applies to ALL strategies equally - exchange-agnostic logic.
    """
    
    def __init__(
        self,
        exchange_config: ExchangeCommissionConfig,
        optimization_strategy: OrderOptimizationStrategy = OrderOptimizationStrategy.HYBRID,
        volume_30d: float = 0.0,
        has_bnb: bool = False,
        max_execution_time: int = 300
    ):
        """
        Initialize Order Optimizer
        
        Args:
            exchange_config: Commission configuration
            optimization_strategy: Strategy to use for optimization
            volume_30d: 30-day trading volume for tier discounts
            has_bnb: Whether user has BNB for discount
            max_execution_time: Maximum time to execute orders (seconds)
        """
        self.exchange_config = exchange_config
        self.optimization_strategy = optimization_strategy
        self.volume_30d = volume_30d
        self.has_bnb = has_bnb
        self.max_execution_time = max_execution_time
        
        # Statistics
        self.total_commissions_saved = 0.0
        self.total_orders_optimized = 0
        
        logger.info(
            f"✓ Order Optimizer initialized for {exchange_config.exchange_name} "
            f"(strategy={optimization_strategy.value})"
        )
    
    def create_execution_plan(
        self,
        symbol: str,
        side: str,  # BUY or SELL
        amount: float,  # Total EUR to execute
        current_price: float,
        market_volatility: float = 0.02,
        market_spread: float = 0.0005,  # Bid-ask spread
        strategy_name: str = "unknown",
        confidence: float = 0.5,
        liquidity_rank: int = 1,  # 1=most liquid, 5=least
    ) -> OrderExecutionPlan:
        """
        Create optimized execution plan for a trade signal
        
        Applies to ALL strategies - returns best execution method.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            amount: Total EUR amount
            current_price: Current market price
            market_volatility: Annualized volatility (0.02 = 2%)
            market_spread: Current bid-ask spread
            strategy_name: Name of originating strategy
            confidence: Signal confidence (0-1)
            liquidity_rank: 1=most liquid, 5=least
            
        Returns:
            OrderExecutionPlan with optimized execution method
        """
        
        # Validate amount
        if amount < self.exchange_config.min_order_size:
            logger.warning(
                f"Order amount €{amount:.2f} below minimum €{self.exchange_config.min_order_size}"
            )
            return self._create_empty_plan()
        
        # Decide execution method based on strategy
        if self.optimization_strategy == OrderOptimizationStrategy.AGGRESSIVE_MARKET:
            plan = self._plan_aggressive_market(
                symbol, side, amount, current_price,
                market_volatility, strategy_name, confidence, liquidity_rank
            )
        
        elif self.optimization_strategy == OrderOptimizationStrategy.PATIENT_MAKER:
            plan = self._plan_patient_maker(
                symbol, side, amount, current_price,
                market_volatility, strategy_name, confidence, liquidity_rank
            )
        
        elif self.optimization_strategy == OrderOptimizationStrategy.HYBRID:
            plan = self._plan_hybrid(
                symbol, side, amount, current_price,
                market_volatility, market_spread, strategy_name, confidence, liquidity_rank
            )
        
        elif self.optimization_strategy == OrderOptimizationStrategy.SIZE_AWARE:
            plan = self._plan_size_aware(
                symbol, side, amount, current_price,
                market_volatility, strategy_name, confidence, liquidity_rank
            )
        
        else:
            plan = self._plan_hybrid(
                symbol, side, amount, current_price,
                market_volatility, market_spread, strategy_name, confidence, liquidity_rank
            )
        
        # Calculate commission savings
        worst_case_fee = self.exchange_config.taker_fee
        savings = (worst_case_fee - plan.estimated_commission_percent) * amount
        self.total_commissions_saved += max(0, savings)
        self.total_orders_optimized += 1
        
        logger.info(
            f"Execution plan: {symbol} {side} €{amount:.2f} | "
            f"Method: {plan.order_type.value} | "
            f"Est. fee: {plan.estimated_commission_percent:.4%} | "
            f"Savings vs taker: €{savings:.2f}"
        )
        
        return plan
    
    def _plan_aggressive_market(
        self,
        symbol: str,
        side: str,
        amount: float,
        current_price: float,
        market_volatility: float,
        strategy_name: str,
        confidence: float,
        liquidity_rank: int
    ) -> OrderExecutionPlan:
        """
        Aggressive market strategy: Always use market orders (taker)
        
        Best for: High confidence signals, need guaranteed fill, low slippage expected
        Commission: ~0.10% per side (Binance taker)
        """
        
        # Estimate slippage
        slippage = self._estimate_slippage(
            side, amount, current_price, market_volatility, liquidity_rank
        )
        
        # Get taker fee
        taker_fee = self.exchange_config.get_effective_fee(
            OrderType.MARKET, self.volume_30d, self.has_bnb
        )
        
        plan = OrderExecutionPlan(
            symbol=symbol,
            side=side,
            total_amount=amount,
            order_type=OrderType.MARKET,
            optimization_strategy=OrderOptimizationStrategy.AGGRESSIVE_MARKET,
            number_of_orders=1,
            estimated_commission_percent=taker_fee,
            estimated_total_commission=amount * taker_fee,
            estimated_slippage_percent=slippage,
            estimated_total_cost=amount * (1 + taker_fee + slippage),
            time_limit_seconds=10,  # Quick execution
            strategy_name=strategy_name,
            confidence=confidence,
            priority=5 if confidence > 0.7 else 3
        )
        
        # Create single market order
        plan.orders = [{
            'type': 'market',
            'size': amount,
            'price_limit': current_price * 1.02 if side == 'BUY' else current_price * 0.98
        }]
        
        return plan
    
    def _plan_patient_maker(
        self,
        symbol: str,
        side: str,
        amount: float,
        current_price: float,
        market_volatility: float,
        strategy_name: str,
        confidence: float,
        liquidity_rank: int
    ) -> OrderExecutionPlan:
        """
        Patient maker strategy: Always limit orders (maker)
        
        Best for: Low-urgency trades, willing to wait for fill, maximize rebates
        Commission: ~0.075% per side (Binance maker with rebate)
        Risk: May not fill if price moves against us
        """
        
        # Get maker fee (typically cheaper)
        maker_fee = self.exchange_config.get_effective_fee(
            OrderType.LIMIT, self.volume_30d, self.has_bnb
        )
        
        # Place limit just inside the spread to improve fill odds
        if side == 'BUY':
            limit_price = current_price * 1.001  # Bid at +0.1% (inside ask)
        else:
            limit_price = current_price * 0.999  # Ask at -0.1% (inside bid)
        
        plan = OrderExecutionPlan(
            symbol=symbol,
            side=side,
            total_amount=amount,
            order_type=OrderType.LIMIT,
            optimization_strategy=OrderOptimizationStrategy.PATIENT_MAKER,
            number_of_orders=1,
            estimated_commission_percent=maker_fee,
            estimated_total_commission=amount * maker_fee,
            estimated_slippage_percent=0.001,  # Minimal if fills at limit
            estimated_total_cost=amount * (1 + maker_fee),
            time_limit_seconds=300,  # 5 minutes to fill
            strategy_name=strategy_name,
            confidence=confidence,
            priority=1  # Lower priority, can wait
        )
        
        # Create single limit order
        plan.orders = [{
            'type': 'limit',
            'size': amount,
            'price': limit_price,
            'time_in_force': 'GTC'  # Good 'til canceled
        }]
        
        return plan
    
    def _plan_hybrid(
        self,
        symbol: str,
        side: str,
        amount: float,
        current_price: float,
        market_volatility: float,
        market_spread: float,
        strategy_name: str,
        confidence: float,
        liquidity_rank: int
    ) -> OrderExecutionPlan:
        """
        Hybrid strategy: Intelligently mix market and limit orders
        
        Decision logic:
        - High confidence + small size + good liquidity → Market (quick, low slippage)
        - Low confidence + large size + poor liquidity → Limit (patient, rebate)
        - Medium → Split execution (part market, part limit)
        
        Commission: Blend of 0.075% and 0.10% depending on mix
        """
        
        # Calculate decision factors
        size_factor = min(1.0, (amount / 5000.0))  # 0-1, 5000 EUR = threshold
        liquidity_factor = liquidity_rank / 5.0  # 0.2 (best) to 1.0 (worst)
        confidence_factor = confidence  # 0-1
        volatility_factor = min(1.0, market_volatility / 0.05)  # Normalize to 5%
        
        # Score: Higher = more likely to use market orders
        market_score = (
            0.4 * confidence_factor +  # High confidence → market
            0.2 * (1 - size_factor) +  # Small size → market
            0.2 * (1 - liquidity_factor) +  # Good liquidity → market
            0.2 * (1 - volatility_factor)  # Low volatility → market
        )
        
        # Decision threshold
        if market_score > 0.65:
            # Strong market signal
            return self._plan_aggressive_market(
                symbol, side, amount, current_price,
                market_volatility, strategy_name, confidence, liquidity_rank
            )
        
        elif market_score < 0.35:
            # Strong limit signal
            return self._plan_patient_maker(
                symbol, side, amount, current_price,
                market_volatility, strategy_name, confidence, liquidity_rank
            )
        
        else:
            # Middle ground: split 60% limit / 40% market
            return self._plan_split_execution(
                symbol, side, amount, current_price,
                market_volatility, strategy_name, confidence, liquidity_rank,
                market_ratio=0.40, limit_ratio=0.60
            )
    
    def _plan_size_aware(
        self,
        symbol: str,
        side: str,
        amount: float,
        current_price: float,
        market_volatility: float,
        strategy_name: str,
        confidence: float,
        liquidity_rank: int
    ) -> OrderExecutionPlan:
        """
        Size-aware strategy: Split large orders into multiple pieces
        
        This minimizes market impact and slippage for large trades.
        
        Rules:
        - EUR 0-1000: Single order (market or limit)
        - EUR 1000-5000: 2-3 orders with time delays
        - EUR 5000+: VWAP or TWAP algorithm
        """
        
        if amount <= 1000:
            # Small order: use hybrid logic
            return self._plan_hybrid(
                symbol, side, amount, current_price,
                market_volatility, 0.0005, strategy_name, confidence, liquidity_rank
            )
        
        elif amount <= 5000:
            # Medium order: split into 2-3 pieces
            num_orders = 3
            order_size = amount / num_orders
            
            maker_fee = self.exchange_config.get_effective_fee(
                OrderType.LIMIT, self.volume_30d, self.has_bnb
            )
            taker_fee = self.exchange_config.get_effective_fee(
                OrderType.MARKET, self.volume_30d, self.has_bnb
            )
            
            # Mix: 1 limit (patient), 2 market (for fill)
            avg_fee = (maker_fee + 2 * taker_fee) / 3
            
            plan = OrderExecutionPlan(
                symbol=symbol,
                side=side,
                total_amount=amount,
                order_type=OrderType.ICEBERG,
                optimization_strategy=OrderOptimizationStrategy.SIZE_AWARE,
                number_of_orders=num_orders,
                estimated_commission_percent=avg_fee,
                estimated_total_commission=amount * avg_fee,
                estimated_slippage_percent=0.003,  # Reduced due to split
                estimated_total_cost=amount * (1 + avg_fee + 0.003),
                time_limit_seconds=120,  # 2 minutes to complete all
                strategy_name=strategy_name,
                confidence=confidence,
                priority=3
            )
            
            # Create multiple orders
            plan.orders = [
                {
                    'type': 'limit',
                    'size': order_size,
                    'price': current_price * (1.001 if side == 'BUY' else 0.999),
                    'delay_seconds': 0
                },
                {
                    'type': 'market',
                    'size': order_size,
                    'delay_seconds': 30
                },
                {
                    'type': 'market',
                    'size': order_size,
                    'delay_seconds': 60
                }
            ]
            
            return plan
        
        else:
            # Large order: use VWAP
            num_orders = max(5, int(amount / 2000))  # ~2000 EUR per order
            order_size = amount / num_orders
            time_between = self.max_execution_time // num_orders
            
            maker_fee = self.exchange_config.get_effective_fee(
                OrderType.LIMIT, self.volume_30d, self.has_bnb
            )
            
            plan = OrderExecutionPlan(
                symbol=symbol,
                side=side,
                total_amount=amount,
                order_type=OrderType.VWAP,
                optimization_strategy=OrderOptimizationStrategy.SIZE_AWARE,
                number_of_orders=num_orders,
                estimated_commission_percent=maker_fee * 0.95,  # Slight discount for volume
                estimated_total_commission=amount * maker_fee * 0.95,
                estimated_slippage_percent=0.002,  # Minimal
                estimated_total_cost=amount * (1 + maker_fee * 0.95),
                time_limit_seconds=self.max_execution_time,
                strategy_name=strategy_name,
                confidence=confidence,
                priority=2
            )
            
            # Create VWAP orders
            plan.orders = [
                {
                    'type': 'limit',
                    'size': order_size,
                    'price': current_price,
                    'delay_seconds': i * time_between
                }
                for i in range(num_orders)
            ]
            
            return plan
    
    def _plan_split_execution(
        self,
        symbol: str,
        side: str,
        amount: float,
        current_price: float,
        market_volatility: float,
        strategy_name: str,
        confidence: float,
        liquidity_rank: int,
        market_ratio: float = 0.4,
        limit_ratio: float = 0.6
    ) -> OrderExecutionPlan:
        """
        Split execution: Combine market and limit orders
        
        Balances between speed (market) and cost (limit)
        """
        
        market_size = amount * market_ratio
        limit_size = amount * limit_ratio
        
        market_fee = self.exchange_config.get_effective_fee(
            OrderType.MARKET, self.volume_30d, self.has_bnb
        )
        maker_fee = self.exchange_config.get_effective_fee(
            OrderType.LIMIT, self.volume_30d, self.has_bnb
        )
        
        # Weighted average fee
        avg_fee = (market_size * market_fee + limit_size * maker_fee) / amount
        
        plan = OrderExecutionPlan(
            symbol=symbol,
            side=side,
            total_amount=amount,
            order_type=OrderType.ICEBERG,
            optimization_strategy=OrderOptimizationStrategy.HYBRID,
            number_of_orders=2,
            estimated_commission_percent=avg_fee,
            estimated_total_commission=amount * avg_fee,
            estimated_slippage_percent=0.002,
            estimated_total_cost=amount * (1 + avg_fee + 0.002),
            time_limit_seconds=60,
            strategy_name=strategy_name,
            confidence=confidence,
            priority=3
        )
        
        # Create split orders
        plan.orders = [
            {
                'type': 'limit',
                'size': limit_size,
                'price': current_price * (1.001 if side == 'BUY' else 0.999),
                'delay_seconds': 0
            },
            {
                'type': 'market',
                'size': market_size,
                'delay_seconds': 20
            }
        ]
        
        return plan
    
    def _estimate_slippage(
        self,
        side: str,
        amount: float,
        current_price: float,
        market_volatility: float,
        liquidity_rank: int
    ) -> float:
        """
        Estimate slippage for market orders
        
        Args:
            side: BUY or SELL
            amount: Order size in EUR
            current_price: Current market price
            market_volatility: Annualized volatility
            liquidity_rank: 1=best, 5=worst
            
        Returns:
            Estimated slippage as decimal
        """
        
        # Base slippage from bid-ask spread
        base_slippage = 0.0005  # 0.05% typical spread
        
        # Market impact: larger orders have more slippage
        # Order value factor (0-1)
        amount_factor = min(1.0, amount / 10000.0)  # 10k EUR = max impact
        market_impact = amount_factor * 0.002  # Up to 0.2%
        
        # Liquidity factor: worse liquidity = more slippage
        liquidity_impact = (liquidity_rank / 5.0) * 0.001  # Up to 0.1%
        
        # Volatility factor: higher vol = more slippage
        volatility_impact = market_volatility * 0.5  # Scale by 50%
        
        total_slippage = base_slippage + market_impact + liquidity_impact + volatility_impact
        
        return total_slippage
    
    def _create_empty_plan(self) -> OrderExecutionPlan:
        """Create empty/failed plan"""
        return OrderExecutionPlan(
            symbol="UNKNOWN",
            side="NONE",
            total_amount=0.0,
            order_type=OrderType.MARKET,
            optimization_strategy=OrderOptimizationStrategy.HYBRID,
            estimated_commission_percent=0.0,
            estimated_total_commission=0.0
        )
    
    def update_volume_30d(self, new_volume: float):
        """Update 30-day trading volume (affects fee tiers)"""
        self.volume_30d = new_volume
        logger.info(f"Updated 30-day volume to €{new_volume:,.2f}")
    
    def toggle_bnb(self, has_bnb: bool):
        """Toggle BNB discount eligibility"""
        self.has_bnb = has_bnb
        logger.info(f"BNB discount {'enabled' if has_bnb else 'disabled'}")
    
    def get_optimizer_stats(self) -> Dict:
        """Get optimizer statistics"""
        return {
            'total_commissions_saved': self.total_commissions_saved,
            'total_orders_optimized': self.total_orders_optimized,
            'avg_savings_per_order': (
                self.total_commissions_saved / self.total_orders_optimized
                if self.total_orders_optimized > 0
                else 0.0
            ),
            'optimization_strategy': self.optimization_strategy.value,
            'exchange': self.exchange_config.exchange_name
        }
    
    def __repr__(self) -> str:
        return (
            f"OrderOptimizer("
            f"exchange={self.exchange_config.exchange_name}, "
            f"strategy={self.optimization_strategy.value}, "
            f"volume_30d={self.volume_30d:,.2f}€"
            f")"
        )
