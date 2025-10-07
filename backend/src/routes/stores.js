const express = require('express');
const router = express.Router();
const { Store } = require('../models/core');
const { authMiddleware } = require('../middleware/auth');
const { requirePermissions, PERMISSIONS } = require('../middleware/rbac');
const { body, validationResult } = require('express-validator');

// Get all stores
router.get('/', authMiddleware, requirePermissions([PERMISSIONS.ADMIN]), async (req, res) => {
  try {
    const stores = await Store.find({ tenant_id: req.tenantId || 'default' })
      .sort({ created_at: -1 });

    res.json({
      success: true,
      data: stores
    });
  } catch (error) {
    console.error('Error fetching stores:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get store by ID
router.get('/:id', authMiddleware, requirePermissions([PERMISSIONS.ADMIN]), async (req, res) => {
  try {
    const store = await Store.findOne({ 
      store_id: req.params.id,
      tenant_id: req.tenantId || 'default'
    });

    if (!store) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Store not found'
        }
      });
    }

    res.json({
      success: true,
      data: store
    });
  } catch (error) {
    console.error('Error fetching store:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Create new store
router.post('/', [
  authMiddleware,
  requirePermissions([PERMISSIONS.ADMIN]),
  body('name').notEmpty().withMessage('Store name is required'),
  body('address.street').optional().isString(),
  body('address.city').optional().isString(),
  body('address.state').optional().isString(),
  body('address.postal_code').optional().isString(),
  body('address.country').optional().isString(),
  body('timezone').optional().isString(),
  body('tax_id').optional().isString(),
  body('receipt_header').optional().isString(),
  body('receipt_footer').optional().isString(),
  body('logo_ref').optional().isString()
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

    const storeData = {
      ...req.body,
      tenant_id: req.tenantId || 'default'
    };

    const store = new Store(storeData);
    await store.save();

    res.status(201).json({
      success: true,
      data: store
    });
  } catch (error) {
    console.error('Error creating store:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Update store
router.put('/:id', [
  authMiddleware,
  requirePermissions([PERMISSIONS.ADMIN]),
  body('name').optional().notEmpty().withMessage('Store name cannot be empty'),
  body('address.street').optional().isString(),
  body('address.city').optional().isString(),
  body('address.state').optional().isString(),
  body('address.postal_code').optional().isString(),
  body('address.country').optional().isString(),
  body('timezone').optional().isString(),
  body('tax_id').optional().isString(),
  body('receipt_header').optional().isString(),
  body('receipt_footer').optional().isString(),
  body('logo_ref').optional().isString(),
  body('active').optional().isBoolean()
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

    const store = await Store.findOneAndUpdate(
      { 
        store_id: req.params.id,
        tenant_id: req.tenantId || 'default'
      },
      { ...req.body, updated_at: new Date() },
      { new: true, runValidators: true }
    );

    if (!store) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Store not found'
        }
      });
    }

    res.json({
      success: true,
      data: store
    });
  } catch (error) {
    console.error('Error updating store:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Delete store
router.delete('/:id', authMiddleware, requirePermissions([PERMISSIONS.ADMIN]), async (req, res) => {
  try {
    const store = await Store.findOneAndDelete({
      store_id: req.params.id,
      tenant_id: req.tenantId || 'default'
    });

    if (!store) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Store not found'
        }
      });
    }

    res.json({
      success: true,
      message: 'Store deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting store:', error);
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
