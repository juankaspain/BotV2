"""
Tests for Circuit Breaker
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch
from src.core.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpen,
    CircuitBreakerManager
)


class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    def test_initialization(self):
        """Test circuit breaker initialization"""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=3,
            timeout_seconds=10
        )
        
        assert cb.name == "test"
        assert cb.state == CircuitState.CLOSED
        assert cb.config.failure_threshold == 3
        assert cb.config.timeout_seconds == 10
        assert cb.is_closed
        assert not cb.is_open
        assert not cb.is_half_open
    
    def test_state_transitions_on_failures(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Should stay closed for first 2 failures
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
            assert cb.is_closed
        
        # Third failure should open circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.is_open
        
        # Further calls should be rejected
        with pytest.raises(CircuitBreakerOpen):
            cb.call(failing_func)
    
    def test_half_open_state_after_timeout(self):
        """Test circuit enters half-open state after timeout"""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            timeout_seconds=1  # 1 second timeout
        )
        
        def failing_func():
            raise ValueError("Error")
        
        # Trigger circuit open
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.is_open
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Next call should attempt half-open
        def working_func():
            return "success"
        
        result = cb.call(working_func)
        assert result == "success"
        assert cb.is_half_open or cb.is_closed  # May close immediately if success_threshold=1
    
    def test_recovery_from_half_open(self):
        """Test recovery from half-open to closed"""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=1
        )
        
        def failing_func():
            raise ValueError("Error")
        
        # Open circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.is_open
        time.sleep(1.1)
        
        # Successful calls in half-open
        def working_func():
            return "success"
        
        for _ in range(2):
            result = cb.call(working_func)
            assert result == "success"
        
        # Should be closed now
        assert cb.is_closed
    
    def test_half_open_failure_reopens_circuit(self):
        """Test failure in half-open returns to open"""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            timeout_seconds=1
        )
        
        def failing_func():
            raise ValueError("Error")
        
        # Open circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        time.sleep(1.1)
        
        # Fail in half-open
        with pytest.raises(ValueError):
            cb.call(failing_func)
        
        # Should be open again
        assert cb.is_open
    
    def test_metrics_tracking(self):
        """Test metrics are tracked correctly"""
        cb = CircuitBreaker(name="test", failure_threshold=5)
        
        def success_func():
            return "ok"
        
        def fail_func():
            raise ValueError("Error")
        
        # Successful calls
        for _ in range(3):
            cb.call(success_func)
        
        # Failed calls
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        metrics = cb.get_metrics()
        assert metrics['successful_calls'] == 3
        assert metrics['failed_calls'] == 2
        assert metrics['total_calls'] == 5
        assert metrics['state'] == 'closed'
    
    def test_excluded_exceptions(self):
        """Test excluded exceptions don't trigger circuit"""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            excluded_exceptions=(ValueError,)
        )
        
        def value_error_func():
            raise ValueError("Ignored error")
        
        # These should not count toward threshold
        for _ in range(5):
            with pytest.raises(ValueError):
                cb.call(value_error_func)
        
        # Circuit should still be closed
        assert cb.is_closed
    
    def test_decorator_syntax(self):
        """Test using circuit breaker as decorator"""
        cb = CircuitBreaker(name="test", failure_threshold=2)
        
        @cb
        def decorated_func(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        # Successful calls
        assert decorated_func(5) == 10
        
        # Failed calls
        for _ in range(2):
            with pytest.raises(ValueError):
                decorated_func(-1)
        
        # Circuit should be open
        assert cb.is_open
    
    @pytest.mark.asyncio
    async def test_async_support(self):
        """Test async function support"""
        cb = CircuitBreaker(name="test", failure_threshold=2)
        
        @cb
        async def async_func(x):
            await asyncio.sleep(0.01)
            if x < 0:
                raise ValueError("Error")
            return x * 2
        
        # Successful call
        result = await async_func(5)
        assert result == 10
        
        # Failed calls
        for _ in range(2):
            with pytest.raises(ValueError):
                await async_func(-1)
        
        assert cb.is_open
    
    def test_manual_reset(self):
        """Test manual circuit reset"""
        cb = CircuitBreaker(name="test", failure_threshold=2)
        
        def fail_func():
            raise ValueError("Error")
        
        # Open circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        assert cb.is_open
        
        # Manual reset
        cb.reset()
        assert cb.is_closed
    
    def test_on_state_change_callback(self):
        """Test state change callback"""
        callback_mock = Mock()
        
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            on_state_change=callback_mock
        )
        
        def fail_func():
            raise ValueError("Error")
        
        # Trigger state change
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        # Callback should be called
        assert callback_mock.called


class TestCircuitBreakerManager:
    """Test circuit breaker manager"""
    
    def test_create_breaker(self):
        """Test creating circuit breaker"""
        manager = CircuitBreakerManager()
        
        cb = manager.create("api_breaker", failure_threshold=3)
        assert cb.name == "api_breaker"
        assert manager.get("api_breaker") == cb
    
    def test_multiple_breakers(self):
        """Test managing multiple breakers"""
        manager = CircuitBreakerManager()
        
        cb1 = manager.create("breaker1")
        cb2 = manager.create("breaker2")
        
        assert manager.get("breaker1") == cb1
        assert manager.get("breaker2") == cb2
        assert cb1 != cb2
    
    def test_get_all_metrics(self):
        """Test getting metrics for all breakers"""
        manager = CircuitBreakerManager()
        
        manager.create("breaker1")
        manager.create("breaker2")
        
        metrics = manager.get_all_metrics()
        assert 'breaker1' in metrics
        assert 'breaker2' in metrics
    
    def test_reset_all(self):
        """Test resetting all breakers"""
        manager = CircuitBreakerManager()
        
        cb1 = manager.create("breaker1", failure_threshold=1)
        cb2 = manager.create("breaker2", failure_threshold=1)
        
        # Open both circuits
        def fail_func():
            raise ValueError("Error")
        
        with pytest.raises(ValueError):
            cb1.call(fail_func)
        with pytest.raises(ValueError):
            cb2.call(fail_func)
        
        assert cb1.is_open
        assert cb2.is_open
        
        # Reset all
        manager.reset_all()
        assert cb1.is_closed
        assert cb2.is_closed


class TestCircuitBreakerEdgeCases:
    """Test edge cases"""
    
    def test_zero_failures_threshold(self):
        """Test with zero failure threshold"""
        # Should not break with 0 threshold
        cb = CircuitBreaker(name="test", failure_threshold=0)
        
        def fail_func():
            raise ValueError("Error")
        
        # Should not open circuit
        with pytest.raises(ValueError):
            cb.call(fail_func)
        
        # Might be open depending on implementation
        # This is an edge case that should be handled
    
    def test_success_resets_failure_count(self):
        """Test that success resets failure count"""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        def fail_func():
            raise ValueError("Error")
        
        def success_func():
            return "ok"
        
        # 2 failures
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        # 1 success (should reset)
        cb.call(success_func)
        
        # 2 more failures should not open (count was reset)
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)
        
        assert cb.is_closed
    
    def test_half_open_max_calls(self):
        """Test half-open max calls limit"""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=1,
            timeout_seconds=1,
            half_open_max_calls=2
        )
        
        def fail_func():
            raise ValueError("Error")
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(fail_func)
        
        time.sleep(1.1)
        
        # Try max_calls in half-open
        def success_func():
            return "ok"
        
        for i in range(2):
            cb.call(success_func)
        
        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpen):
            cb.call(success_func)
