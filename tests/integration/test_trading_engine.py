import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.trading_engine.engine import TradingEngine
from src.trading_engine.risk_manager.risk_manager import RiskManager
from src.trading_engine.order_executor.order_executor import OrderExecutor
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.ai_strategy.strategies.base_strategy import Signal, SignalType


@pytest.mark.asyncio
async def test_trading_engine_executes_buy_signal():
    """Test trading engine executes buy when signal is strong"""
    # Create mocked components
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    mock_exchange = Mock()
    order_executor = OrderExecutor(exchange=mock_exchange, paper_trading=True)
    position_tracker = PositionTracker()

    # Mock strategy coordinator to return BUY signal
    mock_coordinator = Mock(spec=StrategyCoordinator)
    mock_coordinator.get_combined_signal = AsyncMock(return_value=Signal(
        signal_type=SignalType.BUY,
        confidence=80,
        reasoning="Strong bullish signal"
    ))

    # Create mock database session
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()

    # Create trading engine
    engine = TradingEngine(
        risk_manager=risk_manager,
        order_executor=order_executor,
        position_tracker=position_tracker,
        strategy_coordinator=mock_coordinator,
        db_session=mock_db,
        symbol='BTC/USD',
        poll_interval=1
    )

    # Execute one trading cycle
    await engine._trading_cycle()

    # Verify position was created
    open_positions = position_tracker.get_open_positions()
    assert len(open_positions) == 1
    assert open_positions[0].symbol == 'BTC/USD'

    # Verify trade was saved to database
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_trading_engine_respects_daily_loss_limit():
    """Test trading engine stops trading when daily loss limit hit"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    mock_exchange = Mock()
    order_executor = OrderExecutor(exchange=mock_exchange, paper_trading=True)
    position_tracker = PositionTracker()

    mock_coordinator = Mock(spec=StrategyCoordinator)
    mock_coordinator.get_combined_signal = AsyncMock(return_value=Signal(
        signal_type=SignalType.BUY,
        confidence=80,
        reasoning="Bullish"
    ))

    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()

    engine = TradingEngine(
        risk_manager=risk_manager,
        order_executor=order_executor,
        position_tracker=position_tracker,
        strategy_coordinator=mock_coordinator,
        db_session=mock_db,
        symbol='BTC/USD',
        poll_interval=1
    )

    # Simulate daily loss exceeding limit
    engine.daily_pnl = -1500  # -15% of 10000

    # Execute trading cycle
    await engine._trading_cycle()

    # Verify no position was created due to risk limit
    open_positions = position_tracker.get_open_positions()
    assert len(open_positions) == 0
