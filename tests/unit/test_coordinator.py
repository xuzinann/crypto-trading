import pytest
from unittest.mock import Mock, AsyncMock
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.ai_strategy.strategies.base_strategy import Signal, SignalType


@pytest.mark.asyncio
async def test_combine_signals_with_weighted_voting():
    """Test signal combination uses weighted voting"""
    # Create mock strategies
    strategy1 = Mock()
    strategy1.name = "Strategy1"
    strategy1.weight = 0.5
    strategy1.enabled = True
    strategy1.analyze = AsyncMock(return_value=Signal(
        signal_type=SignalType.BUY,
        confidence=80,
        reasoning="Strategy1 bullish"
    ))

    strategy2 = Mock()
    strategy2.name = "Strategy2"
    strategy2.weight = 0.3
    strategy2.enabled = True
    strategy2.analyze = AsyncMock(return_value=Signal(
        signal_type=SignalType.SELL,
        confidence=60,
        reasoning="Strategy2 bearish"
    ))

    coordinator = StrategyCoordinator(strategies=[strategy1, strategy2], confidence_threshold=30.0)

    final_signal = await coordinator.get_combined_signal(market_data={})

    # BUY: 80 * 0.5 = 40
    # SELL: 60 * 0.3 = 18
    # BUY should win
    assert final_signal.signal_type == SignalType.BUY
