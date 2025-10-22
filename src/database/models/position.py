from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from src.database.models.base import Base, TimestampMixin
from datetime import datetime
import enum


class PositionStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Position(Base, TimestampMixin):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    entry_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, default=0.0)
    stop_loss_price = Column(Float, nullable=False)
    status = Column(Enum(PositionStatus), default=PositionStatus.OPEN, nullable=False, index=True)

    def __repr__(self):
        return f"<Position(id={self.id}, symbol={self.symbol}, status={self.status}, pnl={self.unrealized_pnl})>"
