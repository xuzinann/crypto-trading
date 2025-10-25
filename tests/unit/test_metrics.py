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
