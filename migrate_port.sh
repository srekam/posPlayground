#!/bin/bash

# PlayPark Port Migration Script
# This script helps restart services with the new port configuration

echo "🚀 PlayPark Port Migration to 50080"
echo "=================================="

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        echo "   Process: $(lsof -Pi :$port -sTCP:LISTEN)"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Check if old port is still in use
echo "Checking port 48080..."
if check_port 48080; then
    echo "✅ Port 48080 is free - no conflicts detected"
else
    echo "⚠️  Port 48080 is still in use - you may need to stop the conflicting service"
fi

# Check if new port is available
echo "Checking port 50080..."
if check_port 50080; then
    echo "✅ Port 50080 is available - ready to start services"
else
    echo "❌ Port 50080 is already in use - please choose a different port"
    exit 1
fi

echo ""
echo "📋 Updated Configuration Files:"
echo "  ✅ Flutter App: lib/core/config/app_config.dart"
echo "  ✅ FastAPI Backend: backend-fastapi/app/config.py"
echo "  ✅ Admin UI: backend/admin-ui/package.json"
echo "  ✅ Docker Compose: backend-fastapi/docker-compose.yml"
echo "  ✅ Environment: backend-fastapi/env.example"
echo "  ✅ API Config: backend/admin-ui/src/config/api.js"

echo ""
echo "🔄 To restart services:"
echo ""
echo "1. Stop existing services:"
echo "   docker-compose -f backend-fastapi/docker-compose.yml down"
echo ""
echo "2. Start services with new port:"
echo "   docker-compose -f backend-fastapi/docker-compose.yml up -d"
echo ""
echo "3. Start Admin UI:"
echo "   cd backend/admin-ui && npm start"
echo ""
echo "4. Start Flutter App:"
echo "   flutter run"
echo ""
echo "🌐 New URLs:"
echo "  • FastAPI Backend: http://localhost:50080"
echo "  • Admin UI: http://localhost:3000"
echo "  • API Docs: http://localhost:50080/docs"
echo ""
echo "✨ Migration complete! Your services are now running on port 50080"
