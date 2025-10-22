#!/bin/bash

# Lead Backend Docker Startup Script

echo "Starting Lead Backend service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create one from .env.example"
    echo "Copy and modify: cp .env.example .env"
    exit 1
fi

echo "✅ .env file found"

# Build and start the container
echo "🔨 Building Docker container..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Build successful"
    echo "🚀 Starting services..."
    docker-compose up -d
    
    echo "📊 Service status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Service should be available at: http://localhost:3000"
    echo "📋 Health check endpoint: http://localhost:3000/health"
    echo ""
    echo "📝 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Build failed"
    exit 1
fi