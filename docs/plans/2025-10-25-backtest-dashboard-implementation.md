# Backtest Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build comprehensive backtesting system with Streamlit dashboard for testing trading strategies against historical data and comparing vs buy-and-hold.

**Architecture:** Integrated approach reusing existing strategy code. Historical data manager with hybrid caching (PostgreSQL + OKX API), backtest engine running simulations, Streamlit UI for visualization and metrics.

**Tech Stack:** Python, SQLAlchemy, Streamlit, Plotly, Pandas, CCXT, PostgreSQL

---

## Task 1: Database Models for Historical Data

**Files:**
- Create: `src/database/models/historical_price.py`
- Modify: `src/database/models/__init__.py`
- Test: `tests/unit/test_historical_price_model.py`

**Step 1: Write the failing test**

Create `tests/unit/test_historical_price_model.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_historical_price_model.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.database.models.historical_price'"

**Step 3: Write minimal implementation**

Create `src/database/models/historical_price.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from src.database.models.base import Base, TimestampMixin
from datetime import datetime


class HistoricalPrice(Base, TimestampMixin):
    __tablename__ = 'historical_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
    )

    def __repr__(self):
        return f"<HistoricalPrice(symbol={self.symbol}, timeframe={self.timeframe}, timestamp={self.timestamp})>"
```

Update `src/database/models/__init__.py`:

```python
from src.database.models.base import Base
from src.database.models.trade import Trade
from src.database.models.position import Position
from src.database.models.daily_stats import DailyStats
from src.database.models.system_log import SystemLog
from src.database.models.historical_price import HistoricalPrice

__all__ = ['Base', 'Trade', 'Position', 'DailyStats', 'SystemLog', 'HistoricalPrice']
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_historical_price_model.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/database/models/historical_price.py src/database/models/__init__.py tests/unit/test_historical_price_model.py
git commit -m "feat: add HistoricalPrice database model"
```

---

## Task 2: Database Model for Backtest Results

**Files:**
- Create: `src/database/models/backtest_result.py`
- Modify: `src/database/models/__init__.py`
- Test: `tests/unit/test_backtest_result_model.py`

**Step 1: Write the failing test**

Create `tests/unit/test_backtest_result_model.py`:

```python
from datetime import datetime
from src.database.models.backtest_result import BacktestResult


def test_backtest_result_model_has_required_fields():
    """Test BacktestResult model has all required fields"""
    result = BacktestResult(
        symbol='BTC/USDT',
        strategy_name='TechnicalIndicators',
        execution_timeframe='1h',
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        initial_capital=10000.0,
        final_capital=14520.0,
        total_return_pct=45.2,
        max_drawdown_pct=12.5,
        sharpe_ratio=1.82,
        total_trades=42,
        win_rate=58.0
    )

    assert result.symbol == 'BTC/USDT'
    assert result.strategy_name == 'TechnicalIndicators'
    assert result.execution_timeframe == '1h'
    assert result.total_return_pct == 45.2
    assert result.sharpe_ratio == 1.82


def test_backtest_result_calculates_profit():
    """Test BacktestResult can calculate profit"""
    result = BacktestResult(
        symbol='BTC/USDT',
        strategy_name='Test',
        execution_timeframe='1h',
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        initial_capital=10000.0,
        final_capital=14520.0
    )

    profit = result.final_capital - result.initial_capital
    assert profit == 4520.0
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_backtest_result_model.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.database.models.backtest_result'"

**Step 3: Write minimal implementation**

Create `src/database/models/backtest_result.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from src.database.models.base import Base, TimestampMixin
from datetime import datetime


class BacktestResult(Base, TimestampMixin):
    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    strategy_name = Column(String(100), nullable=False)
    execution_timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)

    # Returns
    total_return_pct = Column(Float, nullable=True)
    annualized_return_pct = Column(Float, nullable=True)

    # Risk Metrics
    max_drawdown_pct = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)

    # Trade Statistics
    total_trades = Column(Integer, nullable=True)
    winning_trades = Column(Integer, nullable=True)
    losing_trades = Column(Integer, nullable=True)
    win_rate = Column(Float, nullable=True)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)

    # Buy & Hold Comparison
    buyhold_return_pct = Column(Float, nullable=True)
    outperformance_pct = Column(Float, nullable=True)

    # Detailed Data
    metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<BacktestResult(symbol={self.symbol}, strategy={self.strategy_name}, return={self.total_return_pct}%)>"
```

Update `src/database/models/__init__.py`:

```python
from src.database.models.base import Base
from src.database.models.trade import Trade
from src.database.models.position import Position
from src.database.models.daily_stats import DailyStats
from src.database.models.system_log import SystemLog
from src.database.models.historical_price import HistoricalPrice
from src.database.models.backtest_result import BacktestResult

__all__ = ['Base', 'Trade', 'Position', 'DailyStats', 'SystemLog', 'HistoricalPrice', 'BacktestResult']
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_backtest_result_model.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/database/models/backtest_result.py src/database/models/__init__.py tests/unit/test_backtest_result_model.py
git commit -m "feat: add BacktestResult database model"
```

---

## Task 3: Historical Data Manager - Basic Structure

**Files:**
- Create: `src/backtesting/__init__.py`
- Create: `src/backtesting/data_manager.py`
- Test: `tests/unit/test_data_manager.py`

**Step 1: Write the failing test**

Create `tests/unit/test_data_manager.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_data_manager.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.backtesting'"

**Step 3: Write minimal implementation**

Create `src/backtesting/__init__.py`:

```python
"""Backtesting module for strategy performance analysis"""
```

Create `src/backtesting/data_manager.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_data_manager.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/backtesting/__init__.py src/backtesting/data_manager.py tests/unit/test_data_manager.py
git commit -m "feat: add DataManager with gap detection"
```

---

## Task 4: Historical Data Manager - Database Integration

**Files:**
- Modify: `src/backtesting/data_manager.py`
- Modify: `tests/unit/test_data_manager.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_data_manager.py`:

```python
from unittest.mock import MagicMock


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
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_data_manager.py::test_get_cached_data_queries_database -v`

Expected: FAIL with "AttributeError: 'DataManager' object has no attribute 'get_cached_data'"

**Step 3: Write minimal implementation**

Update `src/backtesting/data_manager.py`:

```python
from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session
from src.database.models.historical_price import HistoricalPrice


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
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_data_manager.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/backtesting/data_manager.py tests/unit/test_data_manager.py
git commit -m "feat: add database query method to DataManager"
```

---

## Task 5: Historical Data Manager - API Integration

**Files:**
- Modify: `src/backtesting/data_manager.py`
- Modify: `tests/unit/test_data_manager.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_data_manager.py`:

```python
@patch('src.backtesting.data_manager.get_exchange')
def test_fetch_from_api(mock_get_exchange):
    """Test fetching data from OKX API"""
    manager = DataManager()

    # Mock exchange
    mock_exchange = Mock()
    mock_exchange.fetch_ohlcv.return_value = [
        [1704067200000, 45000.0, 45500.0, 44800.0, 45200.0, 100.5],  # timestamp in ms
        [1704070800000, 45200.0, 45600.0, 45000.0, 45400.0, 98.3],
    ]
    mock_get_exchange.return_value = mock_exchange

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 1, 2, 0)

    result = manager.fetch_from_api(
        symbol='BTC/USDT',
        start=start,
        end=end,
        timeframe='1h'
    )

    assert len(result) == 2
    assert result[0]['open'] == 45000.0
    assert result[0]['close'] == 45200.0
    assert result[1]['open'] == 45200.0
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_data_manager.py::test_fetch_from_api -v`

Expected: FAIL with "AttributeError: 'DataManager' object has no attribute 'fetch_from_api'"

**Step 3: Write minimal implementation**

Update `src/backtesting/data_manager.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_data_manager.py -v`

Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add src/backtesting/data_manager.py tests/unit/test_data_manager.py
git commit -m "feat: add API fetching to DataManager"
```

---

## Task 6: Backtest Engine - Basic Structure

**Files:**
- Create: `src/backtesting/engine.py`
- Test: `tests/unit/test_backtest_engine.py`

**Step 1: Write the failing test**

Create `tests/unit/test_backtest_engine.py`:

```python
from datetime import datetime
from unittest.mock import Mock
from src.backtesting.engine import BacktestEngine


def test_backtest_engine_initializes():
    """Test BacktestEngine can be initialized"""
    engine = BacktestEngine(
        strategy=Mock(),
        initial_capital=10000.0
    )

    assert engine.initial_capital == 10000.0
    assert engine.current_capital == 10000.0
    assert engine.position_size == 0


def test_execute_buy():
    """Test executing buy order"""
    engine = BacktestEngine(
        strategy=Mock(),
        initial_capital=10000.0
    )

    price = 45000.0
    timestamp = datetime(2024, 1, 1, 12, 0)

    engine.execute_buy(price, timestamp)

    # Should buy with all capital minus slippage
    expected_shares = 10000.0 / (45000.0 * 1.001)  # 0.1% slippage
    assert engine.position_size > 0
    assert engine.entry_price == price
    assert engine.current_capital < 10000.0


def test_execute_sell():
    """Test executing sell order"""
    engine = BacktestEngine(
        strategy=Mock(),
        initial_capital=10000.0
    )

    # First buy
    engine.execute_buy(45000.0, datetime(2024, 1, 1, 12, 0))

    # Then sell at higher price
    sell_price = 46000.0
    sell_time = datetime(2024, 1, 1, 13, 0)

    engine.execute_sell(sell_price, sell_time)

    # Should have closed position and have capital > initial
    assert engine.position_size == 0
    assert engine.current_capital > 10000.0
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_backtest_engine.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.backtesting.engine'"

**Step 3: Write minimal implementation**

Create `src/backtesting/engine.py`:

```python
from datetime import datetime
from typing import List, Dict, Optional


class BacktestEngine:
    """Core backtesting engine for strategy simulation"""

    def __init__(self, strategy, initial_capital: float = 10000.0):
        """
        Initialize backtest engine

        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital in USD
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position_size = 0.0
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = []
        self.slippage = 0.001  # 0.1% slippage per trade

    def execute_buy(self, price: float, timestamp: datetime):
        """
        Execute buy order

        Args:
            price: Buy price
            timestamp: Execution time
        """
        if self.position_size > 0:
            return  # Already in position

        # Calculate buy price with slippage
        buy_price = price * (1 + self.slippage)

        # Buy maximum shares with available capital
        self.position_size = self.current_capital / buy_price
        self.entry_price = price
        self.current_capital = 0.0

        self.trades.append({
            'timestamp': timestamp,
            'type': 'BUY',
            'price': price,
            'size': self.position_size,
            'capital': self.current_capital
        })

    def execute_sell(self, price: float, timestamp: datetime):
        """
        Execute sell order

        Args:
            price: Sell price
            timestamp: Execution time
        """
        if self.position_size == 0:
            return  # No position to sell

        # Calculate sell price with slippage
        sell_price = price * (1 - self.slippage)

        # Sell all shares
        self.current_capital = self.position_size * sell_price

        # Calculate P&L
        profit = self.current_capital - self.initial_capital

        self.trades.append({
            'timestamp': timestamp,
            'type': 'SELL',
            'price': price,
            'size': self.position_size,
            'capital': self.current_capital,
            'profit': profit
        })

        self.position_size = 0.0
        self.entry_price = 0.0
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_backtest_engine.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/backtesting/engine.py tests/unit/test_backtest_engine.py
git commit -m "feat: add BacktestEngine with buy/sell execution"
```

---

## Task 7: Backtest Engine - Simulation Loop

**Files:**
- Modify: `src/backtesting/engine.py`
- Modify: `tests/unit/test_backtest_engine.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_backtest_engine.py`:

```python
import pandas as pd


def test_run_backtest():
    """Test running complete backtest simulation"""
    # Create simple mock strategy
    mock_strategy = Mock()
    mock_strategy.generate_signal.side_effect = [
        'BUY',   # Bar 1: Buy
        'HOLD',  # Bar 2: Hold
        'SELL',  # Bar 3: Sell
        'HOLD',  # Bar 4: Hold
    ]

    engine = BacktestEngine(
        strategy=mock_strategy,
        initial_capital=10000.0
    )

    # Create sample historical data
    historical_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=4, freq='1h'),
        'open': [45000.0, 45200.0, 46000.0, 45800.0],
        'high': [45500.0, 45600.0, 46500.0, 46000.0],
        'low': [44800.0, 45000.0, 45800.0, 45500.0],
        'close': [45200.0, 45400.0, 46200.0, 45900.0],
        'volume': [100.0, 98.0, 105.0, 95.0]
    })

    result = engine.run(historical_data)

    # Should have executed trades
    assert len(engine.trades) == 2  # 1 buy, 1 sell
    assert engine.trades[0]['type'] == 'BUY'
    assert engine.trades[1]['type'] == 'SELL'
    assert result is not None
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_backtest_engine.py::test_run_backtest -v`

Expected: FAIL with "AttributeError: 'BacktestEngine' object has no attribute 'run'"

**Step 3: Write minimal implementation**

Update `src/backtesting/engine.py`:

```python
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


class BacktestEngine:
    """Core backtesting engine for strategy simulation"""

    def __init__(self, strategy, initial_capital: float = 10000.0):
        """
        Initialize backtest engine

        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital in USD
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position_size = 0.0
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = []
        self.slippage = 0.001  # 0.1% slippage per trade

    def run(self, historical_data: pd.DataFrame) -> Dict:
        """
        Run backtest simulation

        Args:
            historical_data: DataFrame with OHLCV data

        Returns:
            Dictionary with backtest results
        """
        for idx, row in historical_data.iterrows():
            # Get strategy signal
            signal = self.strategy.generate_signal(row, historical_data[:idx+1])

            # Execute based on signal
            if signal == 'BUY' and self.position_size == 0:
                self.execute_buy(row['close'], row['timestamp'])
            elif signal == 'SELL' and self.position_size > 0:
                self.execute_sell(row['close'], row['timestamp'])

            # Track equity
            current_equity = self.get_current_equity(row['close'])
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'equity': current_equity
            })

        return {
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'final_capital': self.get_current_equity(historical_data.iloc[-1]['close'])
        }

    def get_current_equity(self, current_price: float) -> float:
        """Calculate current total equity value"""
        if self.position_size > 0:
            return self.position_size * current_price
        else:
            return self.current_capital

    def execute_buy(self, price: float, timestamp: datetime):
        """
        Execute buy order

        Args:
            price: Buy price
            timestamp: Execution time
        """
        if self.position_size > 0:
            return  # Already in position

        # Calculate buy price with slippage
        buy_price = price * (1 + self.slippage)

        # Buy maximum shares with available capital
        self.position_size = self.current_capital / buy_price
        self.entry_price = price
        self.current_capital = 0.0

        self.trades.append({
            'timestamp': timestamp,
            'type': 'BUY',
            'price': price,
            'size': self.position_size,
            'capital': self.current_capital
        })

    def execute_sell(self, price: float, timestamp: datetime):
        """
        Execute sell order

        Args:
            price: Sell price
            timestamp: Execution time
        """
        if self.position_size == 0:
            return  # No position to sell

        # Calculate sell price with slippage
        sell_price = price * (1 - self.slippage)

        # Sell all shares
        self.current_capital = self.position_size * sell_price

        # Calculate P&L
        profit = self.current_capital - self.initial_capital

        self.trades.append({
            'timestamp': timestamp,
            'type': 'SELL',
            'price': price,
            'size': self.position_size,
            'capital': self.current_capital,
            'profit': profit
        })

        self.position_size = 0.0
        self.entry_price = 0.0
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_backtest_engine.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/backtesting/engine.py tests/unit/test_backtest_engine.py
git commit -m "feat: add simulation loop to BacktestEngine"
```

---

## Task 8: Backtest Metrics Calculator

**Files:**
- Create: `src/backtesting/metrics.py`
- Test: `tests/unit/test_metrics.py`

**Step 1: Write the failing test**

Create `tests/unit/test_metrics.py`:

```python
import pandas as pd
from src.backtesting.metrics import MetricsCalculator


def test_calculate_total_return():
    """Test total return calculation"""
    calc = MetricsCalculator()

    initial = 10000.0
    final = 14520.0

    return_pct = calc.calculate_total_return(initial, final)

    assert return_pct == 45.2


def test_calculate_max_drawdown():
    """Test max drawdown calculation"""
    calc = MetricsCalculator()

    equity_curve = pd.Series([10000, 11000, 10500, 12000, 9000, 11000])

    max_dd = calc.calculate_max_drawdown(equity_curve)

    # Peak at 12000, trough at 9000 = 25% drawdown
    assert abs(max_dd - 25.0) < 0.1


def test_calculate_sharpe_ratio():
    """Test Sharpe ratio calculation"""
    calc = MetricsCalculator()

    returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.01, 0.02])

    sharpe = calc.calculate_sharpe_ratio(returns, risk_free_rate=0.02)

    assert sharpe > 0


def test_calculate_win_rate():
    """Test win rate calculation"""
    calc = MetricsCalculator()

    trades = [
        {'profit': 100},
        {'profit': -50},
        {'profit': 200},
        {'profit': -30},
        {'profit': 150},
    ]

    win_rate = calc.calculate_win_rate(trades)

    # 3 wins out of 5 = 60%
    assert win_rate == 60.0
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_metrics.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.backtesting.metrics'"

**Step 3: Write minimal implementation**

Create `src/backtesting/metrics.py`:

```python
import pandas as pd
import numpy as np
from typing import List, Dict


class MetricsCalculator:
    """Calculate backtest performance metrics"""

    def calculate_total_return(self, initial_capital: float, final_capital: float) -> float:
        """
        Calculate total return percentage

        Args:
            initial_capital: Starting capital
            final_capital: Ending capital

        Returns:
            Total return as percentage
        """
        return ((final_capital - initial_capital) / initial_capital) * 100

    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown percentage

        Args:
            equity_curve: Series of equity values

        Returns:
            Max drawdown as percentage
        """
        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown at each point
        drawdown = ((equity_curve - running_max) / running_max) * 100

        # Return worst drawdown (most negative)
        return abs(drawdown.min())

    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe ratio

        Args:
            returns: Series of periodic returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Annualize returns (assuming daily)
        excess_return = returns.mean() * 252 - risk_free_rate
        volatility = returns.std() * np.sqrt(252)

        return excess_return / volatility if volatility > 0 else 0.0

    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """
        Calculate win rate percentage

        Args:
            trades: List of trade dictionaries with 'profit' key

        Returns:
            Win rate as percentage
        """
        if not trades:
            return 0.0

        winning_trades = sum(1 for trade in trades if trade.get('profit', 0) > 0)
        total_trades = len(trades)

        return (winning_trades / total_trades) * 100
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard ./venv/bin/pytest tests/unit/test_metrics.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/backtesting/metrics.py tests/unit/test_metrics.py
git commit -m "feat: add MetricsCalculator for backtest metrics"
```

---

## Task 9: Update Dependencies

**Files:**
- Modify: `requirements.txt`

**Step 1: No test needed for dependencies**

Skip to implementation.

**Step 2: Write minimal implementation**

Update `requirements.txt` to add Streamlit and Plotly:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
ccxt==4.1.50
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
redis==5.0.1
pandas==2.1.3
numpy==1.26.2
aiohttp==3.9.1
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
black==23.11.0
pylint==3.0.2
streamlit==1.28.0
plotly==5.17.0
```

**Step 3: Verify installation**

Run: `./venv/bin/pip install -q streamlit==1.28.0 plotly==5.17.0`

Expected: Successful installation

**Step 4: Commit**

```bash
git add requirements.txt
git commit -m "deps: add streamlit and plotly for dashboard"
```

---

## Task 10: Streamlit Dashboard - Basic Structure

**Files:**
- Create: `streamlit_app/__init__.py`
- Create: `streamlit_app/backtest_dashboard.py`

**Step 1: No unit test for Streamlit UI**

Manual testing only.

**Step 2: Write minimal implementation**

Create `streamlit_app/__init__.py`:

```python
"""Streamlit dashboard for backtesting"""
```

Create `streamlit_app/backtest_dashboard.py`:

```python
import streamlit as st
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Bitcoin Autotrader Backtest",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Bitcoin Autotrader Backtest Dashboard")

# Sidebar configuration
st.sidebar.header("Configuration")

# Symbol selector
symbol = st.sidebar.selectbox(
    "Symbol",
    options=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    index=0
)

# Date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=90)
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now()
    )

# Execution timeframe
execution_timeframe = st.sidebar.selectbox(
    "Execution Timeframe",
    options=["1h", "4h", "1d"],
    index=0
)

# Chart view zoom
chart_zoom = st.sidebar.selectbox(
    "Chart View",
    options=["1h", "4h", "1d", "1w"],
    index=2
)

# Initial capital
initial_capital = st.sidebar.number_input(
    "Initial Capital ($)",
    min_value=1000.0,
    max_value=1000000.0,
    value=10000.0,
    step=1000.0
)

# Run button
run_button = st.sidebar.button("🚀 Run Backtest", type="primary")

# Main content
if run_button:
    st.info("Running backtest... (Implementation in progress)")
else:
    st.info("Configure parameters and click 'Run Backtest' to start")

# Placeholder for results
st.subheader("Results")
st.write("Backtest results will appear here")
```

**Step 3: Manual test**

Run: `streamlit run streamlit_app/backtest_dashboard.py`

Expected: Dashboard opens in browser at http://localhost:8501

**Step 4: Commit**

```bash
git add streamlit_app/__init__.py streamlit_app/backtest_dashboard.py
git commit -m "feat: add basic Streamlit dashboard structure"
```

---

## Task 11: Create Database Migration

**Files:**
- Create: `src/database/migrations/add_backtest_tables.py`

**Step 1: Write migration script**

Create `src/database/migrations/add_backtest_tables.py`:

```python
"""
Database migration to add backtest tables

Run with: python src/database/migrations/add_backtest_tables.py
"""
from sqlalchemy import create_engine
from src.database.connection import get_database_url
from src.database.models.base import Base
from src.database.models.historical_price import HistoricalPrice
from src.database.models.backtest_result import BacktestResult


def run_migration():
    """Create backtest tables in database"""
    database_url = get_database_url()
    engine = create_engine(database_url)

    # Create tables
    Base.metadata.create_all(engine, tables=[
        HistoricalPrice.__table__,
        BacktestResult.__table__
    ])

    print("✅ Migration complete: backtest tables created")


if __name__ == "__main__":
    run_migration()
```

**Step 2: Run migration**

Run: `PYTHONPATH=/home/RV414CE/test01/financial/apt/.worktrees/backtest-dashboard python src/database/migrations/add_backtest_tables.py`

Expected: "✅ Migration complete: backtest tables created"

**Step 3: Commit**

```bash
git add src/database/migrations/add_backtest_tables.py
git commit -m "feat: add database migration for backtest tables"
```

---

## Task 12: Create Launcher Script

**Files:**
- Create: `run_backtest.sh`

**Step 1: Write launcher script**

Create `run_backtest.sh`:

```bash
#!/bin/bash

echo "🚀 Starting Bitcoin Autotrader Backtesting Dashboard"
echo ""

# Check if PostgreSQL is running
if ! docker ps | grep -q postgres; then
    echo "📦 Starting PostgreSQL..."
    docker-compose up -d postgres
    sleep 3
else
    echo "✅ PostgreSQL already running"
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
python src/database/migrations/add_backtest_tables.py

# Launch Streamlit
echo ""
echo "✅ Launching dashboard at http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""
streamlit run streamlit_app/backtest_dashboard.py
```

**Step 2: Make executable**

Run: `chmod +x run_backtest.sh`

Expected: Script is now executable

**Step 3: Test script**

Run: `./run_backtest.sh`

Expected: Dashboard launches successfully

**Step 4: Commit**

```bash
git add run_backtest.sh
git commit -m "feat: add launcher script for backtest dashboard"
```

---

## Task 13: Integration - Connect Dashboard to Backend

**Files:**
- Modify: `streamlit_app/backtest_dashboard.py`

**Step 1: Update dashboard with backend integration**

Update `streamlit_app/backtest_dashboard.py`:

```python
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.backtesting.data_manager import DataManager
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import MetricsCalculator
from src.ai_strategy.strategies.technical_indicators import TechnicalIndicatorsStrategy

# Page configuration
st.set_page_config(
    page_title="Bitcoin Autotrader Backtest",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Bitcoin Autotrader Backtest Dashboard")

# Sidebar configuration
st.sidebar.header("Configuration")

# Symbol selector
symbol = st.sidebar.selectbox(
    "Symbol",
    options=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    index=0
)

# Date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=90)
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now()
    )

# Execution timeframe
execution_timeframe = st.sidebar.selectbox(
    "Execution Timeframe",
    options=["1h", "4h", "1d"],
    index=0
)

# Chart view zoom
chart_zoom = st.sidebar.selectbox(
    "Chart View",
    options=["1h", "4h", "1d", "1w"],
    index=2
)

# Initial capital
initial_capital = st.sidebar.number_input(
    "Initial Capital ($)",
    min_value=1000.0,
    max_value=1000000.0,
    value=10000.0,
    step=1000.0
)

# Run button
run_button = st.sidebar.button("🚀 Run Backtest", type="primary")

# Main content
if run_button:
    with st.spinner("Running backtest..."):
        try:
            # Convert dates to datetime
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            # Get database session
            db = next(get_db())

            # Fetch historical data
            data_manager = DataManager()
            cached_data = data_manager.get_cached_data(
                db=db,
                symbol=symbol,
                start=start_dt,
                end=end_dt,
                timeframe=execution_timeframe
            )

            if not cached_data:
                st.warning(f"No cached data found. Fetching from API...")
                api_data = data_manager.fetch_from_api(
                    symbol=symbol,
                    start=start_dt,
                    end=end_dt,
                    timeframe=execution_timeframe
                )
                st.info(f"Fetched {len(api_data)} data points from API")

                # Convert to DataFrame
                df = pd.DataFrame(api_data)
            else:
                # Convert cached data to DataFrame
                df = pd.DataFrame([
                    {
                        'timestamp': d.timestamp,
                        'open': d.open,
                        'high': d.high,
                        'low': d.low,
                        'close': d.close,
                        'volume': d.volume
                    }
                    for d in cached_data
                ])

            # Run backtest
            strategy = TechnicalIndicatorsStrategy()
            engine = BacktestEngine(strategy=strategy, initial_capital=initial_capital)
            result = engine.run(df)

            # Calculate metrics
            calc = MetricsCalculator()
            total_return = calc.calculate_total_return(
                initial_capital,
                result['final_capital']
            )

            # Calculate buy-and-hold
            buyhold_shares = initial_capital / df.iloc[0]['close']
            buyhold_final = buyhold_shares * df.iloc[-1]['close']
            buyhold_return = calc.calculate_total_return(initial_capital, buyhold_final)

            # Display results
            st.success("Backtest complete!")

            # Summary cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Strategy Return",
                    f"{total_return:.2f}%",
                    delta=f"{total_return:.2f}%"
                )

            with col2:
                st.metric(
                    "Buy & Hold Return",
                    f"{buyhold_return:.2f}%",
                    delta=f"{buyhold_return:.2f}%"
                )

            with col3:
                outperformance = total_return - buyhold_return
                st.metric(
                    "Outperformance",
                    f"{outperformance:.2f}%"
                )

            with col4:
                st.metric(
                    "Total Trades",
                    len(engine.trades)
                )

            # Trade details
            st.subheader("Trade History")
            if engine.trades:
                trades_df = pd.DataFrame(engine.trades)
                st.dataframe(trades_df, use_container_width=True)
            else:
                st.info("No trades executed")

        except Exception as e:
            st.error(f"Error running backtest: {str(e)}")
else:
    st.info("Configure parameters and click 'Run Backtest' to start")

# Placeholder for results
st.subheader("Charts")
st.write("Price charts with trade markers will appear here")
```

**Step 2: Test integration**

Run: `./run_backtest.sh`

Expected: Dashboard can run backtest (may show "No cached data" warning)

**Step 3: Commit**

```bash
git add streamlit_app/backtest_dashboard.py
git commit -m "feat: integrate dashboard with backtest backend"
```

---

## Task 14: Add Price Chart with Plotly

**Files:**
- Modify: `streamlit_app/backtest_dashboard.py`

**Step 1: Add chart after metrics display**

Update `streamlit_app/backtest_dashboard.py` to add Plotly chart:

```python
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.backtesting.data_manager import DataManager
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import MetricsCalculator
from src.ai_strategy.strategies.technical_indicators import TechnicalIndicatorsStrategy

# ... (keep existing code up to trade history) ...

# After trade history, add chart
st.subheader("Price Chart with Trade Markers")

# Create candlestick chart
fig = make_subplots(rows=1, cols=1)

# Add candlestick
fig.add_trace(go.Candlestick(
    x=df['timestamp'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name='Price'
))

# Add buy markers
buy_trades = [t for t in engine.trades if t['type'] == 'BUY']
if buy_trades:
    buy_times = [t['timestamp'] for t in buy_trades]
    buy_prices = [t['price'] for t in buy_trades]
    fig.add_trace(go.Scatter(
        x=buy_times,
        y=buy_prices,
        mode='markers',
        marker=dict(
            symbol='triangle-up',
            size=15,
            color='green'
        ),
        name='Buy'
    ))

# Add sell markers
sell_trades = [t for t in engine.trades if t['type'] == 'SELL']
if sell_trades:
    sell_times = [t['timestamp'] for t in sell_trades]
    sell_prices = [t['price'] for t in sell_trades]
    fig.add_trace(go.Scatter(
        x=sell_times,
        y=sell_prices,
        mode='markers',
        marker=dict(
            symbol='triangle-down',
            size=15,
            color='red'
        ),
        name='Sell'
    ))

# Update layout
fig.update_layout(
    title=f'{symbol} Price with Trade Markers',
    yaxis_title='Price (USD)',
    xaxis_title='Date',
    height=600,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)
```

**Step 2: Test chart display**

Run: `./run_backtest.sh`

Expected: Chart displays with candlesticks and trade markers

**Step 3: Commit**

```bash
git add streamlit_app/backtest_dashboard.py
git commit -m "feat: add price chart with buy/sell markers"
```

---

## Execution Notes

**Total Tasks:** 14
**Estimated Time:** 2-3 hours
**Approach:** TDD with frequent commits

**Key Principles Applied:**
- ✅ Write test first, watch it fail
- ✅ Minimal implementation to pass
- ✅ Commit after each task
- ✅ DRY: Reuse existing strategy code
- ✅ YAGNI: Only build what's specified

**Next Steps After Implementation:**
1. Add data seeding script for initial historical data
2. Improve chart with equity curves
3. Add metrics comparison table
4. Add CSV export functionality
5. Optimize for larger date ranges
6. Add caching of backtest results in database

**Testing:**
- Unit tests: Run `pytest tests/unit/ -v`
- Manual testing: Run `./run_backtest.sh`
- Integration: Test with real OKX API data

**Deployment:**
- Local: `./run_backtest.sh`
- Docker: Add to docker-compose.yml (future enhancement)
