#!/bin/bash

# Quick Admin UI Start Script with Force Kill
# Simple script to start Admin UI without full rebuild

echo "🚀 Quick Admin UI Start"
echo "======================"

# Force kill any existing processes on port 3000
echo "🛑 Checking for existing processes on port 3000..."
if lsof -ti:3000 >/dev/null 2>&1; then
    echo "Found existing process on port 3000, killing it..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
    echo "✅ Port 3000 cleared"
else
    echo "Port 3000 is free"
fi

# Also kill any react-scripts processes
echo "🛑 Killing any existing react-scripts processes..."
pkill -f "react-scripts start" 2>/dev/null || true
sleep 1

cd /Users/Shared/posPlayground/backend/admin-ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies first..."
    npm install
fi

echo "🎯 Starting Admin UI..."
echo "Admin UI will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

npm start
