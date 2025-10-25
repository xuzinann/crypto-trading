#!/bin/bash

echo "🚀 Starting Bitcoin Autotrader Backtesting Dashboard"
echo ""

# Check if PostgreSQL is running
if ! docker ps | grep -q postgres; then
    echo "📦 Starting PostgreSQL..."
    docker-compose up -d postgres
    sleep 3
else
    echo "✅ PostgreSQL already running"
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

# Run database migrations
echo "🗄️  Running database migrations..."
python src/database/migrations/add_backtest_tables.py

# Launch Streamlit
echo ""
echo "✅ Launching dashboard at http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""
streamlit run streamlit_app/backtest_dashboard.py
