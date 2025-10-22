# Bitcoin Autotrader Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an automated Bitcoin trading system with DeepSeek AI, technical indicators, news analysis, and mobile dashboard for real-time monitoring.

**Architecture:** Hybrid design with separate Trading Engine and AI Strategy Service communicating via REST API. PostgreSQL for data storage, FastAPI for backend, React for dashboard, Docker for deployment.

**Tech Stack:** Python 3.11+, FastAPI, CCXT, PostgreSQL, Redis, React 18, TailwindCSS, Docker, Binance US API, DeepSeek API

---

## Phase 1: Project Setup & Infrastructure

### Task 1: Initialize Python project structure

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.env.example`
- Create: `README.md`

**Step 1: Write requirements.txt**

Create `requirements.txt` with core dependencies:

```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0

# Exchange Integration
ccxt==4.1.50

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1

# Cache
redis==5.0.1

# Data Processing
pandas==2.1.3
numpy==1.26.2

# Technical Analysis
TA-Lib==0.4.28

# HTTP Client
aiohttp==3.9.1
requests==2.31.0

# Environment
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Code Quality
black==23.11.0
pylint==3.0.2
```

**Step 2: Create pytest.ini**

Create `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    --verbose
    --cov=src
    --cov-report=term-missing
    --cov-report=html
```

**Step 3: Create .env.example**

Create `.env.example`:

```bash
# Binance US API
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true  # Set to false for live trading

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# News APIs
CRYPTOPANIC_API_KEY=free
NEWSAPI_KEY=your_newsapi_key_here

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/bitcoin_trader
REDIS_URL=redis://localhost:6379/0

# Risk Management
POSITION_SIZE_PERCENT=5
DAILY_LOSS_LIMIT_PERCENT=15
KILL_SWITCH_PERCENT=50
INITIAL_CAPITAL=10000

# Trading
PAPER_TRADING=true
STRATEGY_POLL_INTERVAL=300  # seconds

# Dashboard
JWT_SECRET_KEY=change_this_to_random_secret
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Notifications (optional)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
TWILIO_TO_NUMBER=
```

**Step 4: Create README.md**

Create `README.md`:

```markdown
# Bitcoin Autotrader

Automated Bitcoin trading system with AI analysis, technical indicators, and real-time mobile dashboard.

## Features

- DeepSeek AI market analysis
- Technical indicators (RSI, MACD, moving averages)
- News event monitoring
- Comprehensive risk management
- Mobile-friendly web dashboard
- Backtesting framework
- Paper trading mode

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run database migrations: `alembic upgrade head`
4. Start services: `docker-compose up`

## Testing

Run tests: `pytest`

## Architecture

See `docs/plans/2025-10-22-bitcoin-autotrading-design.md` for detailed design documentation.
```

**Step 5: Commit**

```bash
git add requirements.txt pytest.ini .env.example README.md
git commit -m "feat: initialize project structure with dependencies and configuration"
```

---

### Task 2: Create directory structure

**Files:**
- Create directories for organized code structure

**Step 1: Create directory structure**

```bash
mkdir -p src/{trading_engine,ai_strategy,news_monitor,dashboard,database,common}
mkdir -p src/trading_engine/{risk_manager,order_executor,position_tracker,strategy_coordinator}
mkdir -p src/ai_strategy/strategies
mkdir -p src/dashboard/{api,websocket}
mkdir -p src/database/{models,migrations}
mkdir -p tests/{unit,integration}
mkdir -p config
mkdir -p logs
```

**Step 2: Create __init__.py files**

```bash
touch src/__init__.py
touch src/trading_engine/__init__.py
touch src/ai_strategy/__init__.py
touch src/news_monitor/__init__.py
touch src/dashboard/__init__.py
touch src/database/__init__.py
touch src/common/__init__.py
```

**Step 3: Commit**

```bash
git add src/ tests/ config/ logs/
git commit -m "feat: create directory structure for modules"
```

---

## Phase 2: Database Models & Schema

### Task 3: Define database models

**Files:**
- Create: `src/database/models/base.py`
- Create: `src/database/models/trade.py`
- Create: `src/database/models/position.py`
- Create: `src/database/models/daily_stats.py`
- Create: `src/database/models/system_log.py`
- Create: `tests/unit/test_models.py`

**Step 1: Write test for base model**

Create `tests/unit/test_models.py`:

```python
import pytest
from datetime import datetime
from src.database.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_base_model_can_be_created():
    """Test that SQLAlchemy base can be instantiated"""
    assert Base is not None
    assert hasattr(Base, 'metadata')
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_models.py::test_base_model_can_be_created -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.database.models.base'"

**Step 3: Implement base model**

Create `src/database/models/base.py`:

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_models.py::test_base_model_can_be_created -v`
Expected: PASS

**Step 5: Write test for Trade model**

Add to `tests/unit/test_models.py`:

```python
from src.database.models.trade import Trade


def test_trade_model_has_required_fields():
    """Test Trade model has all required fields"""
    assert hasattr(Trade, 'id')
    assert hasattr(Trade, 'timestamp')
    assert hasattr(Trade, 'symbol')
    assert hasattr(Trade, 'type')
    assert hasattr(Trade, 'amount')
    assert hasattr(Trade, 'entry_price')
    assert hasattr(Trade, 'exit_price')
    assert hasattr(Trade, 'profit_loss')
    assert hasattr(Trade, 'strategy_signals')
    assert hasattr(Trade, 'reasoning')
```

**Step 6: Run test to verify failure**

Run: `pytest tests/unit/test_models.py::test_trade_model_has_required_fields -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 7: Implement Trade model**

Create `src/database/models/trade.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum
from src.database.models.base import Base, TimestampMixin
from datetime import datetime
import enum


class TradeType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Trade(Base, TimestampMixin):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    type = Column(Enum(TradeType), nullable=False)
    amount = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    strategy_signals = Column(JSON, nullable=True)
    reasoning = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, type={self.type}, amount={self.amount})>"
```

**Step 8: Run test to verify pass**

Run: `pytest tests/unit/test_models.py::test_trade_model_has_required_fields -v`
Expected: PASS

**Step 9: Implement Position model**

Create `src/database/models/position.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from src.database.models.base import Base, TimestampMixin
from datetime import datetime
import enum


class PositionStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Position(Base, TimestampMixin):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    entry_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, default=0.0)
    stop_loss_price = Column(Float, nullable=False)
    status = Column(Enum(PositionStatus), default=PositionStatus.OPEN, nullable=False, index=True)

    def __repr__(self):
        return f"<Position(id={self.id}, symbol={self.symbol}, status={self.status}, pnl={self.unrealized_pnl})>"
```

**Step 10: Implement DailyStats model**

Create `src/database/models/daily_stats.py`:

```python
from sqlalchemy import Column, Integer, String, Float, Date
from src.database.models.base import Base, TimestampMixin
from datetime import date


class DailyStats(Base, TimestampMixin):
    __tablename__ = 'daily_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=date.today, nullable=False, unique=True, index=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)

    def __repr__(self):
        return f"<DailyStats(date={self.date}, trades={self.total_trades}, pnl={self.total_pnl})>"
```

**Step 11: Implement SystemLog model**

Create `src/database/models/system_log.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from src.database.models.base import Base
from datetime import datetime
import enum


class LogLevel(enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class SystemLog(Base):
    __tablename__ = 'system_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(Enum(LogLevel), nullable=False, index=True)
    component = Column(String(100), nullable=False, index=True)
    message = Column(String(1000), nullable=False)
    details = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<SystemLog(level={self.level}, component={self.component}, message={self.message[:50]})>"
```

**Step 12: Commit**

```bash
git add src/database/models/ tests/unit/test_models.py
git commit -m "feat: add database models for trades, positions, stats, and logs"
```

---

### Task 4: Setup database connection and initialization

**Files:**
- Create: `src/database/connection.py`
- Create: `tests/unit/test_database_connection.py`

**Step 1: Write test for database connection**

Create `tests/unit/test_database_connection.py`:

```python
import pytest
from src.database.connection import get_database_url, create_engine_from_config


def test_get_database_url_returns_valid_url():
    """Test that database URL is correctly formatted"""
    url = get_database_url()
    assert url is not None
    assert url.startswith("postgresql://")


def test_create_engine_returns_sqlalchemy_engine():
    """Test that engine creation returns valid SQLAlchemy engine"""
    engine = create_engine_from_config()
    assert engine is not None
    assert hasattr(engine, 'connect')
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_database_connection.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement database connection**

Create `src/database/connection.py`:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Get database URL from environment or use default"""
    return os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bitcoin_trader')


def create_engine_from_config():
    """Create SQLAlchemy engine from configuration"""
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL query logging
    )
    return engine


def get_session_maker():
    """Create session maker for database operations"""
    engine = create_engine_from_config()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    SessionLocal = get_session_maker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables"""
    from src.database.models.base import Base
    from src.database.models.trade import Trade
    from src.database.models.position import Position
    from src.database.models.daily_stats import DailyStats
    from src.database.models.system_log import SystemLog

    engine = create_engine_from_config()
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_database_connection.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/database/connection.py tests/unit/test_database_connection.py
git commit -m "feat: add database connection and session management"
```

---

## Phase 3: Core Trading Engine - Risk Manager

### Task 5: Implement Risk Manager

**Files:**
- Create: `src/trading_engine/risk_manager/risk_manager.py`
- Create: `tests/unit/test_risk_manager.py`

**Step 1: Write test for position size validation**

Create `tests/unit/test_risk_manager.py`:

```python
import pytest
from src.trading_engine.risk_manager.risk_manager import RiskManager


def test_calculate_position_size_returns_5_percent_of_balance():
    """Test position sizing is 5% of account balance"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    position_size = risk_manager.calculate_position_size(balance=10000)
    assert position_size == 500  # 5% of 10000


def test_validate_trade_rejects_when_insufficient_balance():
    """Test trade validation rejects when balance too low"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    is_valid, reason = risk_manager.validate_trade(
        balance=100,
        current_daily_loss_percent=0
    )

    assert is_valid is False
    assert "insufficient balance" in reason.lower()
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_risk_manager.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement RiskManager**

Create `src/trading_engine/risk_manager/risk_manager.py`:

```python
from typing import Tuple
from datetime import datetime, date


class RiskManager:
    """Manages risk parameters and validates trades"""

    def __init__(
        self,
        position_size_percent: float = 5.0,
        daily_loss_limit_percent: float = 15.0,
        kill_switch_percent: float = 50.0,
        initial_capital: float = 10000.0
    ):
        self.position_size_percent = position_size_percent
        self.daily_loss_limit_percent = daily_loss_limit_percent
        self.kill_switch_percent = kill_switch_percent
        self.initial_capital = initial_capital
        self.is_trading_locked = False
        self.daily_loss_reset_date = date.today()

    def calculate_position_size(self, balance: float) -> float:
        """Calculate position size as percentage of balance"""
        return balance * (self.position_size_percent / 100)

    def validate_trade(
        self,
        balance: float,
        current_daily_loss_percent: float
    ) -> Tuple[bool, str]:
        """
        Validate if a trade can be executed based on risk rules

        Returns:
            (is_valid, reason) tuple
        """
        # Check if trading is locked by kill switch
        if self.is_trading_locked:
            return False, "Trading locked by kill switch"

        # Check daily loss limit
        if current_daily_loss_percent >= self.daily_loss_limit_percent:
            return False, f"Daily loss limit reached ({current_daily_loss_percent}%)"

        # Check if balance is sufficient for minimum position
        position_size = self.calculate_position_size(balance)
        if position_size < 10:  # Minimum position size $10
            return False, "Insufficient balance for minimum position size"

        return True, "Trade validated"

    def check_kill_switch(self, total_loss_percent: float) -> bool:
        """
        Check if kill switch should be triggered

        Returns:
            True if kill switch triggered
        """
        if total_loss_percent >= self.kill_switch_percent:
            self.is_trading_locked = True
            return True
        return False

    def reset_daily_loss(self) -> None:
        """Reset daily loss tracking at midnight UTC"""
        today = date.today()
        if today > self.daily_loss_reset_date:
            self.daily_loss_reset_date = today
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_risk_manager.py -v`
Expected: PASS

**Step 5: Add test for daily loss limit**

Add to `tests/unit/test_risk_manager.py`:

```python
def test_validate_trade_rejects_when_daily_loss_limit_reached():
    """Test trade validation rejects when daily loss limit hit"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    is_valid, reason = risk_manager.validate_trade(
        balance=9000,
        current_daily_loss_percent=15
    )

    assert is_valid is False
    assert "daily loss limit" in reason.lower()


def test_check_kill_switch_locks_trading_at_50_percent_loss():
    """Test kill switch activates at 50% total loss"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    triggered = risk_manager.check_kill_switch(total_loss_percent=50)

    assert triggered is True
    assert risk_manager.is_trading_locked is True
```

**Step 6: Run test to verify pass**

Run: `pytest tests/unit/test_risk_manager.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/trading_engine/risk_manager/ tests/unit/test_risk_manager.py
git commit -m "feat: implement risk manager with position sizing and limits"
```

---

## Phase 4: Core Trading Engine - Order Executor

### Task 6: Implement Order Executor

**Files:**
- Create: `src/trading_engine/order_executor/order_executor.py`
- Create: `tests/unit/test_order_executor.py`

**Step 1: Write test for order placement**

Create `tests/unit/test_order_executor.py`:

```python
import pytest
from unittest.mock import Mock, patch
from src.trading_engine.order_executor.order_executor import OrderExecutor


@pytest.fixture
def mock_exchange():
    """Create mock exchange for testing"""
    exchange = Mock()
    exchange.create_market_buy_order = Mock(return_value={
        'id': '12345',
        'symbol': 'BTC/USD',
        'type': 'market',
        'side': 'buy',
        'price': 50000,
        'amount': 0.01,
        'filled': 0.01,
        'status': 'closed'
    })
    return exchange


def test_place_buy_order_calls_exchange_api(mock_exchange):
    """Test buy order placement calls exchange correctly"""
    executor = OrderExecutor(exchange=mock_exchange, paper_trading=False)

    result = executor.place_buy_order(symbol='BTC/USD', amount=0.01)

    assert result['id'] == '12345'
    assert result['side'] == 'buy'
    mock_exchange.create_market_buy_order.assert_called_once_with('BTC/USD', 0.01)


def test_paper_trading_mode_simulates_order():
    """Test paper trading mode doesn't call real exchange"""
    mock_exchange = Mock()
    executor = OrderExecutor(exchange=mock_exchange, paper_trading=True)

    result = executor.place_buy_order(symbol='BTC/USD', amount=0.01)

    assert result['simulated'] is True
    assert result['side'] == 'buy'
    mock_exchange.create_market_buy_order.assert_not_called()
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_order_executor.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement OrderExecutor**

Create `src/trading_engine/order_executor/order_executor.py`:

```python
import ccxt
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Executes orders on Binance US exchange"""

    def __init__(self, exchange: ccxt.Exchange, paper_trading: bool = True):
        self.exchange = exchange
        self.paper_trading = paper_trading
        self.simulated_price = 50000  # Default BTC price for paper trading

    def place_buy_order(self, symbol: str, amount: float) -> Dict:
        """
        Place a market buy order

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            amount: Amount to buy in base currency

        Returns:
            Order details dictionary
        """
        if self.paper_trading:
            return self._simulate_order(symbol=symbol, amount=amount, side='buy')

        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            logger.info(f"Buy order placed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
            raise

    def place_sell_order(self, symbol: str, amount: float) -> Dict:
        """
        Place a market sell order

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            amount: Amount to sell in base currency

        Returns:
            Order details dictionary
        """
        if self.paper_trading:
            return self._simulate_order(symbol=symbol, amount=amount, side='sell')

        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            logger.info(f"Sell order placed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")
            raise

    def place_stop_loss(self, symbol: str, amount: float, stop_price: float) -> Dict:
        """
        Place a stop-loss order

        Args:
            symbol: Trading pair
            amount: Position size
            stop_price: Price to trigger stop loss

        Returns:
            Order details dictionary
        """
        if self.paper_trading:
            return {
                'id': f'sim_sl_{datetime.utcnow().timestamp()}',
                'symbol': symbol,
                'type': 'stop_loss',
                'amount': amount,
                'stopPrice': stop_price,
                'simulated': True
            }

        try:
            # Binance US stop-loss market order
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop_loss',
                side='sell',
                amount=amount,
                params={'stopPrice': stop_price}
            )
            logger.info(f"Stop-loss placed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing stop-loss: {e}")
            raise

    def _simulate_order(self, symbol: str, amount: float, side: str) -> Dict:
        """Simulate order execution for paper trading"""
        return {
            'id': f'sim_{datetime.utcnow().timestamp()}',
            'symbol': symbol,
            'type': 'market',
            'side': side,
            'price': self.simulated_price,
            'amount': amount,
            'filled': amount,
            'status': 'closed',
            'simulated': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        if self.paper_trading:
            return self.simulated_price

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            raise
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_order_executor.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/trading_engine/order_executor/ tests/unit/test_order_executor.py
git commit -m "feat: implement order executor with paper trading support"
```

---

## Phase 5: Core Trading Engine - Position Tracker

### Task 7: Implement Position Tracker

**Files:**
- Create: `src/trading_engine/position_tracker/position_tracker.py`
- Create: `tests/unit/test_position_tracker.py`

**Step 1: Write test for position tracking**

Create `tests/unit/test_position_tracker.py`:

```python
import pytest
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.database.models.position import Position, PositionStatus


def test_add_position_creates_new_position():
    """Test adding a new position"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    assert position.symbol == 'BTC/USD'
    assert position.entry_price == 50000
    assert position.amount == 0.01
    assert position.stop_loss_price == 47500
    assert position.status == PositionStatus.OPEN


def test_calculate_unrealized_pnl_for_long_position():
    """Test P&L calculation for open long position"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    pnl = tracker.calculate_unrealized_pnl(position, current_price=51000)

    assert pnl == 10.0  # (51000 - 50000) * 0.01 = 10
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_position_tracker.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement PositionTracker**

Create `src/trading_engine/position_tracker/position_tracker.py`:

```python
from typing import List, Optional
from datetime import datetime
from src.database.models.position import Position, PositionStatus


class PositionTracker:
    """Tracks open and closed positions"""

    def __init__(self):
        self.positions: List[Position] = []

    def add_position(
        self,
        symbol: str,
        entry_price: float,
        amount: float,
        stop_loss_price: float
    ) -> Position:
        """
        Add a new position

        Args:
            symbol: Trading pair
            entry_price: Entry price
            amount: Position size
            stop_loss_price: Stop-loss price

        Returns:
            Position object
        """
        position = Position(
            symbol=symbol,
            entry_time=datetime.utcnow(),
            entry_price=entry_price,
            amount=amount,
            current_price=entry_price,
            unrealized_pnl=0.0,
            stop_loss_price=stop_loss_price,
            status=PositionStatus.OPEN
        )
        self.positions.append(position)
        return position

    def calculate_unrealized_pnl(self, position: Position, current_price: float) -> float:
        """
        Calculate unrealized P&L for a position

        Args:
            position: Position object
            current_price: Current market price

        Returns:
            Unrealized P&L
        """
        pnl = (current_price - position.entry_price) * position.amount
        position.current_price = current_price
        position.unrealized_pnl = pnl
        return pnl

    def close_position(self, position: Position, exit_price: float) -> float:
        """
        Close a position and calculate realized P&L

        Args:
            position: Position to close
            exit_price: Exit price

        Returns:
            Realized P&L
        """
        realized_pnl = (exit_price - position.entry_price) * position.amount
        position.status = PositionStatus.CLOSED
        position.current_price = exit_price
        position.unrealized_pnl = realized_pnl
        return realized_pnl

    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return [p for p in self.positions if p.status == PositionStatus.OPEN]

    def get_total_unrealized_pnl(self, current_prices: dict) -> float:
        """
        Calculate total unrealized P&L across all open positions

        Args:
            current_prices: Dict of {symbol: price}

        Returns:
            Total unrealized P&L
        """
        total_pnl = 0.0
        for position in self.get_open_positions():
            if position.symbol in current_prices:
                pnl = self.calculate_unrealized_pnl(position, current_prices[position.symbol])
                total_pnl += pnl
        return total_pnl

    def check_stop_loss_triggers(self, current_prices: dict) -> List[Position]:
        """
        Check if any positions hit stop-loss

        Args:
            current_prices: Dict of {symbol: price}

        Returns:
            List of positions that hit stop-loss
        """
        triggered = []
        for position in self.get_open_positions():
            if position.symbol in current_prices:
                current_price = current_prices[position.symbol]
                if current_price <= position.stop_loss_price:
                    triggered.append(position)
        return triggered
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_position_tracker.py -v`
Expected: PASS

**Step 5: Add tests for closing positions**

Add to `tests/unit/test_position_tracker.py`:

```python
def test_close_position_calculates_realized_pnl():
    """Test closing position calculates correct P&L"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    realized_pnl = tracker.close_position(position, exit_price=52000)

    assert realized_pnl == 20.0  # (52000 - 50000) * 0.01 = 20
    assert position.status == PositionStatus.CLOSED


def test_check_stop_loss_triggers_identifies_hit_positions():
    """Test stop-loss trigger detection"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    triggered = tracker.check_stop_loss_triggers({'BTC/USD': 47000})

    assert len(triggered) == 1
    assert triggered[0] == position
```

**Step 6: Run test to verify pass**

Run: `pytest tests/unit/test_position_tracker.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/trading_engine/position_tracker/ tests/unit/test_position_tracker.py
git commit -m "feat: implement position tracker with P&L calculation"
```

---

## Phase 6: AI Strategy Service - Plugin Architecture

### Task 8: Create base strategy interface

**Files:**
- Create: `src/ai_strategy/strategies/base_strategy.py`
- Create: `tests/unit/test_base_strategy.py`

**Step 1: Write test for base strategy**

Create `tests/unit/test_base_strategy.py`:

```python
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
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_base_strategy.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement base strategy**

Create `src/ai_strategy/strategies/base_strategy.py`:

```python
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
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_base_strategy.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ai_strategy/strategies/base_strategy.py tests/unit/test_base_strategy.py
git commit -m "feat: create base strategy interface for plugin architecture"
```

---

### Task 9: Implement Technical Indicators Strategy

**Files:**
- Create: `src/ai_strategy/strategies/technical_indicators.py`
- Create: `tests/unit/test_technical_indicators.py`

**Step 1: Write test for technical strategy**

Create `tests/unit/test_technical_indicators.py`:

```python
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
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_technical_indicators.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement Technical Indicators Strategy**

Create `src/ai_strategy/strategies/technical_indicators.py`:

```python
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
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_technical_indicators.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ai_strategy/strategies/technical_indicators.py tests/unit/test_technical_indicators.py
git commit -m "feat: implement technical indicators strategy with RSI, MACD, MA"
```

---

## Phase 7: Strategy Coordinator

### Task 10: Implement Strategy Coordinator

**Files:**
- Create: `src/trading_engine/strategy_coordinator/coordinator.py`
- Create: `tests/unit/test_coordinator.py`

**Step 1: Write test for signal combination**

Create `tests/unit/test_coordinator.py`:

```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.ai_strategy.strategies.base_strategy import Signal, SignalType


@pytest.mark.asyncio
async def test_combine_signals_with_weighted_voting():
    """Test signal combination uses weighted voting"""
    # Create mock strategies
    strategy1 = Mock()
    strategy1.name = "Strategy1"
    strategy1.weight = 0.5
    strategy1.enabled = True
    strategy1.analyze = AsyncMock(return_value=Signal(
        signal_type=SignalType.BUY,
        confidence=80,
        reasoning="Strategy1 bullish"
    ))

    strategy2 = Mock()
    strategy2.name = "Strategy2"
    strategy2.weight = 0.3
    strategy2.enabled = True
    strategy2.analyze = AsyncMock(return_value=Signal(
        signal_type=SignalType.SELL,
        confidence=60,
        reasoning="Strategy2 bearish"
    ))

    coordinator = StrategyCoordinator(strategies=[strategy1, strategy2])

    final_signal = await coordinator.get_combined_signal(market_data={})

    # BUY: 80 * 0.5 = 40
    # SELL: 60 * 0.3 = 18
    # BUY should win
    assert final_signal.signal_type == SignalType.BUY
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_coordinator.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement Strategy Coordinator**

Create `src/trading_engine/strategy_coordinator/coordinator.py`:

```python
from typing import List, Dict, Any
from src.ai_strategy.strategies.base_strategy import BaseStrategy, Signal, SignalType
import logging

logger = logging.getLogger(__name__)


class StrategyCoordinator:
    """Coordinates multiple trading strategies and combines their signals"""

    def __init__(self, strategies: List[BaseStrategy], confidence_threshold: float = 70.0):
        self.strategies = strategies
        self.confidence_threshold = confidence_threshold

    async def get_combined_signal(self, market_data: Dict[str, Any], news_events: List[Dict] = None) -> Signal:
        """
        Get combined signal from all enabled strategies

        Args:
            market_data: Market data to analyze
            news_events: Optional news events

        Returns:
            Combined signal using weighted voting
        """
        signals = []

        # Collect signals from all enabled strategies
        for strategy in self.strategies:
            if not strategy.enabled:
                continue

            try:
                signal = await strategy.analyze(market_data, news_events)
                signals.append((strategy, signal))
                logger.info(f"{strategy.name}: {signal.signal_type.value} (confidence: {signal.confidence})")
            except Exception as e:
                logger.error(f"Error in {strategy.name}: {e}")

        if not signals:
            return Signal(
                signal_type=SignalType.HOLD,
                confidence=0,
                reasoning="No strategies enabled"
            )

        # Weighted voting
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0
        reasoning_parts = []

        for strategy, signal in signals:
            weighted_confidence = signal.confidence * strategy.weight

            if signal.signal_type == SignalType.BUY:
                buy_score += weighted_confidence
            elif signal.signal_type == SignalType.SELL:
                sell_score += weighted_confidence
            else:
                hold_score += weighted_confidence

            reasoning_parts.append(f"{strategy.name}: {signal.reasoning}")

        # Determine final signal
        max_score = max(buy_score, sell_score, hold_score)

        if max_score == buy_score:
            final_type = SignalType.BUY
            final_confidence = buy_score
        elif max_score == sell_score:
            final_type = SignalType.SELL
            final_confidence = sell_score
        else:
            final_type = SignalType.HOLD
            final_confidence = hold_score

        # Check confidence threshold
        if final_confidence < self.confidence_threshold and final_type != SignalType.HOLD:
            final_type = SignalType.HOLD
            reasoning_parts.append(f"Confidence {final_confidence:.1f} below threshold {self.confidence_threshold}")

        combined_reasoning = " | ".join(reasoning_parts)

        return Signal(
            signal_type=final_type,
            confidence=min(final_confidence, 100),
            reasoning=combined_reasoning
        )

    def add_strategy(self, strategy: BaseStrategy):
        """Add a new strategy to coordinator"""
        self.strategies.append(strategy)

    def remove_strategy(self, strategy_name: str):
        """Remove a strategy by name"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]

    def get_strategy(self, strategy_name: str) -> BaseStrategy:
        """Get strategy by name"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                return strategy
        return None
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_coordinator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/trading_engine/strategy_coordinator/ tests/unit/test_coordinator.py
git commit -m "feat: implement strategy coordinator with weighted voting"
```

---

## Phase 8: Main Trading Engine Loop

### Task 11: Implement Trading Engine Main Loop

**Files:**
- Create: `src/trading_engine/engine.py`
- Create: `tests/integration/test_trading_engine.py`

**Step 1: Create integration test for trading engine**

Create `tests/integration/test_trading_engine.py`:

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.trading_engine.engine import TradingEngine


@pytest.mark.asyncio
async def test_trading_engine_executes_buy_signal():
    """Test trading engine executes buy when signal is strong"""
    # This is an integration test - we'll implement it after the engine
    pass
```

**Step 2: Implement Trading Engine**

Create `src/trading_engine/engine.py`:

```python
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, date
from src.trading_engine.risk_manager.risk_manager import RiskManager
from src.trading_engine.order_executor.order_executor import OrderExecutor
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.database.models.trade import Trade, TradeType
from src.database.models.daily_stats import DailyStats
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine that coordinates all components"""

    def __init__(
        self,
        risk_manager: RiskManager,
        order_executor: OrderExecutor,
        position_tracker: PositionTracker,
        strategy_coordinator: StrategyCoordinator,
        db_session: Session,
        symbol: str = 'BTC/USD',
        poll_interval: int = 300
    ):
        self.risk_manager = risk_manager
        self.order_executor = order_executor
        self.position_tracker = position_tracker
        self.strategy_coordinator = strategy_coordinator
        self.db = db_session
        self.symbol = symbol
        self.poll_interval = poll_interval
        self.is_running = False
        self.account_balance = risk_manager.initial_capital
        self.daily_pnl = 0.0
        self.total_pnl = 0.0

    async def start(self):
        """Start the trading engine"""
        self.is_running = True
        logger.info("Trading engine started")

        while self.is_running:
            try:
                await self._trading_cycle()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                await asyncio.sleep(60)  # Wait before retry

    def stop(self):
        """Stop the trading engine"""
        self.is_running = False
        logger.info("Trading engine stopped")

    async def _trading_cycle(self):
        """Execute one trading cycle"""
        # Reset daily loss if new day
        self.risk_manager.reset_daily_loss()

        # Get current market data
        market_data = await self._fetch_market_data()

        # Update open positions
        await self._update_positions(market_data)

        # Check stop-loss triggers
        await self._check_stop_losses(market_data)

        # Get trading signal
        signal = await self.strategy_coordinator.get_combined_signal(market_data)
        logger.info(f"Signal: {signal.signal_type.value} (confidence: {signal.confidence})")

        # Calculate current daily loss percentage
        daily_loss_percent = abs(self.daily_pnl / self.risk_manager.initial_capital * 100)
        total_loss_percent = abs(self.total_pnl / self.risk_manager.initial_capital * 100)

        # Check kill switch
        if self.risk_manager.check_kill_switch(total_loss_percent):
            logger.critical(f"KILL SWITCH ACTIVATED - Total loss: {total_loss_percent}%")
            await self._close_all_positions(market_data)
            self.stop()
            return

        # Validate trade with risk manager
        can_trade, reason = self.risk_manager.validate_trade(
            balance=self.account_balance,
            current_daily_loss_percent=daily_loss_percent
        )

        if not can_trade:
            logger.info(f"Trade rejected: {reason}")
            return

        # Execute trade based on signal
        if signal.signal_type.value == 'BUY' and len(self.position_tracker.get_open_positions()) == 0:
            await self._execute_buy(market_data, signal)
        elif signal.signal_type.value == 'SELL' and len(self.position_tracker.get_open_positions()) > 0:
            await self._execute_sell(market_data, signal)

    async def _fetch_market_data(self) -> Dict[str, Any]:
        """Fetch current market data"""
        # For now, return mock data - in real implementation, fetch from exchange
        import pandas as pd
        import numpy as np

        current_price = self.order_executor.get_current_price(self.symbol)

        # Generate mock OHLCV data for strategies
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1H')
        ohlcv = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(current_price * 0.98, current_price * 1.02, 100),
            'high': np.random.uniform(current_price, current_price * 1.03, 100),
            'low': np.random.uniform(current_price * 0.97, current_price, 100),
            'close': np.random.uniform(current_price * 0.98, current_price * 1.02, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })

        return {
            'symbol': self.symbol,
            'current_price': current_price,
            'ohlcv': ohlcv
        }

    async def _update_positions(self, market_data: Dict[str, Any]):
        """Update all open positions with current prices"""
        current_price = market_data['current_price']
        for position in self.position_tracker.get_open_positions():
            self.position_tracker.calculate_unrealized_pnl(position, current_price)

    async def _check_stop_losses(self, market_data: Dict[str, Any]):
        """Check and execute stop-loss orders"""
        current_prices = {self.symbol: market_data['current_price']}
        triggered = self.position_tracker.check_stop_loss_triggers(current_prices)

        for position in triggered:
            logger.warning(f"Stop-loss triggered for position {position.id}")
            await self._close_position(position, market_data['current_price'], "Stop-loss triggered")

    async def _execute_buy(self, market_data: Dict[str, Any], signal):
        """Execute buy order"""
        current_price = market_data['current_price']
        position_size_usd = self.risk_manager.calculate_position_size(self.account_balance)
        amount = position_size_usd / current_price

        # Place buy order
        order = self.order_executor.place_buy_order(self.symbol, amount)
        logger.info(f"Buy order executed: {order}")

        # Calculate stop-loss price (5% below entry)
        stop_loss_price = current_price * 0.95

        # Place stop-loss
        self.order_executor.place_stop_loss(self.symbol, amount, stop_loss_price)

        # Add position to tracker
        position = self.position_tracker.add_position(
            symbol=self.symbol,
            entry_price=current_price,
            amount=amount,
            stop_loss_price=stop_loss_price
        )

        # Save to database
        trade = Trade(
            symbol=self.symbol,
            type=TradeType.BUY,
            amount=amount,
            entry_price=current_price,
            strategy_signals={'combined': signal.signal_type.value},
            reasoning=signal.reasoning
        )
        self.db.add(trade)
        self.db.commit()

        self.account_balance -= position_size_usd

    async def _execute_sell(self, market_data: Dict[str, Any], signal):
        """Execute sell order for all open positions"""
        current_price = market_data['current_price']

        for position in self.position_tracker.get_open_positions():
            await self._close_position(position, current_price, signal.reasoning)

    async def _close_position(self, position, exit_price: float, reason: str):
        """Close a single position"""
        # Place sell order
        order = self.order_executor.place_sell_order(self.symbol, position.amount)
        logger.info(f"Sell order executed: {order}")

        # Calculate realized P&L
        realized_pnl = self.position_tracker.close_position(position, exit_price)

        # Update balances
        self.account_balance += (exit_price * position.amount)
        self.daily_pnl += realized_pnl
        self.total_pnl += realized_pnl

        logger.info(f"Position closed - P&L: ${realized_pnl:.2f}")

        # Update trade in database
        # Find the corresponding buy trade and update it
        # (simplified - in real implementation, match by position ID)

    async def _close_all_positions(self, market_data: Dict[str, Any]):
        """Emergency close all positions"""
        logger.warning("Closing all positions")
        current_price = market_data['current_price']

        for position in self.position_tracker.get_open_positions():
            await self._close_position(position, current_price, "Emergency close")
```

**Step 3: Commit**

```bash
git add src/trading_engine/engine.py tests/integration/test_trading_engine.py
git commit -m "feat: implement main trading engine with trading cycle"
```

---

## Phase 9: FastAPI Backend Setup

### Task 12: Create FastAPI application and WebSocket endpoint

**Files:**
- Create: `src/main.py`
- Create: `src/dashboard/api/routes.py`
- Create: `src/dashboard/websocket/connection_manager.py`

**Step 1: Create main FastAPI application**

Create `src/main.py`:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.dashboard.websocket.connection_manager import ConnectionManager
from src.dashboard.api.routes import router as api_router
from src.database.connection import init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bitcoin Autotrader API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()
    logger.info("Application started")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Echo back or handle commands
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Bitcoin Autotrader"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Step 2: Create WebSocket connection manager**

Create `src/dashboard/websocket/connection_manager.py`:

```python
from fastapi import WebSocket
from typing import List
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_position_update(self, position: dict):
        """Broadcast position update"""
        await self.broadcast({
            "type": "position_update",
            "data": position
        })

    async def broadcast_trade_executed(self, trade: dict):
        """Broadcast trade execution"""
        await self.broadcast({
            "type": "trade_executed",
            "data": trade
        })

    async def broadcast_system_status(self, status: dict):
        """Broadcast system status update"""
        await self.broadcast({
            "type": "system_status",
            "data": status
        })
```

**Step 3: Create API routes**

Create `src/dashboard/api/routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database.connection import get_db
from src.database.models.trade import Trade
from src.database.models.position import Position
from src.database.models.daily_stats import DailyStats
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()


class PositionResponse(BaseModel):
    id: int
    symbol: str
    entry_price: float
    current_price: float
    amount: float
    unrealized_pnl: float
    status: str
    entry_time: datetime

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    id: int
    symbol: str
    type: str
    amount: float
    entry_price: float
    exit_price: float
    profit_loss: float
    timestamp: datetime
    reasoning: str

    class Config:
        from_attributes = True


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(db: Session = Depends(get_db)):
    """Get all open positions"""
    positions = db.query(Position).filter(Position.status == "OPEN").all()
    return positions


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    limit: int = 100,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get trade history"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    trades = db.query(Trade).filter(
        Trade.timestamp >= cutoff_date
    ).order_by(Trade.timestamp.desc()).limit(limit).all()
    return trades


@router.get("/stats/daily")
async def get_daily_stats(db: Session = Depends(get_db)):
    """Get today's trading statistics"""
    from datetime import date
    today = date.today()
    stats = db.query(DailyStats).filter(DailyStats.date == today).first()

    if not stats:
        return {
            "date": today,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0
        }

    return stats


@router.get("/system/status")
async def get_system_status():
    """Get system status"""
    # In real implementation, get actual status from trading engine
    return {
        "status": "running",
        "paper_trading": True,
        "last_signal": "HOLD",
        "account_balance": 10000.0,
        "daily_pnl": 0.0,
        "total_pnl": 0.0
    }


@router.post("/system/pause")
async def pause_trading():
    """Pause trading"""
    # In real implementation, pause the trading engine
    return {"status": "paused"}


@router.post("/system/resume")
async def resume_trading():
    """Resume trading"""
    # In real implementation, resume the trading engine
    return {"status": "running"}


@router.post("/positions/close-all")
async def close_all_positions():
    """Emergency close all positions"""
    # In real implementation, trigger emergency close
    return {"status": "all positions closed"}
```

**Step 4: Commit**

```bash
git add src/main.py src/dashboard/
git commit -m "feat: create FastAPI backend with WebSocket and REST API"
```

---

## Phase 10: Docker Configuration

### Task 13: Create Docker configuration

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`

**Step 1: Create Dockerfile**

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Create docker-compose.yml**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: bitcoin_trader
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  trading-engine:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/bitcoin_trader
      - REDIS_URL=redis://redis:6379/0
      - PAPER_TRADING=true
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

**Step 3: Create .dockerignore**

Create `.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
.idea
.vscode
*.swp
*.swo
*~
.DS_Store
docs/
tests/
.env.local
node_modules/
```

**Step 4: Commit**

```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "feat: add Docker configuration for deployment"
```

---

## Phase 11: Frontend Setup (Basic Structure)

### Task 14: Initialize React dashboard

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/components/Dashboard.jsx`

**Note:** This task creates the basic React structure. Full implementation would be extensive. For now, we create the structure and one simple component.

**Step 1: Create package.json**

Create `frontend/package.json`:

```json
{
  "name": "bitcoin-autotrader-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.10.0",
    "tailwindcss": "^3.3.0",
    "react-router-dom": "^6.20.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

**Step 2: Create basic App component**

Create `frontend/src/App.jsx`:

```jsx
import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
```

**Step 3: Create Dashboard component**

Create `frontend/src/components/Dashboard.jsx`:

```jsx
import React, { useState, useEffect } from 'react';

function Dashboard() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [positions, setPositions] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Fetch initial data
    fetchSystemStatus();
    fetchPositions();

    // Connect WebSocket
    const websocket = new WebSocket('ws://localhost:8000/ws');

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const fetchSystemStatus = async () => {
    const response = await fetch('http://localhost:8000/api/v1/system/status');
    const data = await response.json();
    setSystemStatus(data);
  };

  const fetchPositions = async () => {
    const response = await fetch('http://localhost:8000/api/v1/positions');
    const data = await response.json();
    setPositions(data);
  };

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'position_update':
        fetchPositions();
        break;
      case 'system_status':
        setSystemStatus(message.data);
        break;
      default:
        break;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-6">Bitcoin Autotrader</h1>

      {/* System Status */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        {systemStatus && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-400">Status</p>
              <p className="text-2xl font-bold text-green-500">{systemStatus.status}</p>
            </div>
            <div>
              <p className="text-gray-400">Balance</p>
              <p className="text-2xl font-bold">${systemStatus.account_balance.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-gray-400">Daily P&L</p>
              <p className={`text-2xl font-bold ${systemStatus.daily_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${systemStatus.daily_pnl.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-400">Total P&L</p>
              <p className={`text-2xl font-bold ${systemStatus.total_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${systemStatus.total_pnl.toFixed(2)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Positions */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Open Positions</h2>
        {positions.length === 0 ? (
          <p className="text-gray-400">No open positions</p>
        ) : (
          <div className="space-y-4">
            {positions.map((position) => (
              <div key={position.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{position.symbol}</p>
                    <p className="text-sm text-gray-400">Entry: ${position.entry_price.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${position.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      ${position.unrealized_pnl.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-400">Current: ${position.current_price.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
```

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: initialize React dashboard with basic components"
```

---

## Phase 12: Deployment Script

### Task 15: Create deployment script

**Files:**
- Create: `deploy.sh`
- Create: `scripts/init_db.py`

**Step 1: Create database initialization script**

Create `scripts/init_db.py`:

```python
#!/usr/bin/env python3
"""Initialize database with tables"""

from src.database.connection import init_database

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
```

**Step 2: Create deployment script**

Create `deploy.sh`:

```bash
#!/bin/bash

set -e  # Exit on error

echo "=== Bitcoin Autotrader Deployment ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before continuing"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Initializing database..."
docker-compose exec trading-engine python scripts/init_db.py

echo "=== Deployment Complete ==="
echo ""
echo "Services:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Dashboard: Build frontend and serve"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
```

**Step 3: Make script executable**

```bash
chmod +x deploy.sh
chmod +x scripts/init_db.py
```

**Step 4: Commit**

```bash
git add deploy.sh scripts/init_db.py
git commit -m "feat: add deployment script and database initialization"
```

---

## Summary

This implementation plan provides a comprehensive, bite-sized task breakdown for building the Bitcoin autotrading system. Each task follows TDD principles with:

1. Write failing test
2. Verify failure
3. Implement code
4. Verify pass
5. Commit

**Key components implemented:**
- Project structure and dependencies
- Database models and connections
- Risk management system
- Order execution with paper trading
- Position tracking with P&L calculation
- Plugin-based strategy architecture
- Technical indicators strategy
- Strategy coordinator with weighted voting
- Main trading engine loop
- FastAPI backend with WebSocket
- REST API endpoints
- Docker deployment configuration
- React dashboard foundation
- Deployment automation

**Next phases to implement:**
- Additional strategy plugins (DeepSeek AI, News Analyzer)
- News monitor service
- Backtesting framework
- Full React dashboard with all tabs
- Authentication and security
- Comprehensive testing
- Production deployment configuration

**Estimated total implementation time:** 7-11 weeks with one developer working full-time.
