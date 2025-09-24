# Phase 1 Setup - Provider Data Layer + Core APIs

## Prerequisites

- PHP 8.x with MongoDB extension
- MongoDB 4.4+
- Composer for PHP dependencies

## Installation Steps

### 1. Install Dependencies

```bash
cd backend
composer install
```

### 2. Environment Configuration

Create `.env` file with required environment variables:

```env
# Application
APP_MODE=prod
API_PORT=48080
TZ=Asia/Bangkok

# Database
MONGO_URI=mongodb://mongo:27017/playpark

# JWT
JWT_SECRET=your-super-secure-jwt-secret-key-here

# Provider Configuration
PROVIDER_2FA_REQUIRED=true
HEARTBEAT_OFFLINE_SECONDS=120
SYNC_LAG_WARN_SECONDS=90
```

### 3. Database Setup

#### Create Indexes
```bash
php src/scripts/create_provider_indexes.php
```

#### Seed Sample Data
```bash
php src/scripts/seed_provider_data.php
```

### 4. Update Server Configuration

Add provider routes to your main server file:

```php
// In your main server.php or index.php
require_once 'src/routes/provider.php';
```

### 5. Test the APIs

#### Health Check
```bash
curl http://localhost:48080/health
```

#### Provider Overview (requires provider JWT token)
```bash
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     http://localhost:48080/provider/overview
```

## API Endpoints

### Overview
- `GET /provider/overview` - Fleet dashboard metrics

### Tenants
- `GET /provider/tenants` - List all tenants with pagination
- `GET /provider/tenants/{tenant_id}/summary` - Tenant details
- `GET /provider/tenants/{tenant_id}/stores` - Tenant stores
- `GET /provider/tenants/{tenant_id}/devices` - Tenant devices

### Cross-Tenant
- `GET /provider/stores` - All stores across tenants
- `GET /provider/devices` - All devices across tenants

### Health
- `GET /health` - System health check

## Database Collections Created

1. **provider_metrics_daily** - Daily aggregated metrics
2. **device_heartbeats** - Device health monitoring
3. **provider_alerts** - System alerts and incidents
4. **provider_audits** - Provider action audit trail
5. **subscriptions** - Tenant subscription data
6. **usage_counters** - API and usage tracking
7. **secrets** - Versioned HMAC keys and secrets
8. **provider_users** - Provider console users

## Authentication

Provider APIs require JWT tokens with `scope: "provider"`. The middleware automatically:
- Validates JWT signature
- Checks token expiration
- Verifies provider user exists and is active
- Rejects tenant-scoped tokens

## Response Format

All provider APIs return consistent envelope format:

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "unique_request_id",
  "data": { /* response data */ },
  "error": null
}
```

## Next Steps

Phase 1 provides the foundation for:
- Device heartbeat monitoring (Phase 2)
- Provider RBAC and impersonation (Phase 3)
- Usage tracking and billing (Phase 4)
- Metrics aggregation (Phase 5)
- Advanced reporting (Phase 6)

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check `MONGO_URI` environment variable
   - Ensure MongoDB is running and accessible

2. **JWT Token Invalid**
   - Verify `JWT_SECRET` matches between token creation and validation
   - Check token expiration

3. **Provider User Not Found**
   - Ensure provider users are created in `provider_users` collection
   - Check user is marked as `is_active: true`

4. **Index Creation Failed**
   - Run index creation script with proper MongoDB permissions
   - Check for existing conflicting indexes
