import pytest
from datetime import datetime
from src.database.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_base_model_can_be_created():
    """Test that SQLAlchemy base can be instantiated"""
    assert Base is not None
    assert hasattr(Base, 'metadata')


from src.database.models.trade import Trade


def test_trade_model_has_required_fields():
    """Test Trade model has all required fields"""
    assert hasattr(Trade, 'id')
    assert hasattr(Trade, 'timestamp')
    assert hasattr(Trade, 'symbol')
    assert hasattr(Trade, 'type')
    assert hasattr(Trade, 'amount')
    assert hasattr(Trade, 'entry_price')
    assert hasattr(Trade, 'exit_price')
    assert hasattr(Trade, 'profit_loss')
    assert hasattr(Trade, 'strategy_signals')
    assert hasattr(Trade, 'reasoning')
