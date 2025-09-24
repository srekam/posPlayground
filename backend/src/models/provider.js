const mongoose = require('mongoose');
const { ulid } = require('ulid');

// Provider Metrics Schema (for daily aggregated metrics)
const providerMetricsSchema = new mongoose.Schema({
  date: {
    type: Date,
    required: true,
    unique: true
  },
  tenant_id: {
    type: String,
    ref: 'Tenant'
  },
  store_id: {
    type: String,
    ref: 'Store'
  },
  device_id: {
    type: String,
    ref: 'Device'
  },
  metrics: {
    // Fleet metrics
    tenants_active: { type: Number, default: 0 },
    stores_active: { type: Number, default: 0 },
    devices_online: { type: Number, default: 0 },
    devices_total: { type: Number, default: 0 },
    
    // Sales metrics
    sales_24h: { type: Number, default: 0 },
    sales_7d: { type: Number, default: 0 },
    sales_30d: { type: Number, default: 0 },
    redemptions_24h: { type: Number, default: 0 },
    redemptions_7d: { type: Number, default: 0 },
    refund_rate: { type: Number, default: 0 },
    reprint_rate: { type: Number, default: 0 },
    
    // Performance metrics
    sync_lag_p95: { type: Number, default: 0 },
    sync_lag_p99: { type: Number, default: 0 },
    uptime_percent: { type: Number, default: 100 },
    response_time_p95: { type: Number, default: 0 },
    error_rate: { type: Number, default: 0 },
    
    // Usage metrics
    api_calls_24h: { type: Number, default: 0 },
    api_calls_7d: { type: Number, default: 0 },
    webhook_calls_24h: { type: Number, default: 0 },
    webhook_success_rate: { type: Number, default: 100 },
    
    // Alert metrics
    incidents_open: { type: Number, default: 0 },
    critical_alerts: { type: Number, default: 0 },
    medium_alerts: { type: Number, default: 0 },
    low_alerts: { type: Number, default: 0 }
  },
  created_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Device Heartbeat Schema
const deviceHeartbeatSchema = new mongoose.Schema({
  device_id: {
    type: String,
    required: true,
    ref: 'Device'
  },
  tenant_id: {
    type: String,
    required: true,
    ref: 'Tenant'
  },
  store_id: {
    type: String,
    required: true,
    ref: 'Store'
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  status: {
    type: String,
    enum: ['online', 'offline', 'warning'],
    default: 'online'
  },
  data: {
    type: mongoose.Schema.Types.Mixed
  },
  created_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Provider Alert Schema
const providerAlertSchema = new mongoose.Schema({
  alert_id: {
    type: String,
    required: true,
    unique: true,
    default: () => ulid()
  },
  tenant_id: {
    type: String,
    ref: 'Tenant'
  },
  store_id: {
    type: String,
    ref: 'Store'
  },
  device_id: {
    type: String,
    ref: 'Device'
  },
  alert_type: {
    type: String,
    required: true,
    enum: ['device.offline', 'gate.fail_rate_high', 'sync.lag_high', 'risk.reprint_spike', 'risk.refund_spike']
  },
  severity: {
    type: String,
    required: true,
    enum: ['low', 'medium', 'high', 'critical'],
    default: 'medium'
  },
  status: {
    type: String,
    required: true,
    enum: ['open', 'acknowledged', 'resolved'],
    default: 'open'
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  first_seen: {
    type: Date,
    default: Date.now
  },
  last_seen: {
    type: Date,
    default: Date.now
  },
  acknowledged_at: Date,
  acknowledged_by: {
    type: String,
    ref: 'ProviderUser'
  },
  resolved_at: Date,
  resolved_by: {
    type: String,
    ref: 'ProviderUser'
  },
  resolution_reason: String,
  data: {
    type: mongoose.Schema.Types.Mixed
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

// Usage Counter Schema
const usageCounterSchema = new mongoose.Schema({
  tenant_id: {
    type: String,
    required: true,
    ref: 'Tenant'
  },
  month_key: {
    type: String,
    required: true // Format: YYYY-MM
  },
  api_calls_total: {
    type: Number,
    default: 0
  },
  webhook_calls_total: {
    type: Number,
    default: 0
  },
  storage_bytes: {
    type: Number,
    default: 0
  },
  devices_count: {
    type: Number,
    default: 0
  },
  stores_count: {
    type: Number,
    default: 0
  },
  overage_detected: {
    type: Boolean,
    default: false
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

// Indexes for better performance
providerMetricsSchema.index({ date: 1 }, { unique: true });
providerMetricsSchema.index({ tenant_id: 1, date: -1 });
providerMetricsSchema.index({ store_id: 1, date: -1 });
providerMetricsSchema.index({ device_id: 1, date: -1 });

deviceHeartbeatSchema.index({ device_id: 1, timestamp: -1 });
deviceHeartbeatSchema.index({ tenant_id: 1, timestamp: -1 });
deviceHeartbeatSchema.index({ timestamp: -1 });

providerAlertSchema.index({ alert_id: 1 }, { unique: true });
providerAlertSchema.index({ tenant_id: 1, status: 1 });
providerAlertSchema.index({ status: 1, severity: 1 });
providerAlertSchema.index({ first_seen: -1 });

usageCounterSchema.index({ tenant_id: 1, month_key: 1 }, { unique: true });
usageCounterSchema.index({ month_key: 1 });

// Create models
const ProviderMetrics = mongoose.model('ProviderMetrics', providerMetricsSchema);
const DeviceHeartbeat = mongoose.model('DeviceHeartbeat', deviceHeartbeatSchema);
const ProviderAlert = mongoose.model('ProviderAlert', providerAlertSchema);
const UsageCounter = mongoose.model('UsageCounter', usageCounterSchema);

module.exports = {
  ProviderMetrics,
  DeviceHeartbeat,
  ProviderAlert,
  UsageCounter
};
