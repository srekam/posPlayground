const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

// Tenant Schema
const tenantSchema = new mongoose.Schema({
  tenant_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  legal_name: {
    type: String,
    required: true,
    trim: true
  },
  timezone: {
    type: String,
    default: 'Asia/Bangkok'
  },
  currency: {
    type: String,
    default: 'THB',
    enum: ['THB', 'USD', 'EUR']
  },
  billing_plan: {
    type: String,
    enum: ['free', 'basic', 'premium', 'enterprise'],
    default: 'free'
  },
  status: {
    type: String,
    enum: ['active', 'suspended', 'cancelled'],
    default: 'active'
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

// Store Schema
const storeSchema = new mongoose.Schema({
  store_id: {
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
  name: {
    type: String,
    required: true,
    trim: true
  },
  address: {
    street: String,
    city: String,
    state: String,
    postal_code: String,
    country: String
  },
  timezone: {
    type: String,
    default: 'Asia/Bangkok'
  },
  tax_id: String,
  receipt_header: {
    type: String,
    default: 'PlayPark\nIndoor Playground'
  },
  receipt_footer: {
    type: String,
    default: 'Thank you for visiting!'
  },
  logo_ref: String,
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

// Device Schema
const deviceSchema = new mongoose.Schema({
  device_id: {
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
  type: {
    type: String,
    required: true,
    enum: ['POS', 'GATE', 'KIOSK', 'ADMIN']
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  registered_at: {
    type: Date,
    default: Date.now
  },
  registered_by: String,
  status: {
    type: String,
    enum: ['active', 'suspended', 'revoked'],
    default: 'active'
  },
  device_token_hash: {
    type: String,
    required: true
  },
  capabilities: {
    can_sell: { type: Boolean, default: false },
    can_redeem: { type: Boolean, default: false },
    kiosk_mode: { type: Boolean, default: false },
    offline_cap: { type: Boolean, default: false }
  },
  notes: String,
  last_seen: {
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

// Employee Schema
const employeeSchema = new mongoose.Schema({
  employee_id: {
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
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  pin_hash: {
    type: String,
    required: true
  },
  status: {
    type: String,
    enum: ['active', 'suspended', 'inactive'],
    default: 'active'
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

// Role Schema
const roleSchema = new mongoose.Schema({
  role_id: {
    type: String,
    required: true,
    unique: true,
    default: () => require('ulid').ulid()
  },
  name: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  permissions: [{
    type: String,
    enum: [
      'sell', 'redeem', 'refund', 'reprint', 'manual_discount',
      'shift_open', 'shift_close', 'settings_write', 'employee_manage',
      'reports_view', 'admin_access'
    ]
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

// Membership Schema (Employee-Store-Role relationship)
const membershipSchema = new mongoose.Schema({
  employee_id: {
    type: String,
    required: true,
    ref: 'Employee'
  },
  store_id: {
    type: String,
    required: true,
    ref: 'Store'
  },
  roles: [{
    type: String,
    ref: 'Role'
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

// Pre-save middleware for password hashing
employeeSchema.pre('save', async function(next) {
  if (!this.isModified('pin_hash')) return next();
  
  try {
    const salt = await bcrypt.genSalt(parseInt(process.env.BCRYPT_ROUNDS) || 12);
    this.pin_hash = await bcrypt.hash(this.pin_hash, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Indexes for better performance
tenantSchema.index({ tenant_id: 1 });
storeSchema.index({ tenant_id: 1 });
storeSchema.index({ store_id: 1 });
deviceSchema.index({ tenant_id: 1, store_id: 1 });
deviceSchema.index({ device_id: 1 });
deviceSchema.index({ device_token_hash: 1 });
employeeSchema.index({ tenant_id: 1 });
employeeSchema.index({ email: 1 });
membershipSchema.index({ employee_id: 1, store_id: 1 });

// Create models
const Tenant = mongoose.model('Tenant', tenantSchema);
const Store = mongoose.model('Store', storeSchema);
const Device = mongoose.model('Device', deviceSchema);
const Employee = mongoose.model('Employee', employeeSchema);
const Role = mongoose.model('Role', roleSchema);
const Membership = mongoose.model('Membership', membershipSchema);

module.exports = {
  Tenant,
  Store,
  Device,
  Employee,
  Role,
  Membership
};
