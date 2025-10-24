# OKX/OKEX API Migration Implementation Plan

**Date:** October 24, 2025
**Objective:** Refactor Bitcoin autotrader from Binance US API to OKX (OKEX) API
**Target Completion:** 3-4 hours
**Complexity:** Medium - Primarily configuration and API integration changes

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture Impact Analysis](#architecture-impact-analysis)
4. [Implementation Tasks](#implementation-tasks)
5. [Testing Strategy](#testing-strategy)
6. [Rollback Plan](#rollback-plan)

---

## Overview

### What This Plan Does
Migrate the automated trading system from Binance US API to OKX (OKEX) exchange API while preserving all functionality including:
- Market data fetching (OHLCV, ticker data)
- Order execution (market, limit, stop-loss orders)
- Paper trading mode
- Real-time price monitoring
- All existing strategies and risk management

### Why OKX vs Binance
**OKX Advantages:**
- Lower trading fees (0.08% maker, 0.10% taker vs Binance's 0.10%/0.10%)
- Better liquidity on certain pairs
- More flexible margin trading
- Unified API for spot, futures, and options
- Better international access
- More advanced order types

### Current Binance Integration Points
1. **Environment Variables:** `.env.example` - API keys configuration
2. **Order Executor:** `src/trading_engine/order_executor/order_executor.py` - Direct exchange interaction
3. **Trading Engine:** `src/trading_engine/engine.py` - Initialization and market data fetching
4. **Documentation:** README.md and design docs reference Binance
5. **Tests:** Unit tests mock Binance exchange behavior

### CCXT Library Support
✅ Both Binance and OKX are fully supported by CCXT library (already installed: `ccxt==4.1.50`)
- No new dependencies required
- Similar API structure for both exchanges
- Unified interface makes migration straightforward

---

## Prerequisites

### Before Starting
- [ ] OKX account created at https://www.okx.com
- [ ] API keys generated with trading permissions (API Key, Secret Key, Passphrase)
- [ ] API keys tested in OKX API sandbox/testnet
- [ ] Understanding of OKX API differences from Binance
- [ ] Backup of current working Binance configuration

### OKX API Key Setup
1. Log into OKX account
2. Navigate to API Management
3. Create new API key with permissions:
   - Trade (required for order placement)
   - Read (required for market data)
   - DO NOT enable Withdraw permission (security best practice)
4. Save: API Key, Secret Key, and Passphrase (OKX requires passphrase)
5. Whitelist your server IP (optional but recommended)

### OKX API Endpoints
- **Testnet:** `https://www.okx.com` (demo trading)
- **Production:** `https://www.okx.com` (live trading)
- **WebSocket:** `wss://ws.okx.com:8443/ws/v5/public` (real-time data)

---

## Architecture Impact Analysis

### Files Requiring Changes

#### 1. Configuration Files (2 files)
- `.env.example` - Environment variable template
- `docker-compose.yml` - No changes needed (environment vars passed through)
- `README.md` - Update documentation

#### 2. Source Code Files (3 files)
- `src/trading_engine/order_executor/order_executor.py` - Update docstrings, comments
- `src/trading_engine/engine.py` - Update exchange initialization (if any)
- `src/main.py` - Verify no hardcoded exchange references

#### 3. Test Files (2 files)
- `tests/unit/test_order_executor.py` - Update test assertions
- `tests/integration/test_trading_engine.py` - Update integration tests

#### 4. Documentation Files (3 files)
- `README.md` - Update setup instructions
- `docs/plans/2025-10-22-bitcoin-autotrading-design.md` - Update architecture docs
- `docs/plans/2025-10-22-bitcoin-autotrader-implementation.md` - Update implementation guide

### Files NOT Requiring Changes
- All database models (exchange-agnostic)
- Risk management logic (exchange-agnostic)
- Position tracker (exchange-agnostic)
- Strategy coordinator (exchange-agnostic)
- AI strategies (exchange-agnostic)
- Dashboard/API routes (exchange-agnostic)
- Docker configuration (environment vars only)

### API Differences: Binance vs OKX

| Feature | Binance US | OKX | Impact |
|---------|-----------|-----|--------|
| **API Authentication** | API Key + Secret | API Key + Secret + Passphrase | Add PASSPHRASE to .env |
| **Trading Pairs Format** | `BTC/USD` | `BTC/USDT` or `BTC/USD` | Update symbol in config |
| **Order Types** | market, limit, stop_loss | market, limit, stop, post_only | Compatible via CCXT |
| **Rate Limits** | 1200 req/min | 2400 req/min (higher) | No code changes |
| **WebSocket Streams** | Different format | Different format | Future enhancement |
| **Testnet** | testnet.binance.vision | www.okx.com (sandbox mode) | Update sandbox config |

### CCXT Unified API (No Breaking Changes)
The beauty of CCXT is that both exchanges use the same methods:
```python
# These work identically for both Binance and OKX:
exchange.create_market_buy_order(symbol, amount)
exchange.create_market_sell_order(symbol, amount)
exchange.fetch_ticker(symbol)
exchange.fetch_balance()
exchange.create_order(symbol, type, side, amount, price, params)
```

**Key Difference:** OKX requires passphrase during initialization:
```python
# Binance initialization
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

# OKX initialization
exchange = ccxt.okx({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSPHRASE,  # NEW REQUIREMENT
})
```

---

## Implementation Tasks

### Phase 1: Environment & Configuration (30 minutes)

#### Task 1.1: Update Environment Variables
**File:** `.env.example`

**Changes Required:**
```bash
# OLD (Binance):
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true

# NEW (OKX):
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_api_secret_here
OKX_API_PASSPHRASE=your_okx_passphrase_here
OKX_TESTNET=true  # Set to false for live trading
```

**Complete .env.example after changes:**
```bash
# OKX API Configuration
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_api_secret_here
OKX_API_PASSPHRASE=your_okx_passphrase_here
OKX_TESTNET=true  # Set to false for live trading

# Trading Pair (OKX uses USDT pairs primarily)
TRADING_SYMBOL=BTC/USDT  # BTC/USD also available but less liquid

# DeepSeek API (unchanged)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# News APIs (unchanged)
CRYPTOPANIC_API_KEY=free
NEWSAPI_KEY=your_newsapi_key_here

# Database (unchanged)
DATABASE_URL=postgresql://postgres:password@localhost:5432/bitcoin_trader
REDIS_URL=redis://localhost:6379/0

# Risk Management (unchanged)
POSITION_SIZE_PERCENT=5
DAILY_LOSS_LIMIT_PERCENT=15
KILL_SWITCH_PERCENT=50
INITIAL_CAPITAL=10000

# Trading (unchanged)
PAPER_TRADING=true
STRATEGY_POLL_INTERVAL=300  # seconds

# Dashboard (unchanged)
JWT_SECRET_KEY=change_this_to_random_secret
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Notifications (optional, unchanged)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
TWILIO_TO_NUMBER=
```

**Verification Steps:**
```bash
# 1. Update .env.example with new OKX variables
# 2. Copy to .env for local testing
cp .env.example .env
# 3. Fill in your actual OKX API credentials
# 4. Verify file contains OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE
grep "OKX_" .env
```

**Success Criteria:**
- [ ] .env.example updated with OKX variables
- [ ] All three OKX credentials present (key, secret, passphrase)
- [ ] Old BINANCE_* variables removed
- [ ] Comments explain testnet vs production usage

---

#### Task 1.2: Create Exchange Configuration Module
**File:** `src/common/exchange_config.py` (NEW FILE)

**Purpose:** Centralize exchange initialization logic for easy switching

**Complete File Contents:**
```python
"""
Exchange configuration and initialization.

Supports multiple exchanges via CCXT library:
- OKX (primary)
- Binance (legacy support)
"""

import os
import ccxt
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ExchangeFactory:
    """Factory for creating exchange instances"""

    SUPPORTED_EXCHANGES = {
        'okx': ccxt.okx,
        'binance': ccxt.binance,
        'binanceus': ccxt.binanceus,
    }

    @staticmethod
    def create_exchange(
        exchange_name: str = 'okx',
        testnet: bool = True,
        paper_trading: bool = True
    ) -> ccxt.Exchange:
        """
        Create and configure exchange instance

        Args:
            exchange_name: Exchange to use ('okx', 'binance', 'binanceus')
            testnet: Use testnet/sandbox mode if True
            paper_trading: Used for logging only (doesn't affect exchange init)

        Returns:
            Configured CCXT exchange instance

        Raises:
            ValueError: If exchange not supported or credentials missing
        """
        if exchange_name not in ExchangeFactory.SUPPORTED_EXCHANGES:
            raise ValueError(
                f"Exchange '{exchange_name}' not supported. "
                f"Supported: {list(ExchangeFactory.SUPPORTED_EXCHANGES.keys())}"
            )

        logger.info(f"Initializing {exchange_name} exchange (testnet={testnet}, paper_trading={paper_trading})")

        # Get exchange class
        exchange_class = ExchangeFactory.SUPPORTED_EXCHANGES[exchange_name]

        # Build configuration
        config = {}

        if exchange_name == 'okx':
            config = ExchangeFactory._get_okx_config(testnet)
        elif exchange_name in ['binance', 'binanceus']:
            config = ExchangeFactory._get_binance_config(testnet)

        # Create exchange instance
        exchange = exchange_class(config)

        # Set sandbox mode if testnet
        if testnet and hasattr(exchange, 'set_sandbox_mode'):
            exchange.set_sandbox_mode(True)
            logger.info(f"{exchange_name} sandbox mode enabled")

        return exchange

    @staticmethod
    def _get_okx_config(testnet: bool) -> dict:
        """Get OKX exchange configuration from environment"""
        api_key = os.getenv('OKX_API_KEY')
        api_secret = os.getenv('OKX_API_SECRET')
        api_passphrase = os.getenv('OKX_API_PASSPHRASE')

        if not all([api_key, api_secret, api_passphrase]):
            raise ValueError(
                "OKX credentials incomplete. Required: "
                "OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE"
            )

        config = {
            'apiKey': api_key,
            'secret': api_secret,
            'password': api_passphrase,  # OKX requires passphrase
            'enableRateLimit': True,  # Respect rate limits
            'options': {
                'defaultType': 'spot',  # Use spot trading (not futures)
            }
        }

        if testnet:
            # OKX uses sandbox mode flag
            config['options']['sandboxMode'] = True

        return config

    @staticmethod
    def _get_binance_config(testnet: bool) -> dict:
        """Get Binance exchange configuration from environment"""
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')

        if not all([api_key, api_secret]):
            raise ValueError(
                "Binance credentials incomplete. Required: "
                "BINANCE_API_KEY, BINANCE_API_SECRET"
            )

        config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        }

        if testnet:
            # Binance testnet uses different base URL
            config['urls'] = {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }

        return config


def get_exchange(
    exchange_name: Optional[str] = None,
    testnet: Optional[bool] = None,
    paper_trading: Optional[bool] = None
) -> ccxt.Exchange:
    """
    Convenience function to get configured exchange instance

    Reads from environment variables if parameters not provided:
    - EXCHANGE_NAME (default: 'okx')
    - OKX_TESTNET or BINANCE_TESTNET (default: true)
    - PAPER_TRADING (default: true)

    Args:
        exchange_name: Override exchange from environment
        testnet: Override testnet setting from environment
        paper_trading: Override paper trading setting from environment

    Returns:
        Configured exchange instance
    """
    # Get defaults from environment
    if exchange_name is None:
        exchange_name = os.getenv('EXCHANGE_NAME', 'okx').lower()

    if testnet is None:
        # Check exchange-specific testnet flag
        if exchange_name == 'okx':
            testnet = os.getenv('OKX_TESTNET', 'true').lower() == 'true'
        else:
            testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'

    if paper_trading is None:
        paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'

    return ExchangeFactory.create_exchange(
        exchange_name=exchange_name,
        testnet=testnet,
        paper_trading=paper_trading
    )
```

**Usage Example:**
```python
from src.common.exchange_config import get_exchange

# Simple usage (reads from .env)
exchange = get_exchange()

# Override specific settings
exchange = get_exchange(exchange_name='okx', testnet=False)
```

**Verification Steps:**
```bash
# 1. Create the file
# 2. Test import
PYTHONPATH=/home/RV414CE/test01/financial/apt python3 -c "from src.common.exchange_config import get_exchange; print('Import successful')"

# 3. Test exchange creation (requires valid API keys in .env)
PYTHONPATH=/home/RV414CE/test01/financial/apt python3 -c "
from src.common.exchange_config import get_exchange
exchange = get_exchange()
print(f'Exchange created: {exchange.id}')
print(f'Sandbox mode: {exchange.sandbox}')
"
```

**Success Criteria:**
- [ ] File created at `src/common/exchange_config.py`
- [ ] Import succeeds without errors
- [ ] Exchange creation works with testnet credentials
- [ ] Proper error messages if credentials missing

---

### Phase 2: Code Updates (45 minutes)

#### Task 2.1: Update Order Executor
**File:** `src/trading_engine/order_executor/order_executor.py`

**Changes Required:**
1. Update docstrings from "Binance US" to "OKX" or generic "exchange"
2. Update stop-loss order implementation (OKX uses different params)
3. Ensure compatibility with CCXT unified API

**Specific Changes:**

**Line 10:** Update class docstring
```python
# OLD:
class OrderExecutor:
    """Executes orders on Binance US exchange"""

# NEW:
class OrderExecutor:
    """Executes orders on configured exchange (OKX, Binance, etc.)"""
```

**Lines 84-96:** Update stop-loss implementation for OKX compatibility
```python
# OLD (Binance-specific):
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

# NEW (Exchange-agnostic with OKX support):
def place_stop_loss(self, symbol: str, amount: float, stop_price: float) -> Dict:
    """
    Place a stop-loss order

    Works with multiple exchanges via CCXT unified API.
    OKX uses 'stop_market' type, Binance uses 'stop_loss'.

    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        amount: Position size in base currency
        stop_price: Price to trigger stop loss

    Returns:
        Order details dictionary

    Raises:
        Exception: If order placement fails
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
        # Determine order type based on exchange
        exchange_id = self.exchange.id.lower()

        if exchange_id == 'okx':
            # OKX stop-loss order format
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',  # OKX uses market type with trigger price
                side='sell',
                amount=amount,
                params={
                    'stopLossPrice': stop_price,  # OKX parameter name
                    'tdMode': 'cash'  # Trade mode: cash (spot)
                }
            )
        elif exchange_id in ['binance', 'binanceus']:
            # Binance stop-loss order format
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop_loss',
                side='sell',
                amount=amount,
                params={'stopPrice': stop_price}
            )
        else:
            # Generic CCXT unified API (fallback)
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop',
                side='sell',
                amount=amount,
                price=stop_price
            )

        logger.info(f"Stop-loss placed on {exchange_id}: {order['id']}")
        return order

    except Exception as e:
        logger.error(f"Error placing stop-loss on {self.exchange.id}: {e}")
        raise
```

**Complete Updated File:**
```python
import ccxt
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Executes orders on configured exchange (OKX, Binance, etc.)"""

    def __init__(self, exchange: ccxt.Exchange, paper_trading: bool = True):
        self.exchange = exchange
        self.paper_trading = paper_trading
        self.simulated_price = 50000  # Default BTC price for paper trading

    def place_buy_order(self, symbol: str, amount: float) -> Dict:
        """
        Place a market buy order

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
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
            symbol: Trading pair (e.g., 'BTC/USDT')
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

        Works with multiple exchanges via CCXT unified API.
        OKX uses 'stop_market' type, Binance uses 'stop_loss'.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            amount: Position size in base currency
            stop_price: Price to trigger stop loss

        Returns:
            Order details dictionary

        Raises:
            Exception: If order placement fails
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
            # Determine order type based on exchange
            exchange_id = self.exchange.id.lower()

            if exchange_id == 'okx':
                # OKX stop-loss order format
                order = self.exchange.create_order(
                    symbol=symbol,
                    type='market',
                    side='sell',
                    amount=amount,
                    params={
                        'stopLossPrice': stop_price,
                        'tdMode': 'cash'  # Trade mode: cash (spot)
                    }
                )
            elif exchange_id in ['binance', 'binanceus']:
                # Binance stop-loss order format
                order = self.exchange.create_order(
                    symbol=symbol,
                    type='stop_loss',
                    side='sell',
                    amount=amount,
                    params={'stopPrice': stop_price}
                )
            else:
                # Generic CCXT unified API (fallback)
                order = self.exchange.create_order(
                    symbol=symbol,
                    type='stop',
                    side='sell',
                    amount=amount,
                    price=stop_price
                )

            logger.info(f"Stop-loss placed on {exchange_id}: {order['id']}")
            return order

        except Exception as e:
            logger.error(f"Error placing stop-loss on {self.exchange.id}: {e}")
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

**Verification Steps:**
```bash
# 1. Update the file
# 2. Check for syntax errors
python3 -m py_compile src/trading_engine/order_executor/order_executor.py

# 3. Run unit tests
PYTHONPATH=/home/RV414CE/test01/financial/apt ./venv/bin/pytest tests/unit/test_order_executor.py -v
```

**Success Criteria:**
- [ ] File updated with exchange-agnostic code
- [ ] No syntax errors
- [ ] Unit tests pass
- [ ] Stop-loss logic supports both OKX and Binance

---

#### Task 2.2: Update Trading Engine Initialization
**File:** `src/trading_engine/engine.py`

**Changes Required:**
Only need to update comments and docstrings - no functional changes needed since engine receives exchange instance as dependency.

**Line 26:** Update symbol default and comment
```python
# OLD:
def __init__(
    self,
    risk_manager: RiskManager,
    order_executor: OrderExecutor,
    position_tracker: PositionTracker,
    strategy_coordinator: StrategyCoordinator,
    db_session: Session,
    symbol: str = 'BTC/USD',  # Binance US format
    poll_interval: int = 300
):

# NEW:
def __init__(
    self,
    risk_manager: RiskManager,
    order_executor: OrderExecutor,
    position_tracker: PositionTracker,
    strategy_coordinator: StrategyCoordinator,
    db_session: Session,
    symbol: str = 'BTC/USDT',  # OKX primary pair (BTC/USD also available)
    poll_interval: int = 300
):
```

**Note:** No other changes needed in this file as it uses dependency injection.

**Verification Steps:**
```bash
# Check syntax
python3 -m py_compile src/trading_engine/engine.py
```

**Success Criteria:**
- [ ] Default symbol updated to BTC/USDT
- [ ] Comments updated
- [ ] No functional changes (maintains compatibility)

---

#### Task 2.3: Create Application Bootstrap
**File:** `src/bootstrap.py` (NEW FILE)

**Purpose:** Initialize all components with proper exchange configuration

**Complete File Contents:**
```python
"""
Application bootstrap - initializes trading system components.

Handles:
- Exchange initialization
- Component wiring with dependency injection
- Configuration from environment variables
"""

import os
import logging
from typing import Tuple
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.common.exchange_config import get_exchange
from src.trading_engine.risk_manager.risk_manager import RiskManager
from src.trading_engine.order_executor.order_executor import OrderExecutor
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.trading_engine.engine import TradingEngine
from src.database.connection import get_db_session

load_dotenv()
logger = logging.getLogger(__name__)


def create_trading_engine(db_session: Session) -> TradingEngine:
    """
    Create and configure trading engine with all dependencies

    Reads configuration from environment variables:
    - EXCHANGE_NAME (default: 'okx')
    - PAPER_TRADING (default: true)
    - TRADING_SYMBOL (default: 'BTC/USDT')
    - OKX_TESTNET (default: true)
    - INITIAL_CAPITAL, POSITION_SIZE_PERCENT, etc.

    Args:
        db_session: Database session for persistence

    Returns:
        Fully configured TradingEngine instance
    """
    # Get configuration from environment
    paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
    symbol = os.getenv('TRADING_SYMBOL', 'BTC/USDT')
    poll_interval = int(os.getenv('STRATEGY_POLL_INTERVAL', '300'))

    initial_capital = float(os.getenv('INITIAL_CAPITAL', '10000'))
    position_size_percent = float(os.getenv('POSITION_SIZE_PERCENT', '5'))
    daily_loss_limit = float(os.getenv('DAILY_LOSS_LIMIT_PERCENT', '15'))
    kill_switch_percent = float(os.getenv('KILL_SWITCH_PERCENT', '50'))

    logger.info(f"Initializing trading engine:")
    logger.info(f"  - Symbol: {symbol}")
    logger.info(f"  - Paper Trading: {paper_trading}")
    logger.info(f"  - Initial Capital: ${initial_capital}")

    # Initialize exchange
    exchange = get_exchange()
    logger.info(f"  - Exchange: {exchange.id} (sandbox: {getattr(exchange, 'sandbox', False)})")

    # Initialize components
    risk_manager = RiskManager(
        initial_capital=initial_capital,
        position_size_percent=position_size_percent,
        daily_loss_limit_percent=daily_loss_limit,
        kill_switch_percent=kill_switch_percent
    )

    order_executor = OrderExecutor(
        exchange=exchange,
        paper_trading=paper_trading
    )

    position_tracker = PositionTracker()

    strategy_coordinator = StrategyCoordinator()

    # Create trading engine
    engine = TradingEngine(
        risk_manager=risk_manager,
        order_executor=order_executor,
        position_tracker=position_tracker,
        strategy_coordinator=strategy_coordinator,
        db_session=db_session,
        symbol=symbol,
        poll_interval=poll_interval
    )

    logger.info("Trading engine initialized successfully")
    return engine


def bootstrap_application() -> Tuple[TradingEngine, Session]:
    """
    Bootstrap the entire application

    Returns:
        Tuple of (trading_engine, db_session)
    """
    logger.info("Bootstrapping application...")

    # Get database session
    db_session = next(get_db_session())

    # Create trading engine
    engine = create_trading_engine(db_session)

    logger.info("Application bootstrap complete")
    return engine, db_session
```

**Usage Example:**
```python
from src.bootstrap import bootstrap_application

# Initialize everything
engine, db_session = bootstrap_application()

# Start trading
await engine.start()
```

**Verification Steps:**
```bash
# Test import and initialization
PYTHONPATH=/home/RV414CE/test01/financial/apt python3 -c "
from src.bootstrap import create_trading_engine
from src.database.connection import get_db_session
db_session = next(get_db_session())
engine = create_trading_engine(db_session)
print(f'Engine created with symbol: {engine.symbol}')
"
```

**Success Criteria:**
- [ ] File created successfully
- [ ] Import works without errors
- [ ] Trading engine creation works
- [ ] Configuration loaded from environment

---

### Phase 3: Testing Updates (30 minutes)

#### Task 3.1: Update Unit Tests
**File:** `tests/unit/test_order_executor.py`

**Changes Required:**
Update test fixtures and assertions to be exchange-agnostic

**Complete Updated File:**
```python
import pytest
from unittest.mock import Mock, patch
from src.trading_engine.order_executor.order_executor import OrderExecutor


@pytest.fixture
def mock_okx_exchange():
    """Create mock OKX exchange for testing"""
    exchange = Mock()
    exchange.id = 'okx'
    exchange.create_market_buy_order = Mock(return_value={
        'id': '12345',
        'symbol': 'BTC/USDT',
        'type': 'market',
        'side': 'buy',
        'price': 50000,
        'amount': 0.01,
        'filled': 0.01,
        'status': 'closed'
    })
    exchange.create_market_sell_order = Mock(return_value={
        'id': '12346',
        'symbol': 'BTC/USDT',
        'type': 'market',
        'side': 'sell',
        'price': 50000,
        'amount': 0.01,
        'filled': 0.01,
        'status': 'closed'
    })
    exchange.create_order = Mock(return_value={
        'id': '12347',
        'symbol': 'BTC/USDT',
        'type': 'market',
        'side': 'sell',
        'amount': 0.01,
        'status': 'closed'
    })
    exchange.fetch_ticker = Mock(return_value={
        'last': 50000,
        'bid': 49995,
        'ask': 50005
    })
    return exchange


@pytest.fixture
def mock_binance_exchange():
    """Create mock Binance exchange for testing backward compatibility"""
    exchange = Mock()
    exchange.id = 'binance'
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


def test_place_buy_order_calls_exchange_api(mock_okx_exchange):
    """Test buy order placement calls exchange correctly"""
    executor = OrderExecutor(exchange=mock_okx_exchange, paper_trading=False)

    result = executor.place_buy_order(symbol='BTC/USDT', amount=0.01)

    assert result['id'] == '12345'
    assert result['side'] == 'buy'
    mock_okx_exchange.create_market_buy_order.assert_called_once_with('BTC/USDT', 0.01)


def test_paper_trading_mode_simulates_order():
    """Test paper trading mode doesn't call real exchange"""
    mock_exchange = Mock()
    executor = OrderExecutor(exchange=mock_exchange, paper_trading=True)

    result = executor.place_buy_order(symbol='BTC/USDT', amount=0.01)

    assert result['simulated'] is True
    assert result['side'] == 'buy'
    mock_exchange.create_market_buy_order.assert_not_called()


def test_place_sell_order_works(mock_okx_exchange):
    """Test sell order placement"""
    executor = OrderExecutor(exchange=mock_okx_exchange, paper_trading=False)

    result = executor.place_sell_order(symbol='BTC/USDT', amount=0.01)

    assert result['id'] == '12346'
    assert result['side'] == 'sell'
    mock_okx_exchange.create_market_sell_order.assert_called_once()


def test_stop_loss_order_okx_format(mock_okx_exchange):
    """Test stop-loss order uses OKX format"""
    executor = OrderExecutor(exchange=mock_okx_exchange, paper_trading=False)

    result = executor.place_stop_loss(
        symbol='BTC/USDT',
        amount=0.01,
        stop_price=48000
    )

    assert result['id'] == '12347'
    # Verify OKX-specific parameters were used
    call_args = mock_okx_exchange.create_order.call_args
    assert call_args[1]['params']['stopLossPrice'] == 48000
    assert call_args[1]['params']['tdMode'] == 'cash'


def test_stop_loss_order_binance_format(mock_binance_exchange):
    """Test stop-loss order uses Binance format for backward compatibility"""
    executor = OrderExecutor(exchange=mock_binance_exchange, paper_trading=False)

    mock_binance_exchange.create_order = Mock(return_value={
        'id': '12348',
        'type': 'stop_loss'
    })

    result = executor.place_stop_loss(
        symbol='BTC/USD',
        amount=0.01,
        stop_price=48000
    )

    # Verify Binance-specific parameters were used
    call_args = mock_binance_exchange.create_order.call_args
    assert call_args[1]['type'] == 'stop_loss'
    assert call_args[1]['params']['stopPrice'] == 48000


def test_get_current_price_from_exchange(mock_okx_exchange):
    """Test fetching current price from exchange"""
    executor = OrderExecutor(exchange=mock_okx_exchange, paper_trading=False)

    price = executor.get_current_price('BTC/USDT')

    assert price == 50000
    mock_okx_exchange.fetch_ticker.assert_called_once_with('BTC/USDT')


def test_get_current_price_paper_trading():
    """Test paper trading returns simulated price"""
    mock_exchange = Mock()
    executor = OrderExecutor(exchange=mock_exchange, paper_trading=True)

    price = executor.get_current_price('BTC/USDT')

    assert price == 50000  # Simulated price
    mock_exchange.fetch_ticker.assert_not_called()
```

**Verification Steps:**
```bash
# Run updated unit tests
PYTHONPATH=/home/RV414CE/test01/financial/apt ./venv/bin/pytest tests/unit/test_order_executor.py -v

# Expected output: All tests passing
```

**Success Criteria:**
- [ ] All unit tests pass
- [ ] Tests cover both OKX and Binance formats
- [ ] Paper trading tests still work
- [ ] Exchange-agnostic design validated

---

#### Task 3.2: Create Integration Test
**File:** `tests/integration/test_okx_integration.py` (NEW FILE)

**Purpose:** Test real OKX API integration (testnet only)

**Complete File Contents:**
```python
"""
OKX Integration Tests

Tests real OKX API integration using testnet/sandbox.
Requires valid OKX testnet credentials in .env file.

Run with: pytest tests/integration/test_okx_integration.py -v -s
"""

import pytest
import os
from dotenv import load_dotenv
from src.common.exchange_config import get_exchange
from src.trading_engine.order_executor.order_executor import OrderExecutor

load_dotenv()

# Skip if no OKX credentials configured
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('OKX_API_KEY'),
        os.getenv('OKX_API_SECRET'),
        os.getenv('OKX_API_PASSPHRASE')
    ]),
    reason="OKX credentials not configured"
)


@pytest.fixture
def okx_exchange():
    """Create real OKX exchange instance (testnet)"""
    return get_exchange(exchange_name='okx', testnet=True)


@pytest.fixture
def okx_executor(okx_exchange):
    """Create order executor with OKX testnet exchange"""
    # Use paper trading to avoid real testnet orders
    return OrderExecutor(exchange=okx_exchange, paper_trading=True)


def test_okx_exchange_initialization(okx_exchange):
    """Test that OKX exchange initializes correctly"""
    assert okx_exchange.id == 'okx'
    assert hasattr(okx_exchange, 'apiKey')
    # Testnet/sandbox should be enabled
    # Note: OKX sandbox detection varies, so we just test it doesn't error


def test_fetch_ticker_from_okx(okx_exchange):
    """Test fetching real ticker data from OKX"""
    ticker = okx_exchange.fetch_ticker('BTC/USDT')

    assert 'last' in ticker
    assert 'bid' in ticker
    assert 'ask' in ticker
    assert ticker['last'] > 0
    assert ticker['bid'] > 0
    assert ticker['ask'] > 0
    # Sanity check: BTC price should be reasonable
    assert 10000 < ticker['last'] < 200000


def test_fetch_order_book_from_okx(okx_exchange):
    """Test fetching order book from OKX"""
    orderbook = okx_exchange.fetch_order_book('BTC/USDT', limit=5)

    assert 'bids' in orderbook
    assert 'asks' in orderbook
    assert len(orderbook['bids']) > 0
    assert len(orderbook['asks']) > 0

    # Verify bid/ask structure [price, amount]
    assert len(orderbook['bids'][0]) >= 2
    assert len(orderbook['asks'][0]) >= 2


def test_fetch_balance_from_okx(okx_exchange):
    """Test fetching account balance from OKX testnet"""
    try:
        balance = okx_exchange.fetch_balance()
        assert 'total' in balance
        assert 'free' in balance
        # Testnet might have zero balance, that's okay
    except Exception as e:
        # Some testnet accounts might not have balance access
        pytest.skip(f"Balance fetch not available: {e}")


def test_get_current_price(okx_executor):
    """Test getting current price through executor"""
    # Paper trading mode - returns simulated price
    price = okx_executor.get_current_price('BTC/USDT')
    assert price == 50000  # Simulated price in paper trading


def test_paper_trading_order_simulation(okx_executor):
    """Test that paper trading doesn't hit real API"""
    # This should be simulated, not real
    order = okx_executor.place_buy_order('BTC/USDT', 0.001)

    assert order['simulated'] is True
    assert order['symbol'] == 'BTC/USDT'
    assert order['side'] == 'buy'
    assert order['amount'] == 0.001


@pytest.mark.skipif(
    os.getenv('ALLOW_TESTNET_ORDERS', 'false').lower() != 'true',
    reason="Testnet orders disabled (set ALLOW_TESTNET_ORDERS=true to enable)"
)
def test_real_testnet_market_order():
    """
    Test placing real order on OKX testnet

    WARNING: This test places a real order on OKX testnet.
    Only runs if ALLOW_TESTNET_ORDERS=true in environment.
    """
    exchange = get_exchange(exchange_name='okx', testnet=True)
    executor = OrderExecutor(exchange=exchange, paper_trading=False)

    # Very small test order
    try:
        order = executor.place_buy_order('BTC/USDT', 0.0001)
        assert 'id' in order
        assert order['status'] in ['open', 'closed']
    except Exception as e:
        pytest.fail(f"Testnet order failed: {e}")
```

**Verification Steps:**
```bash
# Run integration tests (requires testnet credentials)
PYTHONPATH=/home/RV414CE/test01/financial/apt ./venv/bin/pytest tests/integration/test_okx_integration.py -v -s

# If credentials not configured, tests should skip gracefully
```

**Success Criteria:**
- [ ] Tests created
- [ ] Tests skip if no credentials
- [ ] Ticker fetch works with real OKX testnet
- [ ] Paper trading simulation works
- [ ] No real orders placed unless explicitly allowed

---

### Phase 4: Documentation Updates (30 minutes)

#### Task 4.1: Update README.md
**File:** `README.md`

**Changes Required:**
Update setup instructions, features, and API references

**Complete Updated README:**
```markdown
# Bitcoin Autotrader (OKX Edition)

Automated Bitcoin trading system with AI analysis, technical indicators, and real-time mobile dashboard.

**Exchange:** OKX (OKEX) - Industry-leading cryptocurrency exchange
**Trading Mode:** Spot trading with automated strategies

## Features

- **Exchange Integration:** OKX API with CCXT unified interface
- **AI Analysis:** DeepSeek AI for market sentiment and pattern recognition
- **Technical Indicators:** RSI, MACD, moving averages, and more
- **News Monitoring:** Real-time crypto news event tracking
- **Risk Management:** Position sizing, daily loss limits, kill switch
- **Dashboard:** Mobile-friendly web interface with real-time updates
- **Backtesting:** Historical strategy performance analysis
- **Paper Trading:** Risk-free testing mode with simulated orders
- **Multi-Exchange Support:** Easily switch between OKX, Binance, and others

## Why OKX?

- ✅ Lower fees: 0.08% maker / 0.10% taker (vs Binance 0.10%/0.10%)
- ✅ Higher rate limits: 2400 req/min (vs Binance 1200 req/min)
- ✅ Better liquidity on major pairs
- ✅ Advanced order types and trading features
- ✅ Global access without restrictions
- ✅ Unified API for spot, futures, and options

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OKX account with API credentials
- PostgreSQL (via Docker)
- Redis (via Docker)

### 1. Get OKX API Credentials

1. Sign up at [OKX.com](https://www.okx.com)
2. Navigate to **API Management** in account settings
3. Create new API key with permissions:
   - ✅ **Trade** - For order placement
   - ✅ **Read** - For market data
   - ❌ **Withdraw** - Keep disabled for security
4. Save your credentials:
   - API Key
   - Secret Key
   - Passphrase (required for OKX)
5. ⚠️ **Optional:** Whitelist your server IP for added security

### 2. Configure Environment

```bash
# Clone repository
git clone <repo-url>
cd apt

# Create environment file from template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required .env Configuration:**
```bash
# OKX API Credentials
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_secret_key_here
OKX_API_PASSPHRASE=your_okx_passphrase_here
OKX_TESTNET=true  # Use testnet for testing, false for live trading

# Trading Configuration
TRADING_SYMBOL=BTC/USDT  # Primary OKX pair
PAPER_TRADING=true       # Enable paper trading mode
INITIAL_CAPITAL=10000    # Starting capital in USD

# Risk Management
POSITION_SIZE_PERCENT=5          # % of capital per trade
DAILY_LOSS_LIMIT_PERCENT=15     # Max daily loss %
KILL_SWITCH_PERCENT=50          # Emergency stop threshold

# AI & News (Optional)
DEEPSEEK_API_KEY=your_deepseek_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

### 3. Deploy with Docker (Recommended)

```bash
# One-command deployment
chmod +x deploy.sh
./deploy.sh
```

The deployment script will:
- ✅ Install Docker and Docker Compose (if needed)
- ✅ Build application containers
- ✅ Start PostgreSQL, Redis, and trading engine
- ✅ Initialize database schema
- ✅ Verify all services are running

**Services Started:**
- API Server: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 4. Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start database services
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Build Frontend Dashboard

```bash
cd frontend
npm install
npm run build
npm start  # Development server on http://localhost:3000
```

## Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/ -v              # Unit tests
pytest tests/integration/ -v       # Integration tests

# Run with coverage
pytest --cov=src --cov-report=html

# Test OKX integration (requires testnet credentials)
pytest tests/integration/test_okx_integration.py -v -s
```

## Usage

### Paper Trading (Recommended for Testing)

1. Set `PAPER_TRADING=true` in `.env`
2. Set `OKX_TESTNET=true` for sandbox environment
3. Start the application
4. Monitor via API docs: http://localhost:8000/docs
5. Check logs: `docker-compose logs -f trading-engine`

### Live Trading (Use with Caution)

⚠️ **WARNING:** Live trading involves real money. Start small and monitor closely.

1. Set `PAPER_TRADING=false` in `.env`
2. Set `OKX_TESTNET=false` for production
3. Start with small `INITIAL_CAPITAL` and `POSITION_SIZE_PERCENT`
4. Monitor the dashboard and logs continuously
5. Be prepared to stop the bot if needed: `docker-compose down`

### API Endpoints

Once running, explore the API at http://localhost:8000/docs

**Key Endpoints:**
- `GET /` - Health check
- `GET /api/v1/stats` - Trading statistics
- `GET /api/v1/positions` - Current positions
- `GET /api/v1/trades` - Trade history
- `WebSocket /ws` - Real-time updates

## Configuration

### Trading Symbols

OKX supports multiple trading pairs:
```bash
TRADING_SYMBOL=BTC/USDT   # Most liquid (recommended)
TRADING_SYMBOL=BTC/USD    # USD stablecoin pair
TRADING_SYMBOL=ETH/USDT   # Ethereum
```

### Strategy Configuration

Edit strategy weights in `src/trading_engine/strategy_coordinator/coordinator.py`:
```python
strategies = [
    TechnicalIndicatorsStrategy(),  # Weight: 0.3
    # Add more strategies here
]
```

### Risk Management

Adjust in `.env`:
```bash
POSITION_SIZE_PERCENT=5      # Conservative: 2-5%, Aggressive: 10-15%
DAILY_LOSS_LIMIT_PERCENT=15  # Stop trading if daily loss exceeds this
KILL_SWITCH_PERCENT=50       # Emergency stop - closes all positions
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Trading Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Strategy   │──────│   Strategy   │                     │
│  │ Coordinator  │      │  Plugins     │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                                                     │
│  ┌──────▼──────┐      ┌──────────────┐                     │
│  │    Risk     │      │    Order     │◄──── OKX API        │
│  │  Manager    │──────│  Executor    │                     │
│  └─────────────┘      └──────────────┘                     │
│         │                                                     │
│  ┌──────▼──────┐      ┌──────────────┐                     │
│  │  Position   │      │   Database   │                     │
│  │   Tracker   │──────│  (Postgres)  │                     │
│  └─────────────┘      └──────────────┘                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│              WebSocket + REST API Endpoints                  │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard                           │
│            Real-time Trading Visualization                   │
└─────────────────────────────────────────────────────────────┘
```

See [docs/plans/2025-10-22-bitcoin-autotrading-design.md](docs/plans/2025-10-22-bitcoin-autotrading-design.md) for detailed architecture.

## Monitoring & Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f trading-engine

# Recent logs only
docker-compose logs --tail=100 -f
```

### Stop/Start Services

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Restart specific service
docker-compose restart trading-engine

# Rebuild after code changes
docker-compose up -d --build
```

### Database Access

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d bitcoin_trader

# View tables
\dt

# Query trades
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

# Query positions
SELECT * FROM positions WHERE status = 'open';
```

## Switching Exchanges

The system supports multiple exchanges via CCXT. To switch:

1. Update `.env`:
```bash
EXCHANGE_NAME=binance  # Options: okx, binance, binanceus
```

2. Add exchange credentials:
```bash
# For Binance
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=true
```

3. Update trading symbol if needed:
```bash
TRADING_SYMBOL=BTC/USD  # Binance US uses USD
```

## Security Best Practices

- ✅ Never commit `.env` file with real credentials
- ✅ Use testnet/paper trading for initial testing
- ✅ Enable IP whitelisting on OKX API keys
- ✅ Disable withdraw permission on API keys
- ✅ Start with small capital amounts
- ✅ Monitor closely during live trading
- ✅ Set conservative risk management limits
- ✅ Use strong, unique API passphrases
- ✅ Regularly rotate API keys
- ❌ Never share API credentials

## Troubleshooting

### API Connection Errors

```bash
# Test OKX API connectivity
python3 -c "
from src.common.exchange_config import get_exchange
exchange = get_exchange(exchange_name='okx', testnet=True)
print(exchange.fetch_ticker('BTC/USDT'))
"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Rebuild database
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

### Docker Issues

```bash
# Check Docker daemon
docker ps

# Free up space
docker system prune -a

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `pytest`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open pull request

## License

[Your License Here]

## Disclaimer

⚠️ **IMPORTANT:** This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Never invest more than you can afford to lose. The authors are not responsible for any financial losses incurred through use of this software.

**Use at your own risk.**

## Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with:** Python, FastAPI, React, PostgreSQL, Redis, CCXT, Docker

**Exchange:** OKX (OKEX) - Professional cryptocurrency trading platform
```

**Verification Steps:**
```bash
# View rendered markdown (optional)
# No verification needed - just update the file
```

**Success Criteria:**
- [ ] README updated with OKX references
- [ ] Setup instructions include OKX API key generation
- [ ] Features list updated
- [ ] Security warnings in place

---

#### Task 4.2: Update Design Documentation
**File:** `docs/plans/2025-10-22-bitcoin-autotrading-design.md`

**Changes Required:**
Find and replace Binance references with OKX or exchange-agnostic language

**Specific Changes:**
```bash
# Use sed to update all Binance references
sed -i 's/Binance US/OKX/g' docs/plans/2025-10-22-bitcoin-autotrading-design.md
sed -i 's/Binance/OKX/g' docs/plans/2025-10-22-bitcoin-autotrading-design.md
sed -i 's/BTC\/USD/BTC\/USDT/g' docs/plans/2025-10-22-bitcoin-autotrading-design.md
```

**Manual Review Areas:**
- Exchange API sections
- Trading pair formats
- API rate limits
- WebSocket endpoints

**Verification Steps:**
```bash
# Check for remaining Binance references
grep -i "binance" docs/plans/2025-10-22-bitcoin-autotrading-design.md

# Should return no results or only in historical context
```

**Success Criteria:**
- [ ] All Binance references updated to OKX
- [ ] Trading pairs updated to USDT format
- [ ] Architecture diagrams still valid
- [ ] No broken references

---

### Phase 5: Deployment & Verification (45 minutes)

#### Task 5.1: Update Deployment Configuration
**File:** `deploy.sh`

**Changes Required:**
Update deployment script messages and checks

**Line 5:** Update banner
```bash
# OLD:
echo "=== Bitcoin Autotrader Deployment ==="

# NEW:
echo "=== Bitcoin Autotrader (OKX Edition) Deployment ==="
```

**Lines 8-13:** Update environment check message
```bash
# OLD:
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before continuing"
    exit 1
fi

# NEW:
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your OKX API credentials before continuing"
    echo "    Required: OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE"
    exit 1
fi

# Add OKX credentials check
echo "Checking OKX credentials..."
if ! grep -q "OKX_API_KEY=your_okx" .env 2>/dev/null; then
    if grep -q "OKX_API_KEY=.*[a-zA-Z0-9]" .env 2>/dev/null; then
        echo "✅ OKX credentials configured"
    else
        echo "❌ OKX credentials not configured"
        echo "   Please edit .env and add your OKX API credentials"
        exit 1
    fi
else
    echo "❌ Please replace placeholder values in .env with real OKX credentials"
    exit 1
fi
```

**Complete Updated deploy.sh:**
```bash
#!/bin/bash

set -e  # Exit on error

echo "=== Bitcoin Autotrader (OKX Edition) Deployment ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your OKX API credentials before continuing"
    echo "    Required: OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE"
    exit 1
fi

# Check OKX credentials are configured
echo "Checking OKX credentials..."
if grep -q "OKX_API_KEY=your_okx" .env 2>/dev/null; then
    echo "❌ Please replace placeholder values in .env with real OKX credentials"
    echo "   Get credentials from: https://www.okx.com/account/my-api"
    exit 1
fi

if ! grep -q "OKX_API_KEY=.*[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "❌ OKX_API_KEY not configured in .env"
    exit 1
fi

if ! grep -q "OKX_API_SECRET=.*[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "❌ OKX_API_SECRET not configured in .env"
    exit 1
fi

if ! grep -q "OKX_API_PASSPHRASE=.*[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "❌ OKX_API_PASSPHRASE not configured in .env"
    exit 1
fi

echo "✅ OKX credentials configured"

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
echo "Exchange: OKX (sandbox mode: see OKX_TESTNET in .env)"
echo "Paper Trading: see PAPER_TRADING in .env"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
echo "⚠️  Remember: Start with paper trading and testnet before going live!"
```

**Verification Steps:**
```bash
# Test deployment script syntax
bash -n deploy.sh

# Check for shellcheck issues (if installed)
shellcheck deploy.sh || echo "shellcheck not installed, skipping"
```

**Success Criteria:**
- [ ] Script updated with OKX references
- [ ] Credential checks added
- [ ] Helpful error messages
- [ ] No syntax errors

---

#### Task 5.2: Create Initialization Script
**File:** `scripts/init_db.py` (NEW FILE)

**Purpose:** Initialize database schema on first deployment

**Complete File Contents:**
```python
"""
Database initialization script

Creates all tables and initial data for the trading system.
Safe to run multiple times (idempotent).
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import engine, init_database
from src.database.models.base import Base
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database schema"""
    logger.info("Starting database initialization...")

    try:
        # Initialize database (creates tables if not exist)
        init_database()

        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info(f"Database initialized successfully. Tables created: {len(tables)}")
        for table in tables:
            logger.info(f"  - {table}")

        expected_tables = ['trades', 'positions', 'daily_stats', 'system_logs']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            logger.warning(f"Missing expected tables: {missing_tables}")
            return 1

        logger.info("✅ Database ready for trading")
        return 0

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Verification Steps:**
```bash
# Test script locally
PYTHONPATH=/home/RV414CE/test01/financial/apt python3 scripts/init_db.py
```

**Success Criteria:**
- [ ] Script created
- [ ] Creates all database tables
- [ ] Idempotent (safe to run multiple times)
- [ ] Proper error handling

---

#### Task 5.3: End-to-End Verification Test
**Purpose:** Verify entire system works with OKX

**Pre-requisites:**
- [ ] OKX testnet credentials in `.env`
- [ ] Docker and Docker Compose installed
- [ ] All code changes completed

**Test Procedure:**

**Step 1: Clean Environment**
```bash
cd /home/RV414CE/test01/financial/apt

# Stop any running containers
docker-compose down -v

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
```

**Step 2: Configure OKX Credentials**
```bash
# Create .env from template
cp .env.example .env

# Edit with your OKX testnet credentials
nano .env

# Verify required variables are set
grep "OKX_API" .env | grep -v "your_okx"
# Should show your actual credentials (not placeholder values)
```

**Step 3: Run Unit Tests**
```bash
# Activate virtual environment
source venv/bin/activate

# Run all unit tests
PYTHONPATH=/home/RV414CE/test01/financial/apt pytest tests/unit/ -v

# Expected: All tests pass
```

**Step 4: Test OKX Integration**
```bash
# Run OKX integration tests
PYTHONPATH=/home/RV414CE/test01/financial/apt pytest tests/integration/test_okx_integration.py -v -s

# Expected:
#   - Tests pass if credentials valid
#   - Tests skip if credentials not configured
```

**Step 5: Test Exchange Initialization**
```bash
# Test exchange configuration module
PYTHONPATH=/home/RV414CE/test01/financial/apt python3 -c "
from src.common.exchange_config import get_exchange

print('Testing OKX exchange initialization...')
exchange = get_exchange(exchange_name='okx', testnet=True)
print(f'✅ Exchange: {exchange.id}')
print(f'✅ Sandbox mode: {getattr(exchange, \"sandbox\", \"unknown\")}')

print('\nTesting ticker fetch...')
ticker = exchange.fetch_ticker('BTC/USDT')
print(f'✅ BTC/USDT price: \${ticker[\"last\"]:.2f}')

print('\nTesting order executor...')
from src.trading_engine.order_executor.order_executor import OrderExecutor
executor = OrderExecutor(exchange=exchange, paper_trading=True)
order = executor.place_buy_order('BTC/USDT', 0.001)
print(f'✅ Simulated order: {order[\"id\"]}')

print('\n✅ All initialization tests passed!')
"
```

**Step 6: Deploy with Docker**
```bash
# Run deployment script
chmod +x deploy.sh
./deploy.sh

# Expected output:
#   - ✅ OKX credentials configured
#   - Building Docker images...
#   - Starting services...
#   - Database initialized...
#   - Deployment Complete
```

**Step 7: Verify Services Running**
```bash
# Check all containers are running
docker-compose ps

# Expected: All services "Up"
#   - postgres
#   - redis
#   - trading-engine

# Check API is responding
curl http://localhost:8000
# Expected: {"status":"ok","service":"Bitcoin Autotrader"}

# Check API docs are accessible
curl http://localhost:8000/docs
# Expected: HTML response (OpenAPI docs)
```

**Step 8: Check Application Logs**
```bash
# View trading engine logs
docker-compose logs trading-engine

# Look for:
#   - "Application started"
#   - "Exchange: okx"
#   - "Sandbox mode: True" (if testnet enabled)
#   - No error messages
```

**Step 9: Test API Endpoints**
```bash
# Test health check
curl http://localhost:8000/

# Test API endpoints (if implemented)
curl http://localhost:8000/api/v1/stats

# Test WebSocket connection
# (Use browser or wscat tool)
```

**Step 10: Monitor Trading Engine**
```bash
# Follow logs in real-time
docker-compose logs -f trading-engine

# Look for:
#   - Trading cycle messages (every 5 minutes by default)
#   - Signal generation
#   - Paper trading order simulations
#   - No exceptions or errors
```

**Success Criteria:**
- [ ] All unit tests pass
- [ ] OKX integration tests pass
- [ ] Exchange initialization works
- [ ] Docker deployment succeeds
- [ ] All containers running
- [ ] API endpoints responding
- [ ] No errors in logs
- [ ] Trading engine operational

**If Issues Occur:**
```bash
# View detailed logs
docker-compose logs --tail=100

# Check specific service
docker-compose logs trading-engine

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

---

## Testing Strategy

### Test Levels

**1. Unit Tests (Phase 3)**
- Order executor with mocked exchanges
- Exchange configuration module
- Risk manager calculations
- Strategy logic

**2. Integration Tests (Phase 3)**
- Real OKX API calls (testnet)
- Database operations
- End-to-end order flow

**3. System Tests (Phase 5)**
- Full Docker deployment
- Multi-component interaction
- Paper trading simulation

### Test Environments

**Local Development:**
```bash
PAPER_TRADING=true
OKX_TESTNET=true
EXCHANGE_NAME=okx
```

**Staging/Testing:**
```bash
PAPER_TRADING=true
OKX_TESTNET=false  # Real market data
EXCHANGE_NAME=okx
```

**Production:**
```bash
PAPER_TRADING=false  # Real trading
OKX_TESTNET=false
EXCHANGE_NAME=okx
```

### Regression Testing

Before deploying to production:
```bash
# Run all tests
pytest tests/ -v

# Check code quality
black --check src/
pylint src/

# Verify Docker build
docker-compose build

# Test deployment script
./deploy.sh
```

---

## Rollback Plan

If issues arise after migration, rollback to Binance:

### Quick Rollback (Emergency)

```bash
# 1. Stop current deployment
docker-compose down

# 2. Revert .env to Binance
cat > .env << EOF
EXCHANGE_NAME=binance
BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret
BINANCE_TESTNET=true
PAPER_TRADING=true
TRADING_SYMBOL=BTC/USD
# ... other config ...
EOF

# 3. Restart
docker-compose up -d
```

### Git Rollback

```bash
# If you committed OKX changes
git log --oneline  # Find commit before migration
git revert <commit-hash>  # Revert migration commit

# Or reset to before migration
git reset --hard <commit-before-migration>
```

### Code Rollback

The system is designed to be exchange-agnostic via CCXT, so both Binance and OKX can coexist:

1. Keep `src/common/exchange_config.py` (supports both)
2. Revert `.env` to Binance credentials
3. Update `EXCHANGE_NAME=binance`
4. Restart application

**No code changes needed** - just configuration!

---

## Post-Migration Checklist

After completing all tasks:

### Functionality Verification
- [ ] Paper trading works with OKX testnet
- [ ] Market data fetching works (ticker, OHLCV)
- [ ] Order placement simulated correctly
- [ ] Stop-loss orders formatted correctly
- [ ] Risk management limits enforced
- [ ] Database operations work
- [ ] Dashboard displays data correctly
- [ ] WebSocket updates work

### Code Quality
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] No linting errors
- [ ] Code formatted with Black
- [ ] No hardcoded Binance references
- [ ] Logging messages updated

### Documentation
- [ ] README reflects OKX setup
- [ ] API docs updated
- [ ] Design docs updated
- [ ] This migration plan archived

### Deployment
- [ ] Docker Compose works
- [ ] Deployment script works
- [ ] Environment variables documented
- [ ] Database migrations work
- [ ] Secrets properly configured

### Security
- [ ] API keys not committed to git
- [ ] .env in .gitignore
- [ ] Testnet used for initial testing
- [ ] Paper trading enabled by default
- [ ] Withdraw permissions disabled on API keys

---

## Timeline Estimate

| Phase | Tasks | Time | Dependencies |
|-------|-------|------|--------------|
| Phase 1 | Environment & Config | 30 min | OKX account, API keys |
| Phase 2 | Code Updates | 45 min | Phase 1 |
| Phase 3 | Testing Updates | 30 min | Phase 2 |
| Phase 4 | Documentation | 30 min | Phase 3 |
| Phase 5 | Deployment & Verification | 45 min | Phase 4 |
| **Total** | **15 tasks** | **3 hours** | Sequential |

**Buffer:** +1 hour for troubleshooting = **4 hours total**

---

## Success Metrics

### Technical Metrics
- ✅ 100% unit tests passing
- ✅ 100% integration tests passing
- ✅ Zero runtime errors in logs
- ✅ API response time < 100ms
- ✅ Order execution latency < 500ms

### Business Metrics
- ✅ Paper trading orders execute successfully
- ✅ Real-time price data accurate
- ✅ Risk limits enforced correctly
- ✅ Dashboard displays correct data
- ✅ No data loss during migration

---

## Support & Resources

### OKX Documentation
- API Docs: https://www.okx.com/docs-v5/en/
- API Management: https://www.okx.com/account/my-api
- Testnet: https://www.okx.com/support/hc/en-us/articles/360043816193

### CCXT Documentation
- OKX Exchange: https://docs.ccxt.com/#/exchanges/okx
- Unified API: https://docs.ccxt.com/#/README?id=unified-api

### Internal Resources
- Design Doc: `docs/plans/2025-10-22-bitcoin-autotrading-design.md`
- Implementation Guide: `docs/plans/2025-10-22-bitcoin-autotrader-implementation.md`

---

## Notes for Engineer

### Critical Considerations
1. **API Passphrase:** OKX requires a passphrase in addition to API key/secret
2. **Trading Pairs:** OKX primarily uses USDT pairs (BTC/USDT vs BTC/USD)
3. **Stop-Loss Format:** Different parameter names between exchanges
4. **Rate Limits:** OKX has different rate limits (higher than Binance)
5. **Testnet Setup:** OKX sandbox mode works differently than Binance testnet

### Common Pitfalls
- ❌ Forgetting API passphrase in configuration
- ❌ Using BTC/USD instead of BTC/USDT
- ❌ Not enabling sandbox mode for testnet
- ❌ Using Binance-specific order parameters with OKX
- ❌ Testing with live API before testnet validation

### Best Practices
- ✅ Test with testnet first, then paper trading, then small live amounts
- ✅ Keep both Binance and OKX configurations for easy switching
- ✅ Log all API calls for debugging
- ✅ Monitor rate limits proactively
- ✅ Use CCXT unified API for maximum portability

---

**End of Implementation Plan**

This plan provides bite-sized, actionable tasks with exact code snippets, file paths, and verification steps. Follow each phase sequentially for a smooth migration from Binance to OKX.
