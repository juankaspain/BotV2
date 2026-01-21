"""
Ensemble Voting System
Combines signals from multiple strategies into final trading decision
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TradeSignal:
    """Trade signal from a strategy"""
    strategy: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0-1
    symbol: str
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Optional[Dict] = None


class EnsembleVoting:
    """
    Ensemble voting mechanism for strategy aggregation
    
    Methods:
    - Weighted average (default)
    - Majority voting
    - Confidence-weighted blend
    """
    
    def __init__(self,
                 method: str = "weighted_average",
                 confidence_threshold: float = 0.5,
                 min_strategies_agree: int = 3):
        """
        Args:
            method: Voting method (weighted_average, majority, blend)
            confidence_threshold: Minimum confidence for final signal
            min_strategies_agree: Minimum strategies that must agree
        """
        self.method = method
        self.confidence_threshold = confidence_threshold
        self.min_strategies_agree = min_strategies_agree
        
        # Voting history
        self.voting_history = []
        
        logger.info(
            f"✓ Ensemble Voting initialized "
            f"(method={method}, threshold={confidence_threshold:.0%})"
        )
    
    def vote(self,
             signals: Dict[str, TradeSignal],
             weights: Dict[str, float]) -> Optional[TradeSignal]:
        """
        Aggregate strategy signals into final decision
        
        Args:
            signals: Dict mapping strategy name to TradeSignal
            weights: Dict mapping strategy name to allocation weight
            
        Returns:
            Final ensemble TradeSignal or None if no consensus
        """
        
        if not signals:
            logger.debug("No signals to vote on")
            return None
        
        # Filter out HOLD signals
        active_signals = {
            name: signal for name, signal in signals.items()
            if signal.action != 'HOLD'
        }
        
        if not active_signals:
            logger.debug("All signals are HOLD")
            return None
        
        # Choose voting method
        if self.method == "weighted_average":
            final_signal = self._weighted_average_vote(active_signals, weights)
        elif self.method == "majority":
            final_signal = self._majority_vote(active_signals, weights)
        elif self.method == "blend":
            final_signal = self._blend_vote(active_signals, weights)
        else:
            logger.warning(f"Unknown voting method: {self.method}, using weighted_average")
            final_signal = self._weighted_average_vote(active_signals, weights)
        
        # Check confidence threshold
        if final_signal and final_signal.confidence < self.confidence_threshold:
            logger.debug(
                f"Ensemble confidence {final_signal.confidence:.2%} below "
                f"threshold {self.confidence_threshold:.2%}"
            )
            return None
        
        # Store in history
        if final_signal:
            self.voting_history.append({
                'timestamp': pd.Timestamp.now(),
                'signal': final_signal,
                'num_strategies': len(active_signals),
                'method': self.method
            })
        
        return final_signal
    
    def _weighted_average_vote(self,
                                signals: Dict[str, TradeSignal],
                                weights: Dict[str, float]) -> Optional[TradeSignal]:
        """
        Weighted average voting
        
        Final confidence = weighted average of individual confidences
        Final action = action with highest weighted vote
        """
        
        # Count weighted votes for each action
        action_votes = {'BUY': 0.0, 'SELL': 0.0}
        weighted_confidences = []
        
        for strategy_name, signal in signals.items():
            weight = weights.get(strategy_name, 1.0 / len(signals))
            
            # Add weighted vote
            action_votes[signal.action] += weight
            
            # Collect weighted confidence
            weighted_confidences.append(signal.confidence * weight)
        
        # Determine winning action
        winning_action = max(action_votes, key=action_votes.get)
        
        # Calculate ensemble confidence
        total_weight = sum(action_votes.values())
        if total_weight == 0:
            return None
        
        ensemble_confidence = sum(weighted_confidences) / total_weight
        
        # Get representative signal (highest confidence for winning action)
        representative_signals = [
            s for s in signals.values()
            if s.action == winning_action
        ]
        
        if not representative_signals:
            return None
        
        best_signal = max(representative_signals, key=lambda s: s.confidence)
        
        # Create ensemble signal
        ensemble_signal = TradeSignal(
            strategy='ensemble',
            action=winning_action,
            confidence=ensemble_confidence,
            symbol=best_signal.symbol,
            entry_price=best_signal.entry_price,
            stop_loss=best_signal.stop_loss,
            take_profit=best_signal.take_profit,
            metadata={
                'voting_method': 'weighted_average',
                'num_votes': len(signals),
                'action_votes': action_votes
            }
        )
        
        logger.debug(
            f"Ensemble signal: {winning_action} "
            f"(confidence: {ensemble_confidence:.2%}, votes: {len(signals)})"
        )
        
        return ensemble_signal
    
    def _majority_vote(self,
                       signals: Dict[str, TradeSignal],
                       weights: Dict[str, float]) -> Optional[TradeSignal]:
        """
        Majority voting (simple majority)
        
        Winner determined by count, confidence by average
        """
        
        # Count votes for each action
        action_counts = {'BUY': 0, 'SELL': 0}
        action_confidences = {'BUY': [], 'SELL': []}
        
        for signal in signals.values():
            action_counts[signal.action] += 1
            action_confidences[signal.action].append(signal.confidence)
        
        # Determine winner
        winning_action = max(action_counts, key=action_counts.get)
        
        # Check if majority exists
        required_majority = (len(signals) + 1) // 2
        if action_counts[winning_action] < required_majority:
            logger.debug(f"No majority for {winning_action}")
            return None
        
        # Average confidence for winning action
        avg_confidence = np.mean(action_confidences[winning_action])
        
        # Get representative signal
        representative_signals = [
            s for s in signals.values()
            if s.action == winning_action
        ]
        best_signal = max(representative_signals, key=lambda s: s.confidence)
        
        # Create ensemble signal
        ensemble_signal = TradeSignal(
            strategy='ensemble',
            action=winning_action,
            confidence=avg_confidence,
            symbol=best_signal.symbol,
            entry_price=best_signal.entry_price,
            stop_loss=best_signal.stop_loss,
            take_profit=best_signal.take_profit,
            metadata={
                'voting_method': 'majority',
                'votes_for': action_counts[winning_action],
                'votes_total': len(signals)
            }
        )
        
        logger.debug(
            f"Majority voting: {winning_action} "
            f"({action_counts[winning_action]}/{len(signals)} votes)"
        )
        
        return ensemble_signal
    
    def _blend_vote(self,
                    signals: Dict[str, TradeSignal],
                    weights: Dict[str, float]) -> Optional[TradeSignal]:
        """
        Confidence-weighted blend
        
        Combines weighted average with confidence normalization
        """
        
        # Get confidences
        buy_confidence = 0.0
        sell_confidence = 0.0
        
        for strategy_name, signal in signals.items():
            weight = weights.get(strategy_name, 1.0 / len(signals))
            
            if signal.action == 'BUY':
                buy_confidence += signal.confidence * weight
            elif signal.action == 'SELL':
                sell_confidence += signal.confidence * weight
        
        # Normalize to 0-1
        total_confidence = buy_confidence + sell_confidence
        if total_confidence == 0:
            return None
        
        buy_confidence = buy_confidence / total_confidence
        sell_confidence = sell_confidence / total_confidence
        
        # Determine action
        if buy_confidence > sell_confidence:
            winning_action = 'BUY'
            final_confidence = buy_confidence
        else:
            winning_action = 'SELL'
            final_confidence = sell_confidence
        
        # Get representative signal
        representative_signals = [
            s for s in signals.values()
            if s.action == winning_action
        ]
        
        if not representative_signals:
            return None
        
        best_signal = max(representative_signals, key=lambda s: s.confidence)
        
        # Create ensemble signal
        ensemble_signal = TradeSignal(
            strategy='ensemble',
            action=winning_action,
            confidence=final_confidence,
            symbol=best_signal.symbol,
            entry_price=best_signal.entry_price,
            stop_loss=best_signal.stop_loss,
            take_profit=best_signal.take_profit,
            metadata={
                'voting_method': 'blend',
                'buy_confidence': buy_confidence,
                'sell_confidence': sell_confidence
            }
        )
        
        logger.debug(
            f"Blend voting: {winning_action} "
            f"(buy:{buy_confidence:.2%}, sell:{sell_confidence:.2%})"
        )
        
        return ensemble_signal
    
    def get_voting_history(self) -> List[Dict]:
        """Get voting history"""
        return self.voting_history.copy()
    
    def clear_history(self):
        """Clear voting history"""
        self.voting_history.clear()
