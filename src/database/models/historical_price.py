from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from src.database.models.base import Base, TimestampMixin
from datetime import datetime


class HistoricalPrice(Base, TimestampMixin):
    __tablename__ = 'historical_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
    )

    def __repr__(self):
        return f"<HistoricalPrice(symbol={self.symbol}, timeframe={self.timeframe}, timestamp={self.timestamp})>"
