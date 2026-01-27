"""
Order Optimizer Configuration Factory

Pre-configured commission settings for all supported exchanges.
Simplifies setup and ensures consistency.

Author: Juan Carlos Garcia Arriero
Date: January 2026
"""

from bot.core.order_optimizer import (
    ExchangeCommissionConfig,
    OrderOptimizationStrategy
)


class ExchangeConfigs:
    """
    Pre-configured exchange commission settings
    """
    
    @staticmethod
    def BINANCE() -> ExchangeCommissionConfig:
        """
        Binance configuration
        - Lowest fees among major exchanges
        - Maker: 0.10% → 0.075% with BNB (25% discount)
        - Taker: 0.10% → 0.075% with BNB
        - Volume tiers available
        - Min order: 10 EUR
        """
        return ExchangeCommissionConfig(
            exchange_name="Binance",
            maker_fee=0.001,  # 0.10%
            taker_fee=0.001,  # 0.10%
            volume_tier_discounts={
                50000: 0.0009,    # 0.09%
                250000: 0.0008,   # 0.08%
                1000000: 0.0007,  # 0.07%
                5000000: 0.0005,  # 0.05%
            },
            supports_bnb_discount=True,
            bnb_discount_percent=0.25,  # 25% off
            min_order_size=10.0
        )
    
    @staticmethod
    def COINBASE_ADVANCED() -> ExchangeCommissionConfig:
        """
        Coinbase Advanced Trade configuration
        - Higher fees than Binance
        - Maker: 0.40% - 0.50%
        - Taker: 0.60% - 0.80%
        - Volume tiers for larger traders
        - Min order: 5 EUR
        """
        return ExchangeCommissionConfig(
            exchange_name="Coinbase Advanced",
            maker_fee=0.004,  # 0.40%
            taker_fee=0.006,  # 0.60%
            volume_tier_discounts={
                1000000: 0.0035,  # 0.35% maker
                5000000: 0.0030,  # 0.30% maker
                10000000: 0.0025,  # 0.25% maker
            },
            supports_bnb_discount=False,
            min_order_size=5.0
        )
    
    @staticmethod
    def KRAKEN() -> ExchangeCommissionConfig:
        """
        Kraken configuration
        - Mid-tier fees
        - Maker: 0.25% - 0.16%
        - Taker: 0.40% - 0.26%
        - Volume tiers available
        - Good for EUR pairs
        - Min order: 20 EUR
        """
        return ExchangeCommissionConfig(
            exchange_name="Kraken",
            maker_fee=0.0025,  # 0.25%
            taker_fee=0.0040,  # 0.40%
            volume_tier_discounts={
                50000: 0.0020,    # 0.20% maker
                100000: 0.0017,   # 0.17% maker
                500000: 0.0016,   # 0.16% maker
                1000000: 0.0014,  # 0.14% maker
            },
            supports_bnb_discount=False,
            min_order_size=20.0
        )
    
    @staticmethod
    def FINST() -> ExchangeCommissionConfig:
        """
        Finst configuration (PREPARATORY - API not yet available)
        - European exchange (Netherlands)
        - Flat fee: 0.15% (no maker/taker distinction)
        - 340+ trading pairs
        - Focus on low fees and security
        - Min order: 50 EUR (estimated)
        
        Note: When Finst API becomes available, update this configuration.
        """
        return ExchangeCommissionConfig(
            exchange_name="Finst",
            maker_fee=0.0015,  # 0.15% (ignored, using flat_fee)
            taker_fee=0.0015,  # 0.15% (ignored, using flat_fee)
            flat_fee=0.0015,   # 0.15% flat on all trades
            supports_bnb_discount=False,
            min_order_size=50.0
        )


def get_optimizer_for_exchange(
    exchange_name: str,
    optimization_strategy: OrderOptimizationStrategy = OrderOptimizationStrategy.HYBRID,
    volume_30d: float = 0.0,
    has_bnb: bool = False,
    max_execution_time: int = 300
):
    """
    Factory function to create optimized OrderOptimizer for an exchange
    
    Args:
        exchange_name: 'binance', 'coinbase', 'kraken', 'finst'
        optimization_strategy: Strategy to use
        volume_30d: 30-day trading volume
        has_bnb: Whether BNB discount should be applied
        max_execution_time: Max time for order execution
        
    Returns:
        Configured OrderOptimizer instance
    """
    from src.core.order_optimizer import OrderOptimizer
    
    exchange_name = exchange_name.lower()
    
    if exchange_name == 'binance':
        config = ExchangeConfigs.BINANCE()
    elif exchange_name == 'coinbase':
        config = ExchangeConfigs.COINBASE_ADVANCED()
    elif exchange_name == 'kraken':
        config = ExchangeConfigs.KRAKEN()
    elif exchange_name == 'finst':
        config = ExchangeConfigs.FINST()
    else:
        raise ValueError(f"Unknown exchange: {exchange_name}")
    
    return OrderOptimizer(
        exchange_config=config,
        optimization_strategy=optimization_strategy,
        volume_30d=volume_30d,
        has_bnb=has_bnb,
        max_execution_time=max_execution_time
    )
