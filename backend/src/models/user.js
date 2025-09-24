const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
    index: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  roles: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Role'
  }],
  permissions: [{
    type: String,
    enum: [
      'read', 'write', 'delete',
      'can_sell', 'can_redeem', 'can_refund',
      'can_access_reports', 'can_manage_users', 'can_manage_devices',
      'can_admin', 'can_manage_settings'
    ]
  }],
  tenant_id: {
    type: String,
    required: true,
    index: true
  },
  store_id: {
    type: String,
    index: true
  },
  is_active: {
    type: Boolean,
    default: true
  },
  is_owner: {
    type: Boolean,
    default: false
  },
  last_login: {
    type: Date
  },
  login_attempts: {
    type: Number,
    default: 0
  },
  lock_until: {
    type: Date
  },
  profile: {
    avatar: String,
    phone: String,
    address: {
      street: String,
      city: String,
      state: String,
      zip: String,
      country: String
    },
    preferences: {
      language: {
        type: String,
        default: 'en'
      },
      timezone: {
        type: String,
        default: 'UTC'
      },
      theme: {
        type: String,
        enum: ['light', 'dark', 'auto'],
        default: 'auto'
      }
    }
  },
  settings: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true
});

// Index for efficient queries
userSchema.index({ email: 1, tenant_id: 1 });
userSchema.index({ tenant_id: 1, is_active: 1 });
userSchema.index({ store_id: 1, is_active: 1 });

// Virtual for account lock status
userSchema.virtual('is_locked').get(function() {
  return !!(this.lock_until && this.lock_until > Date.now());
});

// Virtual for full permissions (roles + direct permissions)
userSchema.virtual('all_permissions').get(function() {
  const rolePermissions = this.roles.reduce((perms, role) => {
    return perms.concat(role.permissions || []);
  }, []);
  
  return [...new Set([...this.permissions, ...rolePermissions])];
});

// Pre-save middleware to hash password
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(parseInt(process.env.BCRYPT_ROUNDS) || 12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to compare password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Method to check if user has permission
userSchema.methods.hasPermission = function(permission) {
  if (this.is_owner) return true; // Owners have all permissions
  return this.all_permissions.includes(permission);
};

// Method to check if user has any of the given permissions
userSchema.methods.hasAnyPermission = function(permissions) {
  if (this.is_owner) return true; // Owners have all permissions
  return permissions.some(permission => this.all_permissions.includes(permission));
};

// Method to check if user has all of the given permissions
userSchema.methods.hasAllPermissions = function(permissions) {
  if (this.is_owner) return true; // Owners have all permissions
  return permissions.every(permission => this.all_permissions.includes(permission));
};

// Method to check if user has role
userSchema.methods.hasRole = function(roleName) {
  return this.roles.some(role => role.name === roleName);
};

// Method to increment login attempts
userSchema.methods.incLoginAttempts = function() {
  // If we have a previous lock that has expired, restart at 1
  if (this.lock_until && this.lock_until < Date.now()) {
    return this.updateOne({
      $unset: { lock_until: 1 },
      $set: { login_attempts: 1 }
    });
  }
  
  const updates = { $inc: { login_attempts: 1 } };
  
  // Lock account after 5 failed attempts for 2 hours
  if (this.login_attempts + 1 >= 5 && !this.is_locked) {
    updates.$set = { lock_until: Date.now() + 2 * 60 * 60 * 1000 }; // 2 hours
  }
  
  return this.updateOne(updates);
};

// Method to reset login attempts
userSchema.methods.resetLoginAttempts = function() {
  return this.updateOne({
    $unset: { login_attempts: 1, lock_until: 1 },
    $set: { last_login: new Date() }
  });
};

// Static method to find users by tenant
userSchema.statics.findByTenant = function(tenantId) {
  return this.find({ tenant_id: tenantId, is_active: true });
};

// Static method to find users by store
userSchema.statics.findByStore = function(storeId) {
  return this.find({ store_id: storeId, is_active: true });
};

// Static method to find owners
userSchema.statics.findOwners = function(tenantId = null) {
  const query = { is_owner: true, is_active: true };
  if (tenantId) query.tenant_id = tenantId;
  return this.find(query);
};

module.exports = mongoose.model('User', userSchema);
