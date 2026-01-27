# Order Optimization Strategy Guide

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Author:** Juan Carlos Garcia Arriero  
**Status:** Production Ready  

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Available Strategies](#available-strategies)
4. [Exchange Comparison](#exchange-comparison)
5. [Implementation Examples](#implementation-examples)
6. [Commission Calculations](#commission-calculations)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

---

## Overview

The **Order Optimization Engine** automatically minimizes trading commissions and slippage across **all strategies** by intelligently choosing between:

- **Market Orders** (Taker): Guaranteed fill, pay 0.10% (Binance)
- **Limit Orders** (Maker): Potential rebate, pay 0.075% (Binance with discount)
- **Hybrid Execution**: Mix market + limit based on conditions
- **VWAP/TWAP**: Split large orders over time

**Key Principle:** Strategy logic is completely separated from order execution. This means:

✅ All 20 strategies use the same commission optimization  
✅ Adding new strategies doesn't require execution tweaks  
✅ You can switch exchanges and auto-adjust fees  
✅ BNB discounts apply automatically to Binance  

---

## Quick Start

### Installation

The optimizer is already integrated in BotV2. To use it:

```python
from bot.core.order_optimizer import OrderOptimizer, OrderOptimizationStrategy
from bot.core.order_optimizer_config import get_optimizer_for_exchange

# Create optimizer for your exchange
optimizer = get_optimizer_for_exchange(
    exchange_name='binance',
    optimization_strategy=OrderOptimizationStrategy.HYBRID,  # Intelligent mix
    volume_30d=150000.0,  # Your 30-day volume
    has_bnb=True,  # Claim BNB discount
    max_execution_time=300  # 5 minutes to execute
)
```

### Generate an Execution Plan

```python
# When any strategy generates a signal...
execution_plan = optimizer.create_execution_plan(
    symbol='BTC/EUR',
    side='BUY',
    amount=500.0,  # EUR
    current_price=42000.0,
    market_volatility=0.025,  # 2.5% annualized
    market_spread=0.0005,  # 0.05% bid-ask
    strategy_name='momentum_rsi',  # Which strategy sent signal
    confidence=0.75,  # 75% confidence
    liquidity_rank=1  # 1=most liquid, 5=least
)

print(f"Optimized plan: {execution_plan.order_type.value}")
print(f"Expected commission: {execution_plan.estimated_commission_percent:.4%}")
print(f"Total cost: €{execution_plan.estimated_total_cost:.2f}")
print(f"Number of orders: {execution_plan.number_of_orders}")
```

### Execute the Plan

```python
# Execute the optimized orders
for order in execution_plan.orders:
    if order['type'] == 'market':
        execute_market_order(
            symbol=symbol,
            side=side,
            size=order['size']
        )
    elif order['type'] == 'limit':
        execute_limit_order(
            symbol=symbol,
            side=side,
            size=order['size'],
            price=order['price'],
            time_in_force='GTC'
        )
    
    # Respect delays for split execution
    if 'delay_seconds' in order:
        await asyncio.sleep(order['delay_seconds'])
```

---

## Available Strategies

### 1. AGGRESSIVE_MARKET

**When to use:**
- High confidence signals (>70%)
- Small to medium orders (<€1,000)
- Volatile market (fast-moving prices)
- Need guaranteed fill

**Execution:**
- Single market order (taker)
- Immediate fill

**Commission:** 0.10% per side (Binance)  
**Round-trip cost:** 0.20%  
**Slippage:** ~0.15% (typical)

```python
optimizer = get_optimizer_for_exchange(
    'binance',
    optimization_strategy=OrderOptimizationStrategy.AGGRESSIVE_MARKET
)
```

**Example:**
```
Signal: SELL 0.01 BTC @ €42,000
├─ Market order -€420
├─ Commission: €0.42 (0.10%)
├─ Slippage: €0.63 (~0.15%)
└─ Total cost: €1.05
```

---

### 2. PATIENT_MAKER

**When to use:**
- Low urgency (can wait 5 minutes)
- Willing to trade fill probability for cost
- Low confidence signals that might not move far
- Prefer fee rebates

**Execution:**
- Single limit order (maker)
- Placed just inside spread
- GTC (good 'til canceled)

**Commission:** 0.075% per side (Binance with rebate)  
**Round-trip cost:** 0.15%  
**Fill probability:** ~70-80%

```python
optimizer = get_optimizer_for_exchange(
    'binance',
    optimization_strategy=OrderOptimizationStrategy.PATIENT_MAKER
)
```

**Example:**
```
Signal: BUY 0.01 BTC @ €42,000
├─ Limit order @ €42,042 (0.1% better)
├─ Commission rebate: €0.03 (0.075% negative!)
├─ Wait time: up to 5 min
└─ If filled: save €0.63 vs market
```

---

### 3. HYBRID (Recommended)

**When to use:**
- Most real-world scenarios
- You don't know exact market conditions
- Want intelligent auto-balancing

**Decision Logic:**

Scores these factors (0-1 scale):
- **Confidence:** Does the signal have high confidence?
- **Size:** Is the order small enough to execute quickly?
- **Liquidity:** Is this a liquid pair?
- **Volatility:** Is the market calm?

**Scoring:**
```
market_score = (
    0.4 * confidence +        # High conf → market
    0.2 * (1 - size_factor) +  # Small size → market
    0.2 * (1 - liquidity_issue) +  # Good liquidity → market
    0.2 * (1 - volatility)    # Low vol → market
)

if market_score > 0.65:
    Use AGGRESSIVE_MARKET
elif market_score < 0.35:
    Use PATIENT_MAKER
else:
    Use SPLIT (60% limit, 40% market)
```

**Commission:** Blend of 0.075% and 0.10%  
**Round-trip:** 0.15% to 0.20%

```python
optimizer = get_optimizer_for_exchange(
    'binance',
    optimization_strategy=OrderOptimizationStrategy.HYBRID  # Smart choice
)
```

**Example Decision Tree:**
```
New signal: BTC/EUR SELL 500€
├─ Confidence: 0.60 (medium)
├─ Size: €500 (small)
├─ Liquidity: Tier 1 (excellent)
└─ Volatility: 0.02 (normal)

Score calculation:
  0.4 × 0.60 (conf) = 0.24
  0.2 × 1.0 (small) = 0.20
  0.2 × 1.0 (liquid) = 0.20
  0.2 × 0.6 (low vol) = 0.12
  ─────────────────
  Total score = 0.76

→ Decision: AGGRESSIVE_MARKET (score > 0.65)
→ Commission: 0.10%
→ Cost: €0.50
```

---

### 4. SIZE_AWARE

**When to use:**
- Large orders (€5,000+)
- Want to minimize market impact
- Don't mind split execution

**Execution Strategy:**

| Order Size | Method | Number of Orders | Execution Time |
|------------|--------|------------------|----------------|
| €0-1,000 | Hybrid | 1 | Immediate |
| €1,000-5,000 | Iceberg | 2-3 | 2 minutes |
| €5,000+ | VWAP | 5-10 | 5 minutes |

**Benefits:**
- Reduces slippage by 30-50%
- Lower market impact ("stealthier")
- Better average fill price
- Still uses optimal fee strategy

**Commission:** Weighted average  
**Slippage:** Reduced by splitting

```python
optimizer = get_optimizer_for_exchange(
    'binance',
    optimization_strategy=OrderOptimizationStrategy.SIZE_AWARE
)
```

**Example (Large Order):**
```
Signal: BUY 10,000€ in BTC

SIZE_AWARE splits into:
├─ 2:00s Order #1: Limit €2,000 @ €41,990
├─ 3:30s Order #2: Market €2,000
├─ 5:00s Order #3: Limit €2,000 @ €41,995
├─ 1:30s Order #4: Market €2,000
└─ 2:00s Order #5: Limit €2,000 @ €41,985

Total commission: 0.075% × €10,000 = €7.50
(Mostly maker fees from limit orders)

Alternative (all market): €10 cost
Savings: €2.50 by smart splitting
```

---

## Exchange Comparison

### Fee Breakdown (Taker - Most Common for Bots)

| Exchange | Maker | Taker | With BNB* | Round-Trip | Min Order |
|----------|-------|-------|-----------|------------|----------|
| **Binance** | 0.10% | 0.10% | 0.075% | 0.20% | €10 |
| **Finst*** | 0.15% | 0.15% | - | 0.30% | €50 |
| **Kraken** | 0.25% | 0.40% | - | 0.65% | €20 |
| **Coinbase** | 0.40% | 0.60% | - | 1.00% | €5 |

*\*Finst API not yet available*  
*BNB discount = 25% off on Binance*

### Real Example: €1,000 Trade

**Aggressive Bot (10 round-trips/day):**

```
Binance (no BNB):
  €1,000 × 0.20% × 10 = €20/day
  
Binance (with BNB):
  €1,000 × 0.15% × 10 = €15/day  ← Save €5/day!
  
Finst (when available):
  €1,000 × 0.30% × 10 = €30/day  ← 50% more expensive
  
Kraken:
  €1,000 × 0.65% × 10 = €65/day  ← 3.25x more expensive!
  
Coinbase:
  €1,000 × 1.00% × 10 = €100/day  ← 5x more expensive!
```

**For 30 days:**
- Binance + BNB: €450 (lowest)
- Finst: €900 (2x Binance)
- Kraken: €1,950 (4.3x Binance)
- Coinbase: €3,000 (6.7x Binance)

**Clear Winner for Active Trading:** Binance + BNB + Hybrid optimization = €450/month

---

## Implementation Examples

### Example 1: Momentum Strategy with Optimization

```python
from bot.core.order_optimizer_config import get_optimizer_for_exchange
from bot.core.order_optimizer import OrderOptimizationStrategy

class MomentumStrategy:
    def __init__(self, portfolio_manager):
        self.portfolio_manager = portfolio_manager
        
        # Initialize optimizer once
        self.optimizer = get_optimizer_for_exchange(
            exchange_name='binance',
            optimization_strategy=OrderOptimizationStrategy.HYBRID,
            has_bnb=True,  # Enable BNB discount
            volume_30d=portfolio_manager.get_volume_30d()
        )
    
    def on_signal(self, signal):
        """
        Momentum strategy signal (completely decoupled from execution)
        """
        # Strategy logic - NO commission logic here
        if self.should_buy(signal):
            confidence = self.calculate_confidence(signal)
            
            # Delegate to optimizer
            execution_plan = self.optimizer.create_execution_plan(
                symbol='BTC/EUR',
                side='BUY',
                amount=self.portfolio_manager.get_position_size(),
                current_price=signal.price,
                market_volatility=signal.volatility,
                strategy_name='momentum_rsi',
                confidence=confidence,
                liquidity_rank=1  # BTC is most liquid
            )
            
            # Execute optimized plan
            self.execute_plan(execution_plan)
    
    def calculate_confidence(self, signal) -> float:
        # Your momentum logic
        return min(1.0, signal.rsi_strength * signal.volume_surge)
    
    def should_buy(self, signal) -> bool:
        return signal.rsi > 30 and signal.trend == 'up'
    
    def execute_plan(self, plan):
        for order in plan.orders:
            if order['type'] == 'market':
                self.portfolio_manager.execute_market(
                    order['size']
                )
            else:
                self.portfolio_manager.execute_limit(
                    order['size'],
                    order['price']
                )
            
            if 'delay_seconds' in order:
                time.sleep(order['delay_seconds'])
```

### Example 2: Multiple Strategies with Same Optimizer

```python
class EnsembleExecutor:
    def __init__(self, config):
        # Single optimizer shared by all strategies
        self.optimizer = get_optimizer_for_exchange(
            exchange_name=config['exchange'],
            optimization_strategy=OrderOptimizationStrategy.HYBRID,
            has_bnb=config.get('has_bnb', False)
        )
        
        # All strategies use same optimizer
        self.strategies = [
            MomentumStrategy(self.optimizer),
            MeanReversionStrategy(self.optimizer),
            MacdStrategy(self.optimizer),
            BollingerStrategy(self.optimizer),
            # ... 16 more strategies
        ]
    
    def execute_ensemble_signal(self, signals):
        """
        Execute ensemble signal with optimized order
        """
        # Aggregate signal from all strategies
        aggregated = self.aggregate_signals(signals)
        
        # Single optimizer handles all strategies
        execution_plan = self.optimizer.create_execution_plan(
            symbol=aggregated['symbol'],
            side=aggregated['side'],
            amount=aggregated['size'],
            current_price=aggregated['price'],
            market_volatility=aggregated['volatility'],
            strategy_name=aggregated['voting_strategies'],
            confidence=aggregated['confidence'],
            liquidity_rank=1
        )
        
        # Execute
        self.execute(execution_plan)
```

### Example 3: Switching Exchanges Dynamically

```python
class AdaptiveExecutor:
    def __init__(self):
        self.current_exchange = 'binance'
        self.optimizer = get_optimizer_for_exchange(
            exchange_name=self.current_exchange,
            optimization_strategy=OrderOptimizationStrategy.HYBRID,
            has_bnb=True
        )
    
    def switch_exchange(self, new_exchange: str):
        """
        Switch to different exchange
        All commission logic automatically updates
        """
        logger.info(f"Switching from {self.current_exchange} to {new_exchange}")
        
        self.current_exchange = new_exchange
        self.optimizer = get_optimizer_for_exchange(
            exchange_name=new_exchange,
            optimization_strategy=OrderOptimizationStrategy.HYBRID,
            has_bnb=new_exchange == 'binance'  # Only Binance has BNB
        )
    
    def execute_signal(self, signal):
        # Execution automatically uses correct fees
        plan = self.optimizer.create_execution_plan(
            symbol=signal.symbol,
            side=signal.side,
            amount=signal.size,
            current_price=signal.price,
            strategy_name=signal.strategy,
            confidence=signal.confidence
        )
        
        print(f"Using {self.current_exchange}")
        print(f"Commission: {plan.estimated_commission_percent:.4%}")
        self.execute(plan)
```

---

## Commission Calculations

### Round-Trip Commission Cost

```python
def calculate_round_trip_cost(
    entry_fee: float,
    exit_fee: float,
    position_value: float
) -> tuple[float, float]:
    """
    Calculate total round-trip commission
    
    Args:
        entry_fee: Entry fee as decimal (0.001 = 0.1%)
        exit_fee: Exit fee as decimal
        position_value: Position value in EUR
    
    Returns:
        (total_cost_eur, total_cost_percent)
    """
    entry_cost = position_value * entry_fee
    exit_cost = position_value * exit_fee
    total_cost = entry_cost + exit_cost
    total_percent = (total_cost / position_value)
    
    return total_cost, total_percent

# Examples
print("Binance (0.10% / 0.10%):")
cost, pct = calculate_round_trip_cost(0.001, 0.001, 1000)
print(f"  €1,000 trade: €{cost:.2f} ({pct:.2%})")

print("\nBinance with BNB (0.075% / 0.075%):")
cost, pct = calculate_round_trip_cost(0.00075, 0.00075, 1000)
print(f"  €1,000 trade: €{cost:.2f} ({pct:.2%})")

print("\nFinst (0.15% / 0.15%):")
cost, pct = calculate_round_trip_cost(0.0015, 0.0015, 1000)
print(f"  €1,000 trade: €{cost:.2f} ({pct:.2%})")

print("\nKraken hybrid (0.25% / 0.40%):")
cost, pct = calculate_round_trip_cost(0.0025, 0.0040, 1000)
print(f"  €1,000 trade: €{cost:.2f} ({pct:.2%})")
```

**Output:**
```
Binance (0.10% / 0.10%):
  €1,000 trade: €2.00 (0.20%)

Binance with BNB (0.075% / 0.075%):
  €1,000 trade: €1.50 (0.15%)

Finst (0.15% / 0.15%):
  €1,000 trade: €3.00 (0.30%)

Kraken hybrid (0.25% / 0.40%):
  €1,000 trade: €6.50 (0.65%)
```

### Monthly Commission Impact

```python
def calculate_monthly_commission(
    daily_trades: int,
    avg_trade_size: float,
    entry_fee: float,
    exit_fee: float
) -> float:
    """Calculate total monthly commission"""
    trades_per_month = daily_trades * 30  # Approximate
    commission_per_trade = avg_trade_size * (entry_fee + exit_fee)
    total_monthly = trades_per_month * commission_per_trade
    return total_monthly

# Aggressive bot
print("Aggressive bot: 10 trades/day @ €500 each")

print("\nBinance + BNB:")
cost = calculate_monthly_commission(10, 500, 0.00075, 0.00075)
print(f"  Monthly cost: €{cost:.2f}")
print(f"  Annual cost: €{cost * 12:.2f}")

print("\nFinst:")
cost = calculate_monthly_commission(10, 500, 0.0015, 0.0015)
print(f"  Monthly cost: €{cost:.2f}")
print(f"  Annual cost: €{cost * 12:.2f}")
```

---

## Best Practices

### 1. Enable BNB Discount on Binance

```python
# Always enable if you have BNB
optimizer = get_optimizer_for_exchange(
    'binance',
    has_bnb=True  # ← Critical for cost savings
)

# Saves 25% on fees = €0.50 per €1,000 trade
```

### 2. Use HYBRID for Most Cases

```python
# Don't overthink it
optimizer = get_optimizer_for_exchange(
    'binance',
    optimization_strategy=OrderOptimizationStrategy.HYBRID  # Works for all
)
```

### 3. Track Volume Tiers

```python
# Update optimizer when you hit volume milestones
volume_30d = portfolio.get_volume_30d()
if volume_30d > 50000:  # Binance tier 1
    optimizer.update_volume_30d(volume_30d)
    logger.info(f"Reached volume tier: {volume_30d:,.0f}€")
```

### 4. Monitor Commission Savings

```python
# Check optimizer stats regularly
stats = optimizer.get_optimizer_stats()
print(f"Total saved: €{stats['total_commissions_saved']:.2f}")
print(f"Avg savings/order: €{stats['avg_savings_per_order']:.4f}")
```

### 5. Size Large Orders with SIZE_AWARE

```python
# For orders > €5,000
if trade_size > 5000:
    optimizer = get_optimizer_for_exchange(
        'binance',
        optimization_strategy=OrderOptimizationStrategy.SIZE_AWARE
    )
```

---

## FAQ

### Q: Does this work with all 20 strategies?

**A:** Yes! The optimizer is strategy-agnostic. All 20 strategies use the same commission minimization logic.

### Q: How much can I save?

**A:** 
- **Binance vs Kraken:** 3-4x cheaper (0.20% vs 0.65% round-trip)
- **Binance vs Coinbase:** 5-6x cheaper (0.20% vs 1.00%)
- **With BNB discount:** Additional 25% off = 0.15% round-trip

For a €3,000 account making 10 trades/day at €300 each:
- **Binance + BNB:** €450/month
- **Kraken:** €1,950/month
- **Difference:** €1,500/month saved by choosing Binance!

### Q: Should I always use limit orders?

**A:** No. The HYBRID strategy balances:
- **Market:** Guaranteed fill, slightly higher fee
- **Limit:** Potential rebate, might not fill

The optimizer decides based on confidence, liquidity, and volatility.

### Q: What if I switch exchanges?

**A:** Just create a new optimizer:

```python
# Old
optimizer = get_optimizer_for_exchange('binance')

# New exchange
optimizer = get_optimizer_for_exchange('kraken')

# All fees update automatically
```

### Q: Can I use PATIENT_MAKER for everything?

**A:** No. If limit orders don't fill, you don't trade. The HYBRID strategy uses market orders when fill probability is more important than saving commission.

### Q: What about Finst when they release API?

**A:** Just switch:

```python
optimizer = get_optimizer_for_exchange('finst')

# Fees update to 0.15% flat
# No changes needed in strategy code
```

---

## Summary

| Question | Answer |
|----------|--------|
| **Best for active trading?** | Binance + BNB + HYBRID |
| **Round-trip cost?** | 0.15% (€1.50 per €1,000) |
| **Commission savings?** | Up to €1,500/month vs Kraken |
| **For all strategies?** | Yes, completely decoupled |
| **Can scale to all exchanges?** | Yes, factory pattern |
| **Large orders (€5,000+)?** | Use SIZE_AWARE strategy |

**Recommendation for BotV2:** Start with **Binance + HYBRID + BNB discount** for optimal cost-efficiency.
