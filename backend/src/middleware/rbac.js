const User = require('../models/user');
const { Role } = require('../models/core');
const ApiKey = require('../models/api_key');

/**
 * RBAC Middleware
 * Checks if the authenticated user/device has the required permissions
 */

// Permission-based access control
const requirePermissions = (requiredPermissions) => {
  return async (req, res, next) => {
    try {
      let user = null;
      let permissions = [];

      // Check if request is authenticated via JWT token
      if (req.user) {
        user = await User.findById(req.user.id).populate('roles');
        if (user) {
          permissions = user.all_permissions;
        }
      }
      // Check if request is authenticated via API key
      else if (req.headers['x-api-key']) {
        const apiKey = await ApiKey.findValidApiKey(req.headers['x-api-key']);
        if (apiKey) {
          permissions = apiKey.permissions;
          // Update last used timestamp
          await apiKey.updateLastUsed();
        }
      }

      if (!user && !req.headers['x-api-key']) {
        return res.status(401).json({
          success: false,
          error: {
            code: 'E_NO_AUTH',
            message: 'Authentication required'
          }
        });
      }

      // Check if user/device has required permissions
      const hasPermission = requiredPermissions.every(permission => 
        permissions.includes(permission)
      );

      if (!hasPermission) {
        return res.status(403).json({
          success: false,
          error: {
            code: 'E_INSUFFICIENT_PERMISSIONS',
            message: `Required permissions: ${requiredPermissions.join(', ')}`
          }
        });
      }

      // Add permissions to request for use in controllers
      req.permissions = permissions;
      req.authType = user ? 'user' : 'api_key';
      
      next();
    } catch (error) {
      console.error('RBAC middleware error:', error);
      res.status(500).json({
        success: false,
        error: {
          code: 'E_INTERNAL',
          message: 'Internal server error'
        }
      });
    }
  };
};

// Role-based access control
const requireRole = (requiredRole) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({
          success: false,
          error: {
            code: 'E_NO_AUTH',
            message: 'Authentication required'
          }
        });
      }

      const user = await User.findById(req.user.id).populate('roles');
      if (!user) {
        return res.status(401).json({
          success: false,
          error: {
            code: 'E_INVALID_USER',
            message: 'User not found'
          }
        });
      }

      const hasRole = user.roles.some(role => role.name === requiredRole);

      if (!hasRole && !user.is_owner) {
        return res.status(403).json({
          success: false,
          error: {
            code: 'E_INSUFFICIENT_ROLE',
            message: `Required role: ${requiredRole}`
          }
        });
      }

      next();
    } catch (error) {
      console.error('Role middleware error:', error);
      res.status(500).json({
        success: false,
        error: {
          code: 'E_INTERNAL',
          message: 'Internal server error'
        }
      });
    }
  };
};

// Owner-only access
const requireOwner = (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'E_NO_AUTH',
        message: 'Authentication required'
      }
    });
  }

  if (!req.user.is_owner) {
    return res.status(403).json({
      success: false,
      error: {
        code: 'E_OWNER_REQUIRED',
        message: 'Owner access required'
      }
    });
  }

  next();
};

// Tenant isolation middleware
const requireTenantAccess = (req, res, next) => {
  try {
    const requestedTenant = req.params.tenantId || req.body.tenant_id || req.query.tenant_id;
    
    if (!requestedTenant) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_TENANT_REQUIRED',
          message: 'Tenant ID is required'
        }
      });
    }

    // For now, allow all requests (in production, check user's tenant access)
    req.tenantId = requestedTenant;
    next();
  } catch (error) {
    console.error('Tenant access middleware error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
};

// Store isolation middleware
const requireStoreAccess = (req, res, next) => {
  try {
    const requestedStore = req.params.storeId || req.body.store_id || req.query.store_id;
    
    if (!requestedStore) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_STORE_REQUIRED',
          message: 'Store ID is required'
        }
      });
    }

    // For now, allow all requests (in production, check user's store access)
    req.storeId = requestedStore;
    next();
  } catch (error) {
    console.error('Store access middleware error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
};

// Permission constants
const PERMISSIONS = {
  READ: 'read',
  WRITE: 'write',
  DELETE: 'delete',
  SELL: 'can_sell',
  REDEEM: 'can_redeem',
  REFUND: 'can_refund',
  REPORTS: 'can_access_reports',
  MANAGE_USERS: 'can_manage_users',
  MANAGE_DEVICES: 'can_manage_devices',
  ADMIN: 'can_admin',
  MANAGE_SETTINGS: 'can_manage_settings'
};

// Role constants
const ROLES = {
  OWNER: 'owner',
  MANAGER: 'manager',
  CASHIER: 'cashier',
  GATE_OPERATOR: 'gate_operator',
  VIEWER: 'viewer'
};

// Permission combinations
const PERMISSION_SETS = {
  POS_OPERATIONS: [PERMISSIONS.READ, PERMISSIONS.SELL],
  GATE_OPERATIONS: [PERMISSIONS.READ, PERMISSIONS.REDEEM],
  MANAGEMENT: [PERMISSIONS.READ, PERMISSIONS.WRITE, PERMISSIONS.REPORTS],
  ADMIN: [PERMISSIONS.ADMIN, PERMISSIONS.MANAGE_USERS, PERMISSIONS.MANAGE_DEVICES]
};

module.exports = {
  requirePermissions,
  requireRole,
  requireOwner,
  requireTenantAccess,
  requireStoreAccess,
  PERMISSIONS,
  ROLES,
  PERMISSION_SETS
};
