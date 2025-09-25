# Operations Guide - PlayPark FastAPI Backend

## 🚀 Deployment & Operations

This guide covers the operational aspects of running the PlayPark FastAPI backend in production environments.

## 📦 Deployment Options

### Docker Compose (Recommended for Development)

#### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd backend-fastapi

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

#### Service Configuration
```yaml
services:
  api:
    image: playpark-api:latest
    ports:
      - "48080:48080"
    environment:
      ENVIRONMENT: production
      MONGODB_URI: mongodb://admin:password@mongo:27017/playpark
      REDIS_URI: redis://redis:6379/0
    depends_on:
      - mongo
      - redis
```

### Kubernetes Deployment

#### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: playpark-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: playpark-api
  template:
    metadata:
      labels:
        app: playpark-api
    spec:
      containers:
      - name: api
        image: playpark-api:latest
        ports:
        - containerPort: 48080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: playpark-secrets
              key: mongodb-uri
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 48080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 48080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Traditional Server Deployment

#### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Python**: 3.11+
- **Memory**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Storage**: 20GB minimum

#### Installation Steps
```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create virtual environment
python3.11 -m venv /opt/playpark-api
source /opt/playpark-api/bin/activate

# Install dependencies
pip install -e .

# Install systemd service
sudo cp playpark-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable playpark-api
sudo systemctl start playpark-api
```

## 🔧 Configuration Management

### Environment Variables

#### Required Variables
```bash
# Application
ENVIRONMENT=production
SECRET_KEY=your-256-bit-secret-key
API_VERSION=v1

# Database
MONGODB_URI=mongodb://admin:password@localhost:27017/playpark
MONGODB_MAX_POOL_SIZE=50

# Redis
REDIS_URI=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# Security
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20
REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS
CORS_ORIGINS=https://admin.playpark.com,https://app.playpark.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### Optional Variables
```bash
# Performance
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MINUTES=15

# Monitoring
ENABLE_METRICS=true
METRICS_PATH=/metrics

# OAuth2
OAUTH2_CLIENT_ID=playpark-web
OAUTH2_CLIENT_SECRET=your-client-secret

# Cookies
COOKIE_SECURE=true
COOKIE_HTTP_ONLY=true
COOKIE_SAME_SITE=strict
```

### Configuration Validation

#### Startup Checks
```python
# Configuration validation on startup
def validate_configuration():
    required_vars = [
        'SECRET_KEY',
        'MONGODB_URI',
        'REDIS_URI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ConfigurationError(f"Missing required environment variables: {missing_vars}")
```

## 📊 Monitoring & Observability

### Health Checks

#### Application Health
```bash
# Basic health check
curl http://localhost:48080/healthz

# Response
{
  "ok": true,
  "status": "healthy",
  "timestamp": "2025-01-24T10:30:00Z",
  "version": "v1",
  "environment": "production"
}
```

#### Readiness Check
```bash
# Readiness check
curl http://localhost:48080/readyz

# Response
{
  "ok": true,
  "status": "ready",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "external_apis": "available"
  }
}
```

### Metrics & Monitoring

#### Prometheus Metrics
```bash
# Metrics endpoint
curl http://localhost:48080/metrics

# Key metrics
http_requests_total{method="POST",endpoint="/api/v1/sales",status="200"}
http_request_duration_seconds{method="POST",endpoint="/api/v1/sales",quantile="0.95"}
database_connections_active
redis_connections_active
```

#### Application Metrics
- **Request Rate**: Requests per second by endpoint
- **Response Time**: P50, P95, P99 latencies
- **Error Rate**: 4xx and 5xx error percentages
- **Database Connections**: Active and idle connections
- **Redis Usage**: Memory usage and hit rates
- **Business Metrics**: Sales volume, ticket redemptions

### Logging

#### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Critical errors that may stop the application

#### Log Format (JSON)
```json
{
  "timestamp": "2025-01-24T10:30:00Z",
  "level": "INFO",
  "logger": "app.sales",
  "message": "Sale created successfully",
  "request_id": "req_123456789",
  "user_id": "emp_001",
  "sale_id": "sale_123456789",
  "amount": 150.00,
  "tenant_id": "tenant_demo_01",
  "store_id": "store_demo_01"
}
```

#### Log Aggregation
```bash
# Using ELK Stack
# Logstash configuration for parsing JSON logs
input {
  beats {
    port => 5044
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "playpark-api-%{+YYYY.MM.dd}"
  }
}
```

## 🔄 Database Operations

### MongoDB Management

#### Connection Management
```python
# Connection pool configuration
client = AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=50,
    serverSelectionTimeoutMS=2000,
    socketTimeoutMS=2000,
    connectTimeoutMS=1000,
    retryWrites=True
)
```

#### Index Management
```javascript
// Database indexes (automatically created)
db.sales.createIndex({"tenant_id": 1, "store_id": 1, "timestamp": -1})
db.tickets.createIndex({"qr_token": 1}, {"unique": true})
db.audit_logs.createIndex({"tenant_id": 1, "timestamp": -1})
```

#### Backup Strategy
```bash
# Daily backups
mongodump --uri="mongodb://admin:password@localhost:27017/playpark" \
  --out=/backups/playpark-$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="mongodb://admin:password@localhost:27017/playpark" \
  --dir=/backups/playpark-20250124
```

### Redis Management

#### Memory Management
```bash
# Redis memory usage
redis-cli info memory

# Key expiration monitoring
redis-cli --scan --pattern "rate_limit:*" | wc -l
redis-cli --scan --pattern "idempotency:*" | wc -l
```

#### Cache Warming
```python
# Warm cache on startup
async def warm_cache():
    # Load frequently accessed data
    popular_packages = await get_popular_packages()
    await redis_set("cache:popular_packages", popular_packages, expire=3600)
    
    pricing_rules = await get_active_pricing_rules()
    await redis_set("cache:pricing_rules", pricing_rules, expire=1800)
```

## 🔐 Security Operations

### SSL/TLS Configuration

#### Nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name api.playpark.com;
    
    ssl_certificate /etc/ssl/certs/playpark-api.crt;
    ssl_certificate_key /etc/ssl/private/playpark-api.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:48080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Configuration

#### UFW Rules (Ubuntu)
```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow internal MongoDB (if needed)
sudo ufw allow from 10.0.0.0/8 to any port 27017

# Enable firewall
sudo ufw enable
```

## 🚨 Incident Response

### Common Issues & Solutions

#### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check Python memory usage
python -m memory_profiler app/main.py

# Solutions:
# 1. Increase server memory
# 2. Optimize database queries
# 3. Implement connection pooling limits
# 4. Add memory monitoring alerts
```

#### Database Connection Issues
```bash
# Check MongoDB connections
mongo --eval "db.serverStatus().connections"

# Check application connections
curl http://localhost:48080/metrics | grep database_connections

# Solutions:
# 1. Increase connection pool size
# 2. Check for connection leaks
# 3. Implement connection timeouts
# 4. Add connection monitoring
```

#### High CPU Usage
```bash
# Check CPU usage
top -p $(pgrep -f "uvicorn")

# Profile application
python -m cProfile -o profile.stats app/main.py

# Solutions:
# 1. Optimize slow queries
# 2. Add caching
# 3. Scale horizontally
# 4. Implement async processing
```

### Disaster Recovery

#### Backup Strategy
```bash
# Daily automated backups
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/playpark-${DATE}"

# MongoDB backup
mongodump --uri="${MONGODB_URI}" --out="${BACKUP_DIR}/mongodb"

# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb "${BACKUP_DIR}/redis/"

# Application code backup
tar -czf "${BACKUP_DIR}/code.tar.gz" /opt/playpark-api/

# Upload to cloud storage
aws s3 sync "${BACKUP_DIR}" s3://playpark-backups/${DATE}/
```

#### Recovery Procedures
```bash
# Full system recovery
#!/bin/bash
DATE=$1  # Backup date
BACKUP_DIR="/backups/playpark-${DATE}"

# Stop services
systemctl stop playpark-api

# Restore MongoDB
mongorestore --uri="${MONGODB_URI}" "${BACKUP_DIR}/mongodb/playpark"

# Restore Redis
systemctl stop redis
cp "${BACKUP_DIR}/redis/dump.rdb" /var/lib/redis/
systemctl start redis

# Restore application
tar -xzf "${BACKUP_DIR}/code.tar.gz" -C /

# Start services
systemctl start playpark-api
```

## 📈 Performance Optimization

### Application Performance

#### Async Processing
```python
# Use async for I/O operations
async def process_sale(sale_data):
    # Database operations
    sale = await create_sale(sale_data)
    
    # External API calls
    await notify_external_systems(sale)
    
    # File operations
    await generate_receipt(sale)
    
    return sale
```

#### Connection Pooling
```python
# Optimize database connections
DATABASE_POOL_SIZE = 50
DATABASE_MAX_IDLE_TIME = 300

# Optimize Redis connections
REDIS_POOL_SIZE = 20
REDIS_TIMEOUT = 5
```

#### Caching Strategy
```python
# Multi-level caching
async def get_package_info(package_id: str):
    # L1: Memory cache
    cached = memory_cache.get(package_id)
    if cached:
        return cached
    
    # L2: Redis cache
    cached = await redis_get(f"package:{package_id}")
    if cached:
        memory_cache.set(package_id, cached, ttl=300)
        return cached
    
    # L3: Database
    package = await db.packages.find_one({"package_id": package_id})
    await redis_set(f"package:{package_id}", package, expire=3600)
    memory_cache.set(package_id, package, ttl=300)
    
    return package
```

### Database Optimization

#### Query Optimization
```python
# Use indexes effectively
async def get_recent_sales(tenant_id: str, limit: int = 100):
    # This query uses the compound index: {tenant_id: 1, store_id: 1, timestamp: -1}
    return await db.sales.find({
        "tenant_id": tenant_id
    }).sort("timestamp", -1).limit(limit).to_list(limit)
```

#### Aggregation Optimization
```python
# Optimized aggregation pipeline
async def get_sales_summary(tenant_id: str, date_range: tuple):
    pipeline = [
        {"$match": {
            "tenant_id": tenant_id,
            "timestamp": {"$gte": date_range[0], "$lte": date_range[1]}
        }},
        {"$group": {
            "_id": "$payment_method",
            "total_amount": {"$sum": "$grand_total"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"total_amount": -1}}
    ]
    
    return await db.sales.aggregate(pipeline).to_list(None)
```

## 🔧 Maintenance Tasks

### Regular Maintenance

#### Daily Tasks
```bash
# Log rotation
logrotate /etc/logrotate.d/playpark-api

# Database maintenance
mongo --eval "db.runCommand({compact: 'sales'})"

# Cache cleanup
redis-cli --scan --pattern "expired:*" | xargs redis-cli del
```

#### Weekly Tasks
```bash
# Database statistics
mongo --eval "db.stats()"

# Index usage analysis
mongo --eval "db.sales.aggregate([{$indexStats: {}}])"

# Performance analysis
python -m app.scripts.performance_analysis
```

#### Monthly Tasks
```bash
# Security updates
apt update && apt upgrade

# Dependency updates
pip list --outdated
pip install --upgrade -r requirements.txt

# Performance review
python -m app.scripts.monthly_report
```

### Monitoring Alerts

#### Critical Alerts
- **Service Down**: API service not responding
- **High Error Rate**: >5% error rate for 5 minutes
- **Database Down**: MongoDB connection failure
- **Memory Usage**: >90% memory usage
- **Disk Space**: >85% disk usage

#### Warning Alerts
- **High Response Time**: P95 > 2 seconds for 10 minutes
- **High CPU Usage**: >80% CPU for 15 minutes
- **Cache Miss Rate**: >20% Redis miss rate
- **Connection Pool**: >80% connection pool usage

## 📞 Support & Troubleshooting

### Support Contacts
- **Technical Support**: tech-support@playpark.com
- **Emergency Support**: +1-555-PLAYPARK
- **Documentation**: https://docs.playpark.com

### Troubleshooting Checklist

#### Service Not Starting
1. Check logs: `journalctl -u playpark-api -f`
2. Verify configuration: `python -c "from app.config import settings; print(settings.dict())"`
3. Test database connection: `mongosh "${MONGODB_URI}"`
4. Test Redis connection: `redis-cli -u "${REDIS_URI}" ping`

#### Performance Issues
1. Check system resources: `htop`, `iostat`, `free -h`
2. Analyze application metrics: `curl http://localhost:48080/metrics`
3. Review database performance: `mongosh --eval "db.currentOp()"`
4. Check Redis performance: `redis-cli --latency-history`

#### Authentication Issues
1. Verify JWT configuration: Check SECRET_KEY and algorithm
2. Check token expiration: Verify ACCESS_TOKEN_EXPIRE_MINUTES
3. Review rate limiting: Check Redis rate limit keys
4. Analyze audit logs: Look for authentication failures

---

**Operations Contact**: ops@playpark.com  
**Last Updated**: 2025-01-24  
**Next Review**: 2025-04-24
