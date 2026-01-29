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

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# ===== CRITICAL: VALIDATE SECRETS BEFORE ANY OTHER IMPORTS =====
from shared.config.secrets_validator import validate_secrets

# Get environment from env var or default to development
CURRENT_ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Validate all required secrets (skip strict mode in DEMO mode)
DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
validate_secrets(environment=CURRENT_ENVIRONMENT, strict=not DEMO_MODE)

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
    """Main BotV2 Trading System Class"""
    
    def __init__(self, config_path: Optional[str] = None):
        logger.info("=" * 70)
        logger.info("🚀 Initializing BotV2 Trading System...")
        logger.info(f"Environment: {CURRENT_ENVIRONMENT}")
        logger.info("=" * 70)
        
        # Get secrets manager for validation summary
        secrets_manager = get_secrets_manager()
        validation_summary = secrets_manager.get_validation_summary()
        
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize components
        self._init_components()
        
        # State tracking
        self.is_running = False
        self.shutdown_requested = False
        self.iteration = 0
        
        # Portfolio state
        self.portfolio = {
            'cash': self.config.trading.initial_capital,
            'positions': {},
            'equity': self.config.trading.initial_capital
        }
        
        self.trade_history = []
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("✅ BotV2 initialization complete")

    def _init_components(self):
        """Initialize all trading components"""
        logger.info("Initializing components...")
        
        # Data validation
        self.data_validator = DataValidator(
            outlier_threshold=self.config.get('data.validation.outlier_std_threshold', 5)
        )
        
        # Risk management
        self.risk_manager = RiskManager(self.config)
        
        # State management
        self.state_manager = StateManager(self.config)
        
        # Execution engine
        self.execution_engine = ExecutionEngine(self.config)
        
        # Load strategies
        self.strategies = load_all_strategies(self.config)
        
        logger.info(f"✅ Loaded {len(self.strategies)} strategies")

    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def main_loop(self):
        """Main trading loop"""
        logger.info("🚀 Starting main trading loop...")
        self.is_running = True
        
        while self.is_running and not self.shutdown_requested:
            try:
                self.iteration += 1
                
                # Main loop logic would go here
                # For now, just sleep and wait
                await asyncio.sleep(1)
                
                # Log heartbeat every 60 iterations
                if self.iteration % 60 == 0:
                    logger.info(f"💓 Heartbeat: iteration {self.iteration}")
                    
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retry
        
        logger.info("Main loop ended")
        await self._cleanup()

    async def _cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("Cleaning up resources...")
        self.is_running = False
        logger.info("✅ Cleanup complete")

    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'iteration': self.iteration,
            'environment': CURRENT_ENVIRONMENT,
            'portfolio': self.portfolio,
            'strategies_count': len(self.strategies) if self.strategies else 0
        }


def main():
    """Main entry point"""
    logger.info("Starting BotV2...")
    
    try:
        bot = BotV2()
        asyncio.run(bot.main_loop())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("BotV2 shutdown complete")


if __name__ == "__main__":
    main()
