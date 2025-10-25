from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from src.backtesting.data_manager import DataManager


def test_data_manager_initializes():
    """Test DataManager can be initialized"""
    manager = DataManager()
    assert manager is not None


def test_detect_missing_ranges_finds_gaps():
    """Test gap detection in cached data"""
    manager = DataManager()

    # Simulate hourly data with a gap
    cached_data = [
        Mock(timestamp=datetime(2024, 1, 1, 0, 0)),
        Mock(timestamp=datetime(2024, 1, 1, 1, 0)),
        # Gap here - missing 2:00
        Mock(timestamp=datetime(2024, 1, 1, 3, 0)),
        Mock(timestamp=datetime(2024, 1, 1, 4, 0)),
    ]

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 1, 4, 0)

    gaps = manager.detect_missing_ranges(cached_data, start, end, '1h')

    assert len(gaps) == 1
    assert gaps[0][0] == datetime(2024, 1, 1, 2, 0)
    assert gaps[0][1] == datetime(2024, 1, 1, 2, 0)


def test_detect_missing_ranges_with_no_gaps():
    """Test gap detection when data is complete"""
    manager = DataManager()

    # Complete hourly data
    cached_data = [
        Mock(timestamp=datetime(2024, 1, 1, 0, 0)),
        Mock(timestamp=datetime(2024, 1, 1, 1, 0)),
        Mock(timestamp=datetime(2024, 1, 1, 2, 0)),
    ]

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 1, 2, 0)

    gaps = manager.detect_missing_ranges(cached_data, start, end, '1h')

    assert len(gaps) == 0


def test_get_cached_data_queries_database():
    """Test get_cached_data queries database correctly"""
    manager = DataManager()

    # Mock database session
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.order_by.return_value.all.return_value = []

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)

    result = manager.get_cached_data(
        db=mock_db,
        symbol='BTC/USDT',
        start=start,
        end=end,
        timeframe='1h'
    )

    # Verify database was queried
    assert mock_db.query.called
    assert result == []
