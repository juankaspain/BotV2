#!/usr/bin/env python3
"""
BotV2 - Main Trading System
Complete Production System with 26 Audit Improvements + Phase 1 Enhancements
"""

import asyncio
import logging
import sys
import signal
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# ===== CRITICAL: VALIDATE SECRETS BEFORE ANY OTHER IMPORTS =====
# This ensures the application fails fast if required configuration is missing
from bot.config.secrets_validator import validate_secrets, HAS_PROFESSIONAL_LOGGER

# Get environment from env var or default to development
CURRENT_ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Validate all required secrets (will exit if validation fails)
# Only do this ONCE at module initialization
_SECRETS_VALIDATED = False

def _validate_secrets_once():
    """Validate secrets only once to avoid duplicate logs"""
    global _SECRETS_VALIDATED
    
    if _SECRETS_VALIDATED:
        return
    
    validate_secrets(environment=CURRENT_ENVIRONMENT, strict=True)
    _SECRETS_VALIDATED = True

# Call validation immediately
_validate_secrets_once()

# ===== NOW SAFE TO IMPORT OTHER COMPONENTS =====
from bot.config.config_manager import ConfigManager
from bot.core.risk_manager import RiskManager, CircuitBreaker
from bot.core.state_manager import StateManager
from bot.core.liquidation_detector import LiquidationDetector
from bot.core.execution_engine import ExecutionEngine
from bot.data.data_validator import DataValidator
from bot.data.normalization_pipeline import NormalizationPipeline
from bot.data.exchange_connector import ExchangeConnector
from bot.ensemble.adaptive_allocation import AdaptiveAllocationEngine
from bot.ensemble.correlation_manager import CorrelationManager
from bot.ensemble.ensemble_voting import EnsembleVoting
from bot.strategies.base_strategy import load_all_strategies
from bot.backtesting.realistic_simulator import RealisticSimulator
from bot.utils.secrets_manager import get_secrets_manager
from bot.utils.sensitive_formatter import setup_sanitized_logger

# Setup sanitized logging
logger = setup_sanitized_logger(__name__)


class BotV2:
    """
    BotV2 Main Trading System
    
    Implements all 26 audit improvements + Phase 1 critical fixes:
    - Round 1: Data validation, Risk management, State recovery
    - Round 2: Adaptive allocation, Correlation management, Ensemble voting
    - Round 3: Realistic execution, Liquidation detection, Market microstructure
    - Phase 1: Exchange integration, Secrets management, Sanitized logging
    - Security: Secrets validation, Fail-fast on missing config
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize BotV2 trading system"""
        
        logger.info("=" * 70)
        logger.info("🚀 Initializing BotV2 Trading System...")
        logger.info(f"Environment: {CURRENT_ENVIRONMENT}")
        logger.info("=" * 70)
        
        # Get secrets manager for verification (no duplicate validation)
        secrets_manager = get_secrets_manager()
        validation_summary = secrets_manager.get_validation_summary()
        logger.info(f"✓ Secrets validated: {validation_summary.get('total_validated', 0)} variables")
        
        # Load configuration
        self.config = ConfigManager(config_path)
        logger.info(f"✓ Config loaded: {self.config.system['name']} v{self.config.system['version']}")
        
        # Log trading mode
        trading_mode = os.getenv('TRADING_MODE', 'paper')
        if trading_mode == 'live':
            logger.warning("⚠️ LIVE TRADING MODE - Real funds at risk!")
        else:
            logger.info(f"✓ Trading mode: {trading_mode.upper()}")
        
        # Initialize components
        self._init_components()
        
        # State
        self.is_running = False
        self.iteration = 0
        self.start_time = None
        self.shutdown_requested = False
        
        # Performance tracking
        self.portfolio = {
            'cash': self.config.trading.initial_capital,
            'positions': {},
            'equity': self.config.trading.initial_capital
        }
        self.trade_history = []
        self.performance_metrics = {}
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        logger.info("✅ BotV2 initialization complete")
        logger.info(f"Initial capital: €{self.config.trading.initial_capital:,.2f}")
        logger.info("=" * 70)
    
    def _init_components(self):
        """Initialize all system components"""
        
        # Round 1: Foundation (Data & Risk)
        logger.info("Initializing Round 1: Foundation components...")
        self.data_validator = DataValidator(
            outlier_threshold=self.config.get('data.validation.outlier_std_threshold', 5)
        )
        self.normalizer = NormalizationPipeline(
            lookback=self.config.get('data.normalization.lookback_period', 252)
        )
        self.risk_manager = RiskManager(self.config)
        self.state_manager = StateManager(self.config)
        self.circuit_breaker = CircuitBreaker(
            level_1=self.config.risk.circuit_breaker['level_1_drawdown'],
            level_2=self.config.risk.circuit_breaker['level_2_drawdown'],
            level_3=self.config.risk.circuit_breaker['level_3_drawdown']
        )
        
        # Round 2: Intelligence (Ensemble)
        logger.info("Initializing Round 2: Intelligence components...")
        self.allocation_engine = AdaptiveAllocationEngine(
            rebalance_freq=self.config.get('ensemble.adaptive_allocation.rebalance_frequency', 'daily'),
            smoothing_alpha=self.config.get('ensemble.adaptive_allocation.smoothing_alpha', 0.7)
        )
        self.correlation_manager = CorrelationManager(
            threshold=self.config.risk.correlation_threshold,
            method=self.config.get('ensemble.correlation_management.method', 'pearson')
        )
        self.ensemble_voting = EnsembleVoting(
            method=self.config.get('ensemble.voting_method', 'weighted_average'),
            confidence_threshold=self.config.get('ensemble.confidence_threshold', 0.5)
        )
        
        # Round 3: Execution (Realistic)
        logger.info("Initializing Round 3: Execution components...")
        self.liquidation_detector = LiquidationDetector(
            cascade_threshold=self.config.get('liquidation_detection.cascade_threshold', 0.6),
            lookback_window=self.config.get('liquidation_detection.lookback_window', 300)
        )
        self.execution_engine = ExecutionEngine(self.config)
        self.simulator = RealisticSimulator(self.config)
        
        # Phase 1: Exchange Integration
        logger.info("Initializing Phase 1: Exchange connectors...")
        self.exchange_connector = ExchangeConnector(self.config)
        
        # Load strategies
        logger.info("Loading strategies...")
        self.strategies = load_all_strategies(self.config)
        logger.info(f"✓ Loaded {len(self.strategies)} strategies")
        
        # Market data cache
        self.market_data = {}
        self.recent_liquidations = []
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            logger.info(f"\n⚠️ Received {signal_name}, initiating graceful shutdown...")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def fetch_market_data(self):
        """
        Fetch current market data from exchanges
        
        Returns:
            Dictionary of market data or None if error
        """
        try:
            logger.debug("Fetching market data from exchanges...")
            market_data = await self.exchange_connector.fetch_market_data()
            
            if not market_data:
                logger.warning("No market data returned from exchanges")
                return None
            
            # Convert to format expected by strategies
            processed_data = {}
            for symbol, data in market_data.items():
                processed_data[symbol] = {
                    'timestamp': data.timestamp,
                    'open': data.open,
                    'high': data.high,
                    'low': data.low,
                    'close': data.close,
                    'volume': data.volume,
                    'bid': data.bid,
                    'ask': data.ask,
                    'exchange': data.exchange
                }
            
            return processed_data
        
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    async def main_loop(self):
        """
        Main trading loop with all 26 improvements
        
        Execution Flow:
        1. Fetch & Validate Data
        2. Check Liquidation Cascade
        3. Pre-trade Risk Check
        4. Generate Strategy Signals
        5. Adaptive Allocation
        6. Correlation Management
        7. Ensemble Voting
        8. Position Sizing
        9. Execute Trade
        10. Update Portfolio
        11. Persist State
        12. Performance Reporting
        """
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("🎯 Starting main trading loop...")
        logger.info("=" * 70)
        
        while self.is_running and not self.shutdown_requested:
            self.iteration += 1
            loop_start = datetime.now()
            
            try:
                # ===== PHASE 1: DATA PIPELINE =====
                logger.debug(f"[{self.iteration}] Phase 1: Fetching market data")
                raw_data = await self.fetch_market_data()
                
                if raw_data is None or len(raw_data) == 0:
                    logger.warning("No market data available, skipping iteration")
                    await asyncio.sleep(self.config.trading.trading_interval)
                    continue
                
                # ===== PHASE 2: DATA VALIDATION =====
                logger.debug(f"[{self.iteration}] Phase 2: Validating data")
                validation_result = self.data_validator.validate_market_data(raw_data)
                
                if not validation_result.is_valid:
                    logger.warning(f"Data validation failed: {validation_result.errors}")
                    continue
                
                if validation_result.warnings:
                    logger.warning(f"Data warnings: {validation_result.warnings}")
                
                # ===== PHASE 3: NORMALIZATION =====
                logger.debug(f"[{self.iteration}] Phase 3: Normalizing features")
                normalized_data = self.normalizer.normalize_features(raw_data)
                self.market_data = normalized_data
                
                # ===== PHASE 4: LIQUIDATION CASCADE CHECK =====
                logger.debug(f"[{self.iteration}] Phase 4: Checking liquidation cascades")
                cascade_risk = await self.liquidation_detector.detect_cascade_risk(
                    raw_data,
                    self.recent_liquidations
                )
                
                if cascade_risk['probability'] > self.config.get('liquidation_detection.cascade_threshold', 0.6):
                    logger.warning(
                        f"🚨 HIGH CASCADE RISK: {cascade_risk['probability']:.2%} "
                        f"(threshold: {self.config.get('liquidation_detection.cascade_threshold', 0.6):.2%})"
                    )
                    
                    action = self.config.get('liquidation_detection.action_on_cascade', 'reduce_positions')
                    if action == 'reduce_positions':
                        await self.risk_manager.emergency_reduce_positions(self.portfolio)
                    elif action == 'close_all':
                        await self.risk_manager.close_all_positions(self.portfolio)
                    
                    continue
                
                # ===== PHASE 5: PRE-TRADE RISK CHECK =====
                logger.debug(f"[{self.iteration}] Phase 5: Pre-trade risk check")
                
                # Update risk metrics
                current_equity = self.portfolio['equity']
                self.risk_manager.update_metrics(current_equity)
                
                # Check circuit breaker
                daily_dd = self.risk_manager.get_daily_drawdown()
                cb_state = self.circuit_breaker.check(daily_dd)
                
                if not self.circuit_breaker.can_trade():
                    logger.info(f"Circuit breaker {cb_state.value} - skipping trades")
                    await asyncio.sleep(self.config.trading.trading_interval)
                    continue
                
                # ===== PHASE 6: GENERATE STRATEGY SIGNALS =====
                logger.debug(f"[{self.iteration}] Phase 6: Generating strategy signals")
                
                all_signals = {}
                strategy_performance = {}
                
                for name, strategy in self.strategies.items():
                    try:
                        signal = await strategy.generate_signal(normalized_data)
                        if signal is not None:
                            all_signals[name] = signal
                            strategy_performance[name] = strategy.get_performance_metrics()
                    except Exception as e:
                        logger.error(f"Strategy {name} error: {e}")
                        continue
                
                if not all_signals:
                    logger.info("No valid signals generated")
                    await asyncio.sleep(self.config.trading.trading_interval)
                    continue
                
                logger.info(f"✓ Generated {len(all_signals)} signals")
                
                # ===== PHASE 7: ADAPTIVE ALLOCATION =====
                logger.debug(f"[{self.iteration}] Phase 7: Computing adaptive weights")
                
                if self.allocation_engine.should_rebalance():
                    weights = self.allocation_engine.calculate_weights(strategy_performance)
                    logger.debug(f"Rebalanced weights: Top 3 = {list(weights.items())[:3]}")
                else:
                    weights = self.allocation_engine.current_weights
                
                # ===== PHASE 8: CORRELATION MANAGEMENT =====
                logger.debug(f"[{self.iteration}] Phase 8: Correlation management")
                
                # Update correlation matrix
                self.correlation_manager.update_correlations(all_signals, strategy_performance)
                
                # Adjust signals for correlation
                adjusted_signals = self.correlation_manager.adjust_for_correlation(
                    all_signals,
                    self.portfolio['positions']
                )
                
                portfolio_corr = self.correlation_manager.get_portfolio_correlation()
                logger.debug(f"Portfolio correlation: {portfolio_corr:.2%}")
                
                # ===== PHASE 9: ENSEMBLE VOTING =====
                logger.debug(f"[{self.iteration}] Phase 9: Ensemble voting")
                
                final_signal = self.ensemble_voting.vote(adjusted_signals, weights)
                
                if final_signal is None:
                    logger.info("Ensemble voting produced no signal")
                    await asyncio.sleep(self.config.trading.trading_interval)
                    continue
                
                if final_signal.confidence < self.config.get('ensemble.confidence_threshold', 0.5):
                    logger.info(f"Ensemble confidence too low: {final_signal.confidence:.2%}")
                    continue
                
                logger.info(
                    f"🎯 Ensemble Signal: {final_signal.action} "
                    f"@ {final_signal.confidence:.2%} confidence"
                )
                
                # ===== PHASE 10: POSITION SIZING =====
                logger.debug(f"[{self.iteration}] Phase 10: Position sizing")
                
                # Kelly-Modified sizing
                base_size = self.risk_manager.compute_kelly_fraction(
                    win_probability=final_signal.confidence,
                    capital=self.portfolio['cash']
                )
                
                # Correlation-aware adjustment
                correlation_factor = self.correlation_manager.get_correlation_factor(portfolio_corr)
                adjusted_size = base_size * correlation_factor
                
                # Circuit breaker size multiplier
                cb_multiplier = self.circuit_breaker.get_size_multiplier()
                final_size = adjusted_size * cb_multiplier
                
                # Apply hard limits
                final_size = self.risk_manager.apply_limits(final_size)
                
                logger.info(
                    f"Position sizing: Kelly={base_size:.4f} → "
                    f"Corr-adj={adjusted_size:.4f} → "
                    f"CB-adj={final_size:.4f}"
                )
                
                # ===== PHASE 11: EXECUTE TRADE =====
                logger.debug(f"[{self.iteration}] Phase 11: Executing trade")
                
                if final_size > 0:
                    trade_result = await self.execution_engine.execute_trade(
                        symbol=final_signal.symbol,
                        action=final_signal.action,
                        size=final_size,
                        portfolio=self.portfolio
                    )
                    
                    if trade_result.get('success'):
                        # Update portfolio
                        self._update_portfolio(trade_result)
                        
                        # Record trade
                        self.trade_history.append(trade_result)
                        
                        logger.info(
                            f"✅ Trade executed: {final_signal.action} {final_size:.4f} "
                            f"{final_signal.symbol} @ {trade_result.get('price', 0):.2f}"
                        )
                    else:
                        logger.warning(f"⚠️ Trade execution failed: {trade_result.get('error')}")
                else:
                    logger.info("Position size too small, skipping trade")
                
                # ===== PHASE 12: PERSIST STATE & REPORT =====
                logger.debug(f"[{self.iteration}] Phase 12: Persisting state")
                
                # Save state checkpoint
                await self.state_manager.save_checkpoint({
                    'iteration': self.iteration,
                    'timestamp': datetime.now().isoformat(),
                    'portfolio': self.portfolio,
                    'trade_history': self.trade_history[-10:],  # Last 10 trades
                    'performance_metrics': self.performance_metrics
                })
                
                # Update performance metrics
                self._update_performance_metrics()
                
                # Report every 10 iterations
                if self.iteration % 10 == 0:
                    self._log_performance_summary()
                
                # Calculate loop duration
                loop_duration = (datetime.now() - loop_start).total_seconds()
                logger.debug(f"Loop iteration completed in {loop_duration:.2f}s")
                
                # Sleep before next iteration
                await asyncio.sleep(self.config.trading.trading_interval)
            
            except Exception as e:
                logger.error(f"Error in main loop iteration {self.iteration}: {e}", exc_info=True)
                await asyncio.sleep(self.config.trading.trading_interval)
        
        # Cleanup on exit
        await self._cleanup()
    
    def _update_portfolio(self, trade_result: Dict):
        """Update portfolio with trade result"""
        symbol = trade_result['symbol']
        action = trade_result['action']
        size = trade_result['size']
        price = trade_result['price']
        
        if action == 'BUY':
            # Add to position
            if symbol in self.portfolio['positions']:
                # Average up
                current_size = self.portfolio['positions'][symbol]['size']
                current_price = self.portfolio['positions'][symbol]['avg_price']
                
                new_size = current_size + size
                new_avg_price = (current_size * current_price + size * price) / new_size
                
                self.portfolio['positions'][symbol] = {
                    'size': new_size,
                    'avg_price': new_avg_price,
                    'last_update': datetime.now()
                }
            else:
                # New position
                self.portfolio['positions'][symbol] = {
                    'size': size,
                    'avg_price': price,
                    'last_update': datetime.now()
                }
            
            # Decrease cash
            self.portfolio['cash'] -= size * price
        
        elif action == 'SELL':
            # Reduce or close position
            if symbol in self.portfolio['positions']:
                current_size = self.portfolio['positions'][symbol]['size']
                
                if size >= current_size:
                    # Close position
                    realized_pnl = (price - self.portfolio['positions'][symbol]['avg_price']) * current_size
                    del self.portfolio['positions'][symbol]
                    
                    # Increase cash
                    self.portfolio['cash'] += current_size * price
                    
                    logger.info(f"Position closed. Realized P&L: €{realized_pnl:.2f}")
                else:
                    # Reduce position
                    self.portfolio['positions'][symbol]['size'] -= size
                    self.portfolio['cash'] += size * price
        
        # Update equity
        self.portfolio['equity'] = self._calculate_equity()
    
    def _calculate_equity(self) -> float:
        """Calculate current portfolio equity"""
        equity = self.portfolio['cash']
        
        # Add value of open positions (using latest market prices)
        for symbol, position in self.portfolio['positions'].items():
            # Get latest price from market data
            latest_price = self.market_data.get(symbol, {}).get('close', position['avg_price'])
            equity += position['size'] * latest_price
        
        return equity
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        if not self.trade_history:
            return
        
        # Calculate basic metrics
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t.get('pnl', 0) > 0)
        
        self.performance_metrics = {
            'total_trades': total_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'current_equity': self.portfolio['equity'],
            'total_return': (self.portfolio['equity'] - self.config.trading.initial_capital) / self.config.trading.initial_capital,
            'daily_pnl': self.risk_manager.current_metrics.daily_pnl if self.risk_manager.current_metrics else 0,
            'max_drawdown': self.risk_manager.current_metrics.max_drawdown if self.risk_manager.current_metrics else 0,
        }
    
    def _log_performance_summary(self):
        """Log performance summary"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 PERFORMANCE SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Iteration: {self.iteration}")
        logger.info(f"Equity: €{self.portfolio['equity']:.2f}")
        logger.info(f"Cash: €{self.portfolio['cash']:.2f}")
        logger.info(f"Open Positions: {len(self.portfolio['positions'])}")
        logger.info(f"Total Trades: {self.performance_metrics.get('total_trades', 0)}")
        logger.info(f"Win Rate: {self.performance_metrics.get('win_rate', 0):.2%}")
        logger.info(f"Total Return: {self.performance_metrics.get('total_return', 0):.2%}")
        logger.info(f"Max Drawdown: {self.performance_metrics.get('max_drawdown', 0):.2%}")
        logger.info("=" * 70 + "\n")
    
    async def _cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("\n🛡️ Performing cleanup...")
        
        try:
            # Close exchange connections
            await self.exchange_connector.close()
            logger.info("✓ Exchange connections closed")
            
            # Final state save
            await self.state_manager.save_checkpoint({
                'iteration': self.iteration,
                'timestamp': datetime.now().isoformat(),
                'portfolio': self.portfolio,
                'trade_history': self.trade_history,
                'performance_metrics': self.performance_metrics,
                'shutdown': True
            })
            logger.info("✓ Final state saved")
            
            # Clear secrets cache
            get_secrets_manager().clear_cache()
            logger.info("✓ Secrets cache cleared")
            
            logger.info("✅ Cleanup complete")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """
    Main entry point
    
    Flow:
    1. Validate secrets (already done at module import)
    2. Create BotV2 instance
    3. Run main trading loop
    4. Handle shutdown gracefully
    """
    try:
        logger.info("")
        logger.info("╔═══════════════════════════════════════════════════════════════════╗")
        logger.info("║                      BotV2 Trading System                         ║")
        logger.info("║                    Production Ready v4.1                          ║")
        logger.info("╚═══════════════════════════════════════════════════════════════════╝")
        logger.info("")
        
        # Create bot instance
        bot = BotV2()
        
        # Run main loop
        asyncio.run(bot.main_loop())
    
    except KeyboardInterrupt:
        logger.info("\n⚠️ Keyboard interrupt received")
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("👋 BotV2 shutdown complete")
    logger.info("")


if __name__ == "__main__":
    main()
