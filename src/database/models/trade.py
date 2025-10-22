from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum
from src.database.models.base import Base, TimestampMixin
from datetime import datetime
import enum


class TradeType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Trade(Base, TimestampMixin):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    type = Column(Enum(TradeType), nullable=False)
    amount = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    strategy_signals = Column(JSON, nullable=True)
    reasoning = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, type={self.type}, amount={self.amount})>"
