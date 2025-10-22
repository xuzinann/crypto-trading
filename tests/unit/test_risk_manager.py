import pytest
from src.trading_engine.risk_manager.risk_manager import RiskManager


def test_calculate_position_size_returns_5_percent_of_balance():
    """Test position sizing is 5% of account balance"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    position_size = risk_manager.calculate_position_size(balance=10000)
    assert position_size == 500  # 5% of 10000


def test_validate_trade_rejects_when_insufficient_balance():
    """Test trade validation rejects when balance too low"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    is_valid, reason = risk_manager.validate_trade(
        balance=100,
        current_daily_loss_percent=0
    )

    assert is_valid is False
    assert "insufficient balance" in reason.lower()


def test_validate_trade_rejects_when_daily_loss_limit_reached():
    """Test trade validation rejects when daily loss limit hit"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    is_valid, reason = risk_manager.validate_trade(
        balance=9000,
        current_daily_loss_percent=15
    )

    assert is_valid is False
    assert "daily loss limit" in reason.lower()


def test_check_kill_switch_locks_trading_at_50_percent_loss():
    """Test kill switch activates at 50% total loss"""
    risk_manager = RiskManager(
        position_size_percent=5,
        daily_loss_limit_percent=15,
        kill_switch_percent=50,
        initial_capital=10000
    )

    triggered = risk_manager.check_kill_switch(total_loss_percent=50)

    assert triggered is True
    assert risk_manager.is_trading_locked is True
