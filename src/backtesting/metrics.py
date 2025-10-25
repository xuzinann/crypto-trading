import pandas as pd
import numpy as np
from typing import List, Dict


class MetricsCalculator:
    """Calculate backtest performance metrics"""

    def calculate_total_return(self, initial_capital: float, final_capital: float) -> float:
        """
        Calculate total return percentage

        Args:
            initial_capital: Starting capital
            final_capital: Ending capital

        Returns:
            Total return as percentage
        """
        return ((final_capital - initial_capital) / initial_capital) * 100

    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown percentage

        Args:
            equity_curve: Series of equity values

        Returns:
            Max drawdown as percentage
        """
        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown at each point
        drawdown = ((equity_curve - running_max) / running_max) * 100

        # Return worst drawdown (most negative)
        return abs(drawdown.min())

    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe ratio

        Args:
            returns: Series of periodic returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Annualize returns (assuming daily)
        excess_return = returns.mean() * 252 - risk_free_rate
        volatility = returns.std() * np.sqrt(252)

        return excess_return / volatility if volatility > 0 else 0.0

    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """
        Calculate win rate percentage

        Args:
            trades: List of trade dictionaries with 'profit' key

        Returns:
            Win rate as percentage
        """
        if not trades:
            return 0.0

        winning_trades = sum(1 for trade in trades if trade.get('profit', 0) > 0)
        total_trades = len(trades)

        return (winning_trades / total_trades) * 100
