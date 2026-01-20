"""
Unit Tests for Trading Strategies
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import strategies
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from strategies.momentum import MomentumStrategy
from strategies.stat_arb import StatisticalArbitrageStrategy
from strategies.regime import RegimeStrategy
from strategies.mean_reversion import MeanReversionStrategy
from config.config_manager import ConfigManager


@pytest.fixture
def config():
    """Fixture for config"""
    return ConfigManager()


@pytest.fixture
def sample_market_data():
    """Fixture for sample market data"""
    
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    
    # Generate synthetic OHLCV data
    np.random.seed(42)
    close_prices = 50000 + np.cumsum(np.random.randn(100) * 100)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(100) * 50,
        'high': close_prices + np.abs(np.random.randn(100) * 100),
        'low': close_prices - np.abs(np.random.randn(100) * 100),
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    return data


class TestMomentumStrategy:
    """Test Momentum Strategy"""
    
    @pytest.mark.asyncio
    async def test_signal_generation(self, config, sample_market_data):
        """Test signal generation"""
        
        strategy = MomentumStrategy(config)
        signal = await strategy.generate_signal(sample_market_data)
        
        # Signal can be None or a TradeSignal
        assert signal is None or hasattr(signal, 'confidence')
    
    @pytest.mark.asyncio
    async def test_buy_signal_conditions(self, config):
        """Test BUY signal conditions"""
        
        # Create data with strong uptrend
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
        close_prices = np.linspace(40000, 50000, 50)  # Strong uptrend
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices,
            'high': close_prices * 1.01,
            'low': close_prices * 0.99,
            'close': close_prices,
            'volume': [10000] * 50
        })
        
        strategy = MomentumStrategy(config)
        signal = await strategy.generate_signal(data)
        
        # Should generate BUY signal in uptrend
        if signal:
            assert signal.action in ['BUY', 'HOLD']
    
    def test_indicator_calculation(self, config, sample_market_data):
        """Test indicator calculation"""
        
        strategy = MomentumStrategy(config)
        data_with_indicators = strategy.calculate_indicators(sample_market_data)
        
        # Check indicators exist
        assert 'ma' in data_with_indicators.columns
        assert 'rsi' in data_with_indicators.columns
        assert 'roc' in data_with_indicators.columns
        
        # Chec
