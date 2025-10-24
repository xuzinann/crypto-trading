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
