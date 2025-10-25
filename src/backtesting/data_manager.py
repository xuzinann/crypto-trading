from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session


class DataManager:
    """Manages historical price data with hybrid caching"""

    def __init__(self):
        """Initialize data manager"""
        pass

    def detect_missing_ranges(
        self,
        cached_data: List,
        start: datetime,
        end: datetime,
        timeframe: str
    ) -> List[Tuple[datetime, datetime]]:
        """
        Detect missing time ranges in cached data

        Args:
            cached_data: List of cached price records
            start: Start of requested range
            end: End of requested range
            timeframe: Time granularity ('1h', '4h', '1d')

        Returns:
            List of (gap_start, gap_end) tuples
        """
        if not cached_data:
            return [(start, end)]

        # Parse timeframe to timedelta
        interval_map = {
            '1h': timedelta(hours=1),
            '4h': timedelta(hours=4),
            '1d': timedelta(days=1)
        }
        interval = interval_map.get(timeframe, timedelta(hours=1))

        # Build set of expected timestamps
        expected_timestamps = set()
        current = start
        while current <= end:
            expected_timestamps.add(current)
            current += interval

        # Build set of cached timestamps
        cached_timestamps = {record.timestamp for record in cached_data}

        # Find missing timestamps
        missing = sorted(expected_timestamps - cached_timestamps)

        if not missing:
            return []

        # Group consecutive missing timestamps into ranges
        gaps = []
        gap_start = missing[0]
        gap_end = missing[0]

        for i in range(1, len(missing)):
            if missing[i] - gap_end == interval:
                gap_end = missing[i]
            else:
                gaps.append((gap_start, gap_end))
                gap_start = missing[i]
                gap_end = missing[i]

        gaps.append((gap_start, gap_end))

        return gaps
