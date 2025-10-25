"""
Database migration to add backtest tables

Run with: python src/database/migrations/add_backtest_tables.py
"""
from sqlalchemy import create_engine
from src.database.connection import get_database_url
from src.database.models.base import Base
from src.database.models.historical_price import HistoricalPrice
from src.database.models.backtest_result import BacktestResult


def run_migration():
    """Create backtest tables in database"""
    database_url = get_database_url()
    engine = create_engine(database_url)

    # Create tables
    Base.metadata.create_all(engine, tables=[
        HistoricalPrice.__table__,
        BacktestResult.__table__
    ])

    print("✅ Migration complete: backtest tables created")


if __name__ == "__main__":
    run_migration()
