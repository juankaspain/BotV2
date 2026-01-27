"""
Ensemble Module for BotV2

Provides ensemble methods for combining multiple strategies.
"""

from .adaptive_allocation import AdaptiveAllocation
from .correlation_manager import CorrelationManager
from .ensemble_voting import EnsembleVoting

__all__ = [
    'AdaptiveAllocation',
    'CorrelationManager',
    'EnsembleVoting',
]
