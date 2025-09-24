const mongoose = require('mongoose');
const { ulid } = require('ulid');

// Report Template Schema
const reportTemplateSchema = new mongoose.Schema({
  template_id: {
    type: String,
    required: true,
    unique: true,
    default: () => ulid()
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  category: {
    type: String,
    required: true,
    enum: ['fleet', 'sales', 'performance', 'alerts', 'usage', 'custom']
  },
  type: {
    type: String,
    required: true,
    enum: ['dashboard', 'report', 'analytics']
  },
  scope: {
    type: String,
    required: true,
    enum: ['global', 'tenant', 'store'],
    default: 'global'
  },
  config: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  permissions: {
    view: [{
      type: String,
      enum: ['Provider-Admin', 'NOC', 'Billing-Ops', 'Read-Only']
    }],
    edit: [{
      type: String,
      enum: ['Provider-Admin', 'NOC', 'Billing-Ops', 'Read-Only']
    }],
    delete: [{
      type: String,
      enum: ['Provider-Admin', 'NOC', 'Billing-Ops', 'Read-Only']
    }],
    share: [{
      type: String,
      enum: ['Provider-Admin', 'NOC', 'Billing-Ops', 'Read-Only']
    }]
  },
  created_by: {
    type: String,
    ref: 'ProviderUser'
  },
  tags: [String],
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Report Instance Schema
const reportInstanceSchema = new mongoose.Schema({
  instance_id: {
    type: String,
    required: true,
    unique: true,
    default: () => ulid()
  },
  template_id: {
    type: String,
    required: true,
    ref: 'ReportTemplate'
  },
  tenant_id: {
    type: String,
    ref: 'Tenant'
  },
  parameters: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  status: {
    type: String,
    required: true,
    enum: ['pending', 'generating', 'completed', 'failed'],
    default: 'pending'
  },
  generated_by: {
    type: String,
    ref: 'ProviderUser'
  },
  generated_at: {
    type: Date,
    default: Date.now
  },
  completed_at: Date,
  error_message: String,
  report_data_ref: String,
  export_status: {
    type: String,
    enum: ['none', 'pending', 'exporting', 'completed', 'failed'],
    default: 'none'
  },
  export_file_id: {
    type: String,
    ref: 'ExportFile'
  },
  metadata: {
    generation_time_ms: Number,
    data_points: Number,
    cache_hit: Boolean
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Dashboard Widget Schema
const dashboardWidgetSchema = new mongoose.Schema({
  widget_id: {
    type: String,
    required: true,
    unique: true,
    default: () => ulid()
  },
  dashboard_id: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  type: {
    type: String,
    required: true,
    enum: ['metric', 'chart', 'table', 'alert', 'map']
  },
  title: {
    type: String,
    required: true,
    trim: true
  },
  config: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  data_source: {
    type: {
      type: String,
      required: true,
      enum: ['database', 'api', 'calculated']
    },
    collection: String,
    query: mongoose.Schema.Types.Mixed,
    endpoint: String,
    formula: String
  },
  position: {
    x: { type: Number, default: 0 },
    y: { type: Number, default: 0 },
    w: { type: Number, default: 1 },
    h: { type: Number, default: 1 }
  },
  order: {
    type: Number,
    default: 0
  },
  created_by: {
    type: String,
    ref: 'ProviderUser'
  },
  usage_count: {
    type: Number,
    default: 0
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Export File Schema
const exportFileSchema = new mongoose.Schema({
  file_id: {
    type: String,
    required: true,
    unique: true,
    default: () => ulid()
  },
  instance_id: {
    type: String,
    required: true,
    ref: 'ReportInstance'
  },
  format: {
    type: String,
    required: true,
    enum: ['csv', 'excel', 'pdf', 'json']
  },
  file_path: {
    type: String,
    required: true
  },
  mime_type: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    required: true
  },
  download_count: {
    type: Number,
    default: 0
  },
  access_token: {
    type: String,
    required: true,
    unique: true,
    default: () => ulid()
  },
  expires_at: {
    type: Date,
    required: true,
    default: () => new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
  },
  requested_by: {
    type: String,
    ref: 'ProviderUser'
  },
  created_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Analytics Cache Schema
const analyticsCacheSchema = new mongoose.Schema({
  cache_key: {
    type: String,
    required: true,
    unique: true
  },
  data: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  expires_at: {
    type: Date,
    required: true,
    default: () => new Date(Date.now() + 5 * 60 * 1000) // 5 minutes
  },
  hit_count: {
    type: Number,
    default: 0
  },
  created_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Indexes for better performance
reportTemplateSchema.index({ template_id: 1 });
reportTemplateSchema.index({ category: 1, type: 1 });
reportTemplateSchema.index({ created_by: 1 });
reportTemplateSchema.index({ created_at: -1 });

reportInstanceSchema.index({ instance_id: 1 });
reportInstanceSchema.index({ template_id: 1 });
reportInstanceSchema.index({ tenant_id: 1, generated_at: -1 });
reportInstanceSchema.index({ status: 1 });
reportInstanceSchema.index({ generated_at: -1 });

dashboardWidgetSchema.index({ widget_id: 1 });
dashboardWidgetSchema.index({ dashboard_id: 1 });
dashboardWidgetSchema.index({ type: 1 });
dashboardWidgetSchema.index({ created_at: -1 });

exportFileSchema.index({ file_id: 1 });
exportFileSchema.index({ instance_id: 1 });
exportFileSchema.index({ access_token: 1 });
exportFileSchema.index({ expires_at: 1 });

analyticsCacheSchema.index({ cache_key: 1 });
analyticsCacheSchema.index({ expires_at: 1 });

// Create models
const ReportTemplate = mongoose.model('ReportTemplate', reportTemplateSchema);
const ReportInstance = mongoose.model('ReportInstance', reportInstanceSchema);
const DashboardWidget = mongoose.model('DashboardWidget', dashboardWidgetSchema);
const ExportFile = mongoose.model('ExportFile', exportFileSchema);
const AnalyticsCache = mongoose.model('AnalyticsCache', analyticsCacheSchema);

module.exports = {
  ReportTemplate,
  ReportInstance,
  DashboardWidget,
  ExportFile,
  AnalyticsCache
};
