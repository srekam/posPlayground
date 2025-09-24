# Phase 6 Docker Setup - Advanced Reporting & Analytics

## Overview

Phase 6 implements comprehensive advanced reporting and analytics with:

- **Report Templates** - Configurable report templates with widgets and filters
- **Dashboard Builder** - Visual dashboard creation with drag-and-drop widgets
- **Analytics Engine** - Business intelligence with trend analysis and forecasting
- **Export System** - Multi-format export (PDF, CSV, Excel, JSON) with file management
- **Widget Library** - Reusable widgets for metrics, charts, tables, and alerts
- **Real-time Analytics** - Live analytics with trend analysis and insights

## Prerequisites

- Docker and Docker Compose installed
- Existing backend running (Phases 1-5)
- MongoDB accessible within Docker network

## Quick Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Install New Dependencies (if needed)
```bash
docker-compose exec api npm install moment-timezone
```

### 3. Run Phase 6 Setup Script
```bash
docker-compose exec api npm run setup:phase6
```

### 4. Restart the API Container (to load new routes)
```bash
docker-compose restart api
```

### 5. Test the New APIs
```bash
# Test report templates
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reports/templates"

# Test dashboard creation
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Dashboard", "type": "dashboard", "config": {"layout": "grid", "widgets": []}}' \
     "http://localhost:48080/provider/dashboards"

# Test analytics
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/analytics/template_fleet_analytics?period=7d"
```

## Detailed Setup Steps

### 1. Verify Current Setup
```bash
# Check if containers are running
docker-compose ps

# Check API health
curl http://localhost:48080/health
```

### 2. Setup Phase 6 Database Collections
```bash
# Run the setup script inside the Docker container
docker-compose exec api node src/scripts/setupPhase6.js
```

This will:
- Create MongoDB indexes for Phase 6 collections
- Seed sample report templates
- Seed sample dashboard widgets
- Set up analytics cache collection

### 3. Verify Database Setup
```bash
# Connect to MongoDB container
docker-compose exec mongo mongosh -u admin -p playpark123

# Check collections
use playpark
show collections

# Verify Phase 6 collections exist
db.reporttemplates.find().limit(1)
db.dashboardwidgets.find().limit(1)
db.analyticscaches.find().limit(1)
```

### 4. Test API Endpoints

#### Report Template Management
```bash
# List all report templates
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reports/templates"

# Get specific template
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reports/templates/TEMPLATE_ID"

# Create new template
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Custom Sales Report",
       "description": "Custom sales performance report",
       "category": "sales",
       "type": "report",
       "scope": "tenant",
       "config": {"layout": "standard"},
       "permissions": {
         "view": ["Provider-Admin", "NOC"],
         "edit": ["Provider-Admin"],
         "delete": ["Provider-Admin"],
         "share": ["Provider-Admin"]
       }
     }' \
     "http://localhost:48080/provider/reports/templates"
```

#### Dashboard Management
```bash
# List dashboards
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/dashboards"

# Get dashboard data
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/dashboards/template_fleet_analytics"

# Create new dashboard
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Custom Dashboard",
       "description": "Custom monitoring dashboard",
       "config": {"layout": "grid", "widgets": []},
       "permissions": {
         "view": ["Provider-Admin", "NOC"],
         "edit": ["Provider-Admin"],
         "delete": ["Provider-Admin"],
         "share": ["Provider-Admin"]
       }
     }' \
     "http://localhost:48080/provider/dashboards"
```

#### Widget Management
```bash
# List widgets
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/widgets"

# Create new widget
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "dashboard_id": "template_fleet_analytics",
       "name": "Custom Metric",
       "type": "metric",
       "title": "Custom Metric",
       "config": {"size": "medium", "refresh_interval": 300},
       "data_source": {
         "type": "database",
         "collection": "tenants",
         "query": {"filter": {"status": "active"}}
       }
     }' \
     "http://localhost:48080/provider/widgets"
```

#### Analytics
```bash
# Get analytics data
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/analytics/template_fleet_analytics?period=7d"

# Get analytics with tenant filter
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/analytics/template_sales_analytics?tenant_id=tenant_01&period=30d"
```

#### Export System
```bash
# Generate report
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"parameters": {"period": "7d"}}' \
     "http://localhost:48080/provider/reports/templates/TEMPLATE_ID/generate"

# Check report status
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reports/instances/INSTANCE_ID/status"

# Export report
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"format": "csv"}' \
     "http://localhost:48080/provider/reports/instances/INSTANCE_ID/export"

# Download export file
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/exports/download/FILE_ID"
```

#### Statistics
```bash
# Get reporting statistics
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reporting/statistics"
```

## API Endpoints Summary

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

## Database Collections Created

### New Collections
- **reporttemplates** - Report template definitions
- **reportinstances** - Generated report instances
- **dashboardwidgets** - Widget definitions and configurations
- **exportfiles** - Export file metadata and tracking
- **analyticscaches** - Analytics data caching

### Enhanced Collections
- **provider_metrics_daily** - Enhanced for analytics
- **device_heartbeats** - Enhanced for performance analytics
- **provider_alerts** - Enhanced for alert analytics

## Troubleshooting

### Common Issues

#### 1. "Cannot find module" errors
```bash
# Reinstall dependencies
docker-compose exec api npm install

# Check if moment-timezone is installed
docker-compose exec api npm list moment-timezone
```

#### 2. Database connection issues
```bash
# Check MongoDB connection
docker-compose exec api node -e "const mongoose = require('mongoose'); mongoose.connect(process.env.MONGODB_URI).then(() => console.log('Connected')).catch(console.error)"

# Check MongoDB container
docker-compose logs mongo
```

#### 3. Route not found errors
```bash
# Restart API container to load new routes
docker-compose restart api

# Check if routes are loaded
docker-compose logs api | grep "Provider routes"
```

#### 4. Permission errors
```bash
# Check file permissions
docker-compose exec api ls -la src/routes/
docker-compose exec api ls -la src/controllers/
docker-compose exec api ls -la src/models/
```

### Health Checks

#### Check System Health
```bash
# API health
curl http://localhost:48080/health

# Provider routes health
curl -H "Authorization: Bearer YOUR_PROVIDER_JWT_TOKEN" \
     "http://localhost:48080/provider/reporting/statistics"
```

#### Check Database Health
```bash
# Connect to MongoDB
docker-compose exec mongo mongosh -u admin -p playpark123

# Check collections
use playpark
db.reporttemplates.countDocuments()
db.dashboardwidgets.countDocuments()
db.analyticscaches.countDocuments()
```

#### Check Container Health
```bash
# Container status
docker-compose ps

# Container logs
docker-compose logs api
docker-compose logs mongo

# Resource usage
docker stats
```

## Environment Variables

Add these to your `.env` file if needed:

```env
# Phase 6 Configuration
EXPORT_STORAGE_PATH=/tmp/exports
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

## Next Steps

After successful setup:

1. **Test all endpoints** to ensure they're working correctly
2. **Create custom report templates** for your specific needs
3. **Build custom dashboards** with relevant widgets
4. **Set up analytics** for your business metrics
5. **Configure exports** for your reporting needs

## Support

If you encounter issues:

1. Check the container logs: `docker-compose logs api`
2. Verify database connectivity: `docker-compose exec api node -e "console.log(process.env.MONGODB_URI)"`
3. Test individual endpoints with curl commands
4. Check MongoDB collections and indexes

The Phase 6 Advanced Reporting & Analytics system is now ready for use!
