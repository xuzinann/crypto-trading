import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, date
from src.trading_engine.risk_manager.risk_manager import RiskManager
from src.trading_engine.order_executor.order_executor import OrderExecutor
from src.trading_engine.position_tracker.position_tracker import PositionTracker
from src.trading_engine.strategy_coordinator.coordinator import StrategyCoordinator
from src.database.models.trade import Trade, TradeType
from src.database.models.daily_stats import DailyStats
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine that coordinates all components"""

    def __init__(
        self,
        risk_manager: RiskManager,
        order_executor: OrderExecutor,
        position_tracker: PositionTracker,
        strategy_coordinator: StrategyCoordinator,
        db_session: Session,
        symbol: str = 'BTC/USDT',  # OKX primary pair (BTC/USD also available)
        poll_interval: int = 300
    ):
        self.risk_manager = risk_manager
        self.order_executor = order_executor
        self.position_tracker = position_tracker
        self.strategy_coordinator = strategy_coordinator
        self.db = db_session
        self.symbol = symbol
        self.poll_interval = poll_interval
        self.is_running = False
        self.account_balance = risk_manager.initial_capital
        self.daily_pnl = 0.0
        self.total_pnl = 0.0

    async def start(self):
        """Start the trading engine"""
        self.is_running = True
        logger.info("Trading engine started")

        while self.is_running:
            try:
                await self._trading_cycle()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                await asyncio.sleep(60)  # Wait before retry

    def stop(self):
        """Stop the trading engine"""
        self.is_running = False
        logger.info("Trading engine stopped")

    async def _trading_cycle(self):
        """Execute one trading cycle"""
        # Reset daily loss if new day
        self.risk_manager.reset_daily_loss()

        # Get current market data
        market_data = await self._fetch_market_data()

        # Update open positions
        await self._update_positions(market_data)

        # Check stop-loss triggers
        await self._check_stop_losses(market_data)

        # Get trading signal
        signal = await self.strategy_coordinator.get_combined_signal(market_data)
        logger.info(f"Signal: {signal.signal_type.value} (confidence: {signal.confidence})")

        # Calculate current daily loss percentage
        daily_loss_percent = abs(self.daily_pnl / self.risk_manager.initial_capital * 100)
        total_loss_percent = abs(self.total_pnl / self.risk_manager.initial_capital * 100)

        # Check kill switch
        if self.risk_manager.check_kill_switch(total_loss_percent):
            logger.critical(f"KILL SWITCH ACTIVATED - Total loss: {total_loss_percent}%")
            await self._close_all_positions(market_data)
            self.stop()
            return

        # Validate trade with risk manager
        can_trade, reason = self.risk_manager.validate_trade(
            balance=self.account_balance,
            current_daily_loss_percent=daily_loss_percent
        )

        if not can_trade:
            logger.info(f"Trade rejected: {reason}")
            return

        # Execute trade based on signal
        if signal.signal_type.value == 'BUY' and len(self.position_tracker.get_open_positions()) == 0:
            await self._execute_buy(market_data, signal)
        elif signal.signal_type.value == 'SELL' and len(self.position_tracker.get_open_positions()) > 0:
            await self._execute_sell(market_data, signal)

    async def _fetch_market_data(self) -> Dict[str, Any]:
        """Fetch current market data"""
        # For now, return mock data - in real implementation, fetch from exchange
        import pandas as pd
        import numpy as np

        current_price = self.order_executor.get_current_price(self.symbol)

        # Generate mock OHLCV data for strategies
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1H')
        ohlcv = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(current_price * 0.98, current_price * 1.02, 100),
            'high': np.random.uniform(current_price, current_price * 1.03, 100),
            'low': np.random.uniform(current_price * 0.97, current_price, 100),
            'close': np.random.uniform(current_price * 0.98, current_price * 1.02, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })

        return {
            'symbol': self.symbol,
            'current_price': current_price,
            'ohlcv': ohlcv
        }

    async def _update_positions(self, market_data: Dict[str, Any]):
        """Update all open positions with current prices"""
        current_price = market_data['current_price']
        for position in self.position_tracker.get_open_positions():
            self.position_tracker.calculate_unrealized_pnl(position, current_price)

    async def _check_stop_losses(self, market_data: Dict[str, Any]):
        """Check and execute stop-loss orders"""
        current_prices = {self.symbol: market_data['current_price']}
        triggered = self.position_tracker.check_stop_loss_triggers(current_prices)

        for position in triggered:
            logger.warning(f"Stop-loss triggered for position {position.id}")
            await self._close_position(position, market_data['current_price'], "Stop-loss triggered")

    async def _execute_buy(self, market_data: Dict[str, Any], signal):
        """Execute buy order"""
        current_price = market_data['current_price']
        position_size_usd = self.risk_manager.calculate_position_size(self.account_balance)
        amount = position_size_usd / current_price

        # Place buy order
        order = self.order_executor.place_buy_order(self.symbol, amount)
        logger.info(f"Buy order executed: {order}")

        # Calculate stop-loss price (5% below entry)
        stop_loss_price = current_price * 0.95

        # Place stop-loss
        self.order_executor.place_stop_loss(self.symbol, amount, stop_loss_price)

        # Add position to tracker
        position = self.position_tracker.add_position(
            symbol=self.symbol,
            entry_price=current_price,
            amount=amount,
            stop_loss_price=stop_loss_price
        )

        # Save to database
        trade = Trade(
            symbol=self.symbol,
            type=TradeType.BUY,
            amount=amount,
            entry_price=current_price,
            strategy_signals={'combined': signal.signal_type.value},
            reasoning=signal.reasoning
        )
        self.db.add(trade)
        self.db.commit()

        self.account_balance -= position_size_usd

    async def _execute_sell(self, market_data: Dict[str, Any], signal):
        """Execute sell order for all open positions"""
        current_price = market_data['current_price']

        for position in self.position_tracker.get_open_positions():
            await self._close_position(position, current_price, signal.reasoning)

    async def _close_position(self, position, exit_price: float, reason: str):
        """Close a single position"""
        # Place sell order
        order = self.order_executor.place_sell_order(self.symbol, position.amount)
        logger.info(f"Sell order executed: {order}")

        # Calculate realized P&L
        realized_pnl = self.position_tracker.close_position(position, exit_price)

        # Update balances
        self.account_balance += (exit_price * position.amount)
        self.daily_pnl += realized_pnl
        self.total_pnl += realized_pnl

        logger.info(f"Position closed - P&L: ${realized_pnl:.2f}")

        # Update trade in database
        # Find the corresponding buy trade and update it
        # (simplified - in real implementation, match by position ID)

    async def _close_all_positions(self, market_data: Dict[str, Any]):
        """Emergency close all positions"""
        logger.warning("Closing all positions")
        current_price = market_data['current_price']

        for position in self.position_tracker.get_open_positions():
            await self._close_position(position, current_price, "Emergency close")
