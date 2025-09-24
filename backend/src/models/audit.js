const mongoose = require('mongoose');

// Audit Log Schema
const auditLogSchema = new mongoose.Schema({
  audit_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  actor_id: {
    type: String,
    ref: 'Employee'
  },
  device_id: {
    type: String,
    ref: 'Device'
  },
  event_type: {
    type: String,
    required: true,
    enum: [
      'sale.created', 'sale.cancelled', 'sale.refunded',
      'ticket.issued', 'ticket.redeemed.pass', 'ticket.redeemed.fail',
      'ticket.reprinted', 'ticket.refunded',
      'shift.opened', 'shift.closed',
      'employee.login', 'employee.logout',
      'device.registered', 'device.suspended', 'device.revoked',
      'settings.changed', 'permission.granted', 'permission.revoked',
      'refund.requested', 'refund.approved', 'refund.rejected',
      'reprint.requested', 'reprint.approved', 'reprint.rejected'
    ]
  },
  payload: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  ip_address: String,
  user_agent: String,
  store_id: {
    type: String,
    ref: 'Store'
  },
  tenant_id: {
    type: String,
    ref: 'Tenant'
  },
  severity: {
    type: String,
    enum: ['low', 'medium', 'high', 'critical'],
    default: 'low'
  },
  created_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Settings Schema
const settingsSchema = new mongoose.Schema({
  settings_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  scope: {
    type: String,
    required: true,
    enum: ['tenant', 'store']
  },
  scope_id: {
    type: String,
    required: true
  },
  features: {
    kiosk: { type: Boolean, default: false },
    gate_binding: { type: Boolean, default: false },
    multi_price: { type: Boolean, default: false },
    webhooks: { type: Boolean, default: false },
    offline_sync: { type: Boolean, default: true }
  },
  billing: {
    plan: { type: String, enum: ['free', 'basic', 'premium', 'enterprise'], default: 'free' },
    trial_start: Date,
    trial_end: Date,
    subscription_start: Date,
    subscription_end: Date
  },
  payment_types: {
    cash: { enabled: { type: Boolean, default: true }, surcharge: { type: Number, default: 0 } },
    qr: { enabled: { type: Boolean, default: true }, surcharge: { type: Number, default: 0 } },
    card: { enabled: { type: Boolean, default: true }, surcharge: { type: Number, default: 0 } },
    other: { enabled: { type: Boolean, default: false }, surcharge: { type: Number, default: 0 } }
  },
  taxes: {
    inclusive: { type: Boolean, default: true },
    rates: [{
      name: String,
      rate: Number,
      default: { type: Boolean, default: false }
    }]
  },
  receipt: {
    header: { type: String, default: 'PlayPark\nIndoor Playground' },
    footer: { type: String, default: 'Thank you for visiting!' },
    logo_url: String,
    paper_width: { type: Number, default: 80 },
    template_blocks: [{
      type: String,
      content: String,
      position: { type: String, enum: ['header', 'footer', 'item', 'total'] }
    }]
  },
  ticket_printers: [{
    name: String,
    device_id: String,
    printer_profile: String,
    enabled: { type: Boolean, default: true }
  }],
  access_zones: [{
    zone_id: String,
    name: String,
    devices: [String],
    packages: [String]
  }],
  webhooks: [{
    url: String,
    events: [String],
    secret: String,
    enabled: { type: Boolean, default: true },
    retry_attempts: { type: Number, default: 3 },
    timeout: { type: Number, default: 5000 }
  }],
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

// Webhook Delivery Log Schema
const webhookDeliverySchema = new mongoose.Schema({
  delivery_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  webhook_id: String,
  event_type: {
    type: String,
    required: true
  },
  url: {
    type: String,
    required: true
  },
  payload: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  signature: String,
  status: {
    type: String,
    enum: ['pending', 'delivered', 'failed', 'retrying'],
    default: 'pending'
  },
  response_code: Number,
  response_body: String,
  attempt_count: {
    type: Number,
    default: 0
  },
  max_attempts: {
    type: Number,
    default: 3
  },
  next_retry_at: Date,
  delivered_at: Date,
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

// Outbox Event Schema (for offline sync)
const outboxEventSchema = new mongoose.Schema({
  event_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  device_id: {
    type: String,
    required: true,
    ref: 'Device'
  },
  operation_type: {
    type: String,
    required: true,
    enum: ['sale', 'redemption', 'audit', 'shift_open', 'shift_close']
  },
  operation_id: {
    type: String,
    required: true
  },
  payload: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'synced', 'failed'],
    default: 'pending'
  },
  sync_attempts: {
    type: Number,
    default: 0
  },
  last_sync_attempt: Date,
  synced_at: Date,
  error_message: String,
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

// Indexes
auditLogSchema.index({ audit_id: 1 });
auditLogSchema.index({ timestamp: 1 });
auditLogSchema.index({ actor_id: 1 });
auditLogSchema.index({ device_id: 1 });
auditLogSchema.index({ event_type: 1 });
auditLogSchema.index({ store_id: 1, timestamp: 1 });
auditLogSchema.index({ tenant_id: 1, timestamp: 1 });
auditLogSchema.index({ severity: 1 });

settingsSchema.index({ settings_id: 1 });
settingsSchema.index({ scope: 1, scope_id: 1 });

webhookDeliverySchema.index({ delivery_id: 1 });
webhookDeliverySchema.index({ webhook_id: 1 });
webhookDeliverySchema.index({ status: 1 });
webhookDeliverySchema.index({ next_retry_at: 1 });
webhookDeliverySchema.index({ created_at: 1 });

outboxEventSchema.index({ event_id: 1 });
outboxEventSchema.index({ device_id: 1 });
outboxEventSchema.index({ status: 1 });
outboxEventSchema.index({ operation_type: 1 });
outboxEventSchema.index({ created_at: 1 });

// Methods
auditLogSchema.statics.logEvent = function(eventData) {
  return this.create({
    ...eventData,
    timestamp: new Date()
  });
};

webhookDeliverySchema.methods.shouldRetry = function() {
  return this.status === 'failed' && 
         this.attempt_count < this.max_attempts &&
         (!this.next_retry_at || new Date() >= this.next_retry_at);
};

webhookDeliverySchema.methods.scheduleRetry = function() {
  const retryDelay = Math.pow(2, this.attempt_count) * 1000; // Exponential backoff
  this.next_retry_at = new Date(Date.now() + retryDelay);
  this.status = 'retrying';
};

// Create models
const AuditLog = mongoose.model('AuditLog', auditLogSchema);
const Settings = mongoose.model('Settings', settingsSchema);
const WebhookDelivery = mongoose.model('WebhookDelivery', webhookDeliverySchema);
const OutboxEvent = mongoose.model('OutboxEvent', outboxEventSchema);

module.exports = {
  AuditLog,
  Settings,
  WebhookDelivery,
  OutboxEvent
};
