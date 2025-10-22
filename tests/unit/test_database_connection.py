import pytest
from src.database.connection import get_database_url, create_engine_from_config


def test_get_database_url_returns_valid_url():
    """Test that database URL is correctly formatted"""
    url = get_database_url()
    assert url is not None
    assert url.startswith("postgresql://")


def test_create_engine_returns_sqlalchemy_engine():
    """Test that engine creation returns valid SQLAlchemy engine"""
    engine = create_engine_from_config()
    assert engine is not None
    assert hasattr(engine, 'connect')
