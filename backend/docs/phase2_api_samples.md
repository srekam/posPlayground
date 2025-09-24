# Phase 2 API Sample Responses - Device Heartbeats + Alerting

## POST /heartbeat (Device Heartbeat Intake)

**Request:**
```json
{
  "device_id": "device_789",
  "tenant_id": "tenant_123",
  "store_id": "store_456",
  "status": "online",
  "error_rate_5m": 0.02,
  "request_latency_p95": 125,
  "sync_lag_sec": 15,
  "app_version": "1.0.0",
  "memory_usage": 75,
  "cpu_usage": 25,
  "disk_usage": 45.5
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_heartbeat_123",
  "data": {
    "heartbeat_id": "heartbeat_456",
    "received_at": "2024-01-15T10:30:00+07:00",
    "status": "received"
  },
  "error": null
}
```

## GET /heartbeat/{device_id}/status

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_status_789",
  "data": {
    "device_id": "device_789",
    "status": "online",
    "last_seen": "2024-01-15T10:29:45.000Z",
    "metrics": {
      "error_rate_5m": 0.02,
      "request_latency_p95": 125,
      "sync_lag_sec": 15,
      "app_version": "1.0.0",
      "memory_usage": 75,
      "cpu_usage": 25
    }
  },
  "error": null
}
```

## GET /provider/alerts

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_alerts_456",
  "data": {
    "alerts": [
      {
        "alert_id": "alert_789",
        "type": "device.offline",
        "severity": "high",
        "status": "open",
        "tenant_id": "tenant_123",
        "tenant_name": "Fun Zone Playground",
        "store_id": "store_456",
        "store_name": "Central World Branch",
        "device_id": "device_789",
        "device_name": "POS Terminal 1",
        "first_seen": "2024-01-15T10:15:00.000Z",
        "last_seen": "2024-01-15T10:15:00.000Z",
        "count": 1,
        "assignee": null,
        "acknowledged_at": null,
        "acknowledged_by": null,
        "resolved_at": null,
        "resolved_by": null,
        "resolution_reason": null,
        "metadata": {
          "device_name": "POS Terminal 1",
          "device_type": "POS",
          "last_heartbeat": "2024-01-15T10:13:00.000Z",
          "offline_duration_minutes": 17
        },
        "created_at": "2024-01-15T10:15:00.000Z",
        "updated_at": "2024-01-15T10:15:00.000Z"
      },
      {
        "alert_id": "alert_790",
        "type": "gate.fail_rate_high",
        "severity": "medium",
        "status": "acknowledged",
        "tenant_id": "tenant_123",
        "tenant_name": "Fun Zone Playground",
        "store_id": "store_456",
        "store_name": "Central World Branch",
        "device_id": "device_790",
        "device_name": "Gate Terminal 1",
        "first_seen": "2024-01-15T10:10:00.000Z",
        "last_seen": "2024-01-15T10:10:00.000Z",
        "count": 1,
        "assignee": "noc_operator_1",
        "acknowledged_at": "2024-01-15T10:20:00.000Z",
        "acknowledged_by": "noc_operator_1",
        "resolved_at": null,
        "resolved_by": null,
        "resolution_reason": null,
        "metadata": {
          "device_name": "Gate Terminal 1",
          "fail_rate_percent": 15.5,
          "threshold_percent": 10,
          "window_minutes": 60
        },
        "created_at": "2024-01-15T10:10:00.000Z",
        "updated_at": "2024-01-15T10:20:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 8,
      "pages": 1
    }
  },
  "error": null
}
```

## POST /provider/alerts/{alert_id}/ack

**Request:**
```json
{
  "reason": "Investigating device connectivity issues"
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_ack_123",
  "data": {
    "alert_id": "alert_789",
    "status": "acknowledged",
    "acknowledged_by": "noc_operator_1",
    "acknowledged_at": "2024-01-15T10:30:00+07:00"
  },
  "error": null
}
```

## POST /provider/alerts/{alert_id}/resolve

**Request:**
```json
{
  "reason": "Device connectivity restored after network maintenance"
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_resolve_456",
  "data": {
    "alert_id": "alert_789",
    "status": "resolved",
    "resolved_by": "noc_operator_1",
    "resolved_at": "2024-01-15T10:30:00+07:00",
    "resolution_reason": "Device connectivity restored after network maintenance"
  },
  "error": null
}
```

## GET /provider/alerts/rules

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_rules_789",
  "data": [
    {
      "_id": "rule_123",
      "rule_id": "rule_123",
      "name": "Device Offline",
      "description": "Device has not sent heartbeat for more than 2 minutes",
      "type": "device.offline",
      "severity": "high",
      "enabled": true,
      "scope": "global",
      "scope_id": null,
      "conditions": ["no_heartbeat"],
      "thresholds": {
        "offline_seconds": 120
      },
      "auto_resolve": true,
      "auto_resolve_conditions": ["heartbeat_received"],
      "cooldown_minutes": 5,
      "notification_channels": [],
      "created_by": "system",
      "created_at": "2024-01-15T10:00:00.000Z",
      "updated_at": "2024-01-15T10:00:00.000Z"
    },
    {
      "_id": "rule_124",
      "rule_id": "rule_124",
      "name": "Gate Fail Rate High",
      "description": "Gate device has high failure rate for redemptions",
      "type": "gate.fail_rate_high",
      "severity": "medium",
      "enabled": true,
      "scope": "global",
      "scope_id": null,
      "conditions": ["fail_rate_threshold"],
      "thresholds": {
        "fail_rate_percent": 10,
        "window_minutes": 60,
        "min_attempts": 10
      },
      "auto_resolve": true,
      "auto_resolve_conditions": ["fail_rate_normal"],
      "cooldown_minutes": 15,
      "notification_channels": [],
      "created_by": "system",
      "created_at": "2024-01-15T10:00:00.000Z",
      "updated_at": "2024-01-15T10:00:00.000Z"
    }
  ],
  "error": null
}
```

## POST /provider/alerts/rules

**Request:**
```json
{
  "name": "Custom High Memory Usage",
  "description": "Device memory usage exceeds 90%",
  "type": "device.high_memory",
  "severity": "medium",
  "scope": "global",
  "conditions": ["memory_threshold"],
  "thresholds": {
    "memory_percent": 90,
    "window_minutes": 10
  },
  "auto_resolve": true,
  "auto_resolve_conditions": ["memory_normal"],
  "cooldown_minutes": 10
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_create_rule_123",
  "data": {
    "rule_id": "rule_125",
    "status": "created"
  },
  "error": null
}
```

## Error Response Examples

### Device Not Found
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_456",
  "data": null,
  "error": {
    "code": "E_DEVICE_NOT_FOUND",
    "message": "Device not found"
  }
}
```

### Alert Already Resolved
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_789",
  "data": null,
  "error": {
    "code": "E_ALERT_ALREADY_RESOLVED",
    "message": "Alert is already resolved"
  }
}
```

### Missing Resolution Reason
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_101",
  "data": null,
  "error": {
    "code": "E_VALIDATION",
    "message": "Resolution reason is required"
  }
}
```

## Alert Types Reference

| Type | Severity | Description | Auto-Resolve |
|------|----------|-------------|--------------|
| `device.offline` | high | Device has not sent heartbeat | Yes |
| `gate.fail_rate_high` | medium | Gate redemption failure rate high | Yes |
| `sync.lag_high` | medium | Device sync lag exceeds threshold | Yes |
| `risk.reprint_spike` | medium | Unusual spike in ticket reprints | No |
| `risk.refund_spike` | medium | Unusual spike in refunds | No |
| `risk.after_hours_sales` | low | Sales activity outside business hours | No |
| `webhook.failures` | medium | High rate of webhook delivery failures | Yes |

## Worker System Commands

### Start Worker Manager
```bash
php src/scripts/run_workers.php start
```

### Run Once
```bash
php src/scripts/run_workers.php run-once
```

### Stop Worker Manager
```bash
php src/scripts/run_workers.php stop
```
