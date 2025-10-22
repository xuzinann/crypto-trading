from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from src.database.models.base import Base
from datetime import datetime
import enum


class LogLevel(enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class SystemLog(Base):
    __tablename__ = 'system_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(Enum(LogLevel), nullable=False, index=True)
    component = Column(String(100), nullable=False, index=True)
    message = Column(String(1000), nullable=False)
    details = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<SystemLog(level={self.level}, component={self.component}, message={self.message[:50]})>"
