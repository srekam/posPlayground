# Provider API Sample Responses

## GET /provider/overview

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_1234567890",
  "data": {
    "tenants_active": 15,
    "stores_active": 42,
    "devices_online": 156,
    "devices_total": 168,
    "sales_24h": 125000,
    "redemptions_24h": 892,
    "refund_rate": 2.3,
    "reprint_rate": 1.8,
    "sync_lag_p95": 45.2,
    "alerts": {
      "open": 8,
      "critical": 2
    },
    "subscriptions": {
      "total": 15,
      "active": 14,
      "trial": 3
    }
  },
  "error": null
}
```

## GET /provider/tenants

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_1234567891",
  "data": {
    "tenants": [
      {
        "tenant_id": "tenant_123",
        "name": "Fun Zone Playground",
        "plan": "premium",
        "stores": 3,
        "devices": 12,
        "sales_24h": 15000,
        "refund_rate": 1.2,
        "reprint_rate": 0.8,
        "sla_percent": 99.8,
        "alerts_open": 1,
        "last_activity": "2024-01-15T09:45:00.000Z",
        "status": "active"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 15,
      "pages": 1
    }
  },
  "error": null
}
```

## GET /provider/tenants/{tenant_id}/summary

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_1234567892",
  "data": {
    "tenant": {
      "tenant_id": "tenant_123",
      "name": "Fun Zone Playground",
      "legal_name": "Fun Zone Entertainment Co., Ltd.",
      "billing_plan": "premium",
      "status": "active",
      "timezone": "Asia/Bangkok",
      "currency": "THB",
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-15T10:00:00.000Z"
    },
    "subscription": {
      "plan": "premium",
      "status": "active",
      "start_date": "2024-01-01T00:00:00.000Z",
      "renew_on": "2024-02-01T00:00:00.000Z",
      "limits": {
        "stores": 10,
        "devices": 50,
        "api_calls_monthly": 100000,
        "webhook_calls_monthly": 10000,
        "storage_gb": 25
      }
    },
    "usage": {
      "daily": {
        "total_count": 1250,
        "periods": [
          {
            "period": "2024-01-15",
            "count": 1250,
            "store_id": null
          }
        ]
      },
      "monthly": {
        "api_calls": 45000,
        "webhook_calls": 3500
      }
    },
    "alerts": {
      "open": 1,
      "critical": 0
    },
    "metrics_30d": {
      "sales": {
        "amount": 450000,
        "count": 2250
      },
      "uptime": {
        "percentage": 99.8,
        "downtime_minutes": 86
      }
    }
  },
  "error": null
}
```

## GET /provider/stores

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_1234567893",
  "data": {
    "stores": [
      {
        "store_id": "store_456",
        "tenant_id": "tenant_123",
        "tenant_name": "Fun Zone Playground",
        "name": "Central World Branch",
        "address": {
          "street": "999/9 Rama I Road",
          "city": "Bangkok",
          "postal_code": "10330"
        },
        "status": "online",
        "devices_online": 4,
        "devices_total": 4,
        "last_sale": {
          "timestamp": "2024-01-15T10:25:00.000Z",
          "amount": 250
        },
        "open_shifts": true,
        "sales_today": 8500,
        "sales_count_today": 34,
        "alerts": 0,
        "critical_alerts": 0,
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-15T10:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 42,
      "pages": 1
    }
  },
  "error": null
}
```

## GET /provider/devices

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_1234567894",
  "data": {
    "devices": [
      {
        "device_id": "device_789",
        "name": "POS Terminal 1",
        "type": "POS",
        "tenant_id": "tenant_123",
        "tenant_name": "Fun Zone Playground",
        "store_id": "store_456",
        "store_name": "Central World Branch",
        "status": "online",
        "last_seen": "2024-01-15T10:29:45.000Z",
        "app_version": "1.0.0",
        "uptime_24h": 98.5,
        "issues": 0,
        "critical_issues": 0,
        "metrics": {
          "error_rate_5m": 0.02,
          "request_latency_p95": 125,
          "sync_lag_sec": 15,
          "memory_usage": 75,
          "cpu_usage": 25
        },
        "ip_address": "192.168.1.101",
        "mac_address": "00:11:22:33:44:55",
        "created_at": "2024-01-01T00:00:00.000Z",
        "updated_at": "2024-01-15T10:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 168,
      "pages": 4
    }
  },
  "error": null
}
```

## Error Response Example

```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_1234567895",
  "data": null,
  "error": {
    "code": "E_PERMISSION",
    "message": "Provider scope required"
  }
}
```

## Common Error Codes

- `E_AUTH_REQUIRED` - Authorization header required
- `E_INVALID_TOKEN` - Invalid or malformed token
- `E_TOKEN_EXPIRED` - Token has expired
- `E_PERMISSION` - Insufficient permissions
- `E_TENANT_NOT_FOUND` - Tenant not found
- `E_DEVICE_NOT_FOUND` - Device not found
- `E_INTERNAL_ERROR` - Internal server error
