# Bitcoin Autotrading System Design

**Date:** October 22, 2025
**Status:** Design Approved
**Platform:** Binance US
**Deployment:** Cost-effective VPS ($17-22/month)

## Executive Summary

An automated Bitcoin trading system that combines DeepSeek AI analysis, technical indicators, and news monitoring to execute trades on Binance US. Features a mobile-friendly web dashboard for real-time monitoring, comprehensive risk management, and a swappable/extensible AI strategy architecture for continuous improvement.

## Requirements Summary

### Trading Strategy
- **AI-driven analysis**: DeepSeek analyzes market patterns, price action, volume data
- **Technical indicators**: RSI, MACD, moving averages, other traditional signals
- **News analysis**: Monitor and respond to market-moving events (regulations, hacks, partnerships)
- **Plugin architecture**: Swappable AI strategies for continuous evolution

### Risk Management
- **Position sizing**: 5% of capital per trade
- **Daily loss limit**: 15% maximum loss per day, pause trading until next day
- **Kill switch**: 50% total loss triggers complete shutdown with alerts
- **Safety features**: Stop-loss orders, connection loss handling, audit trail

### Mobile Dashboard Requirements
- **Current positions & P&L**: Active trades, entry prices, real-time profit/loss
- **Account balance & daily stats**: Total balance, daily performance, trade count
- **AI decision reasoning**: Why each trade was made, confidence levels, signals detected
- **System health & alerts**: Bot status, API connectivity, error notifications, risk warnings
- **Mobile-first design**: Responsive web app accessible from any phone browser

### Infrastructure
- **Hosting**: Cloud VPS (DigitalOcean/Vultr, $6-12/month recommended)
- **Backtesting**: Required before live trading
- **Paper trading**: Test with real-time data, fake money
- **API setup**: Binance US API keys (to be configured)

## Architecture Overview

### Design Choice: Hybrid Bot + AI Service

**Rationale**: Separates trading execution from AI analysis to prevent AI processing delays from blocking time-sensitive trades. Maintains simplicity by running on a single VPS while enabling strategy extensibility.

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        VPS Server                           │
│  ┌───────────────┐   ┌──────────────┐   ┌───────────────┐  │
│  │   Trading     │◄─►│  AI Strategy │◄─►│     News      │  │
│  │    Engine     │   │   Service    │   │   Monitor     │  │
│  └───────┬───────┘   └──────────────┘   └───────────────┘  │
│          │                                                   │
│          ▼                                                   │
│  ┌───────────────┐   ┌──────────────┐                      │
│  │  PostgreSQL   │   │    Redis     │                      │
│  │   Database    │   │    Cache     │                      │
│  └───────────────┘   └──────────────┘                      │
│          ▲                                                   │
└──────────┼───────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────┐
    │ Web Dashboard│◄────── Mobile Phone (Browser)
    │  (React +   │
    │  WebSocket) │
    └─────────────┘
```

## Component Details

### 1. Trading Engine (Python/FastAPI)

**Responsibilities:**
- Execute trades via Binance US API
- Enforce risk management rules
- Track positions and calculate real-time P&L
- Coordinate with AI Strategy Service for trading signals
- Push updates to web dashboard via WebSocket

**Core Modules:**

**Risk Manager**
- Pre-trade validation: position size, daily loss limits, total loss threshold
- Circuit breaker: locks all trading after 50% total loss
- Daily reset: clears daily loss counter at midnight UTC
- Position limit enforcement: prevents over-leveraging

**Order Executor**
- Places market/limit orders via Binance US REST API
- Handles order confirmations and errors
- Automatic stop-loss placement on all positions
- Rate limiting to comply with Binance API limits

**Position Tracker**
- Maintains list of open positions
- Calculates real-time P&L from live price feeds
- Monitors stop-loss triggers
- Generates position summary for dashboard

**Strategy Coordinator**
- Polls AI Strategy Service every 1-5 minutes (configurable)
- Combines signals from multiple strategy plugins using weighted voting
- Determines final BUY/SELL/HOLD decision
- Logs reasoning for each decision

**Technology:**
- Language: Python 3.11+
- Framework: FastAPI (async performance)
- Exchange Integration: CCXT library (Binance US support)
- WebSocket: FastAPI WebSocket for dashboard updates

### 2. AI Strategy Service (Python with DeepSeek)

**Plugin-Based Architecture:**

```
/strategies/
  base_strategy.py          # Abstract interface all plugins implement
  deepseek_analyzer.py      # DeepSeek AI market analysis
  technical_indicators.py   # RSI, MACD, moving averages
  news_analyzer.py          # Event impact assessment
  custom_strategy.py        # User-defined strategies
```

**Plugin Interface (base_strategy.py):**
```python
class BaseStrategy:
    def analyze(market_data, news_events) -> Signal
        # Returns: signal (BUY/SELL/HOLD)
        #          confidence (0-100%)
        #          reasoning (string explanation)
```

**Strategy Plugins:**

**DeepSeek Analyzer**
- Analyzes price patterns, volume trends, order book depth
- Identifies support/resistance levels
- Detects market regime changes (trending vs ranging)
- Returns confidence-weighted signals

**Technical Indicators**
- RSI (Relative Strength Index): overbought/oversold detection
- MACD (Moving Average Convergence Divergence): trend momentum
- Moving averages: trend direction confirmation
- Volume analysis: validation of price movements

**News Analyzer**
- Evaluates impact of detected news events
- Categorizes: bullish, bearish, neutral
- Adjusts signals based on event severity
- Examples: regulatory announcements, exchange hacks, institutional adoption

**Signal Combination:**
- Weighted voting system (configurable weights per strategy)
- Example: DeepSeek 50%, Technical 30%, News 20%
- Requires minimum combined confidence threshold (e.g., 70%) before trading

**Hot-Swapping:**
- Strategies can be enabled/disabled via dashboard
- New strategies added by dropping file in /strategies/ directory
- No restart required for strategy changes

**Technology:**
- DeepSeek API integration (requires API key)
- TA-Lib for technical indicator calculations
- Pandas for data processing
- REST API interface for Trading Engine communication

### 3. News Monitor Service

**Responsibilities:**
- Fetch cryptocurrency news from APIs
- Detect market-moving events
- Feed events to AI Strategy Service

**Data Sources:**
- CryptoPanic API (crypto-specific news aggregator)
- NewsAPI (general financial news)
- Optional: Twitter/X API for social sentiment (future enhancement)

**Event Detection:**
- Keywords: regulation, ban, hack, partnership, adoption, SEC, ETF
- Severity scoring: high/medium/low impact
- Deduplication: avoid analyzing same news multiple times

**Technology:**
- Python with aiohttp (async news fetching)
- Scheduled polling every 5-10 minutes
- Event storage in PostgreSQL for historical analysis

### 4. Web Dashboard (React + WebSocket)

**Mobile-First Design:**

**Layout Structure:**

**Top Section - Quick Stats Card:**
- Account Balance (large, green/red based on P&L)
- Today's P&L (percentage and dollar amount)
- Active Positions count
- System Status: ● Trading / ● Paused / ● Stopped

**Tab Navigation:**

**Tab 1: Live Positions**
- Real-time position cards showing:
  - Symbol (BTC/USD), Entry Price, Current Price
  - P&L (dollar amount and percentage)
  - Duration, Stop-Loss Level
- Tap to expand: full details + manual close button
- Auto-updates via WebSocket (no refresh needed)

**Tab 2: Trade History**
- Chronological list of completed trades
- Filters: Today, This Week, This Month, All Time
- Each entry shows:
  - Timestamp, Type (BUY/SELL), Amount
  - Entry/Exit Price, Profit/Loss
  - AI Reasoning: "Why this trade was made"
- Export to CSV option

**Tab 3: AI Insights**
- Current market analysis from DeepSeek
- Technical indicator dashboard:
  - RSI: value + interpretation (overbought/oversold)
  - MACD: histogram visualization
  - Moving averages: alignment chart
- Recent news events (last 24 hours)
- Strategy confidence scores (per plugin)
- Current recommendation: "Why trading/not trading now"

**Tab 4: Controls**
- Pause/Resume Trading (toggle switch)
- Emergency: Close All Positions (requires confirmation)
- Strategy Plugin Controls:
  - Enable/disable individual strategies
  - Adjust strategy weights
- Risk Parameter Adjustments:
  - Position size percentage (default 5%)
  - Daily loss limit (default 15%)
  - Requires 2FA confirmation for changes
- System Logs Viewer (last 100 entries)

**Real-Time Features:**
- Live Bitcoin price ticker (top of screen)
- WebSocket connection for instant updates
- Push notifications (via browser notifications API):
  - Trade executed
  - Daily loss limit reached
  - Kill switch triggered
  - Connection errors
- Auto-reconnect on connection loss
- Offline indicator when disconnected

**Security:**
- Username/password authentication
- JWT token-based sessions (24-hour expiry)
- Optional 2FA (TOTP) for critical actions
- HTTPS only (enforced)

**Technology:**
- React 18 (UI framework)
- TailwindCSS (responsive styling)
- Recharts (charts and graphs)
- WebSocket API (real-time communication)
- PWA capabilities (install on home screen)

## Data Storage (PostgreSQL)

**Database Schema:**

**Table: trades**
- id, timestamp, symbol, type (BUY/SELL)
- amount, entry_price, exit_price, profit_loss
- strategy_signals (JSON), reasoning

**Table: positions**
- id, symbol, entry_time, entry_price
- amount, current_price, unrealized_pnl
- stop_loss_price, status (OPEN/CLOSED)

**Table: daily_stats**
- date, total_trades, winning_trades, losing_trades
- total_pnl, max_drawdown, sharpe_ratio

**Table: system_logs**
- timestamp, level (INFO/WARNING/ERROR)
- component, message, details (JSON)

**Table: strategy_performance**
- strategy_name, date, signals_generated
- accuracy, avg_confidence, contribution_to_pnl

## Backtesting System

**Purpose:** Test strategies on historical data before risking real capital.

**Features:**

**Historical Data Management:**
- Download Bitcoin OHLCV data from Binance (1-minute candles)
- Store 2+ years of historical data
- Periodic updates to keep data current

**Simulation Engine:**
- Replay historical market data through strategy plugins
- Simulate order execution with realistic slippage and fees
- Apply risk management rules as in live trading
- Generate tick-by-tick position tracking

**Performance Metrics:**
- Total return vs buy-and-hold benchmark
- Win rate, average profit/loss per trade
- Maximum drawdown, recovery time
- Sharpe ratio, Sortino ratio
- Strategy-specific contribution analysis

**Comparison Tools:**
- Test multiple strategy configurations side-by-side
- Optimize strategy weights
- Identify best-performing indicator combinations
- Sensitivity analysis: how changes affect performance

**Web Interface:**
- Upload custom historical data
- Configure backtest parameters (date range, initial capital)
- View results with interactive charts
- Export reports to PDF

**Paper Trading Mode:**
- Real-time market data with simulated execution
- Test strategies in current market without risk
- Dashboard shows "PAPER TRADING MODE" indicator
- Easy transition to live trading when confident

**Technology:**
- Pandas for data manipulation
- Backtrader or custom backtesting engine
- Matplotlib/Plotly for result visualization

## Risk Management Implementation

### Position Sizing
```
trade_amount = account_balance × 0.05
if available_balance < trade_amount:
    reject_trade("Insufficient balance")
```

### Daily Loss Tracking
- Track all P&L since midnight UTC
- Current daily loss percentage = (today_pnl / starting_balance) × 100
- If daily_loss ≥ 15%:
  - Pause all trading
  - Close no new positions
  - Keep existing positions (with stop-losses)
  - Resume at midnight UTC
  - Dashboard shows: "Daily limit reached, resuming at XX:XX UTC"

### Kill Switch (50% Total Loss)
- Track cumulative P&L from initial deployment
- If total_loss ≥ 50% of initial capital:
  - Immediately close all open positions at market price
  - Lock trading engine (requires manual restart)
  - Send emergency alerts:
    - Email notification
    - SMS via Twilio API
    - Dashboard red alert banner
  - Log detailed incident report
  - Require manual review and restart via dashboard admin panel

### Connection Loss Handling
- Monitor Binance API connection health
- Heartbeat check every 30 seconds
- If connection lost:
  - Stop opening new positions
  - Maintain existing positions (stop-losses remain active)
  - Attempt reconnection every 30 seconds (max 10 retries)
  - Dashboard shows connection status warning
  - Alert after 3 failed reconnection attempts

### Stop-Loss Automation
- Every position automatically gets stop-loss order
- Stop-loss placement: entry_price × 0.95 (5% below entry for longs)
- Implemented as exchange-side stop-loss (survives bot restarts)
- Monitor and adjust trailing stop-loss for profitable positions

### Safety Features
- All trades logged with full context (timestamp, reasoning, market conditions)
- API keys stored in encrypted environment variables (never in code)
- Rate limiting: respect Binance API limits (avoid bans)
- Dry-run mode: test without real execution
- Manual override: pause bot instantly via dashboard

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Web Framework:** FastAPI (async, high performance)
- **Exchange Integration:** CCXT library (Binance US support)
- **AI Integration:** DeepSeek API (market analysis)
- **Database:** PostgreSQL 15 (trade history, logs)
- **Cache:** Redis (rate limiting, session management)
- **Technical Analysis:** TA-Lib (indicators)
- **Data Processing:** Pandas, NumPy
- **News APIs:** CryptoPanic, NewsAPI
- **Notifications:** Twilio (SMS alerts)

### Frontend
- **Framework:** React 18
- **Styling:** TailwindCSS (mobile-responsive)
- **Charts:** Recharts (trading visualizations)
- **Real-time:** WebSocket API
- **Authentication:** JWT tokens
- **2FA:** TOTP (optional enhancement)

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **Reverse Proxy:** Nginx
- **SSL:** Let's Encrypt (free certificates)
- **CI/CD:** GitHub Actions (automated deployment)
- **Monitoring:** Prometheus + Grafana (optional)
- **Logging:** Structured JSON logs with log rotation

### Development Tools
- **Version Control:** Git, GitHub
- **Testing:** pytest, pytest-asyncio
- **Code Quality:** Black (formatter), pylint (linter)
- **Documentation:** Swagger (auto-generated from FastAPI)

## Deployment

### VPS Recommendations
**Recommended Provider:** DigitalOcean or Vultr

**Specs:**
- 2 vCPUs
- 2GB RAM (minimum, 4GB preferred)
- 50GB SSD storage
- Ubuntu 22.04 LTS
- Cost: $12/month (DigitalOcean) or $6/month (Vultr basic)

### One-Command Deployment

**Prerequisites:**
1. VPS provisioned with Ubuntu 22.04
2. Domain name pointed to VPS (for SSL)
3. Binance US account with API keys
4. DeepSeek API key

**Deployment Steps:**
```bash
# Clone repository
git clone https://github.com/username/bitcoin-autotrader.git
cd bitcoin-autotrader

# Configure environment
cp .env.example .env
# Edit .env with API keys

# Deploy everything
./deploy.sh
```

**The deploy.sh script handles:**
- Docker and Docker Compose installation
- SSL certificate generation (Let's Encrypt)
- Database initialization
- Service startup
- Health check verification

**Post-Deployment:**
1. Access dashboard: https://your-domain.com
2. Login with initial admin credentials
3. Run backtests on historical data
4. Enable paper trading mode
5. Monitor for 1-2 weeks
6. Switch to live trading when confident

### Configuration Management
- Environment variables in `.env` file
- Sensitive data (API keys) encrypted at rest
- Strategy configurations in `config/strategies.yml`
- Risk parameters in `config/risk.yml`
- Easy updates via dashboard admin panel

### Monitoring & Maintenance
- System health checks every 5 minutes
- Automated daily backups of database
- Log rotation (keep 30 days)
- Email alerts for critical errors
- Monthly performance reports

## Cost Estimate

### Monthly Operating Costs
| Item | Cost |
|------|------|
| VPS Hosting (DigitalOcean 2GB) | $12 |
| DeepSeek API (estimated usage) | $5-10 |
| News APIs (CryptoPanic free tier) | $0 |
| SSL Certificate (Let's Encrypt) | $0 |
| SMS Alerts (Twilio, ~10 msgs/month) | $1-2 |
| **Total** | **$18-24/month** |

### Optional Enhancements
- Premium news API: +$20/month
- Dedicated IP: +$4/month
- Increased VPS specs (4GB RAM): +$12/month
- Professional monitoring (Datadog): +$15/month

## Development Timeline

### Phase 1: Core Trading Engine (2-3 weeks)
- Binance US API integration
- Order execution and position tracking
- Risk management implementation
- Database schema and models
- Basic logging and error handling

### Phase 2: AI Strategy Plugins (1-2 weeks)
- Plugin architecture framework
- DeepSeek analyzer implementation
- Technical indicators plugin
- News analyzer plugin
- Strategy coordination and signal combination

### Phase 3: Web Dashboard (1-2 weeks)
- React app structure
- Real-time WebSocket integration
- Mobile-responsive UI
- Authentication and security
- All four tabs (Positions, History, Insights, Controls)

### Phase 4: Backtesting Framework (1 week)
- Historical data download and storage
- Simulation engine
- Performance metrics calculation
- Web interface for backtest results
- Paper trading mode

### Phase 5: Testing & Refinement (1-2 weeks)
- Unit tests for critical components
- Integration testing
- Security audit
- Performance optimization
- User acceptance testing

### Phase 6: Deployment & Documentation (1 week)
- VPS setup and configuration
- Deployment automation scripts
- User documentation
- Operational runbooks
- Initial backtesting with real data

**Total Estimated Timeline:** 7-11 weeks

### Iterative Development Approach
- Weekly milestones with working deployments
- Test each component in isolation before integration
- Paper trading before live trading
- Continuous feedback and adjustments

## Success Criteria

### Technical Success Metrics
- System uptime: >99% (excluding maintenance windows)
- Order execution latency: <2 seconds average
- Dashboard real-time updates: <1 second delay
- Zero missed trades due to system errors
- Complete audit trail for all trades

### Trading Performance Metrics
- Backtesting performance: Positive returns over 2-year historical period
- Paper trading: Profitable over 2-week live market test
- Risk compliance: Zero breaches of position size or daily loss limits
- Drawdown management: Maximum drawdown <20% in live trading

### User Experience Metrics
- Mobile dashboard loads in <3 seconds
- Intuitive controls requiring minimal learning
- Clear AI reasoning visible for every trade
- Instant alerts for critical events

## Future Enhancements

### Potential Additions (Post-MVP)
1. **Multi-asset support**: Trade other cryptocurrencies (ETH, SOL, etc.)
2. **Advanced strategies**: Arbitrage, market making, mean reversion
3. **Social sentiment**: Twitter/Reddit analysis integration
4. **Portfolio optimization**: Kelly criterion position sizing
5. **Machine learning**: Train custom models on historical performance
6. **Mobile app**: Native iOS/Android apps
7. **Multi-exchange**: Trade across Coinbase, Kraken, etc.
8. **Automated strategy evolution**: A/B test strategies, auto-optimize weights

### Scalability Considerations
- Current design handles 1-10 trades per day comfortably
- Can scale to 100+ trades/day with minor optimizations
- For high-frequency trading, would need architecture changes (WebSocket feeds, in-memory databases)

## Risk Disclaimers

**Trading Risks:**
- Cryptocurrency trading is highly volatile and risky
- Automated trading can amplify losses if strategies fail
- Past performance (backtesting) does not guarantee future results
- Always start with capital you can afford to lose

**Technical Risks:**
- Exchange API outages can prevent trading
- VPS downtime could cause missed opportunities
- AI models can make incorrect predictions
- Software bugs could cause unintended trades

**Mitigation:**
- Comprehensive testing before live deployment
- Conservative risk limits (5% position, 15% daily, 50% kill switch)
- Manual override capabilities
- Continuous monitoring and alerting
- Regular strategy review and adjustment

## Conclusion

This design provides a robust, extensible Bitcoin autotrading system with comprehensive risk management and real-time monitoring. The hybrid architecture balances simplicity (single VPS deployment) with flexibility (swappable AI strategies), while the mobile-first dashboard ensures you stay informed wherever you are.

The plugin-based strategy architecture enables continuous improvement without system rebuilds, and the backtesting framework ensures strategies are validated before risking capital. With estimated monthly costs of $18-24, this system provides institutional-grade autotrading capabilities at a fraction of typical costs.

**Next Steps:**
1. Review and approve this design
2. Set up git worktree for development
3. Create detailed implementation plan
4. Begin Phase 1 development (Core Trading Engine)
