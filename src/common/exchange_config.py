"""
Exchange configuration and initialization.

Supports multiple exchanges via CCXT library:
- OKX (primary)
- Binance (legacy support)
"""

import os
import ccxt
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ExchangeFactory:
    """Factory for creating exchange instances"""

    SUPPORTED_EXCHANGES = {
        'okx': ccxt.okx,
        'binance': ccxt.binance,
        'binanceus': ccxt.binanceus,
    }

    @staticmethod
    def create_exchange(
        exchange_name: str = 'okx',
        testnet: bool = True,
        paper_trading: bool = True
    ) -> ccxt.Exchange:
        """
        Create and configure exchange instance

        Args:
            exchange_name: Exchange to use ('okx', 'binance', 'binanceus')
            testnet: Use testnet/sandbox mode if True
            paper_trading: Used for logging only (doesn't affect exchange init)

        Returns:
            Configured CCXT exchange instance

        Raises:
            ValueError: If exchange not supported or credentials missing
        """
        if exchange_name not in ExchangeFactory.SUPPORTED_EXCHANGES:
            raise ValueError(
                f"Exchange '{exchange_name}' not supported. "
                f"Supported: {list(ExchangeFactory.SUPPORTED_EXCHANGES.keys())}"
            )

        logger.info(f"Initializing {exchange_name} exchange (testnet={testnet}, paper_trading={paper_trading})")

        # Get exchange class
        exchange_class = ExchangeFactory.SUPPORTED_EXCHANGES[exchange_name]

        # Build configuration
        config = {}

        if exchange_name == 'okx':
            config = ExchangeFactory._get_okx_config(testnet)
        elif exchange_name in ['binance', 'binanceus']:
            config = ExchangeFactory._get_binance_config(testnet)

        # Create exchange instance
        exchange = exchange_class(config)

        # Set sandbox mode if testnet
        if testnet and hasattr(exchange, 'set_sandbox_mode'):
            exchange.set_sandbox_mode(True)
            logger.info(f"{exchange_name} sandbox mode enabled")

        return exchange

    @staticmethod
    def _get_okx_config(testnet: bool) -> dict:
        """Get OKX exchange configuration from environment"""
        api_key = os.getenv('OKX_API_KEY')
        api_secret = os.getenv('OKX_API_SECRET')
        api_passphrase = os.getenv('OKX_API_PASSPHRASE')

        if not all([api_key, api_secret, api_passphrase]):
            raise ValueError(
                "OKX credentials incomplete. Required: "
                "OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE"
            )

        config = {
            'apiKey': api_key,
            'secret': api_secret,
            'password': api_passphrase,  # OKX requires passphrase
            'enableRateLimit': True,  # Respect rate limits
            'options': {
                'defaultType': 'spot',  # Use spot trading (not futures)
            }
        }

        if testnet:
            # OKX uses sandbox mode flag
            config['options']['sandboxMode'] = True

        return config

    @staticmethod
    def _get_binance_config(testnet: bool) -> dict:
        """Get Binance exchange configuration from environment"""
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')

        if not all([api_key, api_secret]):
            raise ValueError(
                "Binance credentials incomplete. Required: "
                "BINANCE_API_KEY, BINANCE_API_SECRET"
            )

        config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        }

        if testnet:
            # Binance testnet uses different base URL
            config['urls'] = {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }

        return config


def get_exchange(
    exchange_name: Optional[str] = None,
    testnet: Optional[bool] = None,
    paper_trading: Optional[bool] = None
) -> ccxt.Exchange:
    """
    Convenience function to get configured exchange instance

    Reads from environment variables if parameters not provided:
    - EXCHANGE_NAME (default: 'okx')
    - OKX_TESTNET or BINANCE_TESTNET (default: true)
    - PAPER_TRADING (default: true)

    Args:
        exchange_name: Override exchange from environment
        testnet: Override testnet setting from environment
        paper_trading: Override paper trading setting from environment

    Returns:
        Configured exchange instance
    """
    # Get defaults from environment
    if exchange_name is None:
        exchange_name = os.getenv('EXCHANGE_NAME', 'okx').lower()

    if testnet is None:
        # Check exchange-specific testnet flag
        if exchange_name == 'okx':
            testnet = os.getenv('OKX_TESTNET', 'true').lower() == 'true'
        else:
            testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'

    if paper_trading is None:
        paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'

    return ExchangeFactory.create_exchange(
        exchange_name=exchange_name,
        testnet=testnet,
        paper_trading=paper_trading
    )
