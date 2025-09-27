#!/bin/bash

# PlayPark POS API Startup Script
# This script sets up and starts the POS API system

set -e

echo "🚀 Starting PlayPark POS API System"
echo "=================================="

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Check if MongoDB is running
if ! command -v mongosh &> /dev/null; then
    echo "⚠️  MongoDB shell not found. Please ensure MongoDB is installed and running."
    echo "   You can install it from: https://docs.mongodb.com/manual/installation/"
fi

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis CLI not found. Please ensure Redis is installed and running."
    echo "   You can install it from: https://redis.io/download"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key-change-in-production"
export MONGODB_URI="mongodb://localhost:27017/playpark"
export REDIS_URI="redis://localhost:6379/0"
export ENVIRONMENT="development"
export PORT="48080"

echo "🔑 Environment variables set:"
echo "   SECRET_KEY: [HIDDEN]"
echo "   MONGODB_URI: $MONGODB_URI"
echo "   REDIS_URI: $REDIS_URI"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   PORT: $PORT"

# Check if MongoDB is accessible
echo "🔍 Checking MongoDB connection..."
if python3 -c "
import asyncio
import motor.motor_asyncio
async def check_mongo():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient('$MONGODB_URI')
        await client.admin.command('ping')
        print('✅ MongoDB connection successful')
        client.close()
    except Exception as e:
        print(f'❌ MongoDB connection failed: {e}')
        exit(1)
asyncio.run(check_mongo())
"; then
    echo "✅ MongoDB connection verified"
else
    echo "❌ MongoDB connection failed. Please ensure MongoDB is running."
    exit 1
fi

# Check if Redis is accessible
echo "🔍 Checking Redis connection..."
if python3 -c "
import redis
try:
    r = redis.from_url('$REDIS_URI')
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
"; then
    echo "✅ Redis connection verified"
else
    echo "❌ Redis connection failed. Please ensure Redis is running."
    exit 1
fi

# Run database migrations and create indexes
echo "🗄️  Setting up database indexes..."
python3 -c "
import asyncio
from app.db.mongo import ensure_indexes
async def setup_db():
    await ensure_indexes()
    print('✅ Database indexes created successfully')
asyncio.run(setup_db())
"

# Seed initial data
echo "🌱 Seeding initial data..."
python3 scripts/seed_data.py

# Start the FastAPI server
echo "🚀 Starting FastAPI server on port $PORT..."
echo "   API Documentation: http://localhost:$PORT/docs"
echo "   ReDoc Documentation: http://localhost:$PORT/redoc"
echo "   Health Check: http://localhost:$PORT/healthz"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
