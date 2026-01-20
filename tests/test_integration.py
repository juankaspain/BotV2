"""
Integration Tests
End-to-end testing of complete trading system
"""

import pytest
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config.config_manager import ConfigManager
from core.risk_manager import RiskManager
from core.state_manager import StateManager
from core.execution_engine import ExecutionEngine
from data.data_validator import DataValidator
from ensemble.ensemble_voting import EnsembleVoting, TradeSignal
from strategies.momentum import MomentumStrategy


@pytest.fixture
def config():
    """Fixture for config"""
    return ConfigManager()


@pytest.fixture
def sample_market_data():
    """Fixture for realistic market data"""
    
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    
    np.random.seed(42)
    close_prices = 50000 + np.cumsum(np.random.randn(200) * 100)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(200) * 50,
        'high': close_prices + np.abs(np.random.randn(200) * 100),
        'low': close_prices - np.abs(np.random.randn(200) * 100),
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 200),
        'volatility': np.random.uniform(0.01, 0.03, 200)
    })
    
    return data


@pytest.mark.integration
class TestDataPipeline:
    """Test complete data pipeline"""
    
    def test_data_validation_pipeline(self, config, sample_market_data):
        """Test data validation flow"""
        
        validator = DataValidator(outlier_threshold=5.0)
        
        # Validate
        result = validator.validate_market_data(sample_market_data)
        
        assert result.is_valid is True
        assert result.data_quality_score > 0.8
        assert len(result.errors) == 0
    
    def test_data_validation_with_errors(self, config):
        """Test data validation with bad data"""
        
        validator = DataValidator()
        
        # Create data with NaN
        bad_data = pd.DataFrame({
            'open': [100, 101, np.nan],
            'high': [102, 103, 104],
            'low': [99, 100, 101],
            'close': [101, 102, 103],
            'volume': [1000, 1100, 1200]
        })
        
        result = validator.validate_market_data(bad_data)
        
        assert result.is_valid is False
        assert len(result.errors) > 0


@pytest.mark.integration
class TestTradingWorkflow:
    """Test complete trading workflow"""
    
    @pytest.mark.asyncio
    async def test_signal_to_execution_flow(self, config, sample_market_data):
        """Test signal generation → execution flow"""
        
        # Components
        strategy = MomentumStrategy(config)
        execution_engine = ExecutionEngine(config)
        
        # Generate signal
        signal = await strategy.generate_signal(sample_market_data)
        
        if signal and signal.action != 'HOLD':
            # Execute
            portfolio = {'cash': 3000, 'equity': 3000, 'positions': {}}
            
            execution_result = await execution_engine.execute(
                signal=signal,
                position_size=0.1,
                market_data=sample_market_data,
                portfolio=portfolio
            )
            
            # Verify execution
            assert 'executed' in execution_result
            if execution_result['executed']:
                assert execution_result['slippage'] >= 0
                assert execution_result['commission'] > 0
    
    @pytest.mark.asyncio
    async def test_ensemble_voting_flow(self, config):
        """Test ensemble voting with multiple signals"""
        
        ensemble = EnsembleVoting(
            method='weighted_average',
            confidence_threshold=0.5
        )
        
        # Create mock signals
        signals = {
            'strategy1': TradeSignal(
                strategy='strategy1',
                action='BUY',
                confidence=0.7,
                symbol='BTC',
                entry_price=50000
            ),
            'strategy2': TradeSignal(
                strategy='strategy2',
                action='BUY',
                confidence=0.6,
                symbol='BTC',
                entry_price=50000
            ),
            'strategy3': TradeSignal(
                strategy='strategy3',
                action='SELL',
                confidence=0.4,
                symbol='BTC',
                entry_price=50000
            )
        }
        
        weights = {
            'strategy1': 0.4,
            'strategy2': 0.35,
            'strategy3': 0.25
        }
        
        # Vote
        final_signal = ensemble.vote(signals, weights)
        
        # Should produce BUY (2 BUY vs 1 SELL, with higher weights)
        assert final_signal is not None
        assert final_signal.action == 'BUY'
        assert final_signal.confidence >= 0.5


@pytest.mark.integration
class TestRiskManagement:
    """Test risk management integration"""
    
    def test_circuit_breaker_integration(self, config):
        """Test circuit breaker in risk management flow"""
        
        risk_manager = RiskManager(config)
        
        # Simulate portfolio drawdown
        risk_manager.update_metrics(3000)  # Start
        risk_manager.update_metrics(2700)  # -10% drawdown
        
        # Check circuit breaker state
        cb_info = risk_manager.circuit_breaker.get_state_info()
        
        # Should trigger level 2
        assert cb_info['state'] in ['yellow', 'red']
        assert cb_info['size_multiplier'] <= 1.0
    
    def test_position_sizing_with_risk(self, config):
        """Test position sizing with risk constraints"""
        
        risk_manager = RiskManager(config)
        risk_manager.update_metrics(3000)
        
        # Calculate Kelly size
        kelly_size = risk_manager.compute_kelly_fraction(
            win_probability=0.65,
            capital=3000
        )
        
        # Apply limits
        final_size = risk_manager.apply_limits(kelly_size)
        
        # Should be within bounds
        assert final_size >= risk_manager.min_position_size
        assert final_size <= risk_manager.max_position_size
    
    @pytest.mark.asyncio
    async def test_emergency_procedures(self, config):
        """Test emergency risk procedures"""
        
        risk_manager = RiskManager(config)
        
        portfolio = {
            'cash': 500,
            'positions': {
                'BTC': {'size': 1000, 'entry_price': 50000},
                'ETH': {'size': 500, 'entry_price': 3000}
            },
            'equity': 2000
        }
        
        # Trigger emergency reduction
        await risk_manager.emergency_reduce_positions(portfolio)
        
        # All positions reduced
        assert portfolio['positions']['BTC']['size'] == 500
        assert portfolio['positions']['ETH']['size'] == 250


@pytest.mark.integration
class TestStateManagement:
    """Test state persistence and recovery"""
    
    @pytest.mark.asyncio
    async def test_state_persistence_flow(self, config):
        """Test save and recovery flow"""
        
        state_manager = StateManager(config)
        
        # Create portfolio state
        portfolio = {
            'cash': 2500,
            'equity': 3200,
            'positions': {
                'BTC': {'size': 700, 'entry_price': 50000}
            }
        }
        
        # Save
        await state_manager.save_portfolio(portfolio)
        
        # Attempt recovery
        recovered = await state_manager.recover()
        
        if recovered:
            assert 'portfolio' in recovered
            assert recovered['portfolio']['cash'] > 0


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEnd:
    """End-to-end system tests"""
    
    @pytest.mark.asyncio
    async def test_complete_trading_loop(self, config, sample_market_data):
        """Test complete trading loop iteration"""
        
        # Initialize all components
        risk_manager = RiskManager(config)
        execution_engine = ExecutionEngine(config)
        strategy = MomentumStrategy(config)
        ensemble = EnsembleVoting()
        
        # Portfolio
        portfolio = {
            'cash': 3000,
            'equity': 3000,
            'positions': {}
        }
        
        # Initialize risk tracking
        risk_manager.update_metrics(portfolio['equity'])
        
        # Generate signal
        signal = await strategy.generate_signal(sample_market_data)
        
        if signal and signal.action != 'HOLD':
            
            # Check risk
            if risk_manager.circuit_breaker.can_trade():
                
                # Position sizing
                kelly_size = risk_manager.compute_kelly_fraction(
                    win_probability=signal.confidence,
                    capital=portfolio['cash']
                )
                
                final_size = risk_manager.apply_limits(kelly_size)
                
                # Execute
                result = await execution_engine.execute(
                    signal=signal,
                    position_size=final_size,
                    market_data=sample_market_data,
                    portfolio=portfolio
                )
                
                # Verify complete flow
                if result['executed']:
                    assert result['slippage'] >= 0
                    assert result['commission'] > 0
                    assert 'execution_price' in result
    
    @pytest.mark.asyncio
    async def test_multi_strategy_integration(self, config, sample_market_data):
        """Test multiple strategies working together"""
        
        from strategies.stat_arb import StatisticalArbitrageStrategy
        from strategies.mean_reversion import MeanReversionStrategy
        
        strategies = [
            MomentumStrategy(config),
            StatisticalArbitrageStrategy(config),
            MeanReversionStrategy(config)
        ]
        
        # Generate signals from all
        signals = {}
        for strategy in strategies:
            signal = await strategy.generate_signal(sample_market_data)
            if signal:
                signals[strategy.name] = signal
        
        # Ensemble voting
        if signals:
            ensemble = EnsembleVoting()
            weights = {name: 1.0/len(signals) for name in signals.keys()}
            
            final_signal = ensemble.vote(signals, weights)
            
            # Should produce aggregated signal
            assert final_signal is None or final_signal.strategy == 'ensemble'


@pytest.mark.integration
class TestPerformanceTracking:
    """Test performance tracking and metrics"""
    
    def test_strategy_performance_tracking(self, config):
        """Test strategy performance metrics"""
        
        strategy = MomentumStrategy(config)
        
        # Simulate trades
        for i in range(10):
            pnl = np.random.uniform(-0.02, 0.05)  # -2% to +5%
            strategy.record_trade({
                'executed': True,
                'pnl_pct': pnl
            })
        
        # Get metrics
        metrics = strategy.get_performance_metrics()
        
        assert metrics['trades'] == 10
        assert len(metrics['returns']) == 10
        assert 'sharpe' in metrics
        assert 'win_rate' in metrics
    
    def test_portfolio_equity_tracking(self, config):
        """Test portfolio equity curve tracking"""
        
        risk_manager = RiskManager(config)
        
        # Simulate equity changes
        equity_values = [3000, 3100, 3050, 3200, 3150]
        
        for equity in equity_values:
            risk_manager.update_metrics(equity)
        
        # Verify tracking
        assert len(risk_manager.portfolio_value_history) == 5
        assert risk_manager.current_metrics.portfolio_value == 3150


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
