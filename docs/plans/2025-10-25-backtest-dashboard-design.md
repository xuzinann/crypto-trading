# Backtest Dashboard Design

**Date:** 2025-10-25
**Status:** Approved
**Author:** Claude Code

## Overview

Add comprehensive backtesting capabilities to the Bitcoin autotrader, allowing users to test strategies against historical data and compare performance vs buy-and-hold baseline. Includes interactive Streamlit dashboard for visualization and easy local deployment.

## Requirements

### Core Features
1. Backtest trading strategies using historical data
2. Compare strategy performance vs buy-and-hold
3. Support multiple cryptocurrencies (BTC, ETH, SOL)
4. Adjustable execution timeframes (1h, 4h, 1d)
5. Flexible chart visualization zoom levels
6. Comprehensive metrics (returns, risk, trade stats)
7. Easy local deployment for testing

### Success Criteria
- Reuse existing strategy code for consistency
- Fast backtests (< 30 seconds for 1 year of data)
- Intuitive UI requiring minimal configuration
- Single command deployment

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Dashboard                     │
│              (streamlit_app/backtest_dashboard.py)       │
│   - Symbol/Date/Timeframe Selection                     │
│   - Interactive Charts with Trade Markers                │
│   - Metrics Comparison Table                             │
│   - Trade History & Export                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Backtest Engine                             │
│              (src/backtesting/engine.py)                 │
│   - Simulation Loop (iterate historical bars)           │
│   - Strategy Signal Execution                            │
│   - Buy-and-Hold Baseline Calculation                   │
│   - Metrics Computation                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           Historical Data Manager                        │
│           (src/backtesting/data_manager.py)              │
│   - Hybrid Caching (DB + API)                           │
│   - 1-hour Base Data Storage                            │
│   - Multi-Timeframe Aggregation                         │
│   - Gap Detection & Filling                             │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌──────────┐          ┌──────────────┐
│PostgreSQL│          │   OKX API    │
│  Cache   │          │ (Historical) │
└──────────┘          └──────────────┘
```

### Architectural Decision: Integrated Approach

**Chosen:** Integrated Backtest Engine within existing codebase

**Rationale:**
- Reuses existing strategy classes from `src/ai_strategy/strategies/`
- Ensures backtested code matches live trading code
- Simpler deployment (fewer microservices)
- Shares database infrastructure

**Trade-offs:**
- Some coupling to trading engine structure
- Must ensure backtest doesn't interfere with live trading

## Data Model

### New Table: `historical_prices`

```sql
CREATE TABLE historical_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,           -- 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'
    timestamp TIMESTAMP NOT NULL,
    timeframe VARCHAR(10) NOT NULL,        -- '1h' (base granularity)
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(symbol, timestamp, timeframe),
    INDEX idx_symbol_time (symbol, timestamp),
    INDEX idx_symbol_timeframe (symbol, timeframe)
);
```

**Storage Estimates:**
- 1 year of 1-hour data: ~8,760 bars
- 3 symbols × 1 year: ~26,000 rows
- Size: ~30MB total (very manageable)

### New Table: `backtest_results`

```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    execution_timeframe VARCHAR(10) NOT NULL,  -- '1h', '4h', '1d'
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    initial_capital FLOAT NOT NULL,
    final_capital FLOAT NOT NULL,

    -- Returns
    total_return_pct FLOAT,
    annualized_return_pct FLOAT,

    -- Risk Metrics
    max_drawdown_pct FLOAT,
    volatility FLOAT,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,

    -- Trade Statistics
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate FLOAT,
    avg_win FLOAT,
    avg_loss FLOAT,
    profit_factor FLOAT,

    -- Buy & Hold Comparison
    buyhold_return_pct FLOAT,
    outperformance_pct FLOAT,

    -- Detailed Data
    metadata JSON,  -- Trade list, equity curve, etc.

    created_at TIMESTAMP DEFAULT NOW()
);
```

## Multi-Timeframe Strategy

### Base Data: 1-Hour Granularity
- Store all historical data as 1-hour OHLCV bars
- Most detailed base without excessive storage
- Supports intraday strategy analysis

### Execution Timeframes
User can run backtests on different timeframes to test strategy behavior:
- **1h execution**: Strategy evaluates every hour (most active)
- **4h execution**: Strategy evaluates every 4 hours (aggregated from 1h data)
- **1d execution**: Strategy evaluates once per day (aggregated from 1h data)

### Visualization Zoom Levels
Dashboard can display results at different zoom levels (independent of execution timeframe):
- **1h view**: Show every hourly candle
- **4h view**: Aggregate to 4-hour candles for cleaner charts
- **1d view**: Daily candles for long-term perspective
- **1w view**: Weekly candles for macro view

**Example:** Run backtest with 1h execution timeframe, but view the chart in daily zoom for cleaner visualization.

### Data Aggregation
```python
# Pandas resample for on-the-fly aggregation
df_1h = load_hourly_data()
df_4h = df_1h.resample('4H').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})
```

## Backtest Engine Logic

### Initialization
1. Load historical 1-hour OHLCV data for symbol/date range
2. Aggregate to execution timeframe if needed (4h, 1d)
3. Initialize strategy instance (reuse from `src/ai_strategy/strategies/`)
4. Set starting capital (default: $10,000)
5. Initialize position tracker

### Simulation Loop
```python
for bar in historical_bars:
    # 1. Calculate technical indicators up to current bar
    indicators = strategy.calculate_indicators(historical_data[:current_index])

    # 2. Get strategy signal
    signal = strategy.generate_signal(bar, indicators)

    # 3. Execute trade if signal and rules allow
    if signal == 'BUY' and position_size == 0:
        execute_buy(bar.close, capital)
    elif signal == 'SELL' and position_size > 0:
        execute_sell(bar.close)

    # 4. Update position and P&L
    update_unrealized_pnl(bar.close)

    # 5. Track metrics
    update_drawdown()
    record_equity_point()
```

### Buy-and-Hold Baseline
```python
# Parallel calculation for comparison
buyhold_shares = initial_capital / first_bar.close
buyhold_final_value = buyhold_shares * last_bar.close
buyhold_return = (buyhold_final_value - initial_capital) / initial_capital * 100
```

### Metrics Calculation

**Returns:**
- Total Return % = (final_capital - initial_capital) / initial_capital × 100
- Annualized Return % = ((final_capital / initial_capital)^(365/days) - 1) × 100

**Risk:**
- Max Drawdown = max((peak - trough) / peak) × 100
- Volatility = std(daily_returns) × sqrt(252)
- Sharpe Ratio = (annualized_return - risk_free_rate) / volatility
- Sortino Ratio = (annualized_return - risk_free_rate) / downside_deviation

**Trade Statistics:**
- Win Rate = winning_trades / total_trades × 100
- Profit Factor = gross_profit / gross_loss
- Avg Win = sum(winning_trades) / count(winning_trades)
- Avg Loss = sum(losing_trades) / count(losing_trades)

**Execution Assumptions:**
- Slippage: 0.1% per trade (OKX taker fee)
- Fill: Assume immediate fill at bar close price
- No partial fills (simplified for backtesting)

## Streamlit Dashboard

### Sidebar Configuration
```
┌─────────────────────────┐
│ Backtest Configuration  │
├─────────────────────────┤
│ Symbol: [BTC/USDT ▼]    │
│ Start: [2024-01-01]     │
│ End:   [2024-12-31]     │
│ Execution: [1h ▼]       │
│ Chart View: [1d ▼]      │
│ Capital: [$10,000]      │
│                         │
│ [Run Backtest Button]   │
└─────────────────────────┘
```

### Main Display

**1. Summary Cards (Top Row)**
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Strategy     │ Buy & Hold   │ Outperform   │ Max Drawdown │
│ +45.2% ↑     │ +32.1% ↑     │ +13.1%       │ -12.5%       │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**2. Price Chart with Trade Markers**
- Candlestick chart (Plotly interactive)
- Green up-arrows (▲) for BUY points
- Red down-arrows (▼) for SELL points
- Two equity lines overlaid:
  - Blue: Strategy equity curve
  - Gray dashed: Buy-and-hold equity curve

**3. Metrics Comparison Table**
```
┌─────────────────────┬──────────┬────────────┐
│ Metric              │ Strategy │ Buy & Hold │
├─────────────────────┼──────────┼────────────┤
│ Total Return        │ +45.2%   │ +32.1%     │
│ Annualized Return   │ +42.8%   │ +30.5%     │
│ Sharpe Ratio        │ 1.82     │ 1.45       │
│ Max Drawdown        │ -12.5%   │ -18.3%     │
│ Win Rate            │ 58%      │ N/A        │
│ Total Trades        │ 42       │ 1          │
│ Profit Factor       │ 2.1      │ N/A        │
└─────────────────────┴──────────┴────────────┘
```

**4. Trade History (Expandable)**
```
┌────────────┬──────┬────────┬──────────┬───────────┐
│ Date       │ Type │ Price  │ P&L      │ Cum. P&L  │
├────────────┼──────┼────────┼──────────┼───────────┤
│ 2024-03-15 │ BUY  │ 65,234 │ -        │ -         │
│ 2024-03-18 │ SELL │ 67,890 │ +$265.60 │ +$265.60  │
│ ...        │ ...  │ ...    │ ...      │ ...       │
└────────────┴──────┴────────┴──────────┴───────────┘
```

**5. Export Button**
- Downloads CSV with all trade data
- Includes metadata (symbol, dates, parameters)

## Historical Data Manager

### Hybrid Caching Strategy

**On Data Request:**
```python
def get_historical_data(symbol, start_date, end_date, timeframe='1h'):
    # 1. Query database cache
    cached_data = db.query(HistoricalPrices).filter(
        symbol=symbol,
        timestamp >= start_date,
        timestamp <= end_date,
        timeframe='1h'
    )

    # 2. Detect gaps in cached data
    gaps = detect_missing_ranges(cached_data, start_date, end_date)

    # 3. Fetch missing data from OKX API
    if gaps:
        for gap_start, gap_end in gaps:
            api_data = fetch_from_okx(symbol, gap_start, gap_end)
            save_to_cache(api_data)

    # 4. Return complete dataset
    return db.query(...).all()
```

**Benefits:**
- First backtest may be slow (fetching data)
- Subsequent backtests are instant (cached)
- Automatically fills gaps if user expands date range
- Works offline after initial data fetch

### Data Validation
- Check for duplicate timestamps
- Validate OHLC relationships (high >= close, low <= close)
- Detect and flag suspicious volume spikes
- Handle exchange downtime gaps gracefully

## Multi-Crypto Support

### Symbol Configuration
Supported symbols (configurable in .env):
- BTC/USDT (default)
- ETH/USDT
- SOL/USDT

### Individual Backtesting
- User selects ONE symbol at a time
- Each backtest is independent
- Clear comparison per asset
- Simpler than portfolio backtesting

**Future Enhancement:** Could add portfolio mode where capital is split across multiple symbols, but keeping it simple for v1.

## Local Deployment

### Method 1: Launcher Script (Recommended)

**Create `run_backtest.sh`:**
```bash
#!/bin/bash

echo "🚀 Starting Bitcoin Autotrader Backtesting Dashboard"

# Check if PostgreSQL is running
if ! docker ps | grep -q postgres; then
    echo "📦 Starting PostgreSQL..."
    docker-compose up -d postgres
    sleep 3
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Check if historical data exists
echo "🔍 Checking historical data..."
python -c "from src.backtesting.data_manager import check_data_exists; check_data_exists()" || {
    echo "📥 Seeding initial historical data (this may take 2-3 minutes)..."
    python scripts/seed_historical_data.py
}

# Launch Streamlit
echo "✅ Launching dashboard at http://localhost:8501"
streamlit run streamlit_app/backtest_dashboard.py
```

**Usage:**
```bash
chmod +x run_backtest.sh
./run_backtest.sh
```

### Method 2: Docker Compose Profile

**Add to `docker-compose.yml`:**
```yaml
services:
  # ... existing services ...

  streamlit-backtest:
    profiles: ["backtest"]
    build: .
    command: streamlit run streamlit_app/backtest_dashboard.py
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/bitcoin_trader
    depends_on:
      - postgres
    volumes:
      - ./streamlit_app:/app/streamlit_app
      - ./src:/app/src
```

**Usage:**
```bash
docker-compose --profile backtest up
```

### First-Time Data Seeding

**Script: `scripts/seed_historical_data.py`**
```python
# Fetch last 90 days of 1-hour data for BTC, ETH, SOL
# Store in historical_prices table
# Show progress bar
# Takes ~2-3 minutes
```

**Auto-triggered when:**
- User runs backtest and no historical data exists
- Optional: Can run manually to update cache

## Dependencies

**Add to `requirements.txt`:**
```
streamlit==1.28.0
plotly==5.17.0
pandas==2.1.3
numpy==1.26.2
```

**Already included:**
- ccxt (for OKX API)
- sqlalchemy (for database)
- pytest (for testing)

## Testing Strategy

### Unit Tests
- `tests/unit/test_backtest_engine.py`: Simulation loop, metrics calculation
- `tests/unit/test_data_manager.py`: Caching, gap detection, aggregation
- `tests/unit/test_metrics.py`: Sharpe ratio, drawdown calculations

### Integration Tests
- `tests/integration/test_full_backtest.py`: End-to-end backtest with real data
- `tests/integration/test_data_fetching.py`: OKX API integration

### Manual Testing
- Run backtest for BTC 2024 full year
- Verify metrics match expected calculations
- Test multiple timeframes (1h, 4h, 1d)
- Confirm dashboard loads and displays correctly

## Success Metrics

**Performance:**
- Backtest 1 year of hourly data in < 30 seconds
- Dashboard loads in < 3 seconds

**Accuracy:**
- Metrics match hand-calculated values
- Strategy signals match live trading logic

**Usability:**
- Single command deployment works on fresh system
- Intuitive UI requires < 5 minutes to learn

## Future Enhancements (Out of Scope for v1)

- Portfolio backtesting (multiple symbols simultaneously)
- Walk-forward optimization
- Monte Carlo simulation
- Parameter optimization grid search
- Email/Slack notifications for backtest completion
- Historical news event correlation
- Custom strategy upload via UI

## Files to Create

```
src/backtesting/
├── __init__.py
├── engine.py                 # Core backtesting logic
├── data_manager.py           # Historical data caching
├── metrics.py                # Metrics calculations
└── models.py                 # SQLAlchemy models

streamlit_app/
├── backtest_dashboard.py     # Main Streamlit UI
├── components/
│   ├── charts.py             # Plotly chart components
│   ├── metrics_table.py      # Metrics display
│   └── config_panel.py       # Sidebar configuration

scripts/
└── seed_historical_data.py   # Initial data fetching

tests/
├── unit/
│   ├── test_backtest_engine.py
│   ├── test_data_manager.py
│   └── test_metrics.py
└── integration/
    └── test_full_backtest.py

run_backtest.sh               # Launcher script
```

## Database Migrations

**Create migration:**
```bash
alembic revision -m "add_historical_prices_and_backtest_results"
```

**Migration content:**
- Create `historical_prices` table
- Create `backtest_results` table
- Add indexes for performance

## Implementation Phases

**Phase 1: Data Foundation**
1. Create database models and migrations
2. Implement data manager with hybrid caching
3. Create seed script for initial data fetch
4. Test with BTC/USDT

**Phase 2: Backtest Engine**
1. Implement simulation loop
2. Add metrics calculations
3. Create buy-and-hold baseline
4. Unit tests for engine

**Phase 3: Dashboard**
1. Create Streamlit UI structure
2. Add chart components
3. Implement metrics display
4. Add export functionality

**Phase 4: Multi-Timeframe & Multi-Crypto**
1. Add timeframe aggregation
2. Support ETH and SOL
3. Test all combinations

**Phase 5: Deployment & Documentation**
1. Create launcher script
2. Add Docker Compose profile
3. Update README with instructions
4. End-to-end testing

## Conclusion

This design provides a comprehensive backtesting system that:
- Reuses existing strategy code for consistency
- Supports multiple timeframes and cryptocurrencies
- Provides rich visualization and metrics
- Deploys easily for local testing
- Maintains clean separation from live trading

The integrated approach leverages existing infrastructure while adding powerful analysis capabilities to improve strategy development and validation.
