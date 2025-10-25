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
