#!/bin/bash
# Quick setup script for duo-crawler using uv

set -e

echo "🚀 Setting up duo-crawler with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    else
        # Linux/macOS
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
fi

echo "📥 Installing dependencies..."
uv sync

echo "⚙️ Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your Duolingo credentials"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Duolingo credentials"
echo "2. Run: uv run duo-crawler base-info"
echo ""
echo "Available commands:"
echo "  uv run duo-crawler base-info    # Download base information"
echo "  uv run pytest                   # Run tests"
echo "  uv run black .                  # Format code"
