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
