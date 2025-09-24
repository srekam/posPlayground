# Phase 6 Setup - Advanced Reporting & Analytics

## Overview

Phase 6 implements comprehensive advanced reporting and analytics with:

- **Report Templates** - Configurable report templates with widgets and filters
- **Dashboard Builder** - Visual dashboard creation with drag-and-drop widgets
- **Analytics Engine** - Business intelligence with trend analysis and forecasting
- **Export System** - Multi-format export (PDF, CSV, Excel, JSON) with file management
- **Widget Library** - Reusable widgets for metrics, charts, tables, and alerts
- **Real-time Analytics** - Live analytics with trend analysis and insights

## Prerequisites

- Phase 1, 2, 3, 4, and 5 completed and running
- MongoDB with proper indexes
- PHP 8.x with MongoDB extension
- Background workers running

## Installation Steps

### 1. Create Phase 6 Indexes

```bash
cd backend
php src/scripts/create_phase6_indexes.php
```

### 2. Test Advanced Reporting APIs

```bash
# Test report templates
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reports/templates"

# Test dashboard creation
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Dashboard", "type": "dashboard", "config": {"layout": "grid", "widgets": []}}' \
     "http://localhost:48080/provider/dashboards"

# Test widget creation
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Widget", "type": "metric", "title": "Test Metric", "data_source": {"type": "database", "collection": "tenants"}}' \
     "http://localhost:48080/provider/widgets"

# Test analytics
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/analytics/template_fleet_analytics?period=7d"
```

## API Endpoints

### Report Template Management
- `GET /provider/reports/templates` - List report templates
- `POST /provider/reports/templates` - Create report template
- `GET /provider/reports/templates/{template_id}` - Get template details

### Report Generation
- `POST /provider/reports/templates/{template_id}/generate` - Generate report
- `GET /provider/reports/instances/{instance_id}/status` - Get generation status
- `GET /provider/reports/instances/{instance_id}/data` - Get report data

### Dashboard Management
- `GET /provider/dashboards` - List dashboards
- `POST /provider/dashboards` - Create dashboard
- `GET /provider/dashboards/{template_id}` - Get dashboard data

### Widget Management
- `GET /provider/widgets` - List widgets
- `POST /provider/widgets` - Create widget

### Analytics
- `GET /provider/analytics/{template_id}` - Get analytics data

### Export System
- `POST /provider/reports/instances/{instance_id}/export` - Export report
- `GET /provider/exports/download/{file_id}` - Download export file

### Statistics
- `GET /provider/reporting/statistics` - Get reporting statistics

## Report Templates

### Template Types
1. **Dashboard** - Real-time interactive dashboards
2. **Report** - Static reports with data export
3. **Analytics** - Business intelligence with trends and forecasting

### Template Categories
- **Fleet** - Fleet monitoring and management
- **Sales** - Sales performance and analytics
- **Performance** - System performance metrics
- **Alerts** - Alert monitoring and management
- **Usage** - Usage tracking and billing
- **Custom** - User-defined templates

### Template Configuration
```json
{
  "name": "Fleet Overview Dashboard",
  "description": "Comprehensive fleet monitoring",
  "category": "fleet",
  "type": "dashboard",
  "scope": "global",
  "config": {
    "layout": "grid",
    "widgets": [
      {
        "widget_id": "widget_tenants_active",
        "position": {"x": 0, "y": 0},
        "size": "medium",
        "title": "Active Tenants"
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
  }
}
```

## Dashboard Builder

### Widget Types
1. **Metric** - Single value metrics with trends
2. **Chart** - Line, bar, pie, area, scatter charts
3. **Table** - Data tables with sorting and filtering
4. **Alert** - Alert monitoring and management
5. **Map** - Geographic data visualization

### Widget Configuration
```json
{
  "name": "Active Tenants Counter",
  "type": "metric",
  "title": "Active Tenants",
  "config": {
    "size": "medium",
    "refresh_interval": 300,
    "auto_refresh": true,
    "chart_type": "number",
    "aggregation": "count",
    "thresholds": [
      {
        "value": 20,
        "color": "green",
        "label": "Good"
      }
    ]
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

### Data Source Types
1. **Database** - Direct MongoDB queries
2. **API** - Internal API endpoints
3. **Calculated** - Formula-based calculations

## Analytics Engine

### Trend Analysis
- **Increasing** - Values trending upward
- **Decreasing** - Values trending downward
- **Stable** - Values remaining constant
- **Insufficient Data** - Not enough data points

### Forecasting
- **Linear Regression** - Simple trend-based forecasting
- **Configurable Periods** - 1-30 day forecasts
- **Accuracy Metrics** - Based on historical patterns

### Insights Generation
- **High Value Detection** - Values exceeding thresholds
- **Low Value Detection** - Values below thresholds
- **Trend Analysis** - Positive/negative trend indicators
- **Anomaly Detection** - Unusual patterns and spikes

### Analytics Features
```json
{
  "trends": {
    "sales_trend": "increasing",
    "error_rate": "decreasing",
    "performance": "stable"
  },
  "forecasts": {
    "sales_trend": [12500, 12800, 13100, 13400, 13700, 14000, 14300],
    "performance": [125.5, 127.2, 129.1, 131.0, 133.2, 135.5, 137.8]
  },
  "insights": [
    {
      "type": "trending_up",
      "metric": "sales_trend",
      "message": "Sales are trending upward"
    },
    {
      "type": "high_value",
      "metric": "total_sales",
      "value": 875000.75,
      "message": "High sales volume detected"
    }
  ]
}
```

## Export System

### Supported Formats
- **CSV** - Comma-separated values for data analysis
- **Excel** - Microsoft Excel format with formatting
- **PDF** - Portable Document Format with charts
- **JSON** - Structured data for API consumption

### Export Features
- **Multi-format Export** - Export same data in multiple formats
- **File Management** - Automatic expiration and cleanup
- **Download Tracking** - Track download counts and usage
- **Secure Access** - Access tokens for shared files
- **Compression** - Optional file compression

### Export Configuration
```json
{
  "format": "pdf",
  "template": "default",
  "include_charts": true,
  "include_data": true,
  "compression": false
}
```

## Widget Library

### Pre-built Widgets
1. **Fleet Metrics**
   - Active Tenants Counter
   - Online Devices Counter
   - Uptime Percentage
   - Fleet Health Status

2. **Sales Metrics**
   - Total Sales Amount
   - Daily Sales Trend
   - Top Performing Stores
   - Sales by Payment Method

3. **Performance Metrics**
   - Response Time P95
   - Error Rate Percentage
   - API Call Volume
   - Sync Lag Monitoring

4. **Alert Metrics**
   - Active Alerts Count
   - Alerts by Severity
   - Recent Alert History
   - Alert Resolution Rate

### Widget Categories
- **Fleet** - Fleet monitoring widgets
- **Sales** - Sales performance widgets
- **Performance** - System performance widgets
- **Alerts** - Alert management widgets
- **Usage** - Usage tracking widgets
- **Custom** - User-defined widgets

## Report Generation

### Generation Process
1. **Template Validation** - Validate template configuration
2. **Data Collection** - Gather data from multiple sources
3. **Widget Processing** - Process each widget in template
4. **Data Aggregation** - Aggregate and format data
5. **Export Generation** - Generate export files
6. **Status Updates** - Update generation status

### Generation Status
- **Pending** - Report queued for generation
- **Generating** - Report being generated
- **Completed** - Report generation completed
- **Failed** - Report generation failed

### Performance Metrics
- **Average Generation Time** - 1-3 seconds for simple reports
- **Complex Reports** - 5-10 seconds for multi-widget reports
- **Data Points** - Handle up to 100,000 data points
- **Concurrent Generation** - Support up to 10 concurrent reports

## Dashboard Performance

### Real-time Updates
- **Refresh Intervals** - 30-60 second intervals
- **Auto-refresh** - Configurable automatic updates
- **Cache Integration** - Leverage Phase 5 caching
- **WebSocket Support** - Real-time data streaming

### Performance Targets
- **Widget Loading** - < 200ms per widget
- **Dashboard Load** - < 2 seconds for complete dashboard
- **Cache Hit Rate** - > 95% for dashboard data
- **Memory Usage** - < 100MB per dashboard session

## Database Collections

### New Collections
- **report_templates** - Report template definitions
- **report_instances** - Generated report instances
- **dashboard_widgets** - Widget definitions and configurations
- **export_files** - Export file metadata and tracking

### Enhanced Collections
- **provider_metrics_daily** - Enhanced for analytics
- **sales** - Enhanced indexes for reporting
- **redemptions** - Enhanced indexes for reporting
- **device_heartbeats** - Enhanced for performance analytics
- **provider_alerts** - Enhanced for alert analytics

## Security and Permissions

### Permission Matrix
- **Provider-Admin** - Full access to all features
- **NOC** - Read access to dashboards and reports
- **Billing-Ops** - Access to billing-related reports
- **Read-Only** - Limited read-only access

### Access Control
- **Template Permissions** - View, edit, delete, share permissions
- **Widget Permissions** - View, edit, delete permissions
- **Export Permissions** - Download and share permissions
- **Tenant Isolation** - Tenant-specific data access

## Monitoring and Troubleshooting

### Check Report Generation
```javascript
// Check report instances
db.report_instances.find().sort({created_at: -1}).limit(5)

// Check generation status
db.report_instances.aggregate([
  {$group: {
    _id: '$status',
    count: {$sum: 1},
    avg_generation_time: {$avg: '$metadata.generation_time_ms'}
  }}
])
```

### Check Dashboard Performance
```javascript
// Check widget usage
db.dashboard_widgets.find().sort({usage_count: -1}).limit(10)

// Check dashboard templates
db.report_templates.find({type: 'dashboard'}).sort({updated_at: -1})
```

### Check Export Files
```javascript
// Check export statistics
db.export_files.aggregate([
  {$group: {
    _id: '$mime_type',
    count: {$sum: 1},
    total_size: {$sum: '$size'},
    total_downloads: {$sum: '$download_count'}
  }}
])

// Check expired files
db.export_files.find({
  expires_at: {$lt: new Date()}
}).count()
```

## Environment Variables

Add these to your `.env` file:

```env
# Reporting Configuration
REPORT_GENERATION_TIMEOUT=300
REPORT_MAX_DATA_POINTS=100000
REPORT_CACHE_TTL=300

# Dashboard Configuration
DASHBOARD_REFRESH_INTERVAL=60
DASHBOARD_AUTO_REFRESH_ENABLED=true
DASHBOARD_MAX_WIDGETS=50

# Export Configuration
EXPORT_FILE_EXPIRY_HOURS=24
EXPORT_MAX_FILE_SIZE_MB=100
EXPORT_CLEANUP_INTERVAL=3600

# Analytics Configuration
ANALYTICS_TREND_THRESHOLD=10
ANALYTICS_FORECAST_PERIODS=7
ANALYTICS_INSIGHT_ENABLED=true

# Performance Configuration
WIDGET_LOAD_TIMEOUT=5000
REPORT_GENERATION_CONCURRENCY=10
CACHE_WIDGET_DATA_TTL=300
```

## Health Checks

### System Health
```bash
# Check report generation status
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reporting/statistics" | jq '.data.reports'

# Check dashboard performance
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/dashboards" | jq '.data | length'

# Check widget availability
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/widgets" | jq '.data | length'
```

### Performance Health
```bash
# Check export file statistics
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reporting/statistics" | jq '.data.exports'

# Check template categories
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reporting/statistics" | jq '.data.templates'
```

## Data Retention

### Report Data
- **Report Instances** - 30 days (configurable)
- **Export Files** - 24 hours (automatic cleanup)
- **Template Metadata** - Indefinite
- **Widget Data** - Cached for 5 minutes

### Cleanup Schedule
- **Export Files** - Every hour
- **Report Instances** - Daily at 2 AM
- **Cache Cleanup** - Every 5 minutes
- **Analytics Data** - 12 months retention

## Next Steps

Phase 6 provides the foundation for:
- **Phase 7**: Advanced integrations and webhooks
- **Real-time Monitoring**: Live dashboard updates
- **Predictive Analytics**: Machine learning integration
- **Custom Visualizations**: Advanced chart types

The advanced reporting and analytics system is now fully operational with comprehensive dashboard building, report generation, analytics engine, and multi-format export capabilities!

## Best Practices

### Template Design
- Keep templates focused on specific use cases
- Use consistent naming conventions
- Include proper descriptions and tags
- Set appropriate refresh intervals

### Widget Configuration
- Optimize data source queries
- Use appropriate chart types for data
- Set meaningful thresholds and colors
- Include proper error handling

### Performance Optimization
- Use caching for frequently accessed data
- Limit data points in time-series widgets
- Optimize aggregation pipelines
- Monitor generation times

### Security Considerations
- Validate all user inputs
- Implement proper access controls
- Sanitize export data
- Monitor for suspicious activity
