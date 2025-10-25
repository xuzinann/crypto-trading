import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.backtesting.data_manager import DataManager
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import MetricsCalculator


class SimpleStrategy:
    """Simple strategy wrapper for backtesting"""

    def generate_signal(self, row, historical_data):
        """Generate trading signal based on simple technical indicators"""
        if len(historical_data) < 50:
            return 'HOLD'

        # Calculate simple moving averages
        closes = historical_data['close']
        ma_20 = closes.rolling(window=20).mean()
        ma_50 = closes.rolling(window=50).mean()

        # Simple crossover strategy
        current_ma20 = ma_20.iloc[-1]
        current_ma50 = ma_50.iloc[-1]
        prev_ma20 = ma_20.iloc[-2]
        prev_ma50 = ma_50.iloc[-2]

        # Golden cross - buy signal
        if prev_ma20 <= prev_ma50 and current_ma20 > current_ma50:
            return 'BUY'
        # Death cross - sell signal
        elif prev_ma20 >= prev_ma50 and current_ma20 < current_ma50:
            return 'SELL'

        return 'HOLD'


# Page configuration
st.set_page_config(
    page_title="Bitcoin Autotrader Backtest",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Bitcoin Autotrader Backtest Dashboard")

# Sidebar configuration
st.sidebar.header("Configuration")

# Symbol selector
symbol = st.sidebar.selectbox(
    "Symbol",
    options=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    index=0
)

# Date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=90)
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now()
    )

# Execution timeframe
execution_timeframe = st.sidebar.selectbox(
    "Execution Timeframe",
    options=["1h", "4h", "1d"],
    index=0
)

# Chart view zoom
chart_zoom = st.sidebar.selectbox(
    "Chart View",
    options=["1h", "4h", "1d", "1w"],
    index=2
)

# Initial capital
initial_capital = st.sidebar.number_input(
    "Initial Capital ($)",
    min_value=1000.0,
    max_value=1000000.0,
    value=10000.0,
    step=1000.0
)

# Run button
run_button = st.sidebar.button("🚀 Run Backtest", type="primary")

# Main content
if run_button:
    with st.spinner("Running backtest..."):
        try:
            # Convert dates to datetime
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            # Get database session
            db = next(get_db())

            # Fetch historical data
            data_manager = DataManager()
            cached_data = data_manager.get_cached_data(
                db=db,
                symbol=symbol,
                start=start_dt,
                end=end_dt,
                timeframe=execution_timeframe
            )

            if not cached_data:
                st.warning(f"No cached data found. Fetching from API...")
                api_data = data_manager.fetch_from_api(
                    symbol=symbol,
                    start=start_dt,
                    end=end_dt,
                    timeframe=execution_timeframe
                )
                st.info(f"Fetched {len(api_data)} data points from API")

                # Convert to DataFrame
                df = pd.DataFrame(api_data)
            else:
                # Convert cached data to DataFrame
                df = pd.DataFrame([
                    {
                        'timestamp': d.timestamp,
                        'open': d.open,
                        'high': d.high,
                        'low': d.low,
                        'close': d.close,
                        'volume': d.volume
                    }
                    for d in cached_data
                ])

            if len(df) == 0:
                st.error("No data available for the selected date range")
            else:
                # Run backtest
                strategy = SimpleStrategy()
                engine = BacktestEngine(strategy=strategy, initial_capital=initial_capital)
                result = engine.run(df)

                # Calculate metrics
                calc = MetricsCalculator()
                total_return = calc.calculate_total_return(
                    initial_capital,
                    result['final_capital']
                )

                # Calculate buy-and-hold
                buyhold_shares = initial_capital / df.iloc[0]['close']
                buyhold_final = buyhold_shares * df.iloc[-1]['close']
                buyhold_return = calc.calculate_total_return(initial_capital, buyhold_final)

                # Display results
                st.success("Backtest complete!")

                # Summary cards
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Strategy Return",
                        f"{total_return:.2f}%",
                        delta=f"{total_return:.2f}%"
                    )

                with col2:
                    st.metric(
                        "Buy & Hold Return",
                        f"{buyhold_return:.2f}%",
                        delta=f"{buyhold_return:.2f}%"
                    )

                with col3:
                    outperformance = total_return - buyhold_return
                    st.metric(
                        "Outperformance",
                        f"{outperformance:.2f}%"
                    )

                with col4:
                    st.metric(
                        "Total Trades",
                        len(engine.trades)
                    )

                # Trade details
                st.subheader("Trade History")
                if engine.trades:
                    trades_df = pd.DataFrame(engine.trades)
                    st.dataframe(trades_df, use_container_width=True)
                else:
                    st.info("No trades executed")

                # Price chart with trade markers
                st.subheader("Price Chart with Trade Markers")

                # Create candlestick chart
                fig = make_subplots(rows=1, cols=1)

                # Add candlestick
                fig.add_trace(go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ))

                # Add buy markers
                buy_trades = [t for t in engine.trades if t['type'] == 'BUY']
                if buy_trades:
                    buy_times = [t['timestamp'] for t in buy_trades]
                    buy_prices = [t['price'] for t in buy_trades]
                    fig.add_trace(go.Scatter(
                        x=buy_times,
                        y=buy_prices,
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up',
                            size=15,
                            color='green'
                        ),
                        name='Buy'
                    ))

                # Add sell markers
                sell_trades = [t for t in engine.trades if t['type'] == 'SELL']
                if sell_trades:
                    sell_times = [t['timestamp'] for t in sell_trades]
                    sell_prices = [t['price'] for t in sell_trades]
                    fig.add_trace(go.Scatter(
                        x=sell_times,
                        y=sell_prices,
                        mode='markers',
                        marker=dict(
                            symbol='triangle-down',
                            size=15,
                            color='red'
                        ),
                        name='Sell'
                    ))

                # Update layout
                fig.update_layout(
                    title=f'{symbol} Price with Trade Markers',
                    yaxis_title='Price (USD)',
                    xaxis_title='Date',
                    height=600,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error running backtest: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
else:
    st.info("Configure parameters and click 'Run Backtest' to start")
