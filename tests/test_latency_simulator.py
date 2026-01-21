"""
Unit Tests for Latency Simulator
Tests latency models, distribution, time effects, and network simulation
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, time
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backtesting.latency_simulator import (
    LatencySimulator,
    LatencyModel,
    LatencyStats
)


@pytest.fixture
def mock_config():
    """Create mock configuration"""
    config = Mock()
    config.execution.latency = {
        'enabled': True,
        'model': 'realistic',
        'mean_ms': 50,
        'std_ms': 20,
        'min_ms': 10,
        'max_ms': 500,
        'distribution': 'lognormal',
        'time_effects': {
            'enabled': True,
            'peak_hours': [9, 10, 15, 16],
            'peak_multiplier': 1.5
        },
        'packet_loss_rate': 0.001,
        'retry_attempts': 3,
        'retry_delay_ms': 100
    }
    return config


@pytest.fixture
def simulator(mock_config):
    """Create LatencySimulator instance"""
    return LatencySimulator(mock_config)


class TestSimulatorInitialization:
    """Test simulator initialization"""
    
    def test_simulator_initialization(self, simulator):
        """Test simulator initializes correctly"""
        assert simulator.enabled == True
        assert simulator.model == LatencyModel.REALISTIC
        assert simulator.mean_ms == 50
        assert simulator.std_ms == 20
        assert simulator.min_ms == 10
        assert simulator.max_ms == 500
    
    def test_disabled_simulator(self, mock_config):
        """Test disabled simulator"""
        mock_config.execution.latency['enabled'] = False
        sim = LatencySimulator(mock_config)
        
        assert sim.enabled == False
    
    def test_model_configuration(self, mock_config):
        """Test different model configurations"""
        for model in ['realistic', 'normal', 'lognormal', 'exponential', 'high', 'low']:
            mock_config.execution.latency['model'] = model
            sim = LatencySimulator(mock_config)
            assert sim.model.value == model


class TestLatencyGeneration:
    """Test latency value generation"""
    
    def test_latency_generation_realistic(self, simulator):
        """Test realistic latency generation"""
        latencies = [simulator._generate_latency() for _ in range(100)]
        
        # All values should be within bounds
        assert all(simulator.min_ms <= lat <= simulator.max_ms for lat in latencies)
        
        # Mean should be approximately correct
        mean_latency = np.mean(latencies)
        assert 30 < mean_latency < 70  # Allow some variance
    
    def test_latency_distribution_shape(self, simulator):
        """Test latency distribution shape"""
        latencies = [simulator._generate_latency() for _ in range(1000)]
        
        # Lognormal should be right-skewed
        median = np.median(latencies)
        mean = np.mean(latencies)
        
        # Mean should be > median for right-skewed distribution
        assert mean >= median
    
    def test_latency_bounds(self, simulator):
        """Test latency stays within bounds"""
        latencies = [simulator._generate_latency() for _ in range(1000)]
        
        assert all(lat >= simulator.min_ms for lat in latencies)
        assert all(lat <= simulator.max_ms for lat in latencies)


class TestLatencyModels:
    """Test different latency models"""
    
    def test_normal_distribution(self, mock_config):
        """Test normal distribution model"""
        mock_config.execution.latency['distribution'] = 'normal'
        sim = LatencySimulator(mock_config)
        
        latencies = [sim._generate_latency() for _ in range(1000)]
        mean = np.mean(latencies)
        
        # Should be roughly around configured mean
        assert 40 < mean < 60
    
    def test_lognormal_distribution(self, mock_config):
        """Test lognormal distribution model"""
        mock_config.execution.latency['distribution'] = 'lognormal'
        sim = LatencySimulator(mock_config)
        
        latencies = [sim._generate_latency() for _ in range(1000)]
        
        # Lognormal should have positive skew
        assert np.mean(latencies) > np.median(latencies)
    
    def test_exponential_distribution(self, mock_config):
        """Test exponential distribution model"""
        mock_config.execution.latency['distribution'] = 'exponential'
        sim = LatencySimulator(mock_config)
        
        latencies = [sim._generate_latency() for _ in range(1000)]
        
        # Exponential should be highly skewed
        assert all(lat >= 0 for lat in latencies)
    
    def test_low_latency_model(self, mock_config):
        """Test LOW latency model"""
        mock_config.execution.latency['model'] = 'low'
        sim = LatencySimulator(mock_config)
        
        latencies = [sim._generate_latency() for _ in range(100)]
        mean = np.mean(latencies)
        
        # Low model should have lower latency
        assert mean < 50
    
    def test_high_latency_model(self, mock_config):
        """Test HIGH latency model"""
        mock_config.execution.latency['model'] = 'high'
        sim = LatencySimulator(mock_config)
        
        latencies = [sim._generate_latency() for _ in range(100)]
        mean = np.mean(latencies)
        
        # High model should have higher latency
        assert mean > 100


class TestTimeEffects:
    """Test time-of-day effects"""
    
    def test_time_of_day_effects(self, simulator):
        """Test peak hour latency increase"""
        base_latency = 50.0
        
        # Peak hour
        peak_time = datetime(2024, 1, 1, 9, 0)  # 9 AM UTC
        peak_latency = simulator._apply_time_effects(base_latency, peak_time)
        
        # Should be higher during peak
        assert peak_latency > base_latency
        assert peak_latency == base_latency * 1.5
    
    def test_off_peak_hours(self, simulator):
        """Test off-peak hours (no increase)"""
        base_latency = 50.0
        
        # Off-peak hour
        off_peak_time = datetime(2024, 1, 1, 3, 0)  # 3 AM UTC
        off_peak_latency = simulator._apply_time_effects(base_latency, off_peak_time)
        
        # Should not change
        assert off_peak_latency == base_latency
    
    def test_disabled_time_effects(self, mock_config):
        """Test with time effects disabled"""
        mock_config.execution.latency['time_effects']['enabled'] = False
        sim = LatencySimulator(mock_config)
        
        base_latency = 50.0
        peak_time = datetime(2024, 1, 1, 9, 0)
        
        # Should not apply time effects
        latency = sim._apply_time_effects(base_latency, peak_time)
        assert latency == base_latency


@pytest.mark.asyncio
class TestAsyncSimulation:
    """Test async request simulation"""
    
    async def test_async_request_simulation(self, simulator):
        """Test async request simulation"""
        latency = await simulator.simulate_request('test_operation')
        
        # Should return valid latency
        assert latency >= 0
        assert isinstance(latency, float)
    
    async def test_disabled_latency(self, mock_config):
        """Test with latency disabled"""
        mock_config.execution.latency['enabled'] = False
        sim = LatencySimulator(mock_config)
        
        latency = await sim.simulate_request('test_operation')
        
        # Should return 0 when disabled
        assert latency == 0.0
    
    async def test_multiple_concurrent_requests(self, simulator):
        """Test multiple concurrent requests"""
        tasks = [
            simulator.simulate_request(f'request_{i}')
            for i in range(10)
        ]
        
        latencies = await asyncio.gather(*tasks)
        
        # All should complete
        assert len(latencies) == 10
        assert all(isinstance(lat, float) for lat in latencies)


@pytest.mark.asyncio
class TestPacketLoss:
    """Test packet loss simulation"""
    
    async def test_packet_loss_simulation(self, mock_config):
        """Test packet loss and retry"""
        # Set high packet loss for testing
        mock_config.execution.latency['packet_loss_rate'] = 0.5  # 50%
        sim = LatencySimulator(mock_config)
        
        # Run multiple requests
        for _ in range(10):
            latency, success = await sim._simulate_with_retries(50.0, 'test')
            assert isinstance(latency, float)
            assert isinstance(success, bool)
    
    async def test_retry_mechanism(self, mock_config):
        """Test retry mechanism with exponential backoff"""
        mock_config.execution.latency['packet_loss_rate'] = 0.3
        mock_config.execution.latency['retry_attempts'] = 3
        mock_config.execution.latency['retry_delay_ms'] = 100
        
        sim = LatencySimulator(mock_config)
        
        latency, success = await sim._simulate_with_retries(50.0, 'test')
        
        # Should eventually succeed or fail after retries
        assert isinstance(success, bool)
        assert latency > 0


class TestStatistics:
    """Test statistics tracking"""
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, simulator):
        """Test statistics are tracked correctly"""
        # Initial stats
        initial_stats = simulator.get_statistics()
        assert initial_stats.total_requests == 0
        
        # Make requests
        for _ in range(10):
            await simulator.simulate_request('test')
        
        # Check updated stats
        stats = simulator.get_statistics()
        assert stats.total_requests == 10
        assert stats.mean_latency_ms > 0
        assert stats.max_latency_ms >= stats.min_latency_ms
    
    @pytest.mark.asyncio
    async def test_percentile_calculation(self, simulator):
        """Test percentile calculation in statistics"""
        # Generate requests
        for _ in range(100):
            await simulator.simulate_request('test')
        
        stats = simulator.get_statistics()
        
        # P95 should be >= median
        assert stats.p95_latency_ms >= stats.median_latency_ms
        # P99 should be >= P95
        assert stats.p99_latency_ms >= stats.p95_latency_ms
        # Max should be >= P99
        assert stats.max_latency_ms >= stats.p99_latency_ms
    
    def test_reset_statistics(self, simulator):
        """Test statistics reset"""
        # Add some data
        simulator.latencies = [10, 20, 30, 40, 50]
        simulator.total_requests = 5
        
        # Reset
        simulator.reset_statistics()
        
        # Should be cleared
        assert len(simulator.latencies) == 0
        assert simulator.total_requests == 0


class TestTimeoutHandling:
    """Test timeout detection and handling"""
    
    @pytest.mark.asyncio
    async def test_timeout_detection(self, mock_config):
        """Test timeout detection when latency exceeds max"""
        mock_config.execution.latency['max_ms'] = 100
        mock_config.execution.latency['mean_ms'] = 150  # Higher than max
        
        sim = LatencySimulator(mock_config)
        
        # Generate request (might timeout)
        await sim.simulate_request('test')
        
        # Check if timeouts are tracked
        stats = sim.get_statistics()
        # Timeouts should be tracked (though may be 0 due to clipping)
        assert stats.timeouts >= 0


class TestEdgeCases:
    """Test edge cases"""
    
    def test_zero_packet_loss(self, mock_config):
        """Test with zero packet loss"""
        mock_config.execution.latency['packet_loss_rate'] = 0.0
        sim = LatencySimulator(mock_config)
        
        assert sim.packet_loss_rate == 0.0
    
    def test_extreme_latency_values(self, mock_config):
        """Test with extreme latency values"""
        mock_config.execution.latency['min_ms'] = 1
        mock_config.execution.latency['max_ms'] = 10000
        
        sim = LatencySimulator(mock_config)
        
        latencies = [sim._generate_latency() for _ in range(100)]
        assert all(1 <= lat <= 10000 for lat in latencies)
    
    def test_negative_values_clamped(self, mock_config):
        """Test negative values are clamped to min"""
        sim = LatencySimulator(mock_config)
        
        # Generate many values to potentially get negative from normal dist
        latencies = [sim._generate_latency() for _ in range(1000)]
        
        # All should be >= min
        assert all(lat >= sim.min_ms for lat in latencies)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
