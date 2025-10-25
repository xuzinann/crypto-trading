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
    extra_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<BacktestResult(symbol={self.symbol}, strategy={self.strategy_name}, return={self.total_return_pct}%)>"
