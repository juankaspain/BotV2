#!/usr/bin/env python3
"""
BotV2 - Main Trading System
Complete Production System with 26 Audit Improvements
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config_manager import ConfigManager
from core.risk_manager import RiskManager, CircuitBreaker
from core.state_manager import StateManager
from core.liquidation_detector import LiquidationDetector
from core.execution_engine import ExecutionEngine
from data.data_validator import DataValidator
from data.normalization_pipeline import NormalizationPipeline
from ensemble.adaptive_allocation import AdaptiveAllocationEngine
from ensemble.correlation_manager import CorrelationManager
from ensemble.ensemble_voting import EnsembleVoting
from strategies.base_strategy import load_all_strategies
from backtesting.realistic_simulator import RealisticSimulator
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


class BotV2:
    """
    BotV2 Main Trading System
    
    Implements all 26 audit improvements:
    - Round 1: Data validation, Risk management, State recovery
    - Round 2: Adaptive allocation, Correlation management, Ensemble voting
    - Round 3: Realistic execution, Liquidation detection, Market microstructure
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize BotV2 trading system"""
        
        logger.info("=" * 70)
        logger.info("🚀 Initializing BotV2 Trading System...")
        logger.info("=" * 70)
        
        # Load configuration
        self.config = ConfigManager(config_path)
        logger.info(f"✓ Config loaded: {self.config.system['name']} v{self.config.system['version']}")
        
        # Initialize components
        self._init_components()
        
        # State
        self.is_running = False
        self.iteration = 0
        self.start_time = None
        
        # Performance tracking
        self.portfolio = {
            'cash': self.config.trading.initial_capital,
            'positions': {},
            'equity': self.config.trading.initial_capital
        }
        self.trade_history = []
        self.performance_metrics = {}
        
        logger.info("✅ BotV2 initialization complete")
    
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
        
        # Load strategies
        logger.info("Loading strategies...")
        self.strategies = load_all_strategies(self.config)
        logger.info(f"✓ Loaded {len(self.strategies)} strategies")
        
        # Market data cache
        self.market_data = {}
        self.recent_liquidations = []
    
    async def fetch_market_data(self):
        """Fetch current market data from exchanges"""
        # TODO: Implement real exchange API calls
        # For now, return placeholder
        logger.debug("Fetching market data...")
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
        10. Persist State
        """
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("🎯 Starting main trading loop...")
        logger.info("=" * 70)
        
        while self.is_running:
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
                correlation_factor = self.correlation_manager.get_correlation_fac
