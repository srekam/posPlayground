#!/bin/bash

# PlayPark Backend Environment Setup Script

echo "🚀 Setting up PlayPark Backend Environment..."

# Create environment files
echo "📝 Creating environment files..."

# Development environment
cat > .env.development << EOF
# Development Environment Variables
NODE_ENV=development
PORT=48080
API_VERSION=v1

# Database
MONGODB_URI=mongodb://localhost:27017/playpark
DB_NAME=playpark

# Security
JWT_SECRET=dev-jwt-secret-key-2025
JWT_EXPIRES_IN=24h
HMAC_SECRET_V1=dev-hmac-secret-key-2025
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# CORS
CORS_ORIGIN=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=debug
LOG_FILE=logs/app.log

# Admin UI
ADMIN_PORT=3000
ADMIN_SECRET=admin-secret-key-dev

# Webhooks
WEBHOOK_TIMEOUT=5000
WEBHOOK_RETRY_ATTEMPTS=3

# Timezone
TZ=Asia/Bangkok

# Features
ENABLE_KIOSK=true
ENABLE_GATE_BINDING=true
ENABLE_MULTI_PRICE=true
ENABLE_WEBHOOKS=true
ENABLE_OFFLINE_SYNC=true

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_ENABLED=true
EOF

# Production environment
cat > .env.production << EOF
# Production Environment Variables
NODE_ENV=production
PORT=48080
API_VERSION=v1

# Database
MONGODB_URI=mongodb://admin:playpark123@mongo:27017/playpark?authSource=admin
DB_NAME=playpark

# Security
JWT_SECRET=your-super-secret-jwt-key-change-in-production-2025
JWT_EXPIRES_IN=24h
HMAC_SECRET_V1=your-hmac-secret-key-for-qr-signing-2025
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# CORS
CORS_ORIGIN=https://admin.playpark.com,https://pos.playpark.com

# Logging
LOG_LEVEL=info
LOG_FILE=logs/app.log

# Admin UI
ADMIN_PORT=3000
ADMIN_SECRET=admin-secret-key-production

# Webhooks
WEBHOOK_TIMEOUT=5000
WEBHOOK_RETRY_ATTEMPTS=3

# Timezone
TZ=Asia/Bangkok

# Features
ENABLE_KIOSK=true
ENABLE_GATE_BINDING=true
ENABLE_MULTI_PRICE=true
ENABLE_WEBHOOKS=true
ENABLE_OFFLINE_SYNC=true

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_ENABLED=true
EOF

# Copy development as default
cp .env.development .env

echo "✅ Environment files created!"
echo "📁 Files created:"
echo "   - .env (development - default)"
echo "   - .env.development"
echo "   - .env.production"

# Create logs directory
mkdir -p logs
echo "📁 Created logs directory"

# Create health check script
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash

# Health check script for Docker
echo "🔍 Checking PlayPark Backend health..."

# Check if API is responding
if curl -f http://localhost:48080/health > /dev/null 2>&1; then
    echo "✅ API health check passed"
    exit 0
else
    echo "❌ API health check failed"
    exit 1
fi
EOF

chmod +x scripts/health-check.sh
echo "📁 Created health check script"

# Create monitoring script
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash

# Monitoring script for PlayPark Backend
echo "📊 PlayPark Backend Monitoring Dashboard"
echo "========================================"

# API Health
echo "🔍 API Health:"
curl -s http://localhost:48080/health | jq '.' 2>/dev/null || echo "❌ API not responding"

echo ""
echo "📈 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"

echo ""
echo "🐳 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep playpark

echo ""
echo "📝 Recent Logs:"
tail -n 10 logs/app.log 2>/dev/null || echo "No logs found"
EOF

chmod +x scripts/monitor.sh
echo "📁 Created monitoring script"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review and update environment variables in .env files"
echo "2. Run 'docker-compose up -d' to start services"
echo "3. Run './scripts/monitor.sh' to check system status"
echo "4. Access Admin UI at http://localhost:3000"
echo "5. Access API at http://localhost:48080"
echo ""
echo "🔐 Demo Credentials:"
echo "   Email: manager@playpark.demo"
echo "   PIN: 1234"
echo "   Device Token: pos-token-1"
