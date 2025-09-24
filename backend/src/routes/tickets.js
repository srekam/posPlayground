const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { Ticket, Redemption } = require('../models/tickets');
const { authMiddleware, employeeAuthMiddleware } = require('../middleware/auth');
const { AuditLog } = require('../models/audit');
const logger = require('../utils/logger');

const router = express.Router();

// Get ticket by ID
router.get('/:ticket_id', [
  authMiddleware,
  employeeAuthMiddleware
], async (req, res, next) => {
  try {
    const { ticket_id } = req.params;

    const ticket = await Ticket.findOne({
      ticket_id: ticket_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!ticket) {
      return res.status(404).json({
        error: 'E_TICKET_NOT_FOUND',
        message: 'Ticket not found'
      });
    }

    // Get redemptions for this ticket
    const redemptions = await Redemption.find({ ticket_id: ticket_id })
      .sort({ timestamp: -1 });

    res.json({
      ticket_id: ticket.ticket_id,
      short_code: ticket.short_code,
      qr_token: ticket.qr_token,
      qr_payload: ticket.qr_payload,
      type: ticket.type,
      quota_or_minutes: ticket.quota_or_minutes,
      used: ticket.used,
      remaining: ticket.getRemainingQuota(),
      valid_from: ticket.valid_from,
      valid_to: ticket.valid_to,
      status: ticket.status,
      sale_id: ticket.sale_id,
      package_id: ticket.package_id,
      price: ticket.price,
      payment_method: ticket.payment_method,
      printed_count: ticket.printed_count,
      device_binding: ticket.device_binding,
      redemptions: redemptions.map(redemption => ({
        redemption_id: redemption.redemption_id,
        device_id: redemption.device_id,
        timestamp: redemption.timestamp,
        result: redemption.result,
        reason: redemption.reason,
        metadata: redemption.metadata
      })),
      created_at: ticket.created_at
    });

  } catch (error) {
    next(error);
  }
});

// Redeem ticket
router.post('/redeem', [
  authMiddleware,
  body('qr_token').notEmpty().withMessage('QR token is required'),
  body('device_id').optional().isString()
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

    const { qr_token, device_id } = req.body;
    const gateDeviceId = device_id || req.device_id;

    // Find ticket by QR token
    const ticket = await Ticket.findOne({
      qr_token: qr_token,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!ticket) {
      // Log failed redemption
      await AuditLog.logEvent({
        event_type: 'ticket.redeemed.fail',
        device_id: gateDeviceId,
        payload: {
          qr_token: qr_token,
          reason: 'ticket_not_found'
        },
        ip_address: req.ip,
        store_id: req.store_id,
        tenant_id: req.tenant_id,
        severity: 'medium'
      });

      return res.status(404).json({
        result: 'fail',
        reason: 'ticket_not_found',
        message: 'Ticket not found'
      });
    }

    // Check if ticket is valid
    if (!ticket.isValid()) {
      let reason = 'expired';
      if (ticket.status !== 'active') {
        reason = ticket.status;
      } else if (new Date() < ticket.valid_from) {
        reason = 'not_started';
      } else if (new Date() > ticket.valid_to) {
        reason = 'expired';
      } else if (ticket.used >= ticket.quota_or_minutes) {
        reason = 'exhausted';
      }

      // Log failed redemption
      await AuditLog.logEvent({
        event_type: 'ticket.redeemed.fail',
        device_id: gateDeviceId,
        payload: {
          ticket_id: ticket.ticket_id,
          qr_token: qr_token,
          reason: reason
        },
        ip_address: req.ip,
        store_id: req.store_id,
        tenant_id: req.tenant_id,
        severity: 'low'
      });

      return res.json({
        result: 'fail',
        reason: reason,
        message: `Ticket ${reason}`,
        ticket_id: ticket.ticket_id,
        remaining: ticket.getRemainingQuota()
      });
    }

    // Check device binding
    if (!ticket.canRedeem(gateDeviceId)) {
      // Log failed redemption
      await AuditLog.logEvent({
        event_type: 'ticket.redeemed.fail',
        device_id: gateDeviceId,
        payload: {
          ticket_id: ticket.ticket_id,
          qr_token: qr_token,
          reason: 'wrong_device'
        },
        ip_address: req.ip,
        store_id: req.store_id,
        tenant_id: req.tenant_id,
        severity: 'medium'
      });

      return res.json({
        result: 'fail',
        reason: 'wrong_device',
        message: 'Ticket not valid for this device',
        ticket_id: ticket.ticket_id,
        remaining: ticket.getRemainingQuota()
      });
    }

    // Check for duplicate use (same ticket, same device, recent time)
    const recentRedemption = await Redemption.findOne({
      ticket_id: ticket.ticket_id,
      device_id: gateDeviceId,
      result: 'pass',
      timestamp: { $gte: new Date(Date.now() - 5 * 60 * 1000) } // 5 minutes
    });

    if (recentRedemption) {
      // Log failed redemption
      await AuditLog.logEvent({
        event_type: 'ticket.redeemed.fail',
        device_id: gateDeviceId,
        payload: {
          ticket_id: ticket.ticket_id,
          qr_token: qr_token,
          reason: 'duplicate_use'
        },
        ip_address: req.ip,
        store_id: req.store_id,
        tenant_id: req.tenant_id,
        severity: 'high'
      });

      return res.json({
        result: 'fail',
        reason: 'duplicate_use',
        message: 'Ticket already used recently',
        ticket_id: ticket.ticket_id,
        remaining: ticket.getRemainingQuota()
      });
    }

    // Verify signature
    if (!ticket.verifySignature()) {
      // Log failed redemption
      await AuditLog.logEvent({
        event_type: 'ticket.redeemed.fail',
        device_id: gateDeviceId,
        payload: {
          ticket_id: ticket.ticket_id,
          qr_token: qr_token,
          reason: 'invalid_sig'
        },
        ip_address: req.ip,
        store_id: req.store_id,
        tenant_id: req.tenant_id,
        severity: 'critical'
      });

      return res.json({
        result: 'fail',
        reason: 'invalid_sig',
        message: 'Invalid ticket signature',
        ticket_id: ticket.ticket_id,
        remaining: ticket.getRemainingQuota()
      });
    }

    // Process redemption
    const remainingBefore = ticket.getRemainingQuota();
    ticket.used += 1;
    await ticket.save();

    // Create redemption record
    const redemption = new Redemption({
      ticket_id: ticket.ticket_id,
      device_id: gateDeviceId,
      result: 'pass',
      metadata: {
        remaining_quota: ticket.getRemainingQuota(),
        remaining_minutes: ticket.getRemainingMinutes()
      }
    });

    await redemption.save();

    // Log successful redemption
    await AuditLog.logEvent({
      event_type: 'ticket.redeemed.pass',
      device_id: gateDeviceId,
      payload: {
        ticket_id: ticket.ticket_id,
        qr_token: qr_token,
        remaining_before: remainingBefore,
        remaining_after: ticket.getRemainingQuota()
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id
    });

    logger.info(`Ticket redeemed: ${ticket.ticket_id}`, {
      ticket_id: ticket.ticket_id,
      device_id: gateDeviceId,
      remaining: ticket.getRemainingQuota()
    });

    res.json({
      result: 'pass',
      message: 'Ticket redeemed successfully',
      ticket_id: ticket.ticket_id,
      short_code: ticket.short_code,
      type: ticket.type,
      remaining: ticket.getRemainingQuota(),
      remaining_minutes: ticket.getRemainingMinutes(),
      redemption_id: redemption.redemption_id
    });

  } catch (error) {
    next(error);
  }
});

// Reprint ticket
router.post('/reprint', [
  authMiddleware,
  employeeAuthMiddleware,
  body('ticket_id').notEmpty().withMessage('Ticket ID is required'),
  body('reason_code').notEmpty().withMessage('Reason code is required'),
  body('reason_text').optional().isString()
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

    const { ticket_id, reason_code, reason_text } = req.body;

    // Find ticket
    const ticket = await Ticket.findOne({
      ticket_id: ticket_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!ticket) {
      return res.status(404).json({
        error: 'E_TICKET_NOT_FOUND',
        message: 'Ticket not found'
      });
    }

    // Increment printed count
    ticket.printed_count += 1;
    await ticket.save();

    // Log reprint
    await AuditLog.logEvent({
      event_type: 'ticket.reprinted',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        ticket_id: ticket.ticket_id,
        printed_count: ticket.printed_count,
        reason_code: reason_code,
        reason_text: reason_text
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id,
      severity: 'medium'
    });

    res.json({
      ticket_id: ticket.ticket_id,
      short_code: ticket.short_code,
      qr_payload: ticket.qr_payload,
      printed_count: ticket.printed_count,
      message: 'Ticket reprinted successfully'
    });

  } catch (error) {
    next(error);
  }
});

// Refund ticket
router.post('/refund', [
  authMiddleware,
  employeeAuthMiddleware,
  body('ticket_id').notEmpty().withMessage('Ticket ID is required'),
  body('reason_code').notEmpty().withMessage('Reason code is required'),
  body('reason_text').optional().isString()
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

    const { ticket_id, reason_code, reason_text } = req.body;

    // Find ticket
    const ticket = await Ticket.findOne({
      ticket_id: ticket_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!ticket) {
      return res.status(404).json({
        error: 'E_TICKET_NOT_FOUND',
        message: 'Ticket not found'
      });
    }

    if (ticket.status === 'refunded') {
      return res.status(400).json({
        error: 'E_TICKET_ALREADY_REFUNDED',
        message: 'Ticket already refunded'
      });
    }

    // Update ticket status
    ticket.status = 'refunded';
    await ticket.save();

    // Log refund
    await AuditLog.logEvent({
      event_type: 'ticket.refunded',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        ticket_id: ticket.ticket_id,
        sale_id: ticket.sale_id,
        price: ticket.price,
        reason_code: reason_code,
        reason_text: reason_text
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id,
      severity: 'high'
    });

    res.json({
      ticket_id: ticket.ticket_id,
      status: ticket.status,
      message: 'Ticket refunded successfully'
    });

  } catch (error) {
    next(error);
  }
});

// Get ticket redemptions
router.get('/:ticket_id/redemptions', [
  authMiddleware,
  employeeAuthMiddleware,
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('offset').optional().isInt({ min: 0 })
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

    const { ticket_id } = req.params;
    const { limit = 50, offset = 0 } = req.query;

    // Verify ticket exists and belongs to tenant/store
    const ticket = await Ticket.findOne({
      ticket_id: ticket_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!ticket) {
      return res.status(404).json({
        error: 'E_TICKET_NOT_FOUND',
        message: 'Ticket not found'
      });
    }

    const redemptions = await Redemption.find({ ticket_id: ticket_id })
      .sort({ timestamp: -1 })
      .limit(parseInt(limit))
      .skip(parseInt(offset));

    const total = await Redemption.countDocuments({ ticket_id: ticket_id });

    res.json({
      ticket_id: ticket_id,
      redemptions: redemptions.map(redemption => ({
        redemption_id: redemption.redemption_id,
        device_id: redemption.device_id,
        timestamp: redemption.timestamp,
        result: redemption.result,
        reason: redemption.reason,
        metadata: redemption.metadata
      })),
      pagination: {
        total: total,
        limit: parseInt(limit),
        offset: parseInt(offset),
        has_more: total > parseInt(offset) + parseInt(limit)
      }
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
