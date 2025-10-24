#!/bin/bash

set -e  # Exit on error

echo "=== Bitcoin Autotrader (OKX Edition) Deployment ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your OKX API credentials before continuing"
    echo "    Required: OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSPHRASE"
    exit 1
fi

# Check OKX credentials are configured
echo "Checking OKX credentials..."
if grep -q "OKX_API_KEY=your_okx" .env 2>/dev/null; then
    echo "❌ Please replace placeholder values in .env with real OKX credentials"
    echo "   Get credentials from: https://www.okx.com/account/my-api"
    exit 1
fi

if ! grep -q "OKX_API_KEY=.*[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "❌ OKX_API_KEY not configured in .env"
    exit 1
fi

if ! grep -q "OKX_API_SECRET=.*[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "❌ OKX_API_SECRET not configured in .env"
    exit 1
fi

if ! grep -q "OKX_API_PASSPHRASE=.*[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "❌ OKX_API_PASSPHRASE not configured in .env"
    exit 1
fi

echo "✅ OKX credentials configured"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Initializing database..."
docker-compose exec trading-engine python scripts/init_db.py

echo "=== Deployment Complete ==="
echo ""
echo "Services:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Dashboard: Build frontend and serve"
echo ""
echo "Exchange: OKX (sandbox mode: see OKX_TESTNET in .env)"
echo "Paper Trading: see PAPER_TRADING in .env"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
echo "⚠️  Remember: Start with paper trading and testnet before going live!"
