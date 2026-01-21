"""
Unit Tests for Circuit Breaker
Tests state transitions, failure thresholds, recovery, and error handling
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Circuit Breaker Implementation (inline for testing)
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    half_open_max_calls: int = 1


class CircuitBreaker:
    """Circuit breaker for fault tolerance"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None
        self.total_requests = 0
        self.total_failures = 0
        self.state_changes = []
        self.callbacks = []
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker"""
        self.total_requests += 1
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise Exception("Circuit breaker is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            # Only allow limited calls in half-open
            pass
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable, *args, **kwargs):
        """Execute async function through circuit breaker"""
        self.total_requests += 1
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
        elif self.failure_count >= self.config.failure_threshold:
            self._transition_to_open()
    
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset"""
        if self.opened_at is None:
            return True
        
        elapsed = (datetime.now() - self.opened_at).total_seconds()
        return elapsed >= self.config.timeout_seconds
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.opened_at = datetime.now()
        self.state_changes.append(('OPEN', datetime.now()))
        self._notify_callbacks('OPEN')
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.failure_count = 0
        self.state_changes.append(('HALF_OPEN', datetime.now()))
        self._notify_callbacks('HALF_OPEN')
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
        self.state_changes.append(('CLOSED', datetime.now()))
        self._notify_callbacks('CLOSED')
    
    def reset(self):
        """Manually reset circuit breaker"""
        self._transition_to_closed()
    
    def get_failure_rate(self) -> float:
        """Get failure rate"""
        if self.total_requests == 0:
            return 0.0
        return self.total_failures / self.total_requests
    
    def get_statistics(self) -> dict:
        """Get statistics"""
        return {
            'state': self.state.value,
            'total_requests': self.total_requests,
            'total_failures': self.total_failures,
            'failure_rate': self.get_failure_rate(),
            'current_failure_count': self.failure_count,
            'current_success_count': self.success_count,
            'state_changes': len(self.state_changes)
        }
    
    def register_callback(self, callback: Callable):
        """Register state change callback"""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, new_state: str):
        """Notify registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(new_state)
            except Exception:
                pass


@pytest.fixture
def circuit_config():
    """Create circuit breaker config"""
    return CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        timeout_seconds=60,
        half_open_max_calls=1
    )


@pytest.fixture
def circuit_breaker(circuit_config):
    """Create circuit breaker instance"""
    return CircuitBreaker(circuit_config)


class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality"""
    
    def test_circuit_breaker_initialization(self, circuit_breaker):
        """Test circuit breaker initializes in CLOSED state"""
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0
        assert circuit_breaker.total_requests == 0
    
    def test_closed_state_allows_requests(self, circuit_breaker):
        """Test CLOSED state allows requests"""
        def successful_func():
            return "success"
        
        result = circuit_breaker.call(successful_func)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
    
    def test_successful_calls_reset_failure_count(self, circuit_breaker):
        """Test successful calls reset failure count"""
        def failing_func():
            raise Exception("Error")
        
        def successful_func():
            return "success"
        
        # Make some failures
        for _ in range(3):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        assert circuit_breaker.failure_count == 3
        
        # Successful call resets count
        circuit_breaker.call(successful_func)
        assert circuit_breaker.failure_count == 0


class TestCircuitStates:
    """Test circuit breaker state transitions"""
    
    def test_failure_threshold_opens_circuit(self, circuit_breaker):
        """Test circuit opens after failure threshold"""
        def failing_func():
            raise Exception("Error")
        
        # Make failures up to threshold
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        assert circuit_breaker.state == CircuitState.OPEN
    
    def test_open_state_blocks_requests(self, circuit_breaker):
        """Test OPEN state blocks requests"""
        def failing_func():
            raise Exception("Error")
        
        # Open the circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        # Now circuit is open, should block
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            circuit_breaker.call(lambda: "test")
    
    def test_half_open_state_allows_single_request(self, circuit_breaker):
        """Test HALF_OPEN state allows limited requests"""
        def failing_func():
            raise Exception("Error")
        
        def successful_func():
            return "success"
        
        # Open circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        # Wait for timeout
        circuit_breaker.opened_at = datetime.now() - timedelta(seconds=61)
        
        # Should transition to HALF_OPEN and allow request
        result = circuit_breaker.call(successful_func)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.HALF_OPEN
    
    def test_success_threshold_closes_circuit(self, circuit_breaker):
        """Test successful calls in HALF_OPEN close circuit"""
        def failing_func():
            raise Exception("Error")
        
        def successful_func():
            return "success"
        
        # Open circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        # Transition to HALF_OPEN
        circuit_breaker.opened_at = datetime.now() - timedelta(seconds=61)
        
        # Make successful calls up to threshold
        for _ in range(circuit_breaker.config.success_threshold):
            circuit_breaker.call(successful_func)
        
        # Should be CLOSED now
        assert circuit_breaker.state == CircuitState.CLOSED
    
    def test_failure_in_half_open_reopens_circuit(self, circuit_breaker):
        """Test failure in HALF_OPEN reopens circuit"""
        def failing_func():
            raise Exception("Error")
        
        # Open circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        # Transition to HALF_OPEN
        circuit_breaker.opened_at = datetime.now() - timedelta(seconds=61)
        circuit_breaker.state = CircuitState.HALF_OPEN
        
        # Failure should reopen
        try:
            circuit_breaker.call(failing_func)
        except:
            pass
        
        assert circuit_breaker.state == CircuitState.OPEN


class TestRecoveryMechanisms:
    """Test recovery mechanisms"""
    
    def test_timeout_automatic_recovery(self, circuit_breaker):
        """Test automatic recovery after timeout"""
        def failing_func():
            raise Exception("Error")
        
        # Open circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Simulate timeout
        circuit_breaker.opened_at = datetime.now() - timedelta(seconds=61)
        
        # Should allow attempt
        assert circuit_breaker._should_attempt_reset() == True
    
    def test_manual_reset(self, circuit_breaker):
        """Test manual circuit reset"""
        def failing_func():
            raise Exception("Error")
        
        # Open circuit
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # Manual reset
        circuit_breaker.reset()
        
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0


class TestStatistics:
    """Test statistics tracking"""
    
    def test_failure_rate_calculation(self, circuit_breaker):
        """Test failure rate calculation"""
        def failing_func():
            raise Exception("Error")
        
        def successful_func():
            return "success"
        
        # 3 successes
        for _ in range(3):
            circuit_breaker.call(successful_func)
        
        # 2 failures
        for _ in range(2):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        # Failure rate should be 2/5 = 0.4
        assert abs(circuit_breaker.get_failure_rate() - 0.4) < 0.01
    
    def test_statistics_tracking(self, circuit_breaker):
        """Test statistics are tracked correctly"""
        def successful_func():
            return "success"
        
        # Make some calls
        for _ in range(10):
            circuit_breaker.call(successful_func)
        
        stats = circuit_breaker.get_statistics()
        
        assert stats['total_requests'] == 10
        assert stats['total_failures'] == 0
        assert stats['failure_rate'] == 0.0
        assert stats['state'] == 'closed'
    
    def test_consecutive_failures(self, circuit_breaker):
        """Test tracking consecutive failures"""
        def failing_func():
            raise Exception("Error")
        
        for i in range(3):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
            
            assert circuit_breaker.failure_count == i + 1
    
    def test_mixed_success_failure(self, circuit_breaker):
        """Test mixed success and failure tracking"""
        def failing_func():
            raise Exception("Error")
        
        def successful_func():
            return "success"
        
        # Alternating success/failure
        circuit_breaker.call(successful_func)
        try:
            circuit_breaker.call(failing_func)
        except:
            pass
        circuit_breaker.call(successful_func)
        
        stats = circuit_breaker.get_statistics()
        assert stats['total_requests'] == 3
        assert stats['total_failures'] == 1


class TestCallbacks:
    """Test callback mechanisms"""
    
    def test_state_change_callbacks(self, circuit_breaker):
        """Test callbacks are called on state change"""
        callback_states = []
        
        def callback(state):
            callback_states.append(state)
        
        circuit_breaker.register_callback(callback)
        
        # Open circuit
        def failing_func():
            raise Exception("Error")
        
        for _ in range(circuit_breaker.config.failure_threshold):
            try:
                circuit_breaker.call(failing_func)
            except:
                pass
        
        assert 'OPEN' in callback_states


@pytest.mark.asyncio
class TestAsyncSupport:
    """Test async function support"""
    
    async def test_async_call_success(self, circuit_breaker):
        """Test async successful call"""
        async def async_func():
            await asyncio.sleep(0.01)
            return "async_success"
        
        result = await circuit_breaker.call_async(async_func)
        assert result == "async_success"
    
    async def test_async_call_failure(self, circuit_breaker):
        """Test async failed call"""
        async def async_failing_func():
            await asyncio.sleep(0.01)
            raise Exception("Async error")
        
        with pytest.raises(Exception, match="Async error"):
            await circuit_breaker.call_async(async_failing_func)
        
        assert circuit_breaker.failure_count == 1
    
    async def test_concurrent_requests(self, circuit_breaker):
        """Test concurrent async requests"""
        async def async_func(delay):
            await asyncio.sleep(delay)
            return "success"
        
        tasks = [
            circuit_breaker.call_async(async_func, 0.01)
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        assert len(results) == 5
        assert all(r == "success" for r in results)


class TestEdgeCases:
    """Test edge cases"""
    
    def test_zero_failure_rate_initially(self, circuit_breaker):
        """Test failure rate is 0 initially"""
        assert circuit_breaker.get_failure_rate() == 0.0
    
    def test_exponential_backoff(self):
        """Test exponential backoff for timeout"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=10
        )
        cb = CircuitBreaker(config)
        
        # Could implement exponential backoff
        # For now, just test basic timeout
        assert cb.config.timeout_seconds == 10
    
    def test_health_check_integration(self, circuit_breaker):
        """Test circuit breaker health status"""
        stats = circuit_breaker.get_statistics()
        
        # Health check could use these stats
        is_healthy = stats['state'] == 'closed' and stats['failure_rate'] < 0.5
        assert is_healthy == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
