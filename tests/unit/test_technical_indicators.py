import pytest
import pandas as pd
import numpy as np
from src.ai_strategy.strategies.technical_indicators import TechnicalIndicatorsStrategy
from src.ai_strategy.strategies.base_strategy import SignalType


@pytest.fixture
def sample_market_data():
    """Create sample OHLCV data for testing"""
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1H')
    data = {
        'timestamp': dates,
        'open': np.random.uniform(49000, 51000, 100),
        'high': np.random.uniform(50000, 52000, 100),
        'low': np.random.uniform(48000, 50000, 100),
        'close': np.random.uniform(49000, 51000, 100),
        'volume': np.random.uniform(100, 1000, 100)
    }
    return {'ohlcv': pd.DataFrame(data), 'symbol': 'BTC/USD'}


@pytest.mark.asyncio
async def test_technical_strategy_returns_signal(sample_market_data):
    """Test technical strategy returns valid signal"""
    strategy = TechnicalIndicatorsStrategy()

    signal = await strategy.analyze(sample_market_data)

    assert signal is not None
    assert signal.signal_type in [SignalType.BUY, SignalType.SELL, SignalType.HOLD]
    assert 0 <= signal.confidence <= 100
    assert len(signal.reasoning) > 0
