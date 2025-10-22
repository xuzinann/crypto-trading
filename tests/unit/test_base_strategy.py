import pytest
from src.ai_strategy.strategies.base_strategy import BaseStrategy, Signal, SignalType


def test_base_strategy_cannot_be_instantiated():
    """Test BaseStrategy is abstract and cannot be instantiated"""
    with pytest.raises(TypeError):
        BaseStrategy()


def test_signal_class_has_required_fields():
    """Test Signal dataclass has correct structure"""
    signal = Signal(
        signal_type=SignalType.BUY,
        confidence=75.0,
        reasoning="Test reasoning"
    )

    assert signal.signal_type == SignalType.BUY
    assert signal.confidence == 75.0
    assert signal.reasoning == "Test reasoning"
