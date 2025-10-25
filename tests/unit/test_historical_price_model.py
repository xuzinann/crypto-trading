from datetime import datetime
from src.database.models.historical_price import HistoricalPrice


def test_historical_price_model_has_required_fields():
    """Test HistoricalPrice model has all required fields"""
    price = HistoricalPrice(
        symbol='BTC/USDT',
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        timeframe='1h',
        open=45000.0,
        high=45500.0,
        low=44800.0,
        close=45200.0,
        volume=100.5
    )

    assert price.symbol == 'BTC/USDT'
    assert price.timestamp == datetime(2024, 1, 1, 12, 0, 0)
    assert price.timeframe == '1h'
    assert price.open == 45000.0
    assert price.high == 45500.0
    assert price.low == 44800.0
    assert price.close == 45200.0
    assert price.volume == 100.5


def test_historical_price_repr():
    """Test HistoricalPrice string representation"""
    price = HistoricalPrice(
        symbol='BTC/USDT',
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        timeframe='1h',
        open=45000.0,
        high=45500.0,
        low=44800.0,
        close=45200.0,
        volume=100.5
    )

    repr_str = repr(price)
    assert 'BTC/USDT' in repr_str
    assert '1h' in repr_str
