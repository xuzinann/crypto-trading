from typing import Tuple
from datetime import datetime, date


class RiskManager:
    """Manages risk parameters and validates trades"""

    def __init__(
        self,
        position_size_percent: float = 5.0,
        daily_loss_limit_percent: float = 15.0,
        kill_switch_percent: float = 50.0,
        initial_capital: float = 10000.0
    ):
        self.position_size_percent = position_size_percent
        self.daily_loss_limit_percent = daily_loss_limit_percent
        self.kill_switch_percent = kill_switch_percent
        self.initial_capital = initial_capital
        self.is_trading_locked = False
        self.daily_loss_reset_date = date.today()

    def calculate_position_size(self, balance: float) -> float:
        """Calculate position size as percentage of balance"""
        return balance * (self.position_size_percent / 100)

    def validate_trade(
        self,
        balance: float,
        current_daily_loss_percent: float
    ) -> Tuple[bool, str]:
        """
        Validate if a trade can be executed based on risk rules

        Returns:
            (is_valid, reason) tuple
        """
        # Check if trading is locked by kill switch
        if self.is_trading_locked:
            return False, "Trading locked by kill switch"

        # Check daily loss limit
        if current_daily_loss_percent >= self.daily_loss_limit_percent:
            return False, f"Daily loss limit reached ({current_daily_loss_percent}%)"

        # Check if balance is sufficient for minimum position
        position_size = self.calculate_position_size(balance)
        if position_size < 10:  # Minimum position size $10
            return False, "Insufficient balance for minimum position size"

        return True, "Trade validated"

    def check_kill_switch(self, total_loss_percent: float) -> bool:
        """
        Check if kill switch should be triggered

        Returns:
            True if kill switch triggered
        """
        if total_loss_percent >= self.kill_switch_percent:
            self.is_trading_locked = True
            return True
        return False

    def reset_daily_loss(self) -> None:
        """Reset daily loss tracking at midnight UTC"""
        today = date.today()
        if today > self.daily_loss_reset_date:
            self.daily_loss_reset_date = today
