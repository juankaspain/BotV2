"""
Retry Handler with Exponential Backoff
Implements retry logic using tenacity library
"""

import logging
from typing import Callable, Optional, Type, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import asyncio

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Retry handler with exponential backoff
    
    Features:
    - Exponential backoff
    - Configurable max attempts
    - Exception filtering
    - Async support
    - Detailed logging
    
    Example:
        retry_handler = RetryHandler(
            max_attempts=3,
            min_wait=1,
            max_wait=10
        )
        
        @retry_handler.retry()
        def unreliable_function():
            return api.call()
    """
    
    def __init__(self,
                 max_attempts: int = 3,
                 min_wait: int = 1,
                 max_wait: int = 60,
                 retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)):
        """
        Initialize retry handler
        
        Args:
            max_attempts: Maximum retry attempts
            min_wait: Minimum wait time (seconds)
            max_wait: Maximum wait time (seconds)
            retryable_exceptions: Exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.retryable_exceptions = retryable_exceptions
        
        logger.info(
            f"✓ Retry Handler initialized "
            f"(max_attempts={max_attempts}, wait={min_wait}-{max_wait}s)"
        )
    
    def retry(self, **kwargs):
        """
        Decorator for retry logic
        
        Args:
            **kwargs: Override default retry parameters
        """
        max_attempts = kwargs.get('max_attempts', self.max_attempts)
        min_wait = kwargs.get('min_wait', self.min_wait)
        max_wait = kwargs.get('max_wait', self.max_wait)
        exceptions = kwargs.get('retryable_exceptions', self.retryable_exceptions)
        
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                min=min_wait,
                max=max_wait,
                multiplier=2
            ),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True
        )
    
    def retry_async(self, **kwargs):
        """
        Decorator for async retry logic
        
        Args:
            **kwargs: Override default retry parameters
        """
        max_attempts = kwargs.get('max_attempts', self.max_attempts)
        min_wait = kwargs.get('min_wait', self.min_wait)
        max_wait = kwargs.get('max_wait', self.max_wait)
        exceptions = kwargs.get('retryable_exceptions', self.retryable_exceptions)
        
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                min=min_wait,
                max=max_wait,
                multiplier=2
            ),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True
        )


# Global retry handler instance
retry_handler = RetryHandler()


# Convenience decorators
def retry_on_failure(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 60):
    """Convenience decorator for retry logic"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(min=min_wait, max=max_wait, multiplier=2),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


def retry_async_on_failure(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 60):
    """Convenience decorator for async retry logic"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(min=min_wait, max=max_wait, multiplier=2),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
