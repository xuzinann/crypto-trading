import ccxt
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Executes orders on Binance US exchange"""

    def __init__(self, exchange: ccxt.Exchange, paper_trading: bool = True):
        self.exchange = exchange
        self.paper_trading = paper_trading
        self.simulated_price = 50000  # Default BTC price for paper trading

    def place_buy_order(self, symbol: str, amount: float) -> Dict:
        """
        Place a market buy order

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            amount: Amount to buy in base currency

        Returns:
            Order details dictionary
        """
        if self.paper_trading:
            return self._simulate_order(symbol=symbol, amount=amount, side='buy')

        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            logger.info(f"Buy order placed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
            raise

    def place_sell_order(self, symbol: str, amount: float) -> Dict:
        """
        Place a market sell order

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            amount: Amount to sell in base currency

        Returns:
            Order details dictionary
        """
        if self.paper_trading:
            return self._simulate_order(symbol=symbol, amount=amount, side='sell')

        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            logger.info(f"Sell order placed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")
            raise

    def place_stop_loss(self, symbol: str, amount: float, stop_price: float) -> Dict:
        """
        Place a stop-loss order

        Args:
            symbol: Trading pair
            amount: Position size
            stop_price: Price to trigger stop loss

        Returns:
            Order details dictionary
        """
        if self.paper_trading:
            return {
                'id': f'sim_sl_{datetime.utcnow().timestamp()}',
                'symbol': symbol,
                'type': 'stop_loss',
                'amount': amount,
                'stopPrice': stop_price,
                'simulated': True
            }

        try:
            # Binance US stop-loss market order
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop_loss',
                side='sell',
                amount=amount,
                params={'stopPrice': stop_price}
            )
            logger.info(f"Stop-loss placed: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing stop-loss: {e}")
            raise

    def _simulate_order(self, symbol: str, amount: float, side: str) -> Dict:
        """Simulate order execution for paper trading"""
        return {
            'id': f'sim_{datetime.utcnow().timestamp()}',
            'symbol': symbol,
            'type': 'market',
            'side': side,
            'price': self.simulated_price,
            'amount': amount,
            'filled': amount,
            'status': 'closed',
            'simulated': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        if self.paper_trading:
            return self.simulated_price

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            raise
