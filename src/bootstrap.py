"""
Application bootstrap - initializes trading system components.

Handles:
- Exchange initialization
- Component wiring with dependency injection
- Configuration from environment variables
"""

import os
import logging
from typing import Tuple
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.common.exchange_config import get_exchange
from src.trading_engine.risk_manager.risk_manager import RiskManager
from src.trading_engine.order_executor.order_executor import OrderExecutor
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.trading_engine.engine import TradingEngine
from src.database.connection import get_db
from src.ai_strategy.strategies.technical_indicators import TechnicalIndicatorsStrategy

load_dotenv()
logger = logging.getLogger(__name__)


def create_trading_engine(db_session: Session) -> TradingEngine:
    """
    Create and configure trading engine with all dependencies

    Reads configuration from environment variables:
    - EXCHANGE_NAME (default: 'okx')
    - PAPER_TRADING (default: true)
    - TRADING_SYMBOL (default: 'BTC/USDT')
    - OKX_TESTNET (default: true)
    - INITIAL_CAPITAL, POSITION_SIZE_PERCENT, etc.

    Args:
        db_session: Database session for persistence

    Returns:
        Fully configured TradingEngine instance
    """
    # Get configuration from environment
    paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
    symbol = os.getenv('TRADING_SYMBOL', 'BTC/USDT')
    poll_interval = int(os.getenv('STRATEGY_POLL_INTERVAL', '300'))

    initial_capital = float(os.getenv('INITIAL_CAPITAL', '10000'))
    position_size_percent = float(os.getenv('POSITION_SIZE_PERCENT', '5'))
    daily_loss_limit = float(os.getenv('DAILY_LOSS_LIMIT_PERCENT', '15'))
    kill_switch_percent = float(os.getenv('KILL_SWITCH_PERCENT', '50'))

    logger.info(f"Initializing trading engine:")
    logger.info(f"  - Symbol: {symbol}")
    logger.info(f"  - Paper Trading: {paper_trading}")
    logger.info(f"  - Initial Capital: ${initial_capital}")

    # Initialize exchange
    exchange = get_exchange()
    logger.info(f"  - Exchange: {exchange.id} (sandbox: {getattr(exchange, 'sandbox', False)})")

    # Initialize components
    risk_manager = RiskManager(
        initial_capital=initial_capital,
        position_size_percent=position_size_percent,
        daily_loss_limit_percent=daily_loss_limit,
        kill_switch_percent=kill_switch_percent
    )

    order_executor = OrderExecutor(
        exchange=exchange,
        paper_trading=paper_trading
    )

    position_tracker = PositionTracker()

    # Initialize strategies
    strategies = [
        TechnicalIndicatorsStrategy(),
        # Add more strategies here as needed
    ]

    strategy_coordinator = StrategyCoordinator(strategies=strategies)

    # Create trading engine
    engine = TradingEngine(
        risk_manager=risk_manager,
        order_executor=order_executor,
        position_tracker=position_tracker,
        strategy_coordinator=strategy_coordinator,
        db_session=db_session,
        symbol=symbol,
        poll_interval=poll_interval
    )

    logger.info("Trading engine initialized successfully")
    return engine


def bootstrap_application() -> Tuple[TradingEngine, Session]:
    """
    Bootstrap the entire application

    Returns:
        Tuple of (trading_engine, db_session)
    """
    logger.info("Bootstrapping application...")

    # Get database session
    db_session = next(get_db())

    # Create trading engine
    engine = create_trading_engine(db_session)

    logger.info("Application bootstrap complete")
    return engine, db_session
