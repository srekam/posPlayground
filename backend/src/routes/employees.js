const express = require('express');
const router = express.Router();
const { Employee } = require('../models/core');
const { authMiddleware } = require('../middleware/auth');
const { requirePermissions, PERMISSIONS } = require('../middleware/rbac');
const { body, validationResult } = require('express-validator');

// Get all employees
router.get('/', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const employees = await Employee.find({ tenant_id: req.tenantId || 'default' })
      .select('-pin_hash')
      .sort({ created_at: -1 });

    res.json({
      success: true,
      data: employees
    });
  } catch (error) {
    console.error('Error fetching employees:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get employee by ID
router.get('/:id', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const employee = await Employee.findOne({ 
      employee_id: req.params.id,
      tenant_id: req.tenantId || 'default'
    }).select('-pin_hash');

    if (!employee) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Employee not found'
        }
      });
    }

    res.json({
      success: true,
      data: employee
    });
  } catch (error) {
    console.error('Error fetching employee:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Create new employee
router.post('/', [
  authMiddleware,
  requirePermissions([PERMISSIONS.MANAGE_USERS]),
  body('name').notEmpty().withMessage('Employee name is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('pin').isLength({ min: 4, max: 6 }).withMessage('PIN must be 4-6 digits'),
  body('status').optional().isIn(['active', 'suspended', 'inactive'])
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

    // Check if email already exists
    const existingEmployee = await Employee.findOne({ 
      email: req.body.email,
      tenant_id: req.tenantId || 'default'
    });

    if (existingEmployee) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_DUPLICATE',
          message: 'Employee with this email already exists'
        }
      });
    }

    const employeeData = {
      name: req.body.name,
      email: req.body.email,
      pin_hash: req.body.pin, // Will be hashed by pre-save middleware
      status: req.body.status || 'active',
      tenant_id: req.tenantId || 'default'
    };

    const employee = new Employee(employeeData);
    await employee.save();

    // Return employee without pin_hash
    const responseEmployee = employee.toObject();
    delete responseEmployee.pin_hash;

    res.status(201).json({
      success: true,
      data: responseEmployee
    });
  } catch (error) {
    console.error('Error creating employee:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Update employee
router.put('/:id', [
  authMiddleware,
  requirePermissions([PERMISSIONS.MANAGE_USERS]),
  body('name').optional().notEmpty().withMessage('Employee name cannot be empty'),
  body('email').optional().isEmail().withMessage('Valid email is required'),
  body('pin').optional().isLength({ min: 4, max: 6 }).withMessage('PIN must be 4-6 digits'),
  body('status').optional().isIn(['active', 'suspended', 'inactive'])
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

    const updateData = { ...req.body };
    
    // If PIN is being updated, hash it
    if (updateData.pin) {
      updateData.pin_hash = updateData.pin;
      delete updateData.pin;
    }

    const employee = await Employee.findOneAndUpdate(
      { 
        employee_id: req.params.id,
        tenant_id: req.tenantId || 'default'
      },
      { ...updateData, updated_at: new Date() },
      { new: true, runValidators: true }
    ).select('-pin_hash');

    if (!employee) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Employee not found'
        }
      });
    }

    res.json({
      success: true,
      data: employee
    });
  } catch (error) {
    console.error('Error updating employee:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Delete employee
router.delete('/:id', authMiddleware, requirePermissions([PERMISSIONS.MANAGE_USERS]), async (req, res) => {
  try {
    const employee = await Employee.findOneAndDelete({
      employee_id: req.params.id,
      tenant_id: req.tenantId || 'default'
    });

    if (!employee) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Employee not found'
        }
      });
    }

    res.json({
      success: true,
      message: 'Employee deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting employee:', error);
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
