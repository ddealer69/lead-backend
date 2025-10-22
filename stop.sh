#!/bin/bash

# Lead Backend Docker Stop Script

echo "🛑 Stopping Lead Backend service..."

# Stop and remove containers
docker-compose down

echo "📊 Checking remaining containers..."
docker-compose ps

echo "✅ Lead Backend service stopped"
echo ""
echo "💡 To start again: ./start.sh"
echo "📝 To view logs: docker-compose logs"