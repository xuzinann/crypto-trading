import pytest
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.database.models.position import Position, PositionStatus


def test_add_position_creates_new_position():
    """Test adding a new position"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    assert position.symbol == 'BTC/USD'
    assert position.entry_price == 50000
    assert position.amount == 0.01
    assert position.stop_loss_price == 47500
    assert position.status == PositionStatus.OPEN


def test_calculate_unrealized_pnl_for_long_position():
    """Test P&L calculation for open long position"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    pnl = tracker.calculate_unrealized_pnl(position, current_price=51000)

    assert pnl == 10.0  # (51000 - 50000) * 0.01 = 10


def test_close_position_calculates_realized_pnl():
    """Test closing position calculates correct P&L"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    realized_pnl = tracker.close_position(position, exit_price=52000)

    assert realized_pnl == 20.0  # (52000 - 50000) * 0.01 = 20
    assert position.status == PositionStatus.CLOSED


def test_check_stop_loss_triggers_identifies_hit_positions():
    """Test stop-loss trigger detection"""
    tracker = PositionTracker()

    position = tracker.add_position(
        symbol='BTC/USD',
        entry_price=50000,
        amount=0.01,
        stop_loss_price=47500
    )

    triggered = tracker.check_stop_loss_triggers({'BTC/USD': 47000})

    assert len(triggered) == 1
    assert triggered[0] == position
