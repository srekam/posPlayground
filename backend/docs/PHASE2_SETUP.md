# Phase 2 Setup - Device Heartbeats + Alerting

## Overview

Phase 2 implements fleet health monitoring and incident management across all tenants with:

- **Device heartbeat intake** - Real-time device health monitoring
- **Background alert engine** - Automated alert detection and management
- **Alert management APIs** - Acknowledge, resolve, and configure alerts
- **Worker system** - Durable background processing

## Prerequisites

- Phase 1 completed and running
- MongoDB with proper indexes
- PHP 8.x with MongoDB extension
- Background process capability (cron/systemd)

## Installation Steps

### 1. Create Phase 2 Indexes

```bash
cd backend
php src/scripts/create_phase2_indexes.php
```

### 2. Seed Alert Rules

```bash
php src/scripts/seed_alert_rules.php
```

### 3. Start Background Workers

#### Option A: Continuous Worker (Production)
```bash
# Start worker manager (runs continuously)
php src/scripts/run_workers.php start
```

#### Option B: Cron Job (Recommended for Production)
```bash
# Add to crontab to run every 2 minutes
*/2 * * * * cd /path/to/backend && php src/scripts/run_workers.php run-once
```

#### Option C: Systemd Service (Linux)
Create `/etc/systemd/system/playpark-workers.service`:
```ini
[Unit]
Description=PlayPark Alert Workers
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/php src/scripts/run_workers.php start
Restart=always
RestartSec=10
Environment=MONGO_URI=mongodb://mongo:27017/playpark
Environment=JWT_SECRET=your-jwt-secret

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable playpark-workers
sudo systemctl start playpark-workers
```

### 4. Configure Device Heartbeats

Devices should send heartbeats every 60-120 seconds to:
```
POST http://api:48080/heartbeat
```

Sample device implementation:
```javascript
// Send heartbeat every 60 seconds
setInterval(async () => {
  try {
    await fetch('http://api:48080/heartbeat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id: 'device_123',
        tenant_id: 'tenant_456',
        store_id: 'store_789',
        status: 'online',
        error_rate_5m: 0.02,
        request_latency_p95: 125,
        sync_lag_sec: 15,
        app_version: '1.0.0',
        memory_usage: 75,
        cpu_usage: 25,
        disk_usage: 45.5
      })
    });
  } catch (error) {
    console.error('Heartbeat failed:', error);
  }
}, 60000);
```

## API Endpoints

### Device Heartbeat (No Auth Required)
- `POST /heartbeat` - Device heartbeat intake
- `GET /heartbeat/{device_id}/status` - Device status check
- `GET /heartbeat/{device_id}/history` - Heartbeat history

### Alert Management (Provider Auth Required)
- `GET /provider/alerts` - List alerts with filters
- `POST /provider/alerts/{alert_id}/ack` - Acknowledge alert
- `POST /provider/alerts/{alert_id}/resolve` - Resolve alert with reason

### Alert Rules Management (Provider Auth Required)
- `GET /provider/alerts/rules` - List alert rules
- `POST /provider/alerts/rules` - Create new alert rule
- `PUT /provider/alerts/rules/{rule_id}` - Update alert rule
- `DELETE /provider/alerts/rules/{rule_id}` - Delete alert rule

## Alert Types

### 1. Device Offline
- **Trigger**: No heartbeat for > 120 seconds
- **Severity**: High
- **Auto-resolve**: Yes (when heartbeat received)
- **Cooldown**: 5 minutes

### 2. Gate Fail Rate High
- **Trigger**: Gate redemption failure rate > 10% in 60 minutes
- **Severity**: Medium
- **Auto-resolve**: Yes (when fail rate normal)
- **Cooldown**: 15 minutes

### 3. Sync Lag High
- **Trigger**: Device sync lag > 90 seconds
- **Severity**: Medium
- **Auto-resolve**: Yes (when sync lag normal)
- **Cooldown**: 10 minutes

### 4. Reprint Spike
- **Trigger**: Reprints > 3x median in 1 hour
- **Severity**: Medium
- **Auto-resolve**: No
- **Cooldown**: 30 minutes

### 5. Refund Spike
- **Trigger**: Refunds > 3x median in 1 hour
- **Severity**: Medium
- **Auto-resolve**: No
- **Cooldown**: 30 minutes

### 6. After Hours Sales
- **Trigger**: Sales activity outside 9 AM - 10 PM
- **Severity**: Low
- **Auto-resolve**: No
- **Cooldown**: 60 minutes

### 7. Webhook Failures
- **Trigger**: Webhook failure rate > 20% in 30 minutes
- **Severity**: Medium
- **Auto-resolve**: Yes (when success rate normal)
- **Cooldown**: 15 minutes

## Environment Variables

Add these to your `.env` file:

```env
# Alert Engine Configuration
HEARTBEAT_OFFLINE_SECONDS=120
SYNC_LAG_WARN_SECONDS=90

# Worker Configuration
WORKER_SLEEP_SECONDS=120
WORKER_MAX_RETRIES=3
```

## Monitoring and Troubleshooting

### Check Worker Status
```bash
# Check if workers are running
ps aux | grep run_workers.php

# Check worker logs (if using systemd)
sudo journalctl -u playpark-workers -f

# Test worker manually
php src/scripts/run_workers.php run-once
```

### Check Alert Status
```bash
# Get all open alerts
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/alerts?status=open"

# Get critical alerts only
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/alerts?severity=critical&status=open"
```

### Check Device Heartbeats
```bash
# Check device status
curl "http://localhost:48080/heartbeat/device_123/status"

# Get heartbeat history
curl "http://localhost:48080/heartbeat/device_123/history?hours=24"
```

### Database Queries

Check recent heartbeats:
```javascript
db.device_heartbeats.find().sort({timestamp: -1}).limit(10)
```

Check open alerts:
```javascript
db.provider_alerts.find({status: "open"}).sort({first_seen: -1})
```

Check alert rules:
```javascript
db.alert_rules.find({enabled: true})
```

## Performance Considerations

### Database Indexes
- All collections have proper indexes for query performance
- Time-series data (heartbeats) indexed by timestamp
- Alert queries optimized for common filters

### Worker Performance
- Workers run every 2 minutes by default
- Alert evaluation is optimized with MongoDB aggregation
- Cooldown periods prevent alert spam

### Memory Usage
- Heartbeats older than 7 days should be archived
- Alert history should be cleaned up periodically
- Consider implementing data retention policies

## Security Considerations

### Device Authentication
- Heartbeat endpoints don't require authentication
- Devices identified by device_id, tenant_id, store_id
- Consider implementing device tokens for production

### Provider Authentication
- Alert management requires provider JWT tokens
- All alert actions are audited
- Role-based permissions enforced

## Next Steps

Phase 2 provides the foundation for:
- **Phase 3**: Provider RBAC and impersonation
- **Phase 4**: Usage tracking and billing
- **Phase 5**: Metrics aggregation and caching
- **Phase 6**: Advanced reporting

The alerting system is now ready to monitor fleet health and manage incidents across all tenants!
