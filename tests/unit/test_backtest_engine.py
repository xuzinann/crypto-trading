from datetime import datetime
from unittest.mock import Mock
import pandas as pd
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
