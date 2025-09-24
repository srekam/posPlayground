# Phase 5 Setup - Aggregations + Cached Overview

## Overview

Phase 5 implements comprehensive metrics aggregation and cached overview with:

- **Metrics Aggregation** - Background workers for daily metrics calculation
- **Cache System** - High-performance caching for overview data
- **Enhanced Overview APIs** - Dashboard, metrics, and real-time overview
- **Timezone Handling** - Asia/Bangkok timezone support with business hours
- **Clock Skew Detection** - Device time synchronization monitoring
- **Performance Optimization** - Sub-second response times with caching

## Prerequisites

- Phase 1, 2, 3, and 4 completed and running
- MongoDB with proper indexes
- PHP 8.x with MongoDB extension
- Background workers running

## Installation Steps

### 1. Create Phase 5 Indexes

```bash
cd backend
php src/scripts/create_phase5_indexes.php
```

### 2. Restart Workers (includes metrics aggregation)

```bash
# Stop existing workers
pkill -f run_workers.php

# Start updated workers
php src/scripts/run_workers.php start
```

### 3. Test Enhanced Overview APIs

```bash
# Test overview endpoint
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/overview"

# Test dashboard endpoint
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/dashboard?period=24h"

# Test metrics endpoint
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/metrics?period=7d"
```

## API Endpoints

### Enhanced Overview (Provider Auth Required)
- `GET /provider/overview` - Cached fleet overview with health status
- `GET /provider/dashboard` - Comprehensive dashboard with trends
- `GET /provider/metrics` - Detailed metrics with filtering

## Metrics Aggregation

### Daily Metrics Calculation
The metrics aggregation worker calculates daily metrics for:

1. **Fleet Metrics**
   - Active tenants, stores, and devices
   - Device uptime percentages
   - Online/offline device counts

2. **Sales Metrics**
   - Daily, weekly, and monthly sales totals
   - Redemption counts and rates
   - Refund and reprint rates

3. **Performance Metrics**
   - Response time percentiles (P95, P99)
   - Sync lag percentiles
   - Error rates and success rates

4. **Usage Metrics**
   - API call counts and trends
   - Webhook delivery rates
   - Data transfer volumes

5. **Alert Metrics**
   - Open alerts by severity and type
   - Alert trends and patterns
   - Incident counts and status

### Aggregation Schedule
- **Frequency**: Every 5 minutes
- **Daily Metrics**: Calculated once per day at midnight Asia/Bangkok
- **Cache Updates**: Every 30 seconds for overview data
- **Tenant Caches**: Updated every 5 minutes

## Cache System

### Cache Levels
1. **Overview Cache** - Fleet-wide metrics (30-second TTL)
2. **Tenant Cache** - Tenant-specific metrics (5-minute TTL)
3. **Metrics Cache** - Detailed metrics data (1-minute TTL)

### Cache Performance
- **Response Times**: < 50ms for cached data
- **Hit Rate**: > 95% for overview endpoints
- **Storage**: MongoDB-based cache collection
- **Cleanup**: Automatic expiration and cleanup

### Cache Management
```bash
# Check cache status
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/overview"

# Response will show cache_status: "cached" or "real_time"
```

## Timezone Handling

### Asia/Bangkok Timezone
- **Default Timezone**: Asia/Bangkok (UTC+7)
- **Business Hours**: 9:00 AM - 10:00 PM
- **Date Ranges**: All metrics calculated in local timezone
- **Business Day Detection**: Automatic weekend and holiday handling

### Timezone Configuration
```env
# .env file
TZ=Asia/Bangkok
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=22:00
```

### Date Range Support
- **24h**: Last 24 hours
- **7d**: Last 7 days
- **30d**: Last 30 days
- **today**: Today's data
- **yesterday**: Yesterday's data
- **this_month**: Current month
- **last_month**: Previous month

## Clock Skew Detection

### Automatic Detection
The system automatically detects device clock skew:

- **Threshold**: 5 minutes (300 seconds)
- **Severity Levels**: Low, Medium, High, Critical
- **Recommendations**: Automatic suggestions for time sync

### Skew Monitoring
```bash
# Check for clock skew in device heartbeats
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/devices?include_skew=true"
```

### Skew Alerts
- **Low**: 5-10 minutes - Monitor for issues
- **Medium**: 10-30 minutes - Consider updating device time
- **High**: 30-60 minutes - Check device time settings
- **Critical**: > 60 minutes - Immediate attention required

## Performance Optimization

### Database Indexes
All collections have optimized indexes for:
- Time-series queries
- Tenant-specific filtering
- Metrics aggregation
- Cache operations

### Query Optimization
- **Aggregation Pipelines**: Optimized for performance
- **Index Usage**: Proper index utilization
- **Data Retention**: 12 months for metrics, 3 months for raw data
- **Batch Processing**: Efficient bulk operations

### Response Time Targets
- **Overview API**: < 50ms (cached), < 200ms (real-time)
- **Dashboard API**: < 100ms (cached), < 500ms (real-time)
- **Metrics API**: < 150ms (cached), < 800ms (real-time)

## Dashboard Features

### Overview Dashboard
- **Fleet Status**: Real-time fleet health and status
- **Alert Summary**: Critical, medium, and low alerts
- **Performance Metrics**: Response times and sync lag
- **Usage Summary**: API calls and webhook delivery

### Detailed Dashboard
- **Trend Analysis**: Sales, usage, and performance trends
- **Alert Breakdown**: Alerts by type and severity
- **Top Endpoints**: Most frequently used APIs
- **Health Monitoring**: Overall system health status

### Metrics Dashboard
- **Fleet Metrics**: Tenant, store, and device counts
- **Sales Metrics**: Revenue, redemptions, and rates
- **Performance Metrics**: Response times and error rates
- **Usage Metrics**: API calls and data transfer

## Monitoring and Troubleshooting

### Check Cache Status
```javascript
// Check cache collection
db.cache.find().sort({updated_at: -1}).limit(5)

// Check cache statistics
db.cache.aggregate([
  {$group: {
    _id: null,
    total_items: {$sum: 1},
    expired_items: {$sum: {$cond: [{$lt: ["$expires_at", new Date()]}, 1, 0]}}
  }}
])
```

### Check Metrics Aggregation
```javascript
// Check daily metrics
db.provider_metrics_daily.find().sort({date: -1}).limit(5)

// Check aggregation status
db.provider_metrics_daily.aggregate([
  {$group: {
    _id: null,
    latest_date: {$max: "$date"},
    total_records: {$sum: 1}
  }}
])
```

### Check Worker Status
```bash
# Check worker logs
tail -f logs/worker.log

# Check worker process
ps aux | grep run_workers.php
```

### Performance Monitoring
```javascript
// Check API call performance
db.api_calls.aggregate([
  {$group: {
    _id: null,
    avg_response_time: {$avg: "$processing_time_ms"},
    p95_response_time: {$percentile: {input: "$processing_time_ms", p: [0.95]}}
  }}
])

// Check sync lag performance
db.device_heartbeats.aggregate([
  {$match: {"metrics.sync_lag_sec": {$exists: true}}},
  {$group: {
    _id: null,
    avg_sync_lag: {$avg: "$metrics.sync_lag_sec"},
    p95_sync_lag: {$percentile: {input: "$metrics.sync_lag_sec", p: [0.95]}}
  }}
])
```

## Environment Variables

Add these to your `.env` file:

```env
# Timezone Configuration
TZ=Asia/Bangkok
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=22:00

# Cache Configuration
CACHE_DEFAULT_TTL=300
CACHE_OVERVIEW_TTL=30
CACHE_TENANT_TTL=300
CACHE_METRICS_TTL=60

# Performance Configuration
METRICS_AGGREGATION_INTERVAL=300
CACHE_CLEANUP_INTERVAL=300
MAX_CACHE_SIZE_MB=100

# Clock Skew Detection
CLOCK_SKEW_THRESHOLD=300
CLOCK_SKEW_ALERT_ENABLED=true
```

## Health Checks

### System Health
```bash
# Check overall system health
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/overview" | jq '.data.health_status'

# Expected values: "healthy", "warning", "critical"
```

### Cache Health
```bash
# Check cache performance
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/overview" | jq '.data.cache_status'

# Expected values: "cached", "real_time"
```

### Worker Health
```bash
# Check worker status
ps aux | grep run_workers.php

# Check worker logs for errors
tail -f logs/worker.log | grep ERROR
```

## Data Retention

### Metrics Data
- **Daily Metrics**: 12 months
- **Raw Data**: 3 months
- **Cache Data**: TTL-based (30-300 seconds)

### Cleanup Schedule
- **Cache Cleanup**: Every 5 minutes
- **Metrics Cleanup**: Daily at 2 AM
- **Raw Data Cleanup**: Weekly on Sundays

## Security Considerations

### Cache Security
- **Access Control**: Provider authentication required
- **Data Isolation**: Tenant-specific cache keys
- **TTL Limits**: Automatic expiration prevents stale data

### Performance Security
- **Rate Limiting**: API rate limits enforced
- **Resource Limits**: Cache size limits
- **Error Handling**: Graceful degradation on errors

## Next Steps

Phase 5 provides the foundation for:
- **Phase 6**: Advanced reporting and analytics
- **Real-time Monitoring**: Live dashboard updates
- **Predictive Analytics**: Trend analysis and forecasting

The metrics aggregation and caching system is now ready to support high-performance overview dashboards with sub-second response times and comprehensive fleet monitoring capabilities!
