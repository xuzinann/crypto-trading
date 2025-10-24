# Bitcoin Autotrader (OKX Edition)

Automated Bitcoin trading system with AI analysis, technical indicators, and real-time mobile dashboard.

**Exchange:** OKX (OKEX) - Industry-leading cryptocurrency exchange
**Trading Mode:** Spot trading with automated strategies

## Features

- **Exchange Integration:** OKX API with CCXT unified interface
- **AI Analysis:** DeepSeek AI for market sentiment and pattern recognition
- **Technical Indicators:** RSI, MACD, moving averages, and more
- **News Monitoring:** Real-time crypto news event tracking
- **Risk Management:** Position sizing, daily loss limits, kill switch
- **Dashboard:** Mobile-friendly web interface with real-time updates
- **Backtesting:** Historical strategy performance analysis
- **Paper Trading:** Risk-free testing mode with simulated orders
- **Multi-Exchange Support:** Easily switch between OKX, Binance, and others

## Why OKX?

- ✅ Lower fees: 0.08% maker / 0.10% taker (vs Binance 0.10%/0.10%)
- ✅ Higher rate limits: 2400 req/min (vs Binance 1200 req/min)
- ✅ Better liquidity on major pairs
- ✅ Advanced order types and trading features
- ✅ Global access without restrictions
- ✅ Unified API for spot, futures, and options

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OKX account with API credentials
- PostgreSQL (via Docker)
- Redis (via Docker)

### 1. Get OKX API Credentials

1. Sign up at [OKX.com](https://www.okx.com)
2. Navigate to **API Management** in account settings
3. Create new API key with permissions:
   - ✅ **Trade** - For order placement
   - ✅ **Read** - For market data
   - ❌ **Withdraw** - Keep disabled for security
4. Save your credentials:
   - API Key
   - Secret Key
   - Passphrase (required for OKX)
5. ⚠️ **Optional:** Whitelist your server IP for added security

### 2. Configure Environment

```bash
# Clone repository
git clone <repo-url>
cd apt

# Create environment file from template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required .env Configuration:**
```bash
# OKX API Credentials
OKX_API_KEY=your_okx_api_key_here
OKX_API_SECRET=your_okx_secret_key_here
OKX_API_PASSPHRASE=your_okx_passphrase_here
OKX_TESTNET=true  # Use testnet for testing, false for live trading

# Trading Configuration
TRADING_SYMBOL=BTC/USDT  # Primary OKX pair
PAPER_TRADING=true       # Enable paper trading mode
INITIAL_CAPITAL=10000    # Starting capital in USD

# Risk Management
POSITION_SIZE_PERCENT=5          # % of capital per trade
DAILY_LOSS_LIMIT_PERCENT=15     # Max daily loss %
KILL_SWITCH_PERCENT=50          # Emergency stop threshold

# AI & News (Optional)
DEEPSEEK_API_KEY=your_deepseek_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

### 3. Deploy with Docker (Recommended)

```bash
# One-command deployment
chmod +x deploy.sh
./deploy.sh
```

The deployment script will:
- ✅ Install Docker and Docker Compose (if needed)
- ✅ Build application containers
- ✅ Start PostgreSQL, Redis, and trading engine
- ✅ Initialize database schema
- ✅ Verify all services are running

**Services Started:**
- API Server: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 4. Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start database services
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Build Frontend Dashboard

```bash
cd frontend
npm install
npm run build
npm start  # Development server on http://localhost:3000
```

## Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/ -v              # Unit tests
pytest tests/integration/ -v       # Integration tests

# Run with coverage
pytest --cov=src --cov-report=html

# Test OKX integration (requires testnet credentials)
pytest tests/integration/test_okx_integration.py -v -s
```

## Usage

### Paper Trading (Recommended for Testing)

1. Set `PAPER_TRADING=true` in `.env`
2. Set `OKX_TESTNET=true` for sandbox environment
3. Start the application
4. Monitor via API docs: http://localhost:8000/docs
5. Check logs: `docker-compose logs -f trading-engine`

### Live Trading (Use with Caution)

⚠️ **WARNING:** Live trading involves real money. Start small and monitor closely.

1. Set `PAPER_TRADING=false` in `.env`
2. Set `OKX_TESTNET=false` for production
3. Start with small `INITIAL_CAPITAL` and `POSITION_SIZE_PERCENT`
4. Monitor the dashboard and logs continuously
5. Be prepared to stop the bot if needed: `docker-compose down`

### API Endpoints

Once running, explore the API at http://localhost:8000/docs

**Key Endpoints:**
- `GET /` - Health check
- `GET /api/v1/stats` - Trading statistics
- `GET /api/v1/positions` - Current positions
- `GET /api/v1/trades` - Trade history
- `WebSocket /ws` - Real-time updates

## Configuration

### Trading Symbols

OKX supports multiple trading pairs:
```bash
TRADING_SYMBOL=BTC/USDT   # Most liquid (recommended)
TRADING_SYMBOL=BTC/USD    # USD stablecoin pair
TRADING_SYMBOL=ETH/USDT   # Ethereum
```

### Strategy Configuration

Edit strategy weights in `src/trading_engine/strategy_coordinator/coordinator.py`:
```python
strategies = [
    TechnicalIndicatorsStrategy(),  # Weight: 0.3
    # Add more strategies here
]
```

### Risk Management

Adjust in `.env`:
```bash
POSITION_SIZE_PERCENT=5      # Conservative: 2-5%, Aggressive: 10-15%
DAILY_LOSS_LIMIT_PERCENT=15  # Stop trading if daily loss exceeds this
KILL_SWITCH_PERCENT=50       # Emergency stop - closes all positions
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Trading Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Strategy   │──────│   Strategy   │                     │
│  │ Coordinator  │      │  Plugins     │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                                                     │
│  ┌──────▼──────┐      ┌──────────────┐                     │
│  │    Risk     │      │    Order     │◄──── OKX API        │
│  │  Manager    │──────│  Executor    │                     │
│  └─────────────┘      └──────────────┘                     │
│         │                                                     │
│  ┌──────▼──────┐      ┌──────────────┐                     │
│  │  Position   │      │   Database   │                     │
│  │   Tracker   │──────│  (Postgres)  │                     │
│  └─────────────┘      └──────────────┘                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│              WebSocket + REST API Endpoints                  │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard                           │
│            Real-time Trading Visualization                   │
└─────────────────────────────────────────────────────────────┘
```

See [docs/plans/2025-10-22-bitcoin-autotrading-design.md](docs/plans/2025-10-22-bitcoin-autotrading-design.md) for detailed architecture.

## Monitoring & Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f trading-engine

# Recent logs only
docker-compose logs --tail=100 -f
```

### Stop/Start Services

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Restart specific service
docker-compose restart trading-engine

# Rebuild after code changes
docker-compose up -d --build
```

### Database Access

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d bitcoin_trader

# View tables
\dt

# Query trades
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

# Query positions
SELECT * FROM positions WHERE status = 'open';
```

## Switching Exchanges

The system supports multiple exchanges via CCXT. To switch:

1. Update `.env`:
```bash
EXCHANGE_NAME=binance  # Options: okx, binance, binanceus
```

2. Add exchange credentials:
```bash
# For Binance
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=true
```

3. Update trading symbol if needed:
```bash
TRADING_SYMBOL=BTC/USD  # Binance US uses USD
```

## Security Best Practices

- ✅ Never commit `.env` file with real credentials
- ✅ Use testnet/paper trading for initial testing
- ✅ Enable IP whitelisting on OKX API keys
- ✅ Disable withdraw permission on API keys
- ✅ Start with small capital amounts
- ✅ Monitor closely during live trading
- ✅ Set conservative risk management limits
- ✅ Use strong, unique API passphrases
- ✅ Regularly rotate API keys
- ❌ Never share API credentials

## Troubleshooting

### API Connection Errors

```bash
# Test OKX API connectivity
python3 -c "
from src.common.exchange_config import get_exchange
exchange = get_exchange(exchange_name='okx', testnet=True)
print(exchange.fetch_ticker('BTC/USDT'))
"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Rebuild database
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

### Docker Issues

```bash
# Check Docker daemon
docker ps

# Free up space
docker system prune -a

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `pytest`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open pull request

## License

[Your License Here]

## Disclaimer

⚠️ **IMPORTANT:** This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Never invest more than you can afford to lose. The authors are not responsible for any financial losses incurred through use of this software.

**Use at your own risk.**

## Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with:** Python, FastAPI, React, PostgreSQL, Redis, CCXT, Docker

**Exchange:** OKX (OKEX) - Professional cryptocurrency trading platform
```

**Verification Steps:**
```bash
# View rendered markdown (optional)
# No verification needed - just update the file
