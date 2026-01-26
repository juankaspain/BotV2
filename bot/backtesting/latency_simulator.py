"""
Latency Simulator
Realistic network latency simulation for backtesting and testing
Models: Normal, Lognormal, Exponential distributions
Features: Time-of-day effects, packet loss, retries
"""

import logging
import numpy as np
import asyncio
from datetime import datetime, time
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class LatencyModel(Enum):
    """Latency distribution models"""
    REALISTIC = "realistic"      # Lognormal (most realistic)
    NORMAL = "normal"            # Normal distribution
    LOGNORMAL = "lognormal"      # Lognormal distribution
    EXPONENTIAL = "exponential"  # Exponential distribution
    HIGH = "high"                # High latency scenario
    LOW = "low"                  # Low latency scenario


@dataclass
class LatencyStats:
    """Latency statistics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    timeouts: int
    retries: int
    packet_losses: int
    
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    min_latency_ms: float


class LatencySimulator:
    """
    Simulates realistic network latency for backtesting
    
    Features:
    - Multiple distribution models
    - Time-of-day effects (higher latency during market open/close)
    - Packet loss simulation
    - Automatic retries with exponential backoff
    - Timeout handling
    - Statistics tracking
    """
    
    def __init__(self, config):
        """
        Initialize latency simulator
        
        Args:
            config: Configuration object with latency settings
        """
        self.config = config
        
        # Get latency configuration
        lat_config = config.execution.latency
        
        self.enabled = lat_config.get('enabled', True)
        self.model = LatencyModel(lat_config.get('model', 'realistic'))
        
        # Latency parameters (milliseconds)
        self.mean_ms = lat_config.get('mean_ms', 50)
        self.std_ms = lat_config.get('std_ms', 20)
        self.min_ms = lat_config.get('min_ms', 10)
        self.max_ms = lat_config.get('max_ms', 500)
        
        # Distribution type
        self.distribution = lat_config.get('distribution', 'lognormal')
        
        # Time-of-day effects
        time_effects = lat_config.get('time_effects', {})
        self.time_effects_enabled = time_effects.get('enabled', True)
        self.peak_hours = time_effects.get('peak_hours', [9, 10, 15, 16])  # UTC
        self.peak_multiplier = time_effects.get('peak_multiplier', 1.5)
        
        # Network quality
        self.packet_loss_rate = lat_config.get('packet_loss_rate', 0.001)  # 0.1%
        self.retry_attempts = lat_config.get('retry_attempts', 3)
        self.retry_delay_ms = lat_config.get('retry_delay_ms', 100)
        
        # Statistics
        self.latencies: List[float] = []
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeouts = 0
        self.retries_count = 0
        self.packet_losses = 0
        
        # Adjust parameters based on model
        self._configure_model()
        
        logger.info(
            f"✓ Latency Simulator initialized "
            f"(model={self.model.value}, mean={self.mean_ms}ms, "
            f"enabled={self.enabled})"
        )
    
    def _configure_model(self):
        """Configure parameters based on selected model"""
        
        if self.model == LatencyModel.LOW:
            self.mean_ms = 20
            self.std_ms = 5
            self.min_ms = 5
            self.max_ms = 100
            
        elif self.model == LatencyModel.HIGH:
            self.mean_ms = 150
            self.std_ms = 50
            self.min_ms = 50
            self.max_ms = 1000
            
        elif self.model == LatencyModel.REALISTIC:
            # Use lognormal for realistic scenario
            self.distribution = 'lognormal'
            self.mean_ms = 50
            self.std_ms = 20
    
    async def simulate_request(self, 
                              operation: str = "api_call",
                              timestamp: Optional[datetime] = None) -> float:
        """
        Simulate a network request with latency
        
        Args:
            operation: Type of operation (for logging)
            timestamp: Timestamp for time-of-day effects
            
        Returns:
            Actual latency experienced (ms)
        """
        
        if not self.enabled:
            return 0.0
        
        self.total_requests += 1
        timestamp = timestamp or datetime.now()
        
        # Generate base latency
        base_latency = self._generate_latency()
        
        # Apply time-of-day effects
        if self.time_effects_enabled:
            base_latency = self._apply_time_effects(base_latency, timestamp)
        
        # Simulate packet loss and retries
        actual_latency, success = await self._simulate_with_retries(
            base_latency, 
            operation
        )
        
        # Record statistics
        self.latencies.append(actual_latency)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Check timeout
        if actual_latency > self.max_ms:
            self.timeouts += 1
            logger.warning(
                f"⚠️ Request timeout: {operation} took {actual_latency:.1f}ms "
                f"(max={self.max_ms}ms)"
            )
        
        return actual_latency
    
    def _generate_latency(self) -> float:
        """
        Generate latency value based on distribution
        
        Returns:
            Latency in milliseconds
        """
        
        if self.distribution == 'normal':
            # Normal distribution
            latency = np.random.normal(self.mean_ms, self.std_ms)
            
        elif self.distribution == 'lognormal':
            # Lognormal distribution (most realistic for network latency)
            # Parameters for lognormal to match desired mean/std
            sigma = np.sqrt(np.log(1 + (self.std_ms / self.mean_ms) ** 2))
            mu = np.log(self.mean_ms) - sigma ** 2 / 2
            latency = np.random.lognormal(mu, sigma)
            
        elif self.distribution == 'exponential':
            # Exponential distribution
            latency = np.random.exponential(self.mean_ms)
            
        else:
            # Default to normal
            latency = np.random.normal(self.mean_ms, self.std_ms)
        
        # Clip to valid range
        latency = np.clip(latency, self.min_ms, self.max_ms)
        
        return latency
    
    def _apply_time_effects(self, latency: float, timestamp: datetime) -> float:
        """
        Apply time-of-day effects (higher latency during peak hours)
        
        Args:
            latency: Base latency
            timestamp: Current timestamp
            
        Returns:
            Adjusted latency
        """
        
        hour = timestamp.hour
        
        # Check if in peak hours
        if hour in self.peak_hours:
            latency *= self.peak_multiplier
            logger.debug(
                f"Peak hour latency: {latency:.1f}ms "
                f"(hour={hour}, multiplier={self.peak_multiplier})"
            )
        
        return latency
    
    async def _simulate_with_retries(self, 
                                    base_latency: float,
                                    operation: str) -> tuple[float, bool]:
        """
        Simulate request with packet loss and retries
        
        Args:
            base_latency: Base latency value
            operation: Operation name
            
        Returns:
            Tuple of (actual_latency, success)
        """
        
        total_latency = 0.0
        attempts = 0
        
        for attempt in range(self.retry_attempts):
            attempts += 1
            
            # Simulate the request delay
            await asyncio.sleep(base_latency / 1000)  # Convert ms to seconds
            total_latency += base_latency
            
            # Check for packet loss
            if np.random.random() < self.packet_loss_rate:
                self.packet_losses += 1
                
                if attempt < self.retry_attempts - 1:
                    # Retry with exponential backoff
                    self.retries_count += 1
                    retry_delay = self.retry_delay_ms * (2 ** attempt)
                    
                    logger.debug(
                        f"Packet loss on {operation}, retry {attempt + 1}/{self.retry_attempts} "
                        f"after {retry_delay}ms"
                    )
                    
                    await asyncio.sleep(retry_delay / 1000)
                    total_latency += retry_delay
                    
                    # Generate new latency for retry
                    base_latency = self._generate_latency()
                else:
                    # Final attempt failed
                    logger.error(
                        f"❌ Request failed after {attempts} attempts: {operation}"
                    )
                    return total_latency, False
            else:
                # Success
                return total_latency, True
        
        return total_latency, False
    
    def get_statistics(self) -> LatencyStats:
        """
        Get latency statistics
        
        Returns:
            LatencyStats object
        """
        
        if len(self.latencies) == 0:
            return LatencyStats(
                total_requests=self.total_requests,
                successful_requests=self.successful_requests,
                failed_requests=self.failed_requests,
                timeouts=self.timeouts,
                retries=self.retries_count,
                packet_losses=self.packet_losses,
                mean_latency_ms=0,
                median_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                max_latency_ms=0,
                min_latency_ms=0
            )
        
        latencies_array = np.array(self.latencies)
        
        return LatencyStats(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            timeouts=self.timeouts,
            retries=self.retries_count,
            packet_losses=self.packet_losses,
            mean_latency_ms=float(np.mean(latencies_array)),
            median_latency_ms=float(np.median(latencies_array)),
            p95_latency_ms=float(np.percentile(latencies_array, 95)),
            p99_latency_ms=float(np.percentile(latencies_array, 99)),
            max_latency_ms=float(np.max(latencies_array)),
            min_latency_ms=float(np.min(latencies_array))
        )
    
    def print_statistics(self):
        """Print latency statistics"""
        
        stats = self.get_statistics()
        
        logger.info("\n" + "=" * 60)
        logger.info("LATENCY STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total Requests:      {stats.total_requests}")
        logger.info(f"Successful:          {stats.successful_requests}")
        logger.info(f"Failed:              {stats.failed_requests}")
        logger.info(f"Timeouts:            {stats.timeouts}")
        logger.info(f"Retries:             {stats.retries}")
        logger.info(f"Packet Losses:       {stats.packet_losses}")
        logger.info("-" * 60)
        logger.info(f"Mean Latency:        {stats.mean_latency_ms:.2f}ms")
        logger.info(f"Median Latency:      {stats.median_latency_ms:.2f}ms")
        logger.info(f"P95 Latency:         {stats.p95_latency_ms:.2f}ms")
        logger.info(f"P99 Latency:         {stats.p99_latency_ms:.2f}ms")
        logger.info(f"Min Latency:         {stats.min_latency_ms:.2f}ms")
        logger.info(f"Max Latency:         {stats.max_latency_ms:.2f}ms")
        logger.info("=" * 60)
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.latencies.clear()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeouts = 0
        self.retries_count = 0
        self.packet_losses = 0
        
        logger.info("✓ Latency statistics reset")
