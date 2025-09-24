# Phase 3 API Sample Responses - Provider RBAC + Impersonation

## POST /provider/auth/login

**Request:**
```json
{
  "email": "admin@playpark.com",
  "password": "Admin123!",
  "totp_code": "123456"
}
```

**Response (Success):**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_login_123",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "provider_user_id": "user_456",
      "email": "admin@playpark.com",
      "name": "System Administrator",
      "roles": ["Provider-Admin"],
      "permissions": ["*"],
      "impersonation_allowed": true,
      "is_2fa_enabled": true,
      "last_login": "2024-01-15T10:30:00.000Z"
    },
    "expires_at": "2024-01-15T11:30:00+07:00"
  },
  "error": null
}
```

**Response (2FA Required):**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_login_456",
  "data": null,
  "error": {
    "code": "E_2FA_REQUIRED",
    "message": "2FA code required",
    "requires_2fa": true
  }
}
```

## POST /provider/auth/2fa/setup

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_2fa_setup_789",
  "data": {
    "totp_secret": "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567",
    "backup_codes": [
      "A1B2C3D4",
      "E5F6G7H8",
      "I9J0K1L2",
      "M3N4O5P6",
      "Q7R8S9T0",
      "U1V2W3X4",
      "Y5Z6A7B8",
      "C9D0E1F2",
      "G3H4I5J6",
      "K7L8M9N0"
    ],
    "qr_code_url": "otpauth://totp/PlayPark%20Provider:admin@playpark.com?secret=ABCDEFGHIJKLMNOPQRSTUVWXYZ234567&issuer=PlayPark%20Provider"
  },
  "error": null
}
```

## POST /provider/auth/2fa/enable

**Request:**
```json
{
  "totp_code": "123456"
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_2fa_enable_101",
  "data": {
    "status": "enabled",
    "message": "2FA has been enabled successfully"
  },
  "error": null
}
```

## POST /provider/impersonate/start

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "reason": "Customer support investigation",
  "expiry_minutes": 60
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_impersonate_202",
  "data": {
    "impersonation_id": "imp_789",
    "tenant_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_at": "2024-01-15T11:30:00+07:00"
  },
  "error": null
}
```

## GET /provider/impersonate/active

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_active_imp_303",
  "data": [
    {
      "impersonation_id": "imp_789",
      "tenant_id": "tenant_123",
      "tenant_name": "Fun Zone Playground",
      "reason": "Customer support investigation",
      "started_at": "2024-01-15T10:00:00.000Z",
      "expires_at": "2024-01-15T11:00:00.000Z",
      "actions_count": 5
    },
    {
      "impersonation_id": "imp_790",
      "tenant_id": "tenant_456",
      "tenant_name": "Adventure Park",
      "reason": "Technical troubleshooting",
      "started_at": "2024-01-15T09:30:00.000Z",
      "expires_at": "2024-01-15T10:30:00.000Z",
      "actions_count": 12
    }
  ],
  "error": null
}
```

## POST /provider/impersonate/{impersonation_id}/stop

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_stop_imp_404",
  "data": {
    "status": "ended",
    "message": "Impersonation ended successfully"
  },
  "error": null
}
```

## Using Impersonation Token

**Request to tenant API with impersonation token:**
```bash
curl -H "Authorization: Bearer IMPERSONATION_TENANT_TOKEN" \
     "http://localhost:48080/api/tenants/tenant_123/stores"
```

**Response (with impersonation context):**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_tenant_505",
  "data": {
    "stores": [
      {
        "store_id": "store_456",
        "name": "Central World Branch",
        "status": "active"
      }
    ],
    "impersonation": {
      "impersonation_id": "imp_789",
      "impersonating_user": "admin@playpark.com",
      "reason": "Customer support investigation",
      "started_at": "2024-01-15T10:00:00.000Z"
    }
  },
  "error": null
}
```

## Error Response Examples

### Invalid Credentials
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_606",
  "data": null,
  "error": {
    "code": "E_INVALID_PASSWORD",
    "message": "Invalid password"
  }
}
```

### 2FA Required
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_707",
  "data": null,
  "error": {
    "code": "E_2FA_REQUIRED",
    "message": "2FA code required"
  }
}
```

### Insufficient Permissions
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_808",
  "data": null,
  "error": {
    "code": "E_PERMISSION",
    "message": "Insufficient permissions"
  }
}
```

### Impersonation Not Allowed
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_909",
  "data": null,
  "error": {
    "code": "E_PERMISSION",
    "message": "Impersonation not allowed for this user"
  }
}
```

### User Account Locked
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_101",
  "data": null,
  "error": {
    "code": "E_USER_LOCKED",
    "message": "User account is locked"
  }
}
```

## Provider Roles and Permissions

### Provider-Admin
- **Permissions**: `["*"]` (Full access)
- **Impersonation**: Allowed for all tenants
- **Use Case**: System administrators

### NOC (Network Operations Center)
- **Permissions**: 
  - `provider.overview.read`
  - `provider.tenants.read`
  - `provider.stores.read`
  - `provider.devices.read`
  - `provider.alerts.read`
  - `provider.alerts.ack`
  - `provider.alerts.resolve`
  - `provider.impersonate.start`
  - `provider.impersonate.stop`
- **Impersonation**: Allowed for all tenants
- **Use Case**: Technical support and incident management

### Billing-Ops
- **Permissions**:
  - `provider.overview.read`
  - `provider.tenants.read`
  - `provider.tenants.update`
  - `provider.billing.read`
  - `provider.billing.update`
  - `provider.reports.read`
- **Impersonation**: Not allowed
- **Use Case**: Billing and account management

### Read-Only
- **Permissions**:
  - `provider.overview.read`
  - `provider.tenants.read`
  - `provider.stores.read`
  - `provider.devices.read`
  - `provider.alerts.read`
  - `provider.reports.read`
- **Impersonation**: Not allowed
- **Use Case**: View-only access for stakeholders

## Security Features

### 2FA/TOTP
- **Setup**: Generate secret and backup codes
- **Enable**: Verify TOTP code to activate
- **Disable**: Verify TOTP code to deactivate
- **Backup Codes**: 10 single-use codes for emergency access

### Account Lockout
- **Failed Attempts**: Lock account after multiple failed logins
- **Lock Duration**: 15 minutes
- **Reset**: Successful login resets failed attempt counter

### Impersonation Security
- **Audit Trail**: All impersonation actions logged
- **Time Limits**: Configurable expiry (default 60 minutes)
- **Reason Required**: Must provide business justification
- **Tenant Scope**: Can be restricted to specific tenants
- **Auto-cleanup**: Expired sessions automatically cleaned up

### Token Security
- **Provider Tokens**: JWT with provider scope
- **Impersonation Tokens**: JWT with tenant_impersonated scope
- **Expiry**: Configurable token lifetime
- **Validation**: Real-time session validation

## Database Collections

### provider_users
- User accounts with roles and permissions
- 2FA secrets and backup codes
- Login attempt tracking and lockout

### impersonations
- Active and historical impersonation sessions
- Action logs for audit trail
- Automatic cleanup of expired sessions

### provider_audits
- Complete audit trail of provider actions
- Login attempts, 2FA changes, impersonations
- IP addresses and user agents logged
