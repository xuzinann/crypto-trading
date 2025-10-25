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
