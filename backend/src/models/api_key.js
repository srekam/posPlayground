const mongoose = require('mongoose');

const apiKeySchema = new mongoose.Schema({
  api_key: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  device_id: {
    type: String,
    required: true,
    index: true
  },
  device_name: {
    type: String,
    required: true
  },
  permissions: [{
    type: String,
    enum: [
      'read', 'write', 'delete',
      'can_sell', 'can_redeem', 'can_refund',
      'can_access_reports', 'can_manage_users', 'can_manage_devices',
      'can_admin', 'can_manage_settings'
    ]
  }],
  expires_at: {
    type: Date,
    default: null
  },
  last_used: {
    type: Date,
    default: null
  },
  created_by: {
    type: String,
    required: true
  },
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
  }
}, {
  timestamps: true
});

// Index for efficient queries
apiKeySchema.index({ device_id: 1, tenant_id: 1 });
apiKeySchema.index({ expires_at: 1 });

// Virtual for checking if API key is expired
apiKeySchema.virtual('is_expired').get(function() {
  return this.expires_at && new Date() > this.expires_at;
});

// Virtual for checking if API key is valid
apiKeySchema.virtual('is_valid').get(function() {
  return this.is_active && !this.is_expired;
});

// Method to update last used timestamp
apiKeySchema.methods.updateLastUsed = function() {
  this.last_used = new Date();
  return this.save();
};

// Static method to find valid API key
apiKeySchema.statics.findValidApiKey = function(apiKey) {
  return this.findOne({
    api_key: apiKey,
    is_active: true,
    $or: [
      { expires_at: null },
      { expires_at: { $gt: new Date() } }
    ]
  });
};

// Pre-save middleware to hash API key (optional - for extra security)
apiKeySchema.pre('save', function(next) {
  // In a production environment, you might want to hash the API key
  // For now, we'll store it as plain text for simplicity
  next();
});

module.exports = mongoose.model('ApiKey', apiKeySchema);
