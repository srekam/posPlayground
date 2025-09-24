# Phase 3 Setup - Provider RBAC + Impersonation

## Overview

Phase 3 implements secure provider roles and safe tenant impersonation with:

- **Provider User Management** - Separate user accounts for provider console
- **Role-Based Access Control** - Granular permissions for different roles
- **2FA/TOTP Authentication** - Two-factor authentication for provider accounts
- **Tenant Impersonation** - Secure impersonation with audit trails
- **Enhanced Security** - Account lockout, session management, and audit logging

## Prerequisites

- Phase 1 and Phase 2 completed and running
- MongoDB with proper indexes
- PHP 8.x with MongoDB extension
- Background workers running

## Installation Steps

### 1. Create Phase 3 Indexes

```bash
cd backend
php src/scripts/create_phase3_indexes.php
```

### 2. Seed Provider Users

```bash
php src/scripts/seed_provider_users.php
```

This creates 4 default provider users:
- **Admin**: `admin@playpark.com` / `Admin123!` (Full access)
- **NOC**: `noc@playpark.com` / `NOC123!` (Technical support)
- **Billing**: `billing@playpark.com` / `Billing123!` (Billing operations)
- **Read-Only**: `readonly@playpark.com` / `ReadOnly123!` (View only)

### 3. Restart Workers (includes impersonation cleanup)

```bash
# Stop existing workers
pkill -f run_workers.php

# Start updated workers
php src/scripts/run_workers.php start
```

### 4. Test Provider Authentication

```bash
# Test login
curl -X POST http://localhost:48080/provider/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@playpark.com", "password": "Admin123!"}'
```

## API Endpoints

### Authentication (No Auth Required)
- `POST /provider/auth/login` - Provider login with optional 2FA

### 2FA Management (Provider Auth Required)
- `POST /provider/auth/2fa/setup` - Setup 2FA (generate secret and backup codes)
- `POST /provider/auth/2fa/enable` - Enable 2FA (verify TOTP code)
- `POST /provider/auth/2fa/disable` - Disable 2FA (verify TOTP code)

### Impersonation (Provider Auth Required)
- `POST /provider/impersonate/start` - Start tenant impersonation
- `POST /provider/impersonate/{id}/stop` - End impersonation session
- `GET /provider/impersonate/active` - List active impersonations

## Provider Roles

### 1. Provider-Admin
- **Permissions**: Full access (`["*"]`)
- **Impersonation**: Allowed for all tenants
- **Use Case**: System administrators
- **Default User**: `admin@playpark.com`

### 2. NOC (Network Operations Center)
- **Permissions**: 
  - Read access to overview, tenants, stores, devices, alerts
  - Acknowledge and resolve alerts
  - Start/stop impersonation
- **Impersonation**: Allowed for all tenants
- **Use Case**: Technical support and incident management
- **Default User**: `noc@playpark.com`

### 3. Billing-Ops
- **Permissions**:
  - Read access to overview, tenants, stores, devices, alerts
  - Update tenant information
  - Read/update billing information
  - Read reports
- **Impersonation**: Not allowed
- **Use Case**: Billing and account management
- **Default User**: `billing@playpark.com`

### 4. Read-Only
- **Permissions**: Read-only access to all data
- **Impersonation**: Not allowed
- **Use Case**: Stakeholders and auditors
- **Default User**: `readonly@playpark.com`

## 2FA/TOTP Setup

### 1. Setup 2FA
```bash
curl -X POST http://localhost:48080/provider/auth/2fa/setup \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN" \
  -H "Content-Type: application/json"
```

### 2. Enable 2FA
```bash
curl -X POST http://localhost:48080/provider/auth/2fa/enable \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"totp_code": "123456"}'
```

### 3. Login with 2FA
```bash
curl -X POST http://localhost:48080/provider/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@playpark.com",
    "password": "Admin123!",
    "totp_code": "123456"
  }'
```

## Impersonation Workflow

### 1. Start Impersonation
```bash
curl -X POST http://localhost:48080/provider/impersonate/start \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_123",
    "reason": "Customer support investigation",
    "expiry_minutes": 60
  }'
```

### 2. Use Tenant Token
```bash
# Use the returned tenant_token to access tenant APIs
curl -H "Authorization: Bearer TENANT_IMPERSONATION_TOKEN" \
     "http://localhost:48080/api/tenants/tenant_123/stores"
```

### 3. End Impersonation
```bash
curl -X POST http://localhost:48080/provider/impersonate/imp_789/stop \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```

## Security Features

### Account Security
- **Password Hashing**: bcrypt with proper salt
- **Account Lockout**: 15-minute lockout after failed attempts
- **2FA Support**: TOTP with backup codes
- **Session Management**: JWT tokens with expiry

### Impersonation Security
- **Audit Trail**: All impersonation actions logged
- **Time Limits**: Configurable expiry (default 60 minutes)
- **Reason Required**: Must provide business justification
- **Tenant Scope**: Can be restricted to specific tenants
- **Auto-cleanup**: Expired sessions automatically cleaned up

### Permission System
- **Role-Based**: Users assigned to roles with specific permissions
- **Granular Permissions**: Fine-grained access control
- **Wildcard Support**: Admin role with full access (`*`)
- **Impersonation Control**: Separate permission for impersonation

## Environment Variables

Add these to your `.env` file:

```env
# Provider Authentication
PROVIDER_2FA_REQUIRED=true
PROVIDER_LOGIN_LOCKOUT_MINUTES=15
PROVIDER_TOKEN_EXPIRY_MINUTES=60

# Impersonation
IMPERSONATION_DEFAULT_EXPIRY_MINUTES=60
IMPERSONATION_MAX_EXPIRY_MINUTES=480
IMPERSONATION_CLEANUP_INTERVAL_MINUTES=5

# JWT Configuration
JWT_SECRET=your-long-random-jwt-secret-key
```

## Monitoring and Troubleshooting

### Check Provider Users
```javascript
// List all provider users
db.provider_users.find({}, {email: 1, name: 1, roles: 1, is_active: 1})
```

### Check Active Impersonations
```javascript
// List active impersonation sessions
db.impersonations.find({status: "active"})
```

### Check Audit Logs
```javascript
// Recent provider audit events
db.provider_audits.find({}).sort({timestamp: -1}).limit(10)
```

### Check Failed Login Attempts
```javascript
// Users with failed login attempts
db.provider_users.find({login_attempts: {$gt: 0}})
```

## Security Best Practices

### 1. Change Default Passwords
```bash
# Update default passwords in production
# Use strong, unique passwords for each user
```

### 2. Enable 2FA
```bash
# Require 2FA for all provider accounts
export PROVIDER_2FA_REQUIRED=true
```

### 3. Regular Audit Review
```bash
# Review audit logs regularly
# Monitor for suspicious activity
# Check impersonation usage patterns
```

### 4. Access Control
```bash
# Assign minimum required permissions
# Regular review of user roles
# Remove unused accounts
```

## Database Collections

### provider_users
- Provider user accounts with roles and permissions
- 2FA secrets and backup codes (encrypted)
- Login attempt tracking and lockout status

### impersonations
- Active and historical impersonation sessions
- Action logs for complete audit trail
- Automatic cleanup of expired sessions

### provider_audits
- Complete audit trail of all provider actions
- Login attempts, 2FA changes, impersonations
- IP addresses and user agents logged
- Searchable by user, action, tenant, date range

## Next Steps

Phase 3 provides the foundation for:
- **Phase 4**: Usage tracking and provider billing
- **Phase 5**: Metrics aggregation and caching
- **Phase 6**: Advanced reporting and analytics

The RBAC and impersonation system is now ready to support secure multi-tenant management with proper audit trails and access controls!
