"""
Ensemble Module for BotV2

Provides ensemble methods for combining multiple strategies.
Uses safe imports to avoid startup failures.
"""

import logging

logger = logging.getLogger(__name__)

__all__ = []

# Adaptive Allocation
try:
    from .adaptive_allocation import AdaptiveAllocationEngine
    # Also export as AdaptiveAllocation for backward compatibility
    AdaptiveAllocation = AdaptiveAllocationEngine
    __all__.extend(['AdaptiveAllocationEngine', 'AdaptiveAllocation'])
except ImportError as e:
    logger.warning(f"Could not import adaptive_allocation: {e}")
    AdaptiveAllocationEngine = None
    AdaptiveAllocation = None

# Correlation Manager
try:
    from .correlation_manager import CorrelationManager
    __all__.append('CorrelationManager')
except ImportError as e:
    logger.warning(f"Could not import correlation_manager: {e}")
    CorrelationManager = None

# Ensemble Voting
try:
    from .ensemble_voting import EnsembleVoting
    __all__.append('EnsembleVoting')
except ImportError as e:
    logger.warning(f"Could not import ensemble_voting: {e}")
    EnsembleVoting = None
