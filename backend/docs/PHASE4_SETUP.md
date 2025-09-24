# Phase 4 Setup - Usage Tracking + Provider Billing APIs

## Overview

Phase 4 implements comprehensive usage tracking and provider billing with:

- **Usage Tracking Middleware** - Automatic tracking of API calls, webhooks, and storage
- **Billing APIs** - Tenant billing data, plan management, and usage analytics
- **Usage Aggregation** - Background workers for data aggregation and limit checking
- **Overage Detection** - Automatic alerts when tenants exceed plan limits
- **Usage Reports** - CSV and JSON reports for billing and analytics

## Prerequisites

- Phase 1, 2, and 3 completed and running
- MongoDB with proper indexes
- PHP 8.x with MongoDB extension
- Background workers running

## Installation Steps

### 1. Create Phase 4 Indexes

```bash
cd backend
php src/scripts/create_phase4_indexes.php
```

### 2. Restart Workers (includes usage aggregation)

```bash
# Stop existing workers
pkill -f run_workers.php

# Start updated workers
php src/scripts/run_workers.php start
```

### 3. Test Usage Tracking

```bash
# Make API calls to trigger usage tracking
curl -H "Authorization: Bearer YOUR_TENANT_JWT_TOKEN" \
     "http://localhost:48080/api/tenants/tenant_123/stores"

# Check usage counters
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/billing/tenants/tenant_123"
```

## API Endpoints

### Billing Management (Provider Auth Required)
- `GET /provider/billing/tenants` - List all tenants with billing data
- `GET /provider/billing/tenants/{tenant_id}` - Get detailed billing for specific tenant
- `POST /provider/billing/tenants/{tenant_id}/plan` - Update tenant plan
- `GET /provider/billing/usage` - Get usage analytics
- `GET /provider/billing/reports` - Generate usage reports (JSON/CSV)

## Usage Tracking

### Automatic Tracking
The usage tracking middleware automatically tracks:

1. **API Calls**
   - Every request to tenant endpoints
   - Request size, response time, status code
   - Monthly counters per tenant

2. **Webhook Calls**
   - Every webhook delivery attempt
   - Success/failure rates and response times
   - Monthly counters per tenant

3. **Storage Usage**
   - Calculated from sales, tickets, and audit data
   - Total storage in bytes and GB
   - Monthly storage usage per tenant

4. **Device/Store Counts**
   - Real-time count of active devices and stores
   - Current counts vs plan limits
   - Monthly device/store counts per tenant

### Manual Tracking
For custom usage tracking:

```php
// Track webhook call
$usageTracking->trackWebhookCall($tenantId, $webhookId, $success, $responseTime);

// Track storage usage
$usageTracking->trackStorageUsage($tenantId, $storageBytes);

// Track device count
$usageTracking->trackDeviceCount($tenantId);

// Track store count
$usageTracking->trackStoreCount($tenantId);
```

## Plan Management

### Update Tenant Plan
```bash
curl -X POST http://localhost:48080/provider/billing/tenants/tenant_123/plan \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "enterprise",
    "reason": "Customer upgraded due to increased usage requirements"
  }'
```

### Plan Limits

| Plan | Stores | Devices | API Calls | Webhooks | Storage |
|------|--------|---------|-----------|----------|---------|
| Free | 1 | 2 | 10,000 | 100 | 1 GB |
| Basic | 5 | 10 | 50,000 | 500 | 10 GB |
| Premium | 20 | 50 | 200,000 | 2,000 | 50 GB |
| Enterprise | 100 | 200 | 1,000,000 | 10,000 | 200 GB |

## Usage Analytics

### Get Usage Analytics
```bash
# All tenants analytics
curl "http://localhost:48080/provider/billing/usage?start_date=2024-01-01&end_date=2024-01-31&group_by=day" \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN"

# Single tenant analytics
curl "http://localhost:48080/provider/billing/usage?tenant_id=tenant_123&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN"
```

### Analytics Features
- **Time-based grouping**: day, week, month
- **Tenant filtering**: All tenants or specific tenant
- **Date range filtering**: Custom start and end dates
- **Usage trends**: Historical usage patterns
- **Performance metrics**: Response times and success rates

## Usage Reports

### Generate JSON Report
```bash
curl "http://localhost:48080/provider/billing/reports?period=2024-01" \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN"
```

### Generate CSV Report
```bash
curl "http://localhost:48080/provider/billing/reports?period=2024-01&format=csv" \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
  -o usage_report_2024-01.csv
```

### Report Features
- **Monthly summaries**: Total usage across all tenants
- **Overage analysis**: Tenants exceeding plan limits
- **Plan distribution**: Breakdown by subscription plan
- **Cost calculation**: Overage costs and billing data
- **Export formats**: JSON and CSV formats

## Overage Detection

### Automatic Alerts
The system automatically creates alerts when tenants exceed plan limits:

- **Alert Type**: `billing.over_limit`
- **Severity**: Medium
- **Trigger**: Any usage exceeds plan limits
- **Details**: Specific overages and amounts

### Overage Costs (Mock)
- **Stores**: $10 per additional store
- **Devices**: $5 per additional device
- **API Calls**: $0.001 per additional call
- **Webhooks**: $0.01 per additional webhook
- **Storage**: $2 per additional GB

## Health Status

### Status Levels
- **Healthy**: All usage under 75% of limits
- **Caution**: Usage between 75-90% of limits
- **Warning**: Usage between 90-100% of limits
- **Critical**: Usage over 100% of limits (overages)

### Health Monitoring
```bash
# Check tenants with critical health status
curl "http://localhost:48080/provider/billing/tenants?health_status=critical" \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN"

# Check tenants with overages
curl "http://localhost:48080/provider/billing/tenants?has_overages=true" \
  -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN"
```

## Background Workers

### Usage Aggregation Worker
- **Frequency**: Every 10 minutes
- **Tasks**:
  - Aggregate device and store counts
  - Calculate storage usage
  - Check usage limits and create overage alerts
  - Clean up old usage data (12 months retention)

### Data Retention
- **Usage Counters**: 12 months
- **API Calls**: 3 months
- **Webhook Calls**: 3 months
- **Response Metrics**: 3 months

## Environment Variables

Add these to your `.env` file:

```env
# Usage Tracking
USAGE_TRACKING_ENABLED=true
USAGE_RETENTION_MONTHS=12
API_CALLS_RETENTION_MONTHS=3

# Billing
OVERAGE_ALERT_ENABLED=true
BILLING_REPORT_GENERATION=true

# Storage Calculation
STORAGE_BASE_MB=100
STORAGE_PER_SALE_KB=1
STORAGE_PER_TICKET_BYTES=512
STORAGE_PER_AUDIT_BYTES=256
```

## Monitoring and Troubleshooting

### Check Usage Counters
```javascript
// Current month usage for all tenants
db.usage_counters.find({period: "2024-01"})

// Specific tenant usage history
db.usage_counters.find({tenant_id: "tenant_123"}).sort({period: -1})
```

### Check API Calls
```javascript
// Recent API calls
db.api_calls.find().sort({timestamp: -1}).limit(10)

// API calls by tenant
db.api_calls.find({tenant_id: "tenant_123"}).sort({timestamp: -1})
```

### Check Overage Alerts
```javascript
// Active overage alerts
db.provider_alerts.find({type: "billing.over_limit", status: "open"})

// All billing alerts
db.provider_alerts.find({type: "billing.over_limit"}).sort({first_seen: -1})
```

### Check Usage Reports
```javascript
// Generated usage reports
db.usage_reports.find().sort({generated_at: -1})

// Specific period report
db.usage_reports.findOne({period: "2024-01"})
```

## Performance Considerations

### Database Indexes
- All collections have proper indexes for query performance
- Time-series data indexed by timestamp
- Tenant-specific queries optimized

### Aggregation Performance
- Usage aggregation runs every 10 minutes
- Data cleanup runs daily
- Monthly reports generated on demand

### Memory Usage
- Usage data older than 12 months is archived
- API call data older than 3 months is cleaned up
- Consider implementing data retention policies

## Security Considerations

### Permission Requirements
- **Billing Read**: Required for viewing billing data
- **Billing Update**: Required for changing tenant plans
- **Reports Read**: Required for generating reports

### Audit Trail
- All plan changes are audited
- Usage tracking includes IP addresses
- Billing actions are logged with reasons

## Next Steps

Phase 4 provides the foundation for:
- **Phase 5**: Metrics aggregation and caching
- **Phase 6**: Advanced reporting and analytics

The usage tracking and billing system is now ready to support comprehensive tenant management with detailed usage analytics and billing capabilities!
