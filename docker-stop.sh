#!/bin/bash
# Stop the Computer Use Backend Docker services

set -e

echo "🛑 Stopping Computer Use Backend..."
echo ""

docker-compose down

echo ""
echo "✅ Services stopped!"
echo ""
echo "💡 To remove volumes (database data):"
echo "   docker-compose down -v"
echo ""
