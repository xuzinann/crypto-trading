import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Get database URL from environment or use default"""
    return os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/bitcoin_trader')


def create_engine_from_config():
    """Create SQLAlchemy engine from configuration"""
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL query logging
    )
    return engine


def get_session_maker():
    """Create session maker for database operations"""
    engine = create_engine_from_config()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    SessionLocal = get_session_maker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables"""
    from src.database.models.base import Base
    from src.database.models.trade import Trade
    from src.database.models.position import Position
    from src.database.models.daily_stats import DailyStats
    from src.database.models.system_log import SystemLog

    engine = create_engine_from_config()
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
