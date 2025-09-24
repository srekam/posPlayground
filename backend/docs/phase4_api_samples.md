# Phase 4 API Sample Responses - Usage Tracking + Provider Billing

## GET /provider/billing/tenants

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_billing_tenants_123",
  "data": {
    "tenants": [
      {
        "tenant_id": "tenant_123",
        "tenant_name": "Fun Zone Playground",
        "plan": "premium",
        "status": "active",
        "usage": {
          "stores_count": 3,
          "devices_count": 8,
          "api_calls": 45000,
          "webhook_calls": 1200,
          "storage_gb": 12.5
        },
        "limits": {
          "max_stores": 20,
          "max_devices": 50,
          "max_api_calls_per_month": 200000,
          "max_webhooks_per_month": 2000,
          "max_storage_gb": 50
        },
        "overages": {},
        "utilization": {
          "stores_count_percent": 15.0,
          "devices_count_percent": 16.0,
          "api_calls_percent": 22.5,
          "webhook_calls_percent": 60.0,
          "storage_gb_percent": 25.0
        },
        "has_overages": false,
        "overage_cost": 0.0,
        "health_status": "healthy"
      },
      {
        "tenant_id": "tenant_456",
        "tenant_name": "Adventure Park",
        "plan": "basic",
        "status": "active",
        "usage": {
          "stores_count": 6,
          "devices_count": 12,
          "api_calls": 65000,
          "webhook_calls": 800,
          "storage_gb": 15.2
        },
        "limits": {
          "max_stores": 5,
          "max_devices": 10,
          "max_api_calls_per_month": 50000,
          "max_webhooks_per_month": 500,
          "max_storage_gb": 10
        },
        "overages": {
          "stores_count": 1,
          "devices_count": 2,
          "api_calls": 15000,
          "storage_gb": 5.2
        },
        "utilization": {
          "stores_count_percent": 120.0,
          "devices_count_percent": 120.0,
          "api_calls_percent": 130.0,
          "webhook_calls_percent": 160.0,
          "storage_gb_percent": 152.0
        },
        "has_overages": true,
        "overage_cost": 185.02,
        "health_status": "critical"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 25,
      "pages": 1
    },
    "period": "2024-01"
  },
  "error": null
}
```

## GET /provider/billing/tenants/{tenant_id}

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_tenant_billing_456",
  "data": {
    "tenant_id": "tenant_123",
    "tenant_name": "Fun Zone Playground",
    "period": "2024-01",
    "plan": "premium",
    "status": "active",
    "usage": {
      "stores_count": 3,
      "devices_count": 8,
      "api_calls": 45000,
      "webhook_calls": 1200,
      "storage_gb": 12.5
    },
    "limits": {
      "max_stores": 20,
      "max_devices": 50,
      "max_api_calls_per_month": 200000,
      "max_webhooks_per_month": 2000,
      "max_storage_gb": 50
    },
    "overages": {},
    "utilization": {
      "stores_count_percent": 15.0,
      "devices_count_percent": 16.0,
      "api_calls_percent": 22.5,
      "webhook_calls_percent": 60.0,
      "storage_gb_percent": 25.0
    },
    "has_overages": false,
    "overage_cost": 0.0,
    "health_status": "healthy",
    "usage_history": [
      {
        "period": "2024-01",
        "usage": {
          "stores_count": 3,
          "devices_count": 8,
          "api_calls": 45000,
          "webhook_calls": 1200,
          "storage_gb": 12.5
        }
      },
      {
        "period": "2023-12",
        "usage": {
          "stores_count": 3,
          "devices_count": 7,
          "api_calls": 38000,
          "webhook_calls": 950,
          "storage_gb": 11.2
        }
      }
    ],
    "usage_trends": {
      "api_calls_trend": [38000, 42000, 45000],
      "webhook_calls_trend": [950, 1100, 1200],
      "storage_gb_trend": [11.2, 11.8, 12.5],
      "periods": ["2023-11", "2023-12", "2024-01"]
    },
    "current_month_stats": {
      "api_calls": {
        "total_calls": 45000,
        "unique_endpoints_count": 25,
        "avg_response_time_ms": 125.5,
        "total_data_transfer_bytes": 15728640
      },
      "webhook_calls": {
        "total_calls": 1200,
        "success_rate_percent": 98.5,
        "avg_response_time_ms": 250.0
      }
    }
  },
  "error": null
}
```

## POST /provider/billing/tenants/{tenant_id}/plan

**Request:**
```json
{
  "plan": "enterprise",
  "reason": "Customer upgraded due to increased usage requirements"
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_plan_update_789",
  "data": {
    "tenant_id": "tenant_123",
    "old_plan": "premium",
    "new_plan": "enterprise",
    "new_limits": {
      "max_stores": 100,
      "max_devices": 200,
      "max_api_calls_per_month": 1000000,
      "max_webhooks_per_month": 10000,
      "max_storage_gb": 200
    },
    "updated_at": "2024-01-15T10:30:00+07:00"
  },
  "error": null
}
```

## GET /provider/billing/usage

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_usage_analytics_101",
  "data": {
    "analytics": {
      "period": {
        "start": "2024-01-01T00:00:00.000Z",
        "end": "2024-01-31T23:59:59.000Z"
      },
      "group_by": "day",
      "data": [
        {
          "date": "2024-01-01",
          "total_api_calls": 15000,
          "total_webhook_calls": 450,
          "total_storage_gb": 125.5,
          "active_tenants": 25
        },
        {
          "date": "2024-01-02",
          "total_api_calls": 18000,
          "total_webhook_calls": 520,
          "total_storage_gb": 127.2,
          "active_tenants": 26
        }
      ]
    },
    "filters": {
      "tenant_id": "",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "group_by": "day"
    }
  },
  "error": null
}
```

## GET /provider/billing/reports

**Response (JSON):**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_usage_report_202",
  "data": {
    "period": "2024-01",
    "generated_at": "2024-01-15T10:30:00+07:00",
    "summary": {
      "total_tenants": 25,
      "tenants_with_overages": 3,
      "overage_rate_percent": 12.0,
      "plan_distribution": {
        "free": 5,
        "basic": 10,
        "premium": 8,
        "enterprise": 2
      },
      "total_overage_cost": 450.75
    },
    "tenants": [
      {
        "tenant_id": "tenant_123",
        "tenant_name": "Fun Zone Playground",
        "plan": "premium",
        "status": "active",
        "usage": {
          "stores_count": 3,
          "devices_count": 8,
          "api_calls": 45000,
          "webhook_calls": 1200,
          "storage_gb": 12.5
        },
        "limits": {
          "max_stores": 20,
          "max_devices": 50,
          "max_api_calls_per_month": 200000,
          "max_webhooks_per_month": 2000,
          "max_storage_gb": 50
        },
        "overages": {},
        "utilization": {
          "stores_count_percent": 15.0,
          "devices_count_percent": 16.0,
          "api_calls_percent": 22.5,
          "webhook_calls_percent": 60.0,
          "storage_gb_percent": 25.0
        },
        "has_overages": false,
        "overage_cost": 0.0,
        "health_status": "healthy"
      }
    ]
  },
  "error": null
}
```

## GET /provider/billing/reports?format=csv

**Response (CSV):**
```csv
Tenant ID,Tenant Name,Plan,Status,Stores Count,Stores Limit,Devices Count,Devices Limit,API Calls,API Limit,Webhook Calls,Webhook Limit,Storage GB,Storage Limit,Has Overages,Overage Cost,Health Status
tenant_123,Fun Zone Playground,premium,active,3,20,8,50,45000,200000,1200,2000,12.50,50.00,No,0.00,healthy
tenant_456,Adventure Park,basic,active,6,5,12,10,65000,50000,800,500,15.20,10.00,Yes,185.02,critical
```

## Usage Tracking Middleware

The usage tracking middleware automatically tracks:

### API Calls
- **Endpoint**: Every API call to tenant endpoints
- **Metrics**: Request size, response time, status code
- **Counters**: Monthly API call counts per tenant

### Webhook Calls
- **Endpoint**: Every webhook delivery attempt
- **Metrics**: Success/failure rate, response time
- **Counters**: Monthly webhook call counts per tenant

### Storage Usage
- **Calculation**: Based on sales, tickets, and audit data
- **Metrics**: Total storage in bytes and GB
- **Counters**: Monthly storage usage per tenant

### Device/Store Counts
- **Aggregation**: Real-time count of active devices and stores
- **Metrics**: Current counts vs plan limits
- **Counters**: Monthly device/store counts per tenant

## Plan Limits

### Free Plan
- **Stores**: 1
- **Devices**: 2
- **API Calls**: 10,000/month
- **Webhooks**: 100/month
- **Storage**: 1 GB

### Basic Plan
- **Stores**: 5
- **Devices**: 10
- **API Calls**: 50,000/month
- **Webhooks**: 500/month
- **Storage**: 10 GB

### Premium Plan
- **Stores**: 20
- **Devices**: 50
- **API Calls**: 200,000/month
- **Webhooks**: 2,000/month
- **Storage**: 50 GB

### Enterprise Plan
- **Stores**: 100
- **Devices**: 200
- **API Calls**: 1,000,000/month
- **Webhooks**: 10,000/month
- **Storage**: 200 GB

## Overage Costs (Mock)

- **Stores**: $10 per additional store
- **Devices**: $5 per additional device
- **API Calls**: $0.001 per additional call
- **Webhooks**: $0.01 per additional webhook
- **Storage**: $2 per additional GB

## Health Status

- **Healthy**: All usage under 75% of limits
- **Caution**: Usage between 75-90% of limits
- **Warning**: Usage between 90-100% of limits
- **Critical**: Usage over 100% of limits (overages)

## Error Responses

### Tenant Not Found
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_303",
  "data": null,
  "error": {
    "code": "E_TENANT_NOT_FOUND",
    "message": "Tenant not found or no billing data available"
  }
}
```

### Invalid Plan
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_404",
  "data": null,
  "error": {
    "code": "E_VALIDATION",
    "message": "Invalid plan. Must be one of: free, basic, premium, enterprise"
  }
}
```

### Insufficient Permissions
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_505",
  "data": null,
  "error": {
    "code": "E_PERMISSION",
    "message": "Insufficient permissions"
  }
}
```

## Database Collections

### api_calls
- Time-series data of all API calls
- Indexed by tenant, device, store, endpoint, timestamp
- Used for usage tracking and analytics

### response_metrics
- Response time and status code data
- Indexed by tenant, endpoint, timestamp
- Used for performance monitoring

### webhook_calls
- Webhook delivery attempts and results
- Indexed by tenant, webhook_id, timestamp
- Used for webhook usage tracking

### usage_counters
- Monthly aggregated usage data
- Indexed by tenant and period
- Used for billing and limit checking

### usage_reports
- Generated monthly usage reports
- Indexed by period
- Used for historical analysis
