# Phase 6 API Sample Responses - Advanced Reporting & Analytics

## GET /provider/reports/templates

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_templates_123",
  "data": [
    {
      "_id": "ObjectId('...')",
      "template_id": "template_fleet_overview",
      "name": "Fleet Overview Dashboard",
      "description": "Comprehensive fleet monitoring dashboard",
      "category": "fleet",
      "type": "dashboard",
      "scope": "global",
      "is_public": true,
      "created_by": "provider_user_123",
      "config": {
        "layout": "grid",
        "widgets": [
          {
            "widget_id": "widget_tenants_active",
            "position": {"x": 0, "y": 0},
            "size": "medium",
            "title": "Active Tenants",
            "type": "metric"
          },
          {
            "widget_id": "widget_devices_online",
            "position": {"x": 1, "y": 0},
            "size": "medium",
            "title": "Online Devices",
            "type": "metric"
          }
        ],
        "filters": [
          {
            "field": "tenant_id",
            "operator": "eq",
            "value": "{{tenant_id}}"
          }
        ],
        "refresh_interval": 300,
        "auto_refresh": true,
        "export_formats": ["pdf", "csv", "excel"]
      },
      "permissions": {
        "view": ["Provider-Admin", "NOC"],
        "edit": ["Provider-Admin"],
        "delete": ["Provider-Admin"],
        "share": ["Provider-Admin", "NOC"]
      },
      "tags": ["fleet", "monitoring", "overview"],
      "is_active": true,
      "version": "1.0",
      "created_at": "2024-01-15T08:00:00+07:00",
      "updated_at": "2024-01-15T10:30:00+07:00"
    }
  ],
  "error": null
}
```

## POST /provider/reports/templates

**Request:**
```json
{
  "name": "Custom Sales Report",
  "description": "Monthly sales performance report",
  "category": "sales",
  "type": "report",
  "scope": "tenant",
  "is_public": false,
  "tenant_id": "tenant_123",
  "config": {
    "layout": "vertical",
    "widgets": [
      {
        "widget_id": "widget_sales_total",
        "position": {"x": 0, "y": 0},
        "size": "large",
        "title": "Total Sales",
        "type": "metric"
      },
      {
        "widget_id": "widget_sales_trend",
        "position": {"x": 0, "y": 1},
        "size": "large",
        "title": "Sales Trend",
        "type": "chart"
      }
    ],
    "filters": [
      {
        "field": "tenant_id",
        "operator": "eq",
        "value": "tenant_123"
      },
      {
        "field": "timestamp",
        "operator": "between",
        "value": ["{{start_date}}", "{{end_date}}"]
      }
    ],
    "refresh_interval": 600,
    "auto_refresh": false,
    "export_formats": ["pdf", "excel"]
  },
  "permissions": {
    "view": ["Provider-Admin", "NOC"],
    "edit": ["Provider-Admin"],
    "delete": ["Provider-Admin"],
    "share": ["Provider-Admin"]
  },
  "tags": ["sales", "monthly", "performance"]
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_create_template_456",
  "data": {
    "template_id": "template_custom_sales_report",
    "message": "Report template created successfully"
  },
  "error": null
}
```

## POST /provider/reports/templates/{template_id}/generate

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "store_id": "store_456",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "period": "30d",
  "timezone": "Asia/Bangkok",
  "format": "json",
  "include_charts": true,
  "include_data": true,
  "compression": false,
  "export_formats": ["pdf", "csv"]
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_generate_report_789",
  "data": {
    "instance_id": "instance_report_123",
    "message": "Report generation started"
  },
  "error": null
}
```

## GET /provider/reports/instances/{instance_id}/status

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_status_101",
  "data": {
    "instance_id": "instance_report_123",
    "status": "completed",
    "progress": 100,
    "estimated_completion": null,
    "metadata": {
      "generated_at": "2024-01-15T10:30:00+07:00",
      "generation_time_ms": 1250,
      "data_points": 1500,
      "file_size_bytes": 2048576,
      "error_message": null
    }
  },
  "error": null
}
```

## GET /provider/reports/instances/{instance_id}/data

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_data_202",
  "data": {
    "metrics": [
      {
        "widget_id": "widget_sales_total",
        "data": [
          {
            "_id": null,
            "total_sales": 125000.50,
            "total_count": 1250,
            "avg_amount": 100.00
          }
        ],
        "metadata": {
          "collection": "sales",
          "query_time_ms": 45,
          "record_count": 1
        }
      }
    ],
    "charts": [
      {
        "widget_id": "widget_sales_trend",
        "data": [
          {
            "_id": {
              "year": 2024,
              "month": 1,
              "day": 1
            },
            "total_sales": 4200.50,
            "count": 42
          },
          {
            "_id": {
              "year": 2024,
              "month": 1,
              "day": 2
            },
            "total_sales": 3800.25,
            "count": 38
          }
        ],
        "metadata": {
          "collection": "sales",
          "query_time_ms": 78,
          "record_count": 31
        }
      }
    ],
    "tables": [
      {
        "widget_id": "widget_top_stores",
        "data": [
          {
            "store_id": "store_456",
            "store_name": "Central Store",
            "total_sales": 45000.75,
            "transaction_count": 450
          },
          {
            "store_id": "store_789",
            "store_name": "Branch Store",
            "total_sales": 38000.25,
            "transaction_count": 380
          }
        ],
        "metadata": {
          "collection": "sales",
          "query_time_ms": 32,
          "record_count": 5
        }
      }
    ],
    "summary": {
      "generated_at": "2024-01-15T10:30:00+07:00",
      "period": "30d",
      "timezone": "Asia/Bangkok",
      "total_metrics": 1,
      "total_charts": 1,
      "total_tables": 1,
      "key_insights": [
        {
          "metric": "widget_sales_total",
          "value": 125000.50,
          "trend": "stable"
        }
      ]
    }
  },
  "error": null
}
```

## GET /provider/dashboards

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_dashboards_303",
  "data": [
    {
      "_id": "ObjectId('...')",
      "template_id": "template_fleet_dashboard",
      "name": "Fleet Monitoring Dashboard",
      "description": "Real-time fleet monitoring with alerts",
      "category": "fleet",
      "type": "dashboard",
      "scope": "global",
      "is_public": true,
      "created_by": "provider_user_123",
      "config": {
        "layout": "grid",
        "widgets": [
          {
            "widget_id": "widget_fleet_overview",
            "position": {"x": 0, "y": 0},
            "size": "large",
            "title": "Fleet Overview",
            "type": "metric"
          },
          {
            "widget_id": "widget_alerts_summary",
            "position": {"x": 1, "y": 0},
            "size": "medium",
            "title": "Active Alerts",
            "type": "alert"
          }
        ],
        "refresh_interval": 60,
        "auto_refresh": true
      },
      "is_active": true,
      "created_at": "2024-01-15T08:00:00+07:00"
    }
  ],
  "error": null
}
```

## GET /provider/dashboards/{template_id}

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_dashboard_404",
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
        }
      ]
    },
    "metadata": {
      "generated_at": "2024-01-15T10:30:00+07:00",
      "refresh_interval": 60,
      "auto_refresh": true,
      "timezone": "Asia/Bangkok"
    }
  },
  "error": null
}
```

## GET /provider/widgets

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_widgets_505",
  "data": [
    {
      "_id": "ObjectId('...')",
      "widget_id": "widget_tenants_active",
      "name": "Active Tenants Counter",
      "type": "metric",
      "category": "fleet",
      "title": "Active Tenants",
      "description": "Real-time count of active tenants",
      "config": {
        "size": "medium",
        "position": {"x": 0, "y": 0},
        "refresh_interval": 300,
        "auto_refresh": true,
        "chart_type": "number",
        "aggregation": "count",
        "group_by": "none",
        "filters": [],
        "thresholds": [
          {
            "value": 20,
            "color": "green",
            "label": "Good"
          },
          {
            "value": 10,
            "color": "yellow",
            "label": "Warning"
          },
          {
            "value": 5,
            "color": "red",
            "label": "Critical"
          }
        ],
        "colors": ["#28a745", "#ffc107", "#dc3545"],
        "display_options": {
          "show_trend": true,
          "show_percentage": false,
          "format": "number"
        }
      },
      "data_source": {
        "type": "database",
        "collection": "tenants",
        "fields": ["tenant_id", "status"],
        "filters": [
          {
            "field": "status",
            "operator": "eq",
            "value": "active"
          }
        ],
        "aggregation": {
          "_id": null,
          "count": {"$sum": 1}
        }
      },
      "permissions": {
        "view": ["Provider-Admin", "NOC"],
        "edit": ["Provider-Admin"],
        "delete": ["Provider-Admin"]
      },
      "is_public": true,
      "is_active": true,
      "tags": ["fleet", "tenants", "counter"],
      "created_by": "provider_user_123",
      "usage_count": 45,
      "last_used": "2024-01-15T10:25:00+07:00",
      "created_at": "2024-01-15T08:00:00+07:00",
      "updated_at": "2024-01-15T10:30:00+07:00"
    }
  ],
  "error": null
}
```

## GET /provider/analytics/{template_id}

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_analytics_606",
  "data": {
    "metrics": [
      {
        "widget_id": "widget_sales_analytics",
        "data": [
          {
            "_id": null,
            "total_sales": 875000.75,
            "avg_daily_sales": 12500.00,
            "growth_rate": 15.5
          }
        ],
        "metadata": {
          "collection": "sales",
          "query_time_ms": 125,
          "record_count": 1
        }
      }
    ],
    "charts": [
      {
        "widget_id": "widget_sales_trend_analysis",
        "data": [
          {
            "_id": {
              "year": 2024,
              "month": 1,
              "day": 1
            },
            "total_sales": 4200.50,
            "count": 42,
            "avg_amount": 100.00
          },
          {
            "_id": {
              "year": 2024,
              "month": 1,
              "day": 2
            },
            "total_sales": 3800.25,
            "count": 38,
            "avg_amount": 100.00
          }
        ],
        "metadata": {
          "collection": "sales",
          "query_time_ms": 156,
          "record_count": 30
        }
      }
    ],
    "tables": [
      {
        "widget_id": "widget_performance_analysis",
        "data": [
          {
            "metric": "Response Time P95",
            "current_value": 125.5,
            "previous_value": 118.2,
            "change_percent": 6.2,
            "trend": "increasing"
          },
          {
            "metric": "Error Rate",
            "current_value": 0.15,
            "previous_value": 0.22,
            "change_percent": -31.8,
            "trend": "decreasing"
          }
        ],
        "metadata": {
          "collection": "response_metrics",
          "query_time_ms": 89,
          "record_count": 5
        }
      }
    ],
    "summary": {
      "generated_at": "2024-01-15T10:30:00+07:00",
      "period": "7d",
      "timezone": "Asia/Bangkok",
      "total_metrics": 1,
      "total_charts": 1,
      "total_tables": 1,
      "key_insights": [
        {
          "metric": "widget_sales_analytics",
          "value": 875000.75,
          "trend": "stable"
        }
      ]
    },
    "trends": {
      "sales_trend_analysis": "increasing",
      "performance_analysis": "stable",
      "error_rate": "decreasing"
    },
    "forecasts": {
      "sales_trend_analysis": [12500, 12800, 13100, 13400, 13700, 14000, 14300],
      "performance_analysis": [125.5, 127.2, 129.1, 131.0, 133.2, 135.5, 137.8]
    },
    "insights": [
      {
        "type": "trending_up",
        "metric": "sales_trend_analysis",
        "trend": "increasing",
        "message": "sales_trend_analysis is trending upward"
      },
      {
        "type": "trending_down",
        "metric": "error_rate",
        "trend": "decreasing",
        "message": "error_rate is trending downward"
      },
      {
        "type": "high_value",
        "metric": "widget_sales_analytics",
        "value": 875000.75,
        "message": "High value detected for widget_sales_analytics: 875000.75"
      }
    ]
  },
  "error": null
}
```

## POST /provider/reports/instances/{instance_id}/export

**Request:**
```json
{
  "format": "pdf",
  "template": "default"
}
```

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_export_707",
  "data": {
    "file_id": "file_export_123",
    "download_url": "/api/exports/download/file_export_123",
    "expires_at": "2024-01-16T10:30:00+07:00"
  },
  "error": null
}
```

## GET /provider/exports/download/{file_id}

**Response:** (File download with appropriate headers)
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="report_2024-01-15_10-30-00.pdf"
Content-Length: 2048576

[PDF file content]
```

## GET /provider/reporting/statistics

**Response:**
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_stats_808",
  "data": {
    "templates": [
      {
        "_id": "fleet",
        "count": 5,
        "templates": [
          {
            "template_id": "template_fleet_overview",
            "name": "Fleet Overview Dashboard",
            "type": "dashboard"
          },
          {
            "template_id": "template_fleet_analytics",
            "name": "Fleet Analytics Report",
            "type": "analytics"
          }
        ]
      },
      {
        "_id": "sales",
        "count": 3,
        "templates": [
          {
            "template_id": "template_sales_report",
            "name": "Monthly Sales Report",
            "type": "report"
          }
        ]
      }
    ],
    "widgets": [
      {
        "_id": "fleet",
        "count": 8,
        "widgets": [
          {
            "widget_id": "widget_tenants_active",
            "name": "Active Tenants Counter",
            "type": "metric",
            "title": "Active Tenants"
          },
          {
            "widget_id": "widget_devices_online",
            "name": "Online Devices Counter",
            "type": "metric",
            "title": "Online Devices"
          }
        ]
      },
      {
        "_id": "sales",
        "count": 5,
        "widgets": [
          {
            "widget_id": "widget_sales_total",
            "name": "Total Sales Metric",
            "type": "metric",
            "title": "Total Sales"
          }
        ]
      }
    ],
    "reports": {
      "total_reports": 1250,
      "completed_reports": 1180,
      "failed_reports": 15,
      "avg_generation_time": 1250.5,
      "total_data_points": 150000
    },
    "exports": {
      "total_files": 450,
      "total_size": 1073741824,
      "total_downloads": 1250,
      "by_mime_type": [
        {
          "mime_type": "application/pdf",
          "size": 524288000
        },
        {
          "mime_type": "text/csv",
          "size": 104857600
        }
      ]
    },
    "supported_formats": {
      "csv": {
        "name": "CSV",
        "mime_type": "text/csv",
        "description": "Comma-separated values"
      },
      "excel": {
        "name": "Excel",
        "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "description": "Microsoft Excel format"
      },
      "pdf": {
        "name": "PDF",
        "mime_type": "application/pdf",
        "description": "Portable Document Format"
      },
      "json": {
        "name": "JSON",
        "mime_type": "application/json",
        "description": "JavaScript Object Notation"
      }
    }
  },
  "error": null
}
```

## Error Responses

### Template Not Found
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_909",
  "data": null,
  "error": {
    "code": "E_TEMPLATE_NOT_FOUND",
    "message": "Report template not found"
  }
}
```

### Report Generation Failed
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_1010",
  "data": null,
  "error": {
    "code": "E_REPORT_GENERATION_FAILED",
    "message": "Failed to generate report: Database connection timeout"
  }
}
```

### Invalid Export Format
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_1111",
  "data": null,
  "error": {
    "code": "E_INVALID_FORMAT",
    "message": "Invalid export format: xml"
  }
}
```

### File Not Found
```json
{
  "server_time": "2024-01-15T10:30:00+07:00",
  "request_id": "req_error_1212",
  "data": null,
  "error": {
    "code": "E_FILE_NOT_FOUND",
    "message": "Export file not found or expired"
  }
}
```

## Report Generation Status

### Pending
```json
{
  "instance_id": "instance_report_123",
  "status": "pending",
  "progress": 0,
  "estimated_completion": "2024-01-15T10:31:00+07:00",
  "metadata": {
    "generated_at": null,
    "generation_time_ms": null,
    "data_points": 0,
    "file_size_bytes": 0,
    "error_message": null
  }
}
```

### Generating
```json
{
  "instance_id": "instance_report_123",
  "status": "generating",
  "progress": 50,
  "estimated_completion": "2024-01-15T10:31:30+07:00",
  "metadata": {
    "generated_at": null,
    "generation_time_ms": null,
    "data_points": 0,
    "file_size_bytes": 0,
    "error_message": null
  }
}
```

### Completed
```json
{
  "instance_id": "instance_report_123",
  "status": "completed",
  "progress": 100,
  "estimated_completion": null,
  "metadata": {
    "generated_at": "2024-01-15T10:30:00+07:00",
    "generation_time_ms": 1250,
    "data_points": 1500,
    "file_size_bytes": 2048576,
    "error_message": null
  }
}
```

### Failed
```json
{
  "instance_id": "instance_report_123",
  "status": "failed",
  "progress": 0,
  "estimated_completion": null,
  "metadata": {
    "generated_at": null,
    "generation_time_ms": null,
    "data_points": 0,
    "file_size_bytes": 0,
    "error_message": "Database connection timeout during aggregation"
  }
}
```

## Widget Configuration Examples

### Metric Widget
```json
{
  "name": "Active Tenants Counter",
  "type": "metric",
  "title": "Active Tenants",
  "config": {
    "size": "medium",
    "refresh_interval": 300,
    "auto_refresh": true,
    "display_options": {
      "show_trend": true,
      "show_percentage": false,
      "format": "number"
    }
  },
  "data_source": {
    "type": "database",
    "collection": "tenants",
    "filters": [
      {
        "field": "status",
        "operator": "eq",
        "value": "active"
      }
    ],
    "aggregation": {
      "_id": null,
      "count": {"$sum": 1}
    }
  }
}
```

### Chart Widget
```json
{
  "name": "Sales Trend Chart",
  "type": "chart",
  "title": "Sales Trend",
  "config": {
    "size": "large",
    "chart_type": "line",
    "aggregation": "sum",
    "group_by": "day",
    "refresh_interval": 600,
    "colors": ["#007bff", "#28a745", "#ffc107"]
  },
  "data_source": {
    "type": "database",
    "collection": "sales",
    "fields": ["timestamp", "amount"],
    "filters": [
      {
        "field": "timestamp",
        "operator": "between",
        "value": ["{{start_date}}", "{{end_date}}"]
      }
    ],
    "aggregation": {
      "_id": {
        "year": {"$year": "$timestamp"},
        "month": {"$month": "$timestamp"},
        "day": {"$dayOfMonth": "$timestamp"}
      },
      "total_sales": {"$sum": "$amount"},
      "count": {"$sum": 1}
    }
  }
}
```

### Table Widget
```json
{
  "name": "Top Stores Table",
  "type": "table",
  "title": "Top Performing Stores",
  "config": {
    "size": "large",
    "refresh_interval": 900,
    "display_options": {
      "sort_by": "total_sales",
      "sort_order": "desc",
      "limit": 10
    }
  },
  "data_source": {
    "type": "database",
    "collection": "sales",
    "fields": ["store_id", "amount"],
    "filters": [
      {
        "field": "timestamp",
        "operator": "between",
        "value": ["{{start_date}}", "{{end_date}}"]
      }
    ],
    "aggregation": {
      "_id": "$store_id",
      "total_sales": {"$sum": "$amount"},
      "transaction_count": {"$sum": 1}
    },
    "sort": {"total_sales": -1},
    "limit": 10
  }
}
```

## Analytics Features

### Trend Analysis
- **Increasing**: Values trending upward over time
- **Decreasing**: Values trending downward over time
- **Stable**: Values remaining relatively constant
- **Insufficient Data**: Not enough data points for analysis

### Forecasting
- **Linear Regression**: Simple trend-based forecasting
- **Periods**: Configurable forecast periods (default: 7 days)
- **Accuracy**: Based on historical data patterns

### Insights Generation
- **High Value**: Values exceeding normal thresholds
- **Low Value**: Values below normal thresholds
- **Trending Up**: Positive trend indicators
- **Trending Down**: Negative trend indicators

## Export Features

### Supported Formats
- **CSV**: Comma-separated values for data analysis
- **Excel**: Microsoft Excel format with formatting
- **PDF**: Portable Document Format with charts and tables
- **JSON**: Structured data format for API consumption

### File Management
- **Automatic Expiration**: Files expire after 24 hours
- **Download Tracking**: Track download counts and usage
- **Secure Access**: Access tokens for shared files
- **Cleanup**: Automatic cleanup of expired files

## Performance Metrics

### Report Generation
- **Average Time**: 1-3 seconds for simple reports
- **Complex Reports**: 5-10 seconds for multi-widget reports
- **Data Points**: Handle up to 100,000 data points per report
- **Concurrent Generation**: Support up to 10 concurrent reports

### Dashboard Performance
- **Real-time Updates**: 30-60 second refresh intervals
- **Widget Loading**: < 200ms per widget
- **Cache Hit Rate**: > 95% for dashboard data
- **Memory Usage**: < 100MB per dashboard session

### Export Performance
- **File Generation**: 1-5 seconds for standard formats
- **File Size**: Optimized compression for large datasets
- **Download Speed**: Streamed downloads for large files
- **Storage**: Temporary storage with automatic cleanup
