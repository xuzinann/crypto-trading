import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.ai_strategy.strategies.base_strategy import BaseStrategy, Signal, SignalType


class TechnicalIndicatorsStrategy(BaseStrategy):
    """Strategy based on technical indicators (RSI, MACD, Moving Averages)"""

    def __init__(self):
        super().__init__(name="TechnicalIndicators", weight=0.3)
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.ma_short = 20
        self.ma_long = 50

    async def analyze(self, market_data: Dict[str, Any], news_events: List[Dict] = None) -> Signal:
        """
        Analyze market using technical indicators

        Returns signal based on RSI, MACD, and moving averages
        """
        df = market_data.get('ohlcv')
        if df is None or len(df) < self.ma_long:
            return Signal(
                signal_type=SignalType.HOLD,
                confidence=0,
                reasoning="Insufficient data for technical analysis"
            )

        # Calculate indicators
        rsi = self._calculate_rsi(df['close'], self.rsi_period)
        ma_short = df['close'].rolling(window=self.ma_short).mean()
        ma_long = df['close'].rolling(window=self.ma_long).mean()
        macd, signal_line = self._calculate_macd(df['close'])

        # Get latest values
        latest_rsi = rsi.iloc[-1]
        latest_price = df['close'].iloc[-1]
        latest_ma_short = ma_short.iloc[-1]
        latest_ma_long = ma_long.iloc[-1]
        latest_macd = macd.iloc[-1]
        latest_signal = signal_line.iloc[-1]

        # Signal logic
        signals = []
        reasoning_parts = []

        # RSI signals
        if latest_rsi < self.rsi_oversold:
            signals.append(('BUY', 30))
            reasoning_parts.append(f"RSI oversold at {latest_rsi:.1f}")
        elif latest_rsi > self.rsi_overbought:
            signals.append(('SELL', 30))
            reasoning_parts.append(f"RSI overbought at {latest_rsi:.1f}")

        # Moving average crossover
        if latest_ma_short > latest_ma_long:
            signals.append(('BUY', 25))
            reasoning_parts.append("MA bullish crossover")
        elif latest_ma_short < latest_ma_long:
            signals.append(('SELL', 25))
            reasoning_parts.append("MA bearish crossover")

        # MACD signals
        if latest_macd > latest_signal:
            signals.append(('BUY', 20))
            reasoning_parts.append("MACD bullish")
        elif latest_macd < latest_signal:
            signals.append(('SELL', 20))
            reasoning_parts.append("MACD bearish")

        # Determine final signal
        if not signals:
            return Signal(
                signal_type=SignalType.HOLD,
                confidence=50,
                reasoning="No clear technical signals"
            )

        # Count votes
        buy_confidence = sum(conf for sig, conf in signals if sig == 'BUY')
        sell_confidence = sum(conf for sig, conf in signals if sig == 'SELL')

        if buy_confidence > sell_confidence:
            signal_type = SignalType.BUY
            confidence = min(buy_confidence, 100)
        elif sell_confidence > buy_confidence:
            signal_type = SignalType.SELL
            confidence = min(sell_confidence, 100)
        else:
            signal_type = SignalType.HOLD
            confidence = 50

        reasoning = "; ".join(reasoning_parts)

        return Signal(
            signal_type=signal_type,
            confidence=confidence,
            reasoning=reasoning
        )

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: pd.Series, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line
