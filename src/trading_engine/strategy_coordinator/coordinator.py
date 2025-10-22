from typing import List, Dict, Any
from src.ai_strategy.strategies.base_strategy import BaseStrategy, Signal, SignalType
import logging

logger = logging.getLogger(__name__)


class StrategyCoordinator:
    """Coordinates multiple trading strategies and combines their signals"""

    def __init__(self, strategies: List[BaseStrategy], confidence_threshold: float = 70.0):
        self.strategies = strategies
        self.confidence_threshold = confidence_threshold

    async def get_combined_signal(self, market_data: Dict[str, Any], news_events: List[Dict] = None) -> Signal:
        """
        Get combined signal from all enabled strategies

        Args:
            market_data: Market data to analyze
            news_events: Optional news events

        Returns:
            Combined signal using weighted voting
        """
        signals = []

        # Collect signals from all enabled strategies
        for strategy in self.strategies:
            if not strategy.enabled:
                continue

            try:
                signal = await strategy.analyze(market_data, news_events)
                signals.append((strategy, signal))
                logger.info(f"{strategy.name}: {signal.signal_type.value} (confidence: {signal.confidence})")
            except Exception as e:
                logger.error(f"Error in {strategy.name}: {e}")

        if not signals:
            return Signal(
                signal_type=SignalType.HOLD,
                confidence=0,
                reasoning="No strategies enabled"
            )

        # Weighted voting
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0
        reasoning_parts = []

        for strategy, signal in signals:
            weighted_confidence = signal.confidence * strategy.weight

            if signal.signal_type == SignalType.BUY:
                buy_score += weighted_confidence
            elif signal.signal_type == SignalType.SELL:
                sell_score += weighted_confidence
            else:
                hold_score += weighted_confidence

            reasoning_parts.append(f"{strategy.name}: {signal.reasoning}")

        # Determine final signal
        max_score = max(buy_score, sell_score, hold_score)

        if max_score == buy_score:
            final_type = SignalType.BUY
            final_confidence = buy_score
        elif max_score == sell_score:
            final_type = SignalType.SELL
            final_confidence = sell_score
        else:
            final_type = SignalType.HOLD
            final_confidence = hold_score

        # Check confidence threshold
        if final_confidence < self.confidence_threshold and final_type != SignalType.HOLD:
            final_type = SignalType.HOLD
            reasoning_parts.append(f"Confidence {final_confidence:.1f} below threshold {self.confidence_threshold}")

        combined_reasoning = " | ".join(reasoning_parts)

        return Signal(
            signal_type=final_type,
            confidence=min(final_confidence, 100),
            reasoning=combined_reasoning
        )

    def add_strategy(self, strategy: BaseStrategy):
        """Add a new strategy to coordinator"""
        self.strategies.append(strategy)

    def remove_strategy(self, strategy_name: str):
        """Remove a strategy by name"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]

    def get_strategy(self, strategy_name: str) -> BaseStrategy:
        """Get strategy by name"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                return strategy
        return None
