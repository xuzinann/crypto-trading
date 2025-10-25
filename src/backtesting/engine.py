from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


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

    def run(self, historical_data: pd.DataFrame) -> Dict:
        """
        Run backtest simulation

        Args:
            historical_data: DataFrame with OHLCV data

        Returns:
            Dictionary with backtest results
        """
        for idx, row in historical_data.iterrows():
            # Get strategy signal
            signal = self.strategy.generate_signal(row, historical_data[:idx+1])

            # Execute based on signal
            if signal == 'BUY' and self.position_size == 0:
                self.execute_buy(row['close'], row['timestamp'])
            elif signal == 'SELL' and self.position_size > 0:
                self.execute_sell(row['close'], row['timestamp'])

            # Track equity
            current_equity = self.get_current_equity(row['close'])
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'equity': current_equity
            })

        return {
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'final_capital': self.get_current_equity(historical_data.iloc[-1]['close'])
        }

    def get_current_equity(self, current_price: float) -> float:
        """Calculate current total equity value"""
        if self.position_size > 0:
            return self.position_size * current_price
        else:
            return self.current_capital

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
