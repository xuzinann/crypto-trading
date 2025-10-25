from datetime import datetime
from typing import List, Dict, Optional


class BacktestEngine:
    """Core backtesting engine for strategy simulation"""

    def __init__(self, strategy, initial_capital: float = 10000.0):
        """
        Initialize backtest engine

        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital in USD
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position_size = 0.0
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = []
        self.slippage = 0.001  # 0.1% slippage per trade

    def execute_buy(self, price: float, timestamp: datetime):
        """
        Execute buy order

        Args:
            price: Buy price
            timestamp: Execution time
        """
        if self.position_size > 0:
            return  # Already in position

        # Calculate buy price with slippage
        buy_price = price * (1 + self.slippage)

        # Buy maximum shares with available capital
        self.position_size = self.current_capital / buy_price
        self.entry_price = price
        self.current_capital = 0.0

        self.trades.append({
            'timestamp': timestamp,
            'type': 'BUY',
            'price': price,
            'size': self.position_size,
            'capital': self.current_capital
        })

    def execute_sell(self, price: float, timestamp: datetime):
        """
        Execute sell order

        Args:
            price: Sell price
            timestamp: Execution time
        """
        if self.position_size == 0:
            return  # No position to sell

        # Calculate sell price with slippage
        sell_price = price * (1 - self.slippage)

        # Sell all shares
        self.current_capital = self.position_size * sell_price

        # Calculate P&L
        profit = self.current_capital - self.initial_capital

        self.trades.append({
            'timestamp': timestamp,
            'type': 'SELL',
            'price': price,
            'size': self.position_size,
            'capital': self.current_capital,
            'profit': profit
        })

        self.position_size = 0.0
        self.entry_price = 0.0
