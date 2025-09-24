const mongoose = require('mongoose');
const crypto = require('crypto');

// Ticket Schema
const ticketSchema = new mongoose.Schema({
  ticket_id: {
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
  sale_id: {
    type: String,
    required: true,
    ref: 'Sale'
  },
  package_id: {
    type: String,
    required: true,
    ref: 'Package'
  },
  short_code: {
    type: String,
    required: true,
    unique: true,
    uppercase: true
  },
  qr_token: {
    type: String,
    required: true,
    unique: true
  },
  signature: {
    type: String,
    required: true
  },
  type: {
    type: String,
    required: true,
    enum: ['single', 'multi', 'timepass', 'credit']
  },
  quota_or_minutes: {
    type: Number,
    required: true,
    min: 1
  },
  used: {
    type: Number,
    default: 0,
    min: 0
  },
  valid_from: {
    type: Date,
    required: true
  },
  valid_to: {
    type: Date,
    required: true
  },
  status: {
    type: String,
    enum: ['active', 'cancelled', 'refunded', 'expired'],
    default: 'active'
  },
  lot_no: {
    type: String,
    required: true
  },
  shift_id: {
    type: String,
    ref: 'Shift'
  },
  issued_by: {
    type: String,
    required: true,
    ref: 'Employee'
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  payment_method: {
    type: String,
    required: true,
    enum: ['cash', 'qr', 'card', 'other']
  },
  printed_count: {
    type: Number,
    default: 0,
    min: 0
  },
  device_binding: [{
    type: String,
    ref: 'Device'
  }],
  access_zones: [{
    type: String,
    ref: 'AccessZone'
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

// Redemption Schema
const redemptionSchema = new mongoose.Schema({
  redemption_id: {
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
  device_id: {
    type: String,
    required: true,
    ref: 'Device'
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  result: {
    type: String,
    required: true,
    enum: ['pass', 'fail']
  },
  reason: {
    type: String,
    enum: [
      'expired', 'duplicate_use', 'wrong_device', 'not_started',
      'exhausted', 'invalid_sig', 'cancelled', 'refunded'
    ]
  },
  metadata: {
    remaining_quota: Number,
    remaining_minutes: Number,
    device_location: String,
    scan_location: {
      lat: Number,
      lng: Number
    },
    notes: String
  },
  created_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Indexes
ticketSchema.index({ ticket_id: 1 });
ticketSchema.index({ qr_token: 1 });
ticketSchema.index({ short_code: 1 });
ticketSchema.index({ tenant_id: 1, store_id: 1 });
ticketSchema.index({ sale_id: 1 });
ticketSchema.index({ status: 1 });
ticketSchema.index({ valid_from: 1, valid_to: 1 });
ticketSchema.index({ lot_no: 1 });

redemptionSchema.index({ redemption_id: 1 });
redemptionSchema.index({ ticket_id: 1 });
redemptionSchema.index({ device_id: 1 });
redemptionSchema.index({ timestamp: 1 });
redemptionSchema.index({ result: 1 });

// Pre-save middleware for ticket generation
ticketSchema.pre('save', function(next) {
  if (this.isNew) {
    // Generate short code if not provided
    if (!this.short_code) {
      this.short_code = this.generateShortCode();
    }
    
    // Generate QR token if not provided
    if (!this.qr_token) {
      this.qr_token = this.generateQRToken();
    }
    
    // Generate signature if not provided
    if (!this.signature) {
      this.signature = this.generateSignature();
    }
  }
  next();
});

// Methods
ticketSchema.methods.generateShortCode = function() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 7; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

ticketSchema.methods.generateQRToken = function() {
  return require('ulid').ulid();
};

ticketSchema.methods.generateSignature = function() {
  const hmacSecret = process.env.HMAC_SECRET_V1 || 'default-secret';
  const data = `${this.ticket_id}:${this.qr_token}:${this.valid_from}:${this.valid_to}`;
  return crypto.createHmac('sha256', hmacSecret).update(data).digest('hex');
};

ticketSchema.methods.verifySignature = function() {
  const hmacSecret = process.env.HMAC_SECRET_V1 || 'default-secret';
  const data = `${this.ticket_id}:${this.qr_token}:${this.valid_from}:${this.valid_to}`;
  const expectedSignature = crypto.createHmac('sha256', hmacSecret).update(data).digest('hex');
  return this.signature === expectedSignature;
};

ticketSchema.methods.isValid = function() {
  const now = new Date();
  return this.status === 'active' && 
         now >= this.valid_from && 
         now <= this.valid_to &&
         this.used < this.quota_or_minutes;
};

ticketSchema.methods.canRedeem = function(deviceId) {
  if (!this.isValid()) return false;
  
  // Check device binding if specified
  if (this.device_binding && this.device_binding.length > 0) {
    return this.device_binding.includes(deviceId);
  }
  
  return true;
};

ticketSchema.methods.getRemainingQuota = function() {
  return Math.max(0, this.quota_or_minutes - this.used);
};

ticketSchema.methods.getRemainingMinutes = function() {
  if (this.type !== 'timepass') return null;
  return Math.max(0, this.quota_or_minutes - this.used);
};

// Virtual for QR payload
ticketSchema.virtual('qr_payload').get(function() {
  return JSON.stringify({
    ticket_id: this.ticket_id,
    qr_token: this.qr_token,
    short_code: this.short_code,
    type: this.type,
    valid_from: this.valid_from.toISOString(),
    valid_to: this.valid_to.toISOString(),
    sig: this.signature
  });
});

// Create models
const Ticket = mongoose.model('Ticket', ticketSchema);
const Redemption = mongoose.model('Redemption', redemptionSchema);

module.exports = {
  Ticket,
  Redemption
};
