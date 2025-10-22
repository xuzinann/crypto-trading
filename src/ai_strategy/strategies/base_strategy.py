from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List


class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Signal:
    """Trading signal with confidence and reasoning"""
    signal_type: SignalType
    confidence: float  # 0-100
    reasoning: str

    def __post_init__(self):
        if not 0 <= self.confidence <= 100:
            raise ValueError("Confidence must be between 0 and 100")


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight  # Weight for signal combination
        self.enabled = True

    @abstractmethod
    async def analyze(self, market_data: Dict[str, Any], news_events: List[Dict] = None) -> Signal:
        """
        Analyze market data and return trading signal

        Args:
            market_data: Dict containing OHLCV data, ticker info, etc.
            news_events: Optional list of recent news events

        Returns:
            Signal with type, confidence, and reasoning
        """
        pass

    def enable(self):
        """Enable this strategy"""
        self.enabled = True

    def disable(self):
        """Disable this strategy"""
        self.enabled = False

    def set_weight(self, weight: float):
        """Set strategy weight for signal combination"""
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        self.weight = weight
