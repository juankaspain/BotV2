"""
Circuit Breaker Pattern Implementation
Prevents cascading failures and provides automatic recovery

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failures detected, requests blocked
- HALF_OPEN: Testing recovery, limited requests allowed
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional, Any, Dict
from dataclasses import dataclass, field
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Blocking requests
    HALF_OPEN = "half_open"    # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5           # Failures to open circuit
    success_threshold: int = 2           # Successes to close from half-open
    timeout_seconds: int = 60            # Time before trying half-open
    half_open_max_calls: int = 3         # Max calls in half-open state
    excluded_exceptions: tuple = ()      # Exceptions to ignore
    

@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.now)
    state_durations: Dict[str, float] = field(default_factory=dict)


class CircuitBreaker:
    """
    Circuit Breaker implementation with automatic recovery
    
    Features:
    - Automatic failure detection
    - Half-open state for recovery testing
    - Configurable thresholds and timeouts
    - Metrics tracking
    - Async support
    - Exception filtering
    
    Example:
        circuit = CircuitBreaker(
            name="exchange_api",
            failure_threshold=5,
            timeout_seconds=60
        )
        
        @circuit
        def call_api():
            return exchange.get_ticker("BTCUSDT")
    """
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 success_threshold: int = 2,
                 timeout_seconds: int = 60,
                 half_open_max_calls: int = 3,
                 excluded_exceptions: tuple = (),
                 on_state_change: Optional[Callable] = None):
        """
        Initialize circuit breaker
        
        Args:
            name: Circuit breaker name
            failure_threshold: Failures to open circuit
            success_threshold: Successes to close from half-open
            timeout_seconds: Time before trying half-open
            half_open_max_calls: Max calls in half-open
            excluded_exceptions: Exceptions to ignore
            on_state_change: Callback on state change
        """
        self.name = name
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
            half_open_max_calls=half_open_max_calls,
            excluded_exceptions=excluded_exceptions
        )
        
        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._opened_at = None
        self._half_open_calls = 0
        
        # Metrics
        self.metrics = CircuitBreakerMetrics()
        
        # Callbacks
        self._on_state_change = on_state_change
        
        logger.info(
            f"✓ Circuit Breaker '{name}' initialized "
            f"(threshold={failure_threshold}, timeout={timeout_seconds}s)"
        )
    
    @property
    def state(self) -> CircuitState:
        """Get current state"""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed"""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open"""
        return self._state == CircuitState.HALF_OPEN
    
    def _change_state(self, new_state: CircuitState, reason: str = ""):
        """Change circuit state"""
        if new_state == self._state:
            return
        
        old_state = self._state
        self._state = new_state
        
        # Track state duration
        now = datetime.now()
        if old_state:
            duration = (now - self.metrics.last_state_change).total_seconds()
            state_key = old_state.value
            self.metrics.state_durations[state_key] = \
                self.metrics.state_durations.get(state_key, 0) + duration
        
        self.metrics.last_state_change = now
        
        # State-specific actions
        if new_state == CircuitState.OPEN:
            self._opened_at = time.time()
            self._half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        
        logger.warning(
            f"⚠️ Circuit Breaker '{self.name}': {old_state.value} → {new_state.value}"
            + (f" ({reason})" if reason else "")
        )
        
        # Callback
        if self._on_state_change:
            try:
                self._on_state_change(self.name, old_state, new_state, reason)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    def _should_attempt_reset(self) -> bool:
        """Check if should try half-open state"""
        if not self.is_open:
            return False
        
        if self._opened_at is None:
            return False
        
        elapsed = time.time() - self._opened_at
        return elapsed >= self.config.timeout_seconds
    
    def _on_success(self):
        """Handle successful call"""
        self.metrics.successful_calls += 1
        
        if self.is_half_open:
            self._success_count += 1
            self._half_open_calls += 1
            
            logger.info(
                f"Circuit Breaker '{self.name}': Success in HALF_OPEN "
                f"({self._success_count}/{self.config.success_threshold})"
            )
            
            if self._success_count >= self.config.success_threshold:
                self._change_state(
                    CircuitState.CLOSED,
                    f"Recovered after {self._success_count} successes"
                )
        
        elif self.is_closed:
            # Reset failure count on success
            if self._failure_count > 0:
                self._failure_count = 0
    
    def _on_failure(self, exception: Exception):
        """Handle failed call"""
        # Check if exception should be ignored
        if isinstance(exception, self.config.excluded_exceptions):
            logger.debug(f"Ignoring excluded exception: {type(exception).__name__}")
            return
        
        self.metrics.failed_calls += 1
        self.metrics.last_failure_time = datetime.now()
        self._last_failure_time = time.time()
        
        if self.is_half_open:
            # Failure in half-open → back to open
            self._change_state(
                CircuitState.OPEN,
                f"Failed during recovery test: {type(exception).__name__}"
            )
        
        elif self.is_closed:
            self._failure_count += 1
            
            logger.warning(
                f"Circuit Breaker '{self.name}': Failure {self._failure_count}/"
                f"{self.config.failure_threshold} - {type(exception).__name__}"
            )
            
            if self._failure_count >= self.config.failure_threshold:
                self._change_state(
                    CircuitState.OPEN,
                    f"Threshold reached ({self._failure_count} failures)"
                )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        self.metrics.total_calls += 1
        
        # Check if should try recovery
        if self._should_attempt_reset():
            self._change_state(CircuitState.HALF_OPEN, "Testing recovery")
        
        # Block if open
        if self.is_open:
            self.metrics.rejected_calls += 1
            raise CircuitBreakerOpen(
                f"Circuit breaker '{self.name}' is OPEN "
                f"(will retry in {self.config.timeout_seconds}s)"
            )
        
        # Limit calls in half-open
        if self.is_half_open:
            if self._half_open_calls >= self.config.half_open_max_calls:
                self.metrics.rejected_calls += 1
                raise CircuitBreakerOpen(
                    f"Circuit breaker '{self.name}' HALF_OPEN max calls reached"
                )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure(e)
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        self.metrics.total_calls += 1
        
        # Check if should try recovery
        if self._should_attempt_reset():
            self._change_state(CircuitState.HALF_OPEN, "Testing recovery")
        
        # Block if open
        if self.is_open:
            self.metrics.rejected_calls += 1
            raise CircuitBreakerOpen(
                f"Circuit breaker '{self.name}' is OPEN"
            )
        
        # Limit calls in half-open
        if self.is_half_open:
            if self._half_open_calls >= self.config.half_open_max_calls:
                self.metrics.rejected_calls += 1
                raise CircuitBreakerOpen(
                    f"Circuit breaker '{self.name}' HALF_OPEN max calls reached"
                )
        
        # Execute async function
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure(e)
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker"""
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.call_async(func, *args, **kwargs)
            return async_wrapper
        
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.call(func, *args, **kwargs)
            return wrapper
    
    def reset(self):
        """Manually reset circuit breaker"""
        logger.info(f"Manually resetting circuit breaker '{self.name}'")
        self._change_state(CircuitState.CLOSED, "Manual reset")
        self._failure_count = 0
        self._success_count = 0
    
    def get_metrics(self) -> Dict:
        """Get circuit breaker metrics"""
        return {
            'name': self.name,
            'state': self._state.value,
            'total_calls': self.metrics.total_calls,
            'successful_calls': self.metrics.successful_calls,
            'failed_calls': self.metrics.failed_calls,
            'rejected_calls': self.metrics.rejected_calls,
            'failure_count': self._failure_count,
            'success_count': self._success_count,
            'last_failure_time': self.metrics.last_failure_time.isoformat() 
                if self.metrics.last_failure_time else None,
            'state_durations': self.metrics.state_durations,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'success_threshold': self.config.success_threshold,
                'timeout_seconds': self.config.timeout_seconds
            }
        }


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreakerManager:
    """Manages multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        logger.info("✓ Circuit Breaker Manager initialized")
    
    def create(self, name: str, **kwargs) -> CircuitBreaker:
        """Create new circuit breaker"""
        if name in self.breakers:
            logger.warning(f"Circuit breaker '{name}' already exists")
            return self.breakers[name]
        
        breaker = CircuitBreaker(name=name, **kwargs)
        self.breakers[name] = breaker
        return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.breakers.get(name)
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """Get metrics for all circuit breakers"""
        return {
            name: breaker.get_metrics()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
