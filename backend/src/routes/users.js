const express = require('express');
const router = express.Router();
const User = require('../models/user');
const { Role } = require('../models/core');
const { authMiddleware } = require('../middleware/auth');
const { requirePermissions, requireOwner, PERMISSIONS } = require('../middleware/rbac');
const { body, validationResult } = require('express-validator');

// Get all users (admin only)
router.get('/', authMiddleware, requirePermissions([PERMISSIONS.ADMIN]), async (req, res) => {
  try {
    const users = await User.find({ tenant_id: req.tenantId || 'default' })
      .populate('roles')
      .select('-password')
      .sort({ created_at: -1 });

    const userList = users.map(user => ({
      id: user._id,
      email: user.email,
      name: user.name,
      roles: user.roles,
      permissions: user.all_permissions,
      is_active: user.is_active,
      is_owner: user.is_owner,
      last_login: user.last_login,
      created_at: user.created_at,
      profile: user.profile
    }));

    res.json({
      success: true,
      data: userList
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get current user profile
router.get('/me', authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.user.id)
      .populate('roles')
      .select('-password');

    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_USER_NOT_FOUND',
          message: 'User not found'
        }
      });
    }

    res.json({
      success: true,
      data: {
        id: user._id,
        email: user.email,
        name: user.name,
        roles: user.roles,
        permissions: user.all_permissions,
        is_active: user.is_active,
        is_owner: user.is_owner,
        last_login: user.last_login,
        created_at: user.created_at,
        profile: user.profile,
        settings: user.settings
      }
    });
  } catch (error) {
    console.error('Error fetching user profile:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Create new user (admin only)
router.post('/', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 6 }),
  body('name').notEmpty().trim(),
  body('roles').isArray(),
  body('permissions').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_VALIDATION',
          message: 'Validation failed',
          details: errors.array()
        }
      });
    }

    const { email, password, name, roles = [], permissions = [] } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({
        success: false,
        error: {
          code: 'E_USER_EXISTS',
          message: 'User with this email already exists'
        }
      });
    }

    // Validate roles exist
    const validRoles = await Role.find({ 
      _id: { $in: roles },
      tenant_id: req.tenantId || 'default'
    });

    if (validRoles.length !== roles.length) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_INVALID_ROLES',
          message: 'One or more roles are invalid'
        }
      });
    }

    const user = new User({
      email,
      password,
      name,
      roles,
      permissions,
      tenant_id: req.tenantId || 'default',
      created_by: req.user.id
    });

    await user.save();

    // Return user without password
    const userResponse = await User.findById(user._id)
      .populate('roles')
      .select('-password');

    res.status(201).json({
      success: true,
      data: {
        id: userResponse._id,
        email: userResponse.email,
        name: userResponse.name,
        roles: userResponse.roles,
        permissions: userResponse.all_permissions,
        is_active: userResponse.is_active,
        created_at: userResponse.created_at
      }
    });
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Update user (admin or self)
router.patch('/:userId', authMiddleware, [
  body('name').optional().notEmpty().trim(),
  body('roles').optional().isArray(),
  body('permissions').optional().isArray(),
  body('is_active').optional().isBoolean(),
  body('profile').optional().isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_VALIDATION',
          message: 'Validation failed',
          details: errors.array()
        }
      });
    }

    const { userId } = req.params;
    const updates = req.body;
    const currentUser = await User.findById(req.user.id);

    // Check if user can update this profile
    const canUpdate = currentUser.is_owner || 
                     currentUser.hasPermission(PERMISSIONS.MANAGE_USERS) ||
                     currentUser._id.toString() === userId;

    if (!canUpdate) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'E_INSUFFICIENT_PERMISSIONS',
          message: 'You do not have permission to update this user'
        }
      });
    }

    // Non-admin users can only update their own profile and limited fields
    if (!currentUser.is_owner && !currentUser.hasPermission(PERMISSIONS.MANAGE_USERS)) {
      const allowedFields = ['name', 'profile'];
      const filteredUpdates = {};
      Object.keys(updates).forEach(key => {
        if (allowedFields.includes(key)) {
          filteredUpdates[key] = updates[key];
        }
      });
      Object.assign(updates, filteredUpdates);
    }

    // Validate roles if provided
    if (updates.roles) {
      const validRoles = await Role.find({ 
        _id: { $in: updates.roles },
        tenant_id: req.tenantId || 'default'
      });

      if (validRoles.length !== updates.roles.length) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'E_INVALID_ROLES',
            message: 'One or more roles are invalid'
          }
        });
      }
    }

    const user = await User.findByIdAndUpdate(
      userId,
      { ...updates, updated_by: req.user.id },
      { new: true, runValidators: true }
    ).populate('roles').select('-password');

    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_USER_NOT_FOUND',
          message: 'User not found'
        }
      });
    }

    res.json({
      success: true,
      data: {
        id: user._id,
        email: user.email,
        name: user.name,
        roles: user.roles,
        permissions: user.all_permissions,
        is_active: user.is_active,
        profile: user.profile,
        updated_at: user.updated_at
      }
    });
  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Delete user (admin only)
router.delete('/:userId', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const { userId } = req.params;

    // Prevent deleting yourself
    if (req.user.id === userId) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_CANNOT_DELETE_SELF',
          message: 'You cannot delete your own account'
        }
      });
    }

    const user = await User.findByIdAndDelete(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_USER_NOT_FOUND',
          message: 'User not found'
        }
      });
    }

    res.json({
      success: true,
      message: 'User deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Change password
router.patch('/:userId/password', authMiddleware, [
  body('currentPassword').notEmpty(),
  body('newPassword').isLength({ min: 6 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_VALIDATION',
          message: 'Validation failed',
          details: errors.array()
        }
      });
    }

    const { userId } = req.params;
    const { currentPassword, newPassword } = req.body;

    // Check if user can change this password
    const canChangePassword = req.user.id === userId || 
                             req.user.is_owner ||
                             req.user.hasPermission(PERMISSIONS.MANAGE_USERS);

    if (!canChangePassword) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'E_INSUFFICIENT_PERMISSIONS',
          message: 'You do not have permission to change this password'
        }
      });
    }

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_USER_NOT_FOUND',
          message: 'User not found'
        }
      });
    }

    // Verify current password (unless admin changing someone else's password)
    if (req.user.id === userId) {
      const isCurrentPasswordValid = await user.comparePassword(currentPassword);
      if (!isCurrentPasswordValid) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'E_INVALID_PASSWORD',
            message: 'Current password is incorrect'
          }
        });
      }
    }

    user.password = newPassword;
    await user.save();

    res.json({
      success: true,
      message: 'Password changed successfully'
    });
  } catch (error) {
    console.error('Error changing password:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get user roles
router.get('/:userId/roles', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const { userId } = req.params;
    
    const user = await User.findById(userId).populate('roles');
    if (!user) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_USER_NOT_FOUND',
          message: 'User not found'
        }
      });
    }

    res.json({
      success: true,
      data: {
        roles: user.roles,
        permissions: user.all_permissions
      }
    });
  } catch (error) {
    console.error('Error fetching user roles:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

module.exports = router;
