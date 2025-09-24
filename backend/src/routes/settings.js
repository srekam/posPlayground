const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { Settings } = require('../models/audit');
const { authMiddleware, employeeAuthMiddleware } = require('../middleware/auth');
const { AuditLog } = require('../models/audit');

const router = express.Router();

// Get settings
router.get('/', [
  authMiddleware,
  employeeAuthMiddleware,
  query('scope').optional().isIn(['tenant', 'store']),
  query('scope_id').optional().isString()
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'E_VALIDATION',
        message: 'Validation failed',
        details: errors.array()
      });
    }

    const { scope = 'store', scope_id } = req.query;
    const id = scope_id || (scope === 'store' ? req.store_id : req.tenant_id);

    let settings = await Settings.findOne({
      scope: scope,
      scope_id: id
    });

    // Create default settings if not found
    if (!settings) {
      settings = new Settings({
        scope: scope,
        scope_id: id
      });
      await settings.save();
    }

    res.json({
      settings_id: settings.settings_id,
      scope: settings.scope,
      scope_id: settings.scope_id,
      features: settings.features,
      billing: settings.billing,
      payment_types: settings.payment_types,
      taxes: settings.taxes,
      receipt: settings.receipt,
      ticket_printers: settings.ticket_printers,
      access_zones: settings.access_zones,
      webhooks: settings.webhooks,
      updated_at: settings.updated_at
    });

  } catch (error) {
    next(error);
  }
});

// Update settings
router.put('/', [
  authMiddleware,
  employeeAuthMiddleware,
  body('scope').isIn(['tenant', 'store']).withMessage('Invalid scope'),
  body('scope_id').notEmpty().withMessage('Scope ID is required')
], async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'E_VALIDATION',
        message: 'Validation failed',
        details: errors.array()
      });
    }

    const { scope, scope_id, features, payment_types, taxes, receipt, ticket_printers, access_zones, webhooks } = req.body;

    let settings = await Settings.findOne({
      scope: scope,
      scope_id: scope_id
    });

    if (!settings) {
      settings = new Settings({
        scope: scope,
        scope_id: scope_id
      });
    }

    // Update fields
    if (features) settings.features = { ...settings.features, ...features };
    if (payment_types) settings.payment_types = { ...settings.payment_types, ...payment_types };
    if (taxes) settings.taxes = { ...settings.taxes, ...taxes };
    if (receipt) settings.receipt = { ...settings.receipt, ...receipt };
    if (ticket_printers) settings.ticket_printers = ticket_printers;
    if (access_zones) settings.access_zones = access_zones;
    if (webhooks) settings.webhooks = webhooks;

    await settings.save();

    // Log settings change
    await AuditLog.logEvent({
      event_type: 'settings.changed',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        scope: scope,
        scope_id: scope_id,
        changes: { features, payment_types, taxes, receipt, ticket_printers, access_zones, webhooks }
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id
    });

    res.json({
      settings_id: settings.settings_id,
      scope: settings.scope,
      scope_id: settings.scope_id,
      features: settings.features,
      payment_types: settings.payment_types,
      taxes: settings.taxes,
      receipt: settings.receipt,
      ticket_printers: settings.ticket_printers,
      access_zones: settings.access_zones,
      webhooks: settings.webhooks,
      updated_at: settings.updated_at
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
