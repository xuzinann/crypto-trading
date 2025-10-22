from typing import List, Optional
from datetime import datetime
from src.database.models.position import Position, PositionStatus


class PositionTracker:
    """Tracks open and closed positions"""

    def __init__(self):
        self.positions: List[Position] = []

    def add_position(
        self,
        symbol: str,
        entry_price: float,
        amount: float,
        stop_loss_price: float
    ) -> Position:
        """
        Add a new position

        Args:
            symbol: Trading pair
            entry_price: Entry price
            amount: Position size
            stop_loss_price: Stop-loss price

        Returns:
            Position object
        """
        position = Position(
            symbol=symbol,
            entry_time=datetime.utcnow(),
            entry_price=entry_price,
            amount=amount,
            current_price=entry_price,
            unrealized_pnl=0.0,
            stop_loss_price=stop_loss_price,
            status=PositionStatus.OPEN
        )
        self.positions.append(position)
        return position

    def calculate_unrealized_pnl(self, position: Position, current_price: float) -> float:
        """
        Calculate unrealized P&L for a position

        Args:
            position: Position object
            current_price: Current market price

        Returns:
            Unrealized P&L
        """
        pnl = (current_price - position.entry_price) * position.amount
        position.current_price = current_price
        position.unrealized_pnl = pnl
        return pnl

    def close_position(self, position: Position, exit_price: float) -> float:
        """
        Close a position and calculate realized P&L

        Args:
            position: Position to close
            exit_price: Exit price

        Returns:
            Realized P&L
        """
        realized_pnl = (exit_price - position.entry_price) * position.amount
        position.status = PositionStatus.CLOSED
        position.current_price = exit_price
        position.unrealized_pnl = realized_pnl
        return realized_pnl

    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return [p for p in self.positions if p.status == PositionStatus.OPEN]

    def get_total_unrealized_pnl(self, current_prices: dict) -> float:
        """
        Calculate total unrealized P&L across all open positions

        Args:
            current_prices: Dict of {symbol: price}

        Returns:
            Total unrealized P&L
        """
        total_pnl = 0.0
        for position in self.get_open_positions():
            if position.symbol in current_prices:
                pnl = self.calculate_unrealized_pnl(position, current_prices[position.symbol])
                total_pnl += pnl
        return total_pnl

    def check_stop_loss_triggers(self, current_prices: dict) -> List[Position]:
        """
        Check if any positions hit stop-loss

        Args:
            current_prices: Dict of {symbol: price}

        Returns:
            List of positions that hit stop-loss
        """
        triggered = []
        for position in self.get_open_positions():
            if position.symbol in current_prices:
                current_price = current_prices[position.symbol]
                if current_price <= position.stop_loss_price:
                    triggered.append(position)
        return triggered
