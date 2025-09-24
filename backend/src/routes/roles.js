const express = require('express');
const router = express.Router();
const { Role } = require('../models/core');
const User = require('../models/user');
const { authMiddleware } = require('../middleware/auth');
const { requirePermissions, PERMISSIONS } = require('../middleware/rbac');
const { body, validationResult } = require('express-validator');

// Get all roles
router.get('/', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const roles = await Role.find();
    
    res.json({
      success: true,
      data: roles
    });
  } catch (error) {
    console.error('Error fetching roles:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Create new role (admin only)
router.post('/', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), [
  body('name').notEmpty().trim().isLength({ min: 2, max: 50 }),
  body('permissions').isArray()
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

    const { name, permissions } = req.body;

    // Check if role already exists
    const existingRole = await Role.findOne({ name: name.toLowerCase() });
    
    if (existingRole) {
      return res.status(409).json({
        success: false,
        error: {
          code: 'E_ROLE_EXISTS',
          message: 'Role with this name already exists'
        }
      });
    }

    // Validate permissions
    const validPermissions = [
      'sell', 'redeem', 'refund', 'reprint', 'manual_discount',
      'shift_open', 'shift_close', 'settings_write', 'employee_manage',
      'reports_view', 'admin_access'
    ];

    const invalidPermissions = permissions.filter(p => !validPermissions.includes(p));
    if (invalidPermissions.length > 0) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_INVALID_PERMISSIONS',
          message: `Invalid permissions: ${invalidPermissions.join(', ')}`
        }
      });
    }

    const role = new Role({
      name: name.toLowerCase(),
      permissions
    });

    await role.save();

    res.status(201).json({
      success: true,
      data: role
    });
  } catch (error) {
    console.error('Error creating role:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Update role (admin only)
router.patch('/:roleId', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), [
  body('name').optional().notEmpty().trim(),
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

    const { roleId } = req.params;
    const updates = req.body;

    const role = await Role.findById(roleId);

    if (!role) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_ROLE_NOT_FOUND',
          message: 'Role not found'
        }
      });
    }

    // Validate permissions if provided
    if (updates.permissions) {
      const validPermissions = [
        'sell', 'redeem', 'refund', 'reprint', 'manual_discount',
        'shift_open', 'shift_close', 'settings_write', 'employee_manage',
        'reports_view', 'admin_access'
      ];

      const invalidPermissions = updates.permissions.filter(p => !validPermissions.includes(p));
      if (invalidPermissions.length > 0) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'E_INVALID_PERMISSIONS',
            message: `Invalid permissions: ${invalidPermissions.join(', ')}`
          }
        });
      }
    }

    const updatedRole = await Role.findByIdAndUpdate(
      roleId,
      { ...updates, updated_at: new Date() },
      { new: true, runValidators: true }
    );

    res.json({
      success: true,
      data: updatedRole
    });
  } catch (error) {
    console.error('Error updating role:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Delete role (admin only)
router.delete('/:roleId', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const { roleId } = req.params;

    const role = await Role.findById(roleId);

    if (!role) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_ROLE_NOT_FOUND',
          message: 'Role not found'
        }
      });
    }

    // Check if any users are using this role
    const usersWithRole = await User.find({ 
      roles: roleId
    });

    if (usersWithRole.length > 0) {
      return res.status(409).json({
        success: false,
        error: {
          code: 'E_ROLE_IN_USE',
          message: `Cannot delete role. ${usersWithRole.length} user(s) are using this role.`
        }
      });
    }

    await Role.findByIdAndDelete(roleId);

    res.json({
      success: true,
      message: 'Role deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting role:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get role details
router.get('/:roleId', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const { roleId } = req.params;

    const role = await Role.findById(roleId);

    if (!role) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_ROLE_NOT_FOUND',
          message: 'Role not found'
        }
      });
    }

    // Get users with this role
    const usersWithRole = await User.find({ 
      roles: roleId
    }).select('name email is_active');

    res.json({
      success: true,
      data: {
        role,
        users: usersWithRole
      }
    });
  } catch (error) {
    console.error('Error fetching role details:', error);
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