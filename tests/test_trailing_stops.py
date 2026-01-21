"""
Unit Tests for Trailing Stop Manager
Tests all trailing stop types, activation logic, and position management
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.trailing_stop_manager import (
    TrailingStopManager,
    TrailingStopType,
    TrailingStop
)


@pytest.fixture
def mock_config():
    """Create mock configuration"""
    config = Mock()
    config.risk.trailing_stops = {
        'enabled': True,
        'default_type': 'percentage',
        'activation_profit': 2.0,
        'trail_distance': 1.0,
        'atr_period': 14,
        'atr_multiplier': 2.0,
        'chandelier_period': 22,
        'chandelier_multiplier': 3.0
    }
    return config


@pytest.fixture
def trailing_manager(mock_config):
    """Create TrailingStopManager instance"""
    return TrailingStopManager(mock_config)


@pytest.fixture
def sample_market_data():
    """Create sample market data for ATR calculation"""
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
    
    # Generate realistic OHLC data
    close = 100 + np.cumsum(np.random.randn(50) * 0.5)
    high = close + np.random.rand(50) * 2
    low = close - np.random.rand(50) * 2
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close,
        'high': high,
        'low': low,
        'close': close,
        'volume': np.random.randint(1000, 10000, 50)
    })
    
    return df


class TestTrailingStopBasics:
    """Test basic trailing stop functionality"""
    
    def test_manager_initialization(self, trailing_manager):
        """Test manager initializes correctly"""
        assert trailing_manager.enabled == True
        assert trailing_manager.default_type == TrailingStopType.PERCENTAGE
        assert trailing_manager.default_activation == 2.0
        assert trailing_manager.default_trail_distance == 1.0
        assert len(trailing_manager.stops) == 0
    
    def test_add_position(self, trailing_manager):
        """Test adding a position with trailing stop"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0
        )
        
        assert stop is not None
        assert stop.symbol == 'BTCUSDT'
        assert stop.position_id == 'pos_001'
        assert stop.entry_price == 100.0
        assert stop.activated == False
        assert 'pos_001' in trailing_manager.stops
    
    def test_disabled_trailing_stops(self, mock_config):
        """Test that disabled trailing stops don't create stops"""
        mock_config.risk.trailing_stops['enabled'] = False
        manager = TrailingStopManager(mock_config)
        
        stop = manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0
        )
        
        assert stop is None
        assert len(manager.stops) == 0


class TestPercentageStop:
    """Test percentage-based trailing stops"""
    
    def test_percentage_stop_calculation(self, trailing_manager):
        """Test percentage stop calculation"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            stop_type=TrailingStopType.PERCENTAGE,
            trail_distance=1.0
        )
        
        # Initial stop should be 1% below entry
        expected_stop = 100.0 * 0.99
        assert abs(stop.stop_price - expected_stop) < 0.01
    
    def test_percentage_stop_activation(self, trailing_manager):
        """Test stop activation after profit threshold"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=2.0,
            trail_distance=1.0
        )
        
        # Price increases but below activation threshold
        triggered = trailing_manager.update_position('pos_001', 101.5)
        assert stop.activated == False
        assert triggered == False
        
        # Price increases above activation threshold (2%)
        triggered = trailing_manager.update_position('pos_001', 102.5)
        assert stop.activated == True
        assert triggered == False
    
    def test_percentage_stop_trails_upward(self, trailing_manager):
        """Test that stop trails upward as price increases"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=2.0,
            trail_distance=1.0
        )
        
        # Activate stop
        trailing_manager.update_position('pos_001', 103.0)
        assert stop.activated == True
        initial_stop = stop.stop_price
        
        # Price increases, stop should move up
        trailing_manager.update_position('pos_001', 105.0)
        assert stop.stop_price > initial_stop
        assert stop.highest_price == 105.0
        
        # Expected stop: 105 * 0.99 = 103.95
        assert abs(stop.stop_price - 103.95) < 0.01
    
    def test_percentage_stop_never_decreases(self, trailing_manager):
        """Test that stop never moves down"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=2.0,
            trail_distance=1.0
        )
        
        # Activate and move price up
        trailing_manager.update_position('pos_001', 103.0)
        trailing_manager.update_position('pos_001', 105.0)
        stop_at_105 = stop.stop_price
        
        # Price decreases, stop should NOT move down
        trailing_manager.update_position('pos_001', 104.0)
        assert stop.stop_price == stop_at_105
        
        trailing_manager.update_position('pos_001', 103.0)
        assert stop.stop_price == stop_at_105


class TestATRStop:
    """Test ATR-based trailing stops"""
    
    def test_atr_calculation_accuracy(self, trailing_manager, sample_market_data):
        """Test ATR calculation is accurate"""
        atr = trailing_manager._calculate_atr(sample_market_data, period=14)
        
        # ATR should be positive
        assert atr > 0
        
        # ATR should be reasonable (not too large or small)
        assert 0.1 < atr < 10.0
    
    def test_atr_stop_calculation(self, trailing_manager, sample_market_data):
        """Test ATR stop calculation"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            stop_type=TrailingStopType.ATR
        )
        
        # Activate stop
        trailing_manager.update_position('pos_001', 103.0, sample_market_data)
        assert stop.activated == True
        
        # Update with ATR data
        trailing_manager.update_position('pos_001', 105.0, sample_market_data)
        
        # Stop should be calculated based on ATR
        assert stop.stop_price > 0
        assert stop.stop_price < 105.0


class TestChandelierStop:
    """Test Chandelier Exit trailing stops"""
    
    def test_chandelier_stop_calculation(self, trailing_manager, sample_market_data):
        """Test Chandelier stop calculation"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            stop_type=TrailingStopType.CHANDELIER
        )
        
        # Activate stop
        trailing_manager.update_position('pos_001', 103.0, sample_market_data)
        assert stop.activated == True
        
        # Update with market data
        trailing_manager.update_position('pos_001', 105.0, sample_market_data)
        
        # Stop should be below highest high
        assert stop.stop_price < stop.highest_price


class TestDynamicStop:
    """Test dynamic volatility-based stops"""
    
    def test_dynamic_stop_calculation(self, trailing_manager, sample_market_data):
        """Test dynamic stop adapts to volatility"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            stop_type=TrailingStopType.DYNAMIC
        )
        
        # Activate stop
        trailing_manager.update_position('pos_001', 103.0, sample_market_data)
        assert stop.activated == True
        
        # Update with market data
        trailing_manager.update_position('pos_001', 105.0, sample_market_data)
        
        # Stop should be calculated
        assert stop.stop_price > 0


class TestStopTriggers:
    """Test stop trigger conditions"""
    
    def test_stop_triggered(self, trailing_manager):
        """Test that stop triggers when price hits stop level"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=2.0,
            trail_distance=1.0
        )
        
        # Activate stop
        trailing_manager.update_position('pos_001', 103.0)
        assert stop.activated == True
        
        # Move price up
        trailing_manager.update_position('pos_001', 105.0)
        stop_level = stop.stop_price
        
        # Price drops to stop level
        triggered = trailing_manager.update_position('pos_001', stop_level)
        assert triggered == True
        assert trailing_manager.stops_triggered == 1
    
    def test_stop_not_triggered_when_above(self, trailing_manager):
        """Test stop doesn't trigger when price above stop"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=2.0,
            trail_distance=1.0
        )
        
        # Activate and move up
        trailing_manager.update_position('pos_001', 103.0)
        trailing_manager.update_position('pos_001', 105.0)
        
        # Price stays above stop
        triggered = trailing_manager.update_position('pos_001', 104.5)
        assert triggered == False


class TestPositionManagement:
    """Test position management features"""
    
    def test_multiple_positions(self, trailing_manager):
        """Test managing multiple positions simultaneously"""
        # Add 3 positions
        stop1 = trailing_manager.add_position('BTC', 'pos_001', 100.0)
        stop2 = trailing_manager.add_position('ETH', 'pos_002', 50.0)
        stop3 = trailing_manager.add_position('SOL', 'pos_003', 20.0)
        
        assert len(trailing_manager.stops) == 3
        assert all(stop is not None for stop in [stop1, stop2, stop3])
    
    def test_remove_position(self, trailing_manager):
        """Test removing a position"""
        trailing_manager.add_position('BTCUSDT', 'pos_001', 100.0)
        assert len(trailing_manager.stops) == 1
        
        trailing_manager.remove_position('pos_001')
        assert len(trailing_manager.stops) == 0
    
    def test_get_stop_info(self, trailing_manager):
        """Test retrieving stop information"""
        stop = trailing_manager.add_position('BTCUSDT', 'pos_001', 100.0)
        trailing_manager.update_position('pos_001', 103.0)
        
        info = trailing_manager.get_stop_info('pos_001')
        
        assert info is not None
        assert info['symbol'] == 'BTCUSDT'
        assert info['entry_price'] == 100.0
        assert info['current_price'] == 103.0
        assert 'unrealized_profit_pct' in info
        assert 'distance_to_stop_pct' in info
    
    def test_get_all_stops(self, trailing_manager):
        """Test retrieving all stops"""
        trailing_manager.add_position('BTC', 'pos_001', 100.0)
        trailing_manager.add_position('ETH', 'pos_002', 50.0)
        
        all_stops = trailing_manager.get_all_stops()
        
        assert len(all_stops) == 2
        assert all('symbol' in stop for stop in all_stops)


class TestStatistics:
    """Test statistics tracking"""
    
    def test_statistics_tracking(self, trailing_manager):
        """Test that statistics are tracked correctly"""
        stats = trailing_manager.get_statistics()
        
        assert 'enabled' in stats
        assert 'active_stops' in stats
        assert 'stops_triggered_total' in stats
        assert stats['active_stops'] == 0
        assert stats['stops_triggered_total'] == 0
    
    def test_statistics_after_operations(self, trailing_manager):
        """Test statistics update after operations"""
        # Add positions
        trailing_manager.add_position('BTC', 'pos_001', 100.0)
        trailing_manager.add_position('ETH', 'pos_002', 50.0)
        
        # Activate one
        trailing_manager.update_position('pos_001', 103.0)
        
        stats = trailing_manager.get_statistics()
        assert stats['active_stops'] == 2
        assert stats['activated_stops'] == 1


class TestCustomParameters:
    """Test custom parameters"""
    
    def test_custom_activation_profit(self, trailing_manager):
        """Test custom activation profit threshold"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=5.0  # Custom 5%
        )
        
        # 3% profit - should not activate
        trailing_manager.update_position('pos_001', 103.0)
        assert stop.activated == False
        
        # 5% profit - should activate
        trailing_manager.update_position('pos_001', 105.0)
        assert stop.activated == True
    
    def test_custom_trail_distance(self, trailing_manager):
        """Test custom trail distance"""
        stop = trailing_manager.add_position(
            symbol='BTCUSDT',
            position_id='pos_001',
            entry_price=100.0,
            activation_profit=2.0,
            trail_distance=2.5  # Custom 2.5%
        )
        
        # Activate
        trailing_manager.update_position('pos_001', 103.0)
        
        # Move to 110
        trailing_manager.update_position('pos_001', 110.0)
        
        # Stop should be 2.5% below 110 = 107.25
        expected_stop = 110.0 * 0.975
        assert abs(stop.stop_price - expected_stop) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
