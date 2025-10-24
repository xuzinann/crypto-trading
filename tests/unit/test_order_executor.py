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
