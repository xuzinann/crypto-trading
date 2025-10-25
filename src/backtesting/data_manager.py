from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from sqlalchemy.orm import Session
from src.database.models.historical_price import HistoricalPrice
from src.common.exchange_config import get_exchange


class DataManager:
    """Manages historical price data with hybrid caching"""

    def __init__(self):
        """Initialize data manager"""
        pass

    def get_cached_data(
        self,
        db: Session,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str
    ) -> List[HistoricalPrice]:
        """
        Query cached historical data from database

        Args:
            db: Database session
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            start: Start datetime
            end: End datetime
            timeframe: Time granularity

        Returns:
            List of HistoricalPrice records
        """
        return db.query(HistoricalPrice).filter(
            HistoricalPrice.symbol == symbol,
            HistoricalPrice.timestamp >= start,
            HistoricalPrice.timestamp <= end,
            HistoricalPrice.timeframe == timeframe
        ).order_by(HistoricalPrice.timestamp).all()

    def fetch_from_api(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str
    ) -> List[Dict]:
        """
        Fetch historical data from exchange API

        Args:
            symbol: Trading pair symbol
            start: Start datetime
            end: End datetime
            timeframe: Time granularity

        Returns:
            List of OHLCV dictionaries
        """
        exchange = get_exchange(exchange_name='okx', testnet=False)

        # Convert timeframe to CCXT format
        timeframe_map = {
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        ccxt_timeframe = timeframe_map.get(timeframe, '1h')

        # Fetch OHLCV data
        since = int(start.timestamp() * 1000)  # CCXT expects milliseconds
        ohlcv_list = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=ccxt_timeframe,
            since=since
        )

        # Convert to dictionary format
        result = []
        for ohlcv in ohlcv_list:
            timestamp_ms, open_price, high, low, close, volume = ohlcv
            data_timestamp = datetime.fromtimestamp(timestamp_ms / 1000)

            # Only include data within requested range
            if start <= data_timestamp <= end:
                result.append({
                    'timestamp': data_timestamp,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': volume
                })

        return result

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
