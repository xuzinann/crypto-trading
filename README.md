# Bitcoin Autotrader

Automated Bitcoin trading system with AI analysis, technical indicators, and real-time mobile dashboard.

## Features

- DeepSeek AI market analysis
- Technical indicators (RSI, MACD, moving averages)
- News event monitoring
- Comprehensive risk management
- Mobile-friendly web dashboard
- Backtesting framework
- Paper trading mode

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run database migrations: `alembic upgrade head`
4. Start services: `docker-compose up`

## Testing

Run tests: `pytest`

## Architecture

See `docs/plans/2025-10-22-bitcoin-autotrading-design.md` for detailed design documentation.
