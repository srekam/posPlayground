const mongoose = require('mongoose');

// Package Schema
const packageSchema = new mongoose.Schema({
  package_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
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
  name: {
    type: String,
    required: true,
    trim: true
  },
  type: {
    type: String,
    required: true,
    enum: ['single', 'multi', 'timepass', 'credit', 'bundle']
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  tax_profile: {
    type: String,
    default: 'standard'
  },
  quota_or_minutes: {
    type: Number,
    required: function() {
      return ['multi', 'timepass', 'credit'].includes(this.type);
    }
  },
  allowed_devices: [{
    type: String,
    enum: ['POS', 'GATE', 'KIOSK']
  }],
  visible_on: [{
    type: String,
    enum: ['POS', 'KIOSK'],
    default: ['POS']
  }],
  active_window: {
    from: String, // HH:MM format
    to: String    // HH:MM format
  },
  active: {
    type: Boolean,
    default: true
  },
  description: String,
  image_url: String,
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

// Pricing Rule Schema
const pricingRuleSchema = new mongoose.Schema({
  rule_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  scope: {
    type: String,
    required: true,
    enum: ['store', 'tenant']
  },
  scope_id: {
    type: String,
    required: true // store_id or tenant_id
  },
  kind: {
    type: String,
    required: true,
    enum: [
      'line_percent', 'line_amount', 'cart_percent', 'cart_amount',
      'promo_code', 'bundle', 'time_of_day'
    ]
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: String,
  params: {
    // Flexible object for different rule types
    percentage: Number,
    amount: Number,
    promo_code: String,
    bundle_items: [{
      package_id: String,
      quantity: Number
    }],
    time_from: String, // HH:MM
    time_to: String,   // HH:MM
    days_of_week: [Number], // 0-6 (Sunday-Saturday)
    min_quantity: Number,
    max_quantity: Number,
    target_packages: [String] // package_ids
  },
  active_window: {
    from: Date,
    to: Date
  },
  priority: {
    type: Number,
    default: 0
  },
  active: {
    type: Boolean,
    default: true
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

// Access Zone Schema
const accessZoneSchema = new mongoose.Schema({
  zone_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
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
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: String,
  devices: [{
    type: String,
    ref: 'Device'
  }],
  packages: [{
    type: String,
    ref: 'Package'
  }],
  active: {
    type: Boolean,
    default: true
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

// Indexes
packageSchema.index({ tenant_id: 1, store_id: 1 });
packageSchema.index({ package_id: 1 });
packageSchema.index({ active: 1 });
packageSchema.index({ type: 1 });

pricingRuleSchema.index({ scope: 1, scope_id: 1 });
pricingRuleSchema.index({ rule_id: 1 });
pricingRuleSchema.index({ active: 1, priority: -1 });
pricingRuleSchema.index({ active_window: 1 });

accessZoneSchema.index({ tenant_id: 1, store_id: 1 });
accessZoneSchema.index({ zone_id: 1 });

// Virtual for formatted price
packageSchema.virtual('price_text').get(function() {
  return `฿${this.price.toFixed(0)}`;
});

// Methods
packageSchema.methods.isActive = function() {
  if (!this.active) return false;
  
  if (this.active_window && this.active_window.from && this.active_window.to) {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    const fromTime = this.parseTime(this.active_window.from);
    const toTime = this.parseTime(this.active_window.to);
    
    return currentTime >= fromTime && currentTime <= toTime;
  }
  
  return true;
};

packageSchema.methods.parseTime = function(timeStr) {
  const [hours, minutes] = timeStr.split(':').map(Number);
  return hours * 60 + minutes;
};

// Create models
const Package = mongoose.model('Package', packageSchema);
const PricingRule = mongoose.model('PricingRule', pricingRuleSchema);
const AccessZone = mongoose.model('AccessZone', accessZoneSchema);

module.exports = {
  Package,
  PricingRule,
  AccessZone
};
