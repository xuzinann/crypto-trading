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
