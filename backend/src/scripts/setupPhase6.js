const mongoose = require('mongoose');
const { ReportTemplate, DashboardWidget } = require('../models/reporting');
require('dotenv').config();

const logger = require('../utils/logger');

async function setupPhase6() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/playpark', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    logger.info('Connected to MongoDB');

    // Create indexes
    await createIndexes();
    logger.info('Created Phase 6 indexes');

    // Seed sample data
    await seedReportTemplates();
    logger.info('Seeded report templates');

    await seedDashboardWidgets();
    logger.info('Seeded dashboard widgets');

    logger.info('Phase 6 setup completed successfully');
  } catch (error) {
    logger.error('Phase 6 setup failed:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
  }
}

async function createIndexes() {
  const db = mongoose.connection.db;

  // Report Templates indexes
  await db.collection('reporttemplates').createIndex({ template_id: 1 }, { unique: true });
  await db.collection('reporttemplates').createIndex({ category: 1, type: 1 });
  await db.collection('reporttemplates').createIndex({ created_by: 1 });
  await db.collection('reporttemplates').createIndex({ created_at: -1 });

  // Report Instances indexes
  await db.collection('reportinstances').createIndex({ instance_id: 1 }, { unique: true });
  await db.collection('reportinstances').createIndex({ template_id: 1 });
  await db.collection('reportinstances').createIndex({ tenant_id: 1, generated_at: -1 });
  await db.collection('reportinstances').createIndex({ status: 1 });
  await db.collection('reportinstances').createIndex({ generated_at: -1 });

  // Dashboard Widgets indexes
  await db.collection('dashboardwidgets').createIndex({ widget_id: 1 }, { unique: true });
  await db.collection('dashboardwidgets').createIndex({ dashboard_id: 1 });
  await db.collection('dashboardwidgets').createIndex({ type: 1 });
  await db.collection('dashboardwidgets').createIndex({ created_at: -1 });

  // Export Files indexes
  await db.collection('exportfiles').createIndex({ file_id: 1 }, { unique: true });
  await db.collection('exportfiles').createIndex({ instance_id: 1 });
  await db.collection('exportfiles').createIndex({ access_token: 1 });
  await db.collection('exportfiles').createIndex({ expires_at: 1 });

  // Analytics Cache indexes
  await db.collection('analyticscaches').createIndex({ cache_key: 1 }, { unique: true });
  await db.collection('analyticscaches').createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });

  logger.info('All Phase 6 indexes created');
}

async function seedReportTemplates() {
  // Clear existing templates
  await ReportTemplate.deleteMany({});

  const templates = [
    {
      name: 'Fleet Overview Dashboard',
      description: 'Comprehensive fleet monitoring dashboard',
      category: 'fleet',
      type: 'dashboard',
      scope: 'global',
      config: {
        layout: 'grid',
        widgets: [
          {
            widget_id: 'widget_tenants_active',
            position: { x: 0, y: 0 },
            size: 'medium',
            title: 'Active Tenants'
          },
          {
            widget_id: 'widget_devices_online',
            position: { x: 1, y: 0 },
            size: 'medium',
            title: 'Online Devices'
          }
        ],
        filters: [
          {
            field: 'tenant_id',
            operator: 'eq',
            value: '{{tenant_id}}'
          }
        ],
        refresh_interval: 300,
        auto_refresh: true,
        export_formats: ['pdf', 'csv', 'excel']
      },
      permissions: {
        view: ['Provider-Admin', 'NOC'],
        edit: ['Provider-Admin'],
        delete: ['Provider-Admin'],
        share: ['Provider-Admin', 'NOC']
      },
      tags: ['fleet', 'monitoring', 'dashboard']
    },
    {
      name: 'Sales Performance Report',
      description: 'Detailed sales performance analytics',
      category: 'sales',
      type: 'report',
      scope: 'tenant',
      config: {
        sections: [
          {
            title: 'Daily Sales',
            type: 'chart',
            chart_type: 'line',
            data_source: {
              collection: 'sales',
              aggregation: {
                $group: {
                  _id: { $dateToString: { format: '%Y-%m-%d', date: '$created_at' } },
                  total_sales: { $sum: '$total_amount' },
                  transaction_count: { $sum: 1 }
                }
              }
            }
          },
          {
            title: 'Top Products',
            type: 'table',
            data_source: {
              collection: 'sales',
              aggregation: {
                $unwind: '$items',
                $group: {
                  _id: '$items.package_id',
                  total_sold: { $sum: '$items.quantity' },
                  revenue: { $sum: { $multiply: ['$items.quantity', '$items.unit_price'] } }
                }
              }
            }
          }
        ],
        date_range: {
          default: 'last_30_days',
          options: ['last_7_days', 'last_30_days', 'last_90_days', 'custom']
        }
      },
      permissions: {
        view: ['Provider-Admin', 'NOC', 'Billing-Ops'],
        edit: ['Provider-Admin'],
        delete: ['Provider-Admin'],
        share: ['Provider-Admin', 'NOC']
      },
      tags: ['sales', 'performance', 'analytics']
    },
    {
      name: 'System Performance Analytics',
      description: 'Real-time system performance metrics',
      category: 'performance',
      type: 'analytics',
      scope: 'global',
      config: {
        metrics: [
          'response_time_p95',
          'error_rate',
          'api_calls_per_minute',
          'database_query_time'
        ],
        visualization: {
          type: 'mixed',
          charts: [
            {
              metric: 'response_time_p95',
              type: 'line',
              title: 'Response Time P95'
            },
            {
              metric: 'error_rate',
              type: 'bar',
              title: 'Error Rate'
            }
          ]
        },
        alerts: [
          {
            metric: 'response_time_p95',
            threshold: 1000,
            operator: 'gt',
            severity: 'warning'
          }
        ]
      },
      permissions: {
        view: ['Provider-Admin', 'NOC'],
        edit: ['Provider-Admin'],
        delete: ['Provider-Admin'],
        share: ['Provider-Admin']
      },
      tags: ['performance', 'monitoring', 'system']
    }
  ];

  for (const template of templates) {
    const newTemplate = new ReportTemplate(template);
    await newTemplate.save();
  }

  logger.info(`Seeded ${templates.length} report templates`);
}

async function seedDashboardWidgets() {
  // Clear existing widgets
  await DashboardWidget.deleteMany({});

  const widgets = [
    {
      dashboard_id: 'template_fleet_analytics',
      name: 'Active Tenants Counter',
      type: 'metric',
      title: 'Active Tenants',
      config: {
        size: 'medium',
        refresh_interval: 300,
        auto_refresh: true,
        chart_type: 'number',
        aggregation: 'count',
        thresholds: [
          {
            value: 20,
            color: 'green',
            label: 'Good'
          }
        ]
      },
      data_source: {
        type: 'database',
        collection: 'tenants',
        query: {
          filter: { status: 'active' },
          aggregation: {
            _id: null,
            count: { $sum: 1 }
          }
        }
      },
      position: { x: 0, y: 0, w: 1, h: 1 },
      order: 1
    },
    {
      dashboard_id: 'template_fleet_analytics',
      name: 'Online Devices Chart',
      type: 'chart',
      title: 'Online Devices Trend',
      config: {
        size: 'large',
        refresh_interval: 60,
        auto_refresh: true,
        chart_type: 'line',
        time_range: '24h',
        show_trend: true
      },
      data_source: {
        type: 'database',
        collection: 'provider_metrics_daily',
        query: {
          metric_type: 'fleet',
          metrics: ['devices_online'],
          group_by: 'day',
          period: '7d'
        }
      },
      position: { x: 1, y: 0, w: 2, h: 1 },
      order: 2
    },
    {
      dashboard_id: 'template_fleet_analytics',
      name: 'Alert Status Table',
      type: 'table',
      title: 'Recent Alerts',
      config: {
        size: 'medium',
        refresh_interval: 30,
        auto_refresh: true,
        columns: ['alert_type', 'severity', 'status', 'created_at'],
        sort_by: 'created_at',
        sort_order: 'desc',
        limit: 10
      },
      data_source: {
        type: 'database',
        collection: 'provider_alerts',
        query: {
          filter: { status: 'open' },
          sort: { created_at: -1 },
          limit: 10
        }
      },
      position: { x: 0, y: 1, w: 1, h: 2 },
      order: 3
    },
    {
      dashboard_id: 'template_sales_analytics',
      name: 'Sales Revenue Metric',
      type: 'metric',
      title: 'Total Sales (24h)',
      config: {
        size: 'medium',
        refresh_interval: 300,
        auto_refresh: true,
        chart_type: 'currency',
        currency: 'THB',
        show_change: true
      },
      data_source: {
        type: 'database',
        collection: 'provider_metrics_daily',
        query: {
          metric_type: 'sales',
          metrics: ['sales_24h'],
          group_by: 'day',
          period: '1d'
        }
      },
      position: { x: 0, y: 0, w: 1, h: 1 },
      order: 1
    }
  ];

  for (const widget of widgets) {
    const newWidget = new DashboardWidget(widget);
    await newWidget.save();
  }

  logger.info(`Seeded ${widgets.length} dashboard widgets`);
}

// Run setup if called directly
if (require.main === module) {
  setupPhase6();
}

module.exports = { setupPhase6, createIndexes, seedReportTemplates, seedDashboardWidgets };
