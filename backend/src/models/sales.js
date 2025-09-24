const mongoose = require('mongoose');

// Sale Schema
const saleSchema = new mongoose.Schema({
  sale_id: {
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
  device_id: {
    type: String,
    required: true,
    ref: 'Device'
  },
  cashier_id: {
    type: String,
    required: true,
    ref: 'Employee'
  },
  shift_id: {
    type: String,
    ref: 'Shift'
  },
  items: [{
    package_id: {
      type: String,
      required: true,
      ref: 'Package'
    },
    package_name: String,
    quantity: {
      type: Number,
      required: true,
      min: 1
    },
    unit_price: {
      type: Number,
      required: true,
      min: 0
    },
    line_total: {
      type: Number,
      required: true,
      min: 0
    },
    discounts: [{
      type: {
        type: String,
        enum: ['percent', 'amount', 'promo_code']
      },
      value: Number,
      description: String,
      rule_id: String
    }]
  }],
  subtotal: {
    type: Number,
    required: true,
    min: 0
  },
  discount_total: {
    type: Number,
    default: 0,
    min: 0
  },
  tax_total: {
    type: Number,
    default: 0,
    min: 0
  },
  grand_total: {
    type: Number,
    required: true,
    min: 0
  },
  payment_method: {
    type: String,
    required: true,
    enum: ['cash', 'qr', 'card', 'other']
  },
  amount_tendered: {
    type: Number,
    min: 0
  },
  change: {
    type: Number,
    default: 0,
    min: 0
  },
  reference: {
    type: String,
    unique: true,
    sparse: true
  },
  notes: String,
  status: {
    type: String,
    enum: ['completed', 'cancelled', 'refunded'],
    default: 'completed'
  },
  timestamp: {
    type: Date,
    default: Date.now
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

// Shift Schema
const shiftSchema = new mongoose.Schema({
  shift_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  store_id: {
    type: String,
    required: true,
    ref: 'Store'
  },
  device_id: {
    type: String,
    required: true,
    ref: 'Device'
  },
  opened_by: {
    type: String,
    required: true,
    ref: 'Employee'
  },
  open_at: {
    type: Date,
    required: true,
    default: Date.now
  },
  cash_open: {
    type: Number,
    required: true,
    min: 0
  },
  closed_by: {
    type: String,
    ref: 'Employee'
  },
  close_at: {
    type: Date
  },
  cash_expected: {
    type: Number,
    min: 0
  },
  cash_counted: {
    type: Number,
    min: 0
  },
  cash_diff: {
    type: Number,
    default: 0
  },
  totals: {
    sales: {
      count: { type: Number, default: 0 },
      amount: { type: Number, default: 0 }
    },
    refunds: {
      count: { type: Number, default: 0 },
      amount: { type: Number, default: 0 }
    },
    reprints: {
      count: { type: Number, default: 0 }
    },
    discounts: {
      amount: { type: Number, default: 0 }
    },
    taxes: {
      amount: { type: Number, default: 0 }
    }
  },
  status: {
    type: String,
    enum: ['open', 'closed'],
    default: 'open'
  },
  notes: String,
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

// Refund Schema
const refundSchema = new mongoose.Schema({
  refund_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  sale_id: {
    type: String,
    required: true,
    ref: 'Sale'
  },
  ticket_ids: [{
    type: String,
    ref: 'Ticket'
  }],
  amount: {
    type: Number,
    required: true,
    min: 0
  },
  method: {
    type: String,
    required: true,
    enum: ['cash', 'qr', 'card', 'other']
  },
  requested_by: {
    type: String,
    required: true,
    ref: 'Employee'
  },
  approved_by: {
    type: String,
    ref: 'Employee'
  },
  reason_code: {
    type: String,
    required: true
  },
  reason_text: String,
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected', 'completed'],
    default: 'pending'
  },
  timestamp: {
    type: Date,
    default: Date.now
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

// Reprint Schema
const reprintSchema = new mongoose.Schema({
  reprint_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  ticket_id: {
    type: String,
    required: true,
    ref: 'Ticket'
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  requested_by: {
    type: String,
    required: true,
    ref: 'Employee'
  },
  approved_by: {
    type: String,
    ref: 'Employee'
  },
  reason_code: {
    type: String,
    required: true
  },
  reason_text: String,
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected', 'completed'],
    default: 'pending'
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
saleSchema.index({ sale_id: 1 });
saleSchema.index({ tenant_id: 1, store_id: 1 });
saleSchema.index({ device_id: 1 });
saleSchema.index({ cashier_id: 1 });
saleSchema.index({ shift_id: 1 });
saleSchema.index({ timestamp: 1 });
saleSchema.index({ reference: 1 });

shiftSchema.index({ shift_id: 1 });
shiftSchema.index({ store_id: 1 });
shiftSchema.index({ device_id: 1 });
shiftSchema.index({ status: 1 });
shiftSchema.index({ open_at: 1 });

refundSchema.index({ refund_id: 1 });
refundSchema.index({ sale_id: 1 });
refundSchema.index({ requested_by: 1 });
refundSchema.index({ status: 1 });
refundSchema.index({ timestamp: 1 });

reprintSchema.index({ reprint_id: 1 });
reprintSchema.index({ ticket_id: 1 });
reprintSchema.index({ requested_by: 1 });
reprintSchema.index({ status: 1 });
reprintSchema.index({ timestamp: 1 });

// Virtual for formatted amounts
saleSchema.virtual('subtotal_text').get(function() {
  return `฿${this.subtotal.toFixed(0)}`;
});

saleSchema.virtual('grand_total_text').get(function() {
  return `฿${this.grand_total.toFixed(0)}`;
});

saleSchema.virtual('discount_total_text').get(function() {
  return `฿${this.discount_total.toFixed(0)}`;
});

// Methods
shiftSchema.methods.calculateExpectedCash = function() {
  return this.cash_open + this.totals.sales.amount - this.totals.refunds.amount;
};

shiftSchema.methods.closeShift = function(cashierId, cashCounted) {
  this.closed_by = cashierId;
  this.close_at = new Date();
  this.cash_counted = cashCounted;
  this.cash_expected = this.calculateExpectedCash();
  this.cash_diff = this.cash_counted - this.cash_expected;
  this.status = 'closed';
};

// Pre-save middleware
saleSchema.pre('save', function(next) {
  if (this.isNew && !this.reference) {
    // Generate reference number
    const date = new Date();
    const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
    const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    this.reference = `QR-${dateStr}${random}`;
  }
  next();
});

// Create models
const Sale = mongoose.model('Sale', saleSchema);
const Shift = mongoose.model('Shift', shiftSchema);
const Refund = mongoose.model('Refund', refundSchema);
const Reprint = mongoose.model('Reprint', reprintSchema);

module.exports = {
  Sale,
  Shift,
  Refund,
  Reprint
};
