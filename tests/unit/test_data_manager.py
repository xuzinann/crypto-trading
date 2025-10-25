from datetime import datetime, timedelta
from unittest.mock import Mock, patch
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
