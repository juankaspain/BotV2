"""
Unit Tests for Risk Manager
"""

import pytest
import numpy as np
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.risk_manager import RiskManager, CircuitBreaker, CircuitBreakerState
from config.config_manager import ConfigManager


@pytest.fixture
def config():
    """Fixture for config"""
    return ConfigManager()


@pytest.fixture
def risk_manager(config):
    """Fixture for risk manager"""
    return RiskManager(config)


class TestCircuitBreaker:
    """Test Circuit Breaker"""
    
    def test_initialization(self):
        """Test circuit breaker initialization"""
        
        cb = CircuitBreaker(
            level_1=-5.0,
            level_2=-10.0,
            level_3=-15.0
        )
        
        assert cb.state == CircuitBreakerState.GREEN
        assert cb.can_trade() is True
    
    def test_level_1_trigger(self):
        """Test level 1 trigger"""
        
        cb = CircuitBreaker(level_1=-5.0, level_2=-10.0, level_3=-15.0)
        
        # Trigger level 1
        state = cb.check(-6.0)
        
        assert state == CircuitBreakerState.YELLOW
        assert cb.can_trade() is True
        assert cb.get_size_multiplier() == 0.5
    
    def test_level_3_trigger(self):
        """Test level 3 trigger (stop trading)"""
        
        cb = CircuitBreaker(level_1=-5.0, level_2=-10.0, level_3=-15.0)
        
        # Trigger level 3
        state = cb.check(-16.0)
        
        assert state == CircuitBreakerState.RED
        assert cb.can_trade() is False
        assert cb.get_size_multiplier() == 0.0
    
    def test_recovery(self):
        """Test recovery from circuit breaker"""
        
        cb = CircuitBreaker(level_1=-5.0, level_2=-10.0, level_3=-15.0)
        
        # Trigger
        cb.check(-6.0)
        assert cb.state == CircuitBreakerState.YELLOW
        
        # Recover
        cb.check(-2.0)
        assert cb.state == CircuitBreakerState.GREEN


class TestRiskManager:
    """Test Risk Manager"""
    
    def test_initialization(self, risk_manager):
        """Test risk manager initialization"""
        
        assert risk_manager.circuit_breaker is not None
        assert risk_manager.max_position_size > 0
        assert risk_manager.min_position_size > 0
    
    def test_update_metrics(self, risk_manager):
        """Test metrics update"""
        
        risk_manager.update_metrics(3000)
        
        assert risk_manager.daily_start_value == 3000
        assert risk_manager.current_metrics is not None
    
    def test_drawdown_calculation(self, risk_manager):
        """Test drawdown calculation"""
        
        # Initialize
        risk_manager.update_metrics(3000)
        
        # Drop to 2700 (-10%)
        risk_manager.update_metrics(2700)
        
        dd = risk_manager.get_daily_drawdown()
        assert dd == pytest.approx(-10.0, rel=0.1)
    
    def test_kelly_sizing(self, risk_manager):
        """Test Kelly Criterion sizing"""
        
        # 60% win probability
        size = risk_manager.compute_kelly_fraction(
            win_probability=0.60,
            capital=3000
        )
        
        # Should return a positive fraction
        assert size > 0
        assert size <= 0.5  # Conservative Kelly
    
    def test_kelly_min_probability(self, risk_manager):
        """Test Kelly with low probability"""
        
        # Below minimum threshold
        size = risk_manager.compute_kelly_fraction(
            win_probability=0.45,
            capital=3000
        )
        
        # Should return 0 (below threshold)
        assert size == 0.0
    
    def test_apply_limits(self, risk_manager):
        """Test position size limits"""
        
        # Test max limit
        limited = risk_manager.apply_limits(0.50)  # 50%
        assert limited <= risk_manager.max_position_size
        
        # Test min limit
        limited = risk_manager.apply_limits(0.001)  # 0.1%
        assert limited >= risk_manager.min_position_size
    
    def test_correlation_aware_sizing(self, risk_manager):
        """Test correlation-aware sizing"""
        
        base_size = 0.10
        
        # Low correlation - no penalty
        adjusted = risk_manager.correlation_aware_sizing(base_size, 0.3)
        assert adjusted == base_size
        
        # High correlation - apply penalty
        adjusted = risk_manager.correlation_aware_sizing(base_size, 0.8)
        assert adjusted < base_size
    
    @pytest.mark.asyncio
    async def test_emergency_reduce_positions(self, risk_manager):
        """Test emergency position reduction"""
        
        portfolio = {
            'cash': 1000,
            'positions': {
                'BTC': {'size': 100},
                'ETH': {'size': 50}
            }
        }
        
        await risk_manager.emergency_reduce_positions(portfolio)
        
        # All positions should be reduced by 50%
        assert portfolio['positions']['BTC']['size'] == 50
        assert portfolio['positions']['ETH']['size'] == 25
    
    def test_risk_report(self, risk_manager):
        """Test risk report generation"""
        
        risk_manager.update_metrics(3000)
        
        report = risk_manager.get_risk_report()
        
        assert 'portfolio_value' in report
        assert 'daily_drawdown_pct' in report
        assert 'circuit_breaker' in report


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
