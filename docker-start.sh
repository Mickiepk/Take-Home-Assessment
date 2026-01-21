#!/bin/bash
# Start the Computer Use Backend with Docker

set -e

echo "🚀 Starting Computer Use Backend with Docker..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and set your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter to continue after setting your API key..."
fi

# Check if ANTHROPIC_API_KEY is set
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY not set in .env file"
    echo "Please edit .env and set your API key"
    exit 1
fi

echo "✅ Configuration loaded"
echo ""

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check health
echo ""
echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access points:"
echo "   • Web UI:    http://localhost:8000/"
echo "   • API Docs:  http://localhost:8000/docs"
echo "   • Health:    http://localhost:8000/health/"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
