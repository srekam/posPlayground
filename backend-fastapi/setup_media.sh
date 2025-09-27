#!/bin/bash

# Media API Setup Script for PlayPark FastAPI
# This script sets up the media storage infrastructure

set -e

echo "🚀 Setting up Media API Infrastructure"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Starting infrastructure services..."

# Start the services
docker-compose -f docker-compose.media.yml up -d

print_status "Waiting for services to be ready..."

# Wait for MinIO to be ready
print_status "Waiting for MinIO..."
until docker exec playpark-minio mc ready local 2>/dev/null; do
    sleep 2
done
print_success "MinIO is ready"

# Wait for Redis to be ready
print_status "Waiting for Redis..."
until docker exec playpark-redis redis-cli ping 2>/dev/null | grep -q PONG; do
    sleep 2
done
print_success "Redis is ready"

# Wait for MongoDB to be ready
print_status "Waiting for MongoDB..."
until docker exec playpark-mongodb mongosh --eval "db.adminCommand('ping')" 2>/dev/null | grep -q "ok.*1"; do
    sleep 2
done
print_success "MongoDB is ready"

# Create MinIO bucket
print_status "Creating media bucket in MinIO..."
docker exec playpark-minio mc mb local/media --ignore-existing

# Set bucket policy for public read access (for public assets)
print_status "Setting bucket policy..."
docker exec playpark-minio mc anonymous set public local/media

print_success "Infrastructure setup complete!"

echo ""
echo "📋 Service Information:"
echo "======================="
echo "MinIO Console: http://localhost:9001"
echo "MinIO API: http://localhost:9000"
echo "Username: minioadmin"
echo "Password: minioadmin"
echo ""
echo "Redis: redis://localhost:6379"
echo "MongoDB: mongodb://localhost:27017"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating example..."
    cat > .env << EOF
# Media Storage Configuration
S3_ENDPOINT=http://localhost:9000
S3_REGION=us-east-1
S3_BUCKET=media
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_USE_SSL=false
S3_SIGNED_URL_TTL=3600
S3_MAX_FILE_SIZE=10485760
S3_ALLOWED_MIME_TYPES=image/jpeg,image/png,image/webp,image/avif,image/gif

# Media Processing
MEDIA_CDN_BASE_URL=
MEDIA_PROCESSING_ENABLED=true
MEDIA_VARIANT_SIZES=thumb:150x150,sm:300x300,md:600x600,lg:1200x1200
MEDIA_STRIP_EXIF=true
MEDIA_COMPRESS_QUALITY=85
MEDIA_DOMINANT_COLOR=true

# Database
MONGODB_URI=mongodb://localhost:27017/playpark
REDIS_URI=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
OAUTH2_CLIENT_SECRET=your-oauth2-secret-here
EOF
    print_success "Created .env file with default values"
    print_warning "Please update the SECRET_KEY and OAUTH2_CLIENT_SECRET values"
fi

echo ""
echo "🧪 Testing the setup..."
echo "======================="

# Test MinIO connection
if docker exec playpark-minio mc ls local/media > /dev/null 2>&1; then
    print_success "MinIO connection test passed"
else
    print_error "MinIO connection test failed"
fi

# Test Redis connection
if docker exec playpark-redis redis-cli ping | grep -q PONG; then
    print_success "Redis connection test passed"
else
    print_error "Redis connection test failed"
fi

# Test MongoDB connection
if docker exec playpark-mongodb mongosh --eval "db.adminCommand('ping')" | grep -q "ok.*1"; then
    print_success "MongoDB connection test passed"
else
    print_error "MongoDB connection test failed"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Start the FastAPI server: python -m uvicorn app.main:app --reload"
echo "3. Test the API: python test_media_api.py"
echo ""
echo "📚 Documentation:"
echo "- Media API Docs: MEDIA_API_DOCUMENTATION.md"
echo "- API Documentation: http://localhost:48080/docs (when server is running)"
echo ""
echo "🔧 Troubleshooting:"
echo "- Check service logs: docker-compose -f docker-compose.media.yml logs"
echo "- Restart services: docker-compose -f docker-compose.media.yml restart"
echo "- Stop services: docker-compose -f docker-compose.media.yml down"
