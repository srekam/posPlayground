# Phase 5 API Sample Responses - Aggregations + Cached Overview

## GET /provider/overview

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_overview_123",
  "data": {
    "fleet_overview": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300,
      "uptime_percent": 99.33
    },
    "alert_summary": {
      "total_open": 12,
      "critical": 2,
      "medium": 5,
      "low": 5
    },
    "health_status": "warning",
    "performance_metrics": {
      "response_time_p95_ms": 125.5,
      "sync_lag_p95_sec": 45.2,
      "sync_lag_p99_sec": 89.7,
      "error_rate_percent": 0.15
    },
    "usage_summary": {
      "api_calls_24h": 45000,
      "api_calls_7d": 285000,
      "webhook_calls_24h": 1200,
      "webhook_success_rate_percent": 98.5
    },
    "generated_at": "2024-01-15T10:30:00+07:00",
    "timezone": "Asia/Bangkok",
    "cache_status": "cached"
  },
  "error": null
}
```

## GET /provider/dashboard

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_dashboard_456",
  "data": {
    "overview": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300,
      "sales_amount": 125000.50,
      "redemptions_count": 8500,
      "uptime_percent": 99.33,
      "period": "24h"
    },
    "alerts": {
      "total_open": 12,
      "by_severity": {
        "critical": 2,
        "medium": 5,
        "low": 5
      },
      "by_type": {
        "device.offline": 3,
        "gate.fail_rate_high": 2,
        "sync.lag_high": 4,
        "risk.reprint_spike": 2,
        "risk.refund_spike": 1
      },
      "recent_alerts": [
        {
          "alert_id": "alert_789",
          "type": "device.offline",
          "severity": "critical",
          "message": "Device POS-001 has been offline for more than 120 seconds",
          "first_seen": "2024-01-15T10:25:00+07:00",
          "tenant_id": "tenant_123",
          "store_id": "store_456"
        }
      ]
    },
    "performance": {
      "response_time_p95_ms": 125.5,
      "sync_lag_p95_sec": 45.2,
      "sync_lag_p99_sec": 89.7,
      "error_rate_percent": 0.15,
      "webhook_success_rate_percent": 98.5
    },
    "usage": {
      "api_calls": 45000,
      "webhook_calls": 1200,
      "data_transfer_bytes": 15728640,
      "top_endpoints": [
        {
          "_id": "/api/tenants/tenant_123/stores/store_456/sales",
          "call_count": 1250,
          "avg_response_time": 95.2
        },
        {
          "_id": "/api/tenants/tenant_123/stores/store_456/redemptions",
          "call_count": 980,
          "avg_response_time": 78.5
        }
      ]
    },
    "health": {
      "overall_status": "warning",
      "uptime_percent": 99.33,
      "critical_issues": 2,
      "warning_issues": 5,
      "last_incident": {
        "alert_id": "alert_789",
        "type": "device.offline",
        "first_seen": "2024-01-15T10:25:00+07:00",
        "message": "Device POS-001 has been offline for more than 120 seconds"
      }
    },
    "trends": {
      "sales_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 9
          },
          "total_amount": 12500.50,
          "count": 125
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 10
          },
          "total_amount": 15200.75,
          "count": 152
        }
      ],
      "usage_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 9
          },
          "call_count": 1850
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 10
          },
          "call_count": 2100
        }
      ],
      "performance_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 9
          },
          "avg_response_time": 120.5,
          "error_count": 2
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15,
            "hour": 10
          },
          "avg_response_time": 125.2,
          "error_count": 3
        }
      ],
      "alert_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 14
          },
          "alert_count": 8
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 15
          },
          "alert_count": 12
        }
      ]
    },
    "generated_at": "2024-01-15T10:30:00+07:00",
    "timezone": "Asia/Bangkok"
  },
  "error": null
}
```

## GET /provider/metrics

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_metrics_789",
  "data": {
    "period": "24h",
    "date_range": {
      "start": "2024-01-14T10:30:00+07:00",
      "end": "2024-01-15T10:30:00+07:00"
    },
    "fleet_metrics": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300
    },
    "sales_metrics": {
      "total_amount": 125000.50,
      "total_count": 1250,
      "avg_amount": 100.00,
      "refund_rate": 2.5,
      "reprint_rate": 1.8
    },
    "performance_metrics": {
      "response_time_p95_ms": 125.5,
      "sync_lag_p95_sec": 45.2,
      "sync_lag_p99_sec": 89.7,
      "error_rate_percent": 0.15
    },
    "usage_metrics": {
      "api_calls": 45000,
      "webhook_calls": 1200,
      "webhook_success_rate_percent": 98.5,
      "data_transfer_bytes": 15728640
    },
    "alert_metrics": {
      "total_open": 12,
      "by_severity": {
        "critical": 2,
        "high": 0,
        "medium": 5,
        "low": 5
      },
      "by_type": {
        "device.offline": 3,
        "gate.fail_rate_high": 2,
        "sync.lag_high": 4,
        "risk.reprint_spike": 2,
        "risk.refund_spike": 1
      }
    },
    "generated_at": "2024-01-15T10:30:00+07:00"
  },
  "error": null
}
```

## GET /provider/metrics?tenant_id=tenant_123

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_tenant_metrics_101",
  "data": {
    "period": "24h",
    "date_range": {
      "start": "2024-01-14T10:30:00+07:00",
      "end": "2024-01-15T10:30:00+07:00"
    },
    "fleet_metrics": {
      "tenants_active": 1,
      "stores_active": 5,
      "devices_online": 12,
      "devices_total": 12
    },
    "sales_metrics": {
      "total_amount": 8500.25,
      "total_count": 85,
      "avg_amount": 100.00,
      "refund_rate": 1.2,
      "reprint_rate": 0.8
    },
    "performance_metrics": {
      "response_time_p95_ms": 95.2,
      "sync_lag_p95_sec": 25.5,
      "sync_lag_p99_sec": 45.8,
      "error_rate_percent": 0.05
    },
    "usage_metrics": {
      "api_calls": 2850,
      "webhook_calls": 95,
      "webhook_success_rate_percent": 99.2,
      "data_transfer_bytes": 1250000
    },
    "alert_metrics": {
      "total_open": 2,
      "by_severity": {
        "critical": 0,
        "high": 0,
        "medium": 1,
        "low": 1
      },
      "by_type": {
        "sync.lag_high": 1,
        "risk.reprint_spike": 1
      }
    },
    "generated_at": "2024-01-15T10:30:00+07:00"
  },
  "error": null
}
```

## GET /provider/metrics?period=7d

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_metrics_7d_202",
  "data": {
    "period": "7d",
    "date_range": {
      "start": "2024-01-08T10:30:00+07:00",
      "end": "2024-01-15T10:30:00+07:00"
    },
    "fleet_metrics": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300
    },
    "sales_metrics": {
      "total_amount": 875000.75,
      "total_count": 8750,
      "avg_amount": 100.00,
      "refund_rate": 2.1,
      "reprint_rate": 1.5
    },
    "performance_metrics": {
      "response_time_p95_ms": 118.5,
      "sync_lag_p95_sec": 42.8,
      "sync_lag_p99_sec": 85.2,
      "error_rate_percent": 0.12
    },
    "usage_metrics": {
      "api_calls": 285000,
      "webhook_calls": 8400,
      "webhook_success_rate_percent": 98.8,
      "data_transfer_bytes": 98500000
    },
    "alert_metrics": {
      "total_open": 12,
      "by_severity": {
        "critical": 2,
        "high": 0,
        "medium": 5,
        "low": 5
      },
      "by_type": {
        "device.offline": 3,
        "gate.fail_rate_high": 2,
        "sync.lag_high": 4,
        "risk.reprint_spike": 2,
        "risk.refund_spike": 1
      }
    },
    "generated_at": "2024-01-15T10:30:00+07:00"
  },
  "error": null
}
```

## GET /provider/dashboard?period=7d

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_dashboard_7d_303",
  "data": {
    "overview": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300,
      "sales_amount": 875000.75,
      "redemptions_count": 8750,
      "uptime_percent": 99.33,
      "period": "7d"
    },
    "alerts": {
      "total_open": 12,
      "by_severity": {
        "critical": 2,
        "medium": 5,
        "low": 5
      },
      "by_type": {
        "device.offline": 3,
        "gate.fail_rate_high": 2,
        "sync.lag_high": 4,
        "risk.reprint_spike": 2,
        "risk.refund_spike": 1
      },
      "recent_alerts": [
        {
          "alert_id": "alert_789",
          "type": "device.offline",
          "severity": "critical",
          "message": "Device POS-001 has been offline for more than 120 seconds",
          "first_seen": "2024-01-15T10:25:00+07:00",
          "tenant_id": "tenant_123",
          "store_id": "store_456"
        }
      ]
    },
    "performance": {
      "response_time_p95_ms": 118.5,
      "sync_lag_p95_sec": 42.8,
      "sync_lag_p99_sec": 85.2,
      "error_rate_percent": 0.12,
      "webhook_success_rate_percent": 98.8
    },
    "usage": {
      "api_calls": 285000,
      "webhook_calls": 8400,
      "data_transfer_bytes": 98500000,
      "top_endpoints": [
        {
          "_id": "/api/tenants/tenant_123/stores/store_456/sales",
          "call_count": 8750,
          "avg_response_time": 95.2
        },
        {
          "_id": "/api/tenants/tenant_123/stores/store_456/redemptions",
          "call_count": 6860,
          "avg_response_time": 78.5
        }
      ]
    },
    "health": {
      "overall_status": "warning",
      "uptime_percent": 99.33,
      "critical_issues": 2,
      "warning_issues": 5,
      "last_incident": {
        "alert_id": "alert_789",
        "type": "device.offline",
        "first_seen": "2024-01-15T10:25:00+07:00",
        "message": "Device POS-001 has been offline for more than 120 seconds"
      }
    },
    "trends": {
      "sales_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 8
          },
          "total_amount": 125000.50,
          "count": 1250
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 9
          },
          "total_amount": 132000.75,
          "count": 1320
        }
      ],
      "usage_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 8
          },
          "call_count": 45000
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 9
          },
          "call_count": 46500
        }
      ],
      "performance_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 8
          },
          "avg_response_time": 120.5,
          "error_count": 15
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 9
          },
          "avg_response_time": 118.2,
          "error_count": 12
        }
      ],
      "alert_trend": [
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 8
          },
          "alert_count": 8
        },
        {
          "_id": {
            "year": 2024,
            "month": 1,
            "day": 9
          },
          "alert_count": 10
        }
      ]
    },
    "generated_at": "2024-01-15T10:30:00+07:00",
    "timezone": "Asia/Bangkok"
  },
  "error": null
}
```

## Cache Performance

### Cache Hit Response
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_overview_cached_404",
  "data": {
    "fleet_overview": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300,
      "uptime_percent": 99.33
    },
    "alert_summary": {
      "total_open": 12,
      "critical": 2,
      "medium": 5,
      "low": 5
    },
    "health_status": "warning",
    "performance_metrics": {
      "response_time_p95_ms": 125.5,
      "sync_lag_p95_sec": 45.2,
      "sync_lag_p99_sec": 89.7,
      "error_rate_percent": 0.15
    },
    "usage_summary": {
      "api_calls_24h": 45000,
      "api_calls_7d": 285000,
      "webhook_calls_24h": 1200,
      "webhook_success_rate_percent": 98.5
    },
    "generated_at": "2024-01-15T10:28:00+07:00",
    "timezone": "Asia/Bangkok",
    "cache_status": "cached"
  },
  "error": null
}
```

### Cache Miss Response
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_overview_realtime_505",
  "data": {
    "fleet_overview": {
      "tenants_active": 25,
      "stores_active": 150,
      "devices_online": 298,
      "devices_total": 300,
      "uptime_percent": 99.33
    },
    "alert_summary": {
      "total_open": 12,
      "critical": 2,
      "medium": 5,
      "low": 5
    },
    "health_status": "warning",
    "performance_metrics": {
      "response_time_p95_ms": 125.5,
      "sync_lag_p95_sec": 45.2,
      "sync_lag_p99_sec": 89.7,
      "error_rate_percent": 0.15
    },
    "usage_summary": {
      "api_calls_24h": 45000,
      "api_calls_7d": 285000,
      "webhook_calls_24h": 1200,
      "webhook_success_rate_percent": 98.5
    },
    "generated_at": "2024-01-15T10:30:00+07:00",
    "timezone": "Asia/Bangkok",
    "cache_status": "real_time"
  },
  "error": null
}
```

## Timezone Handling

### Asia/Bangkok Timezone
- **Timezone**: Asia/Bangkok (UTC+7)
- **Business Hours**: 9:00 AM - 10:00 PM
- **Date Ranges**: All metrics are calculated in Asia/Bangkok timezone
- **Cache TTL**: 30 seconds for overview, 60 seconds for metrics

### Clock Skew Detection
```json
{
  "clock_skew": {
    "has_skew": true,
    "skew_seconds": 300,
    "device_time": "2024-01-15T10:25:00+07:00",
    "server_time": "2024-01-15T10:30:00+07:00",
    "device_id": "device_123",
    "severity": "medium",
    "recommendation": "Device clock is moderately out of sync. Consider updating device time settings."
  }
}
```

## Performance Metrics

### Response Times
- **Overview API**: < 50ms (cached), < 200ms (real-time)
- **Dashboard API**: < 100ms (cached), < 500ms (real-time)
- **Metrics API**: < 150ms (cached), < 800ms (real-time)

### Cache Performance
- **Cache Hit Rate**: > 95%
- **Cache TTL**: 30-60 seconds
- **Cache Size**: < 100MB
- **Cache Cleanup**: Every 5 minutes

### Aggregation Performance
- **Metrics Aggregation**: Every 5 minutes
- **Cache Updates**: Every 30 seconds
- **Data Retention**: 12 months for metrics, 3 months for raw data

## Error Responses

### Cache Error
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_606",
  "data": null,
  "error": {
    "code": "E_CACHE_ERROR",
    "message": "Failed to retrieve cached data"
  }
}
```

### Aggregation Error
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_707",
  "data": null,
  "error": {
    "code": "E_AGGREGATION_FAILED",
    "message": "Failed to aggregate metrics data"
  }
}
```

### Timezone Error
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_808",
  "data": null,
  "error": {
    "code": "E_TIMEZONE_ERROR",
    "message": "Invalid timezone specified"
  }
}
```

## Database Collections

### cache
- **Purpose**: Store cached overview and metrics data
- **TTL**: Automatic expiration based on expires_at field
- **Indexes**: key (unique), expires_at, updated_at

### provider_metrics_daily
- **Purpose**: Daily aggregated metrics for all tenants
- **Indexes**: date, tenant_id+date, store_id+date, device_id+date
- **Retention**: 12 months

### Enhanced Collections
- **sales**: Timestamp and tenant-based indexes for metrics
- **redemptions**: Timestamp and tenant-based indexes for metrics
- **refunds**: Timestamp and tenant-based indexes for metrics
- **reprints**: Timestamp and tenant-based indexes for metrics
- **tickets**: Timestamp and tenant-based indexes for metrics
- **device_heartbeats**: Enhanced indexes for sync lag metrics
- **response_metrics**: Enhanced indexes for performance metrics
- **provider_alerts**: Enhanced indexes for alert metrics

## Background Workers

### Metrics Aggregation Worker
- **Frequency**: Every 5 minutes
- **Tasks**:
  - Aggregate daily metrics from raw data
  - Update cached overview data
  - Update tenant-specific caches
  - Clean up expired cache entries

### Cache Management
- **Overview Cache**: 30-second TTL
- **Tenant Cache**: 5-minute TTL
- **Metrics Cache**: 1-minute TTL
- **Cleanup**: Every 5 minutes

## Performance Optimizations

### Database Indexes
- All collections have proper indexes for query performance
- Time-series data indexed by timestamp
- Tenant-specific queries optimized
- Metrics aggregation optimized

### Caching Strategy
- Multi-level caching (overview, tenant, metrics)
- TTL-based expiration
- Automatic cache invalidation
- Cache hit rate monitoring

### Aggregation Optimization
- Pre-calculated daily metrics
- Incremental updates
- Batch processing
- Error handling and retry logic
