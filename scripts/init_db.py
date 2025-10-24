"""
Database initialization script

Creates all tables and initial data for the trading system.
Safe to run multiple times (idempotent).
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import create_engine_from_config, init_database
from src.database.models.base import Base
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database schema"""
    logger.info("Starting database initialization...")

    try:
        # Initialize database (creates tables if not exist)
        init_database()

        # Verify tables were created
        engine = create_engine_from_config()
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info(f"Database initialized successfully. Tables created: {len(tables)}")
        for table in tables:
            logger.info(f"  - {table}")

        expected_tables = ['trades', 'positions', 'daily_stats', 'system_logs']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            logger.warning(f"Missing expected tables: {missing_tables}")
            return 1

        logger.info("✅ Database ready for trading")
        return 0

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
