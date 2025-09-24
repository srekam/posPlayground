const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { OutboxEvent } = require('../models/audit');
const { Sale, Shift } = require('../models/sales');
const { Ticket, Redemption } = require('../models/tickets');
const { authMiddleware } = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// Sync batch operations from offline devices
router.post('/batch', [
  authMiddleware,
  body('operations').isArray().withMessage('Operations array is required'),
  body('operations.*.op_id').notEmpty().withMessage('Operation ID is required'),
  body('operations.*.type').isIn(['sale', 'redemption', 'audit', 'shift_open', 'shift_close']).withMessage('Invalid operation type')
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

    const { operations } = req.body;
    const results = [];

    for (const operation of operations) {
      try {
        // Check if operation already processed
        const existing = await OutboxEvent.findOne({
          operation_id: operation.op_id,
          device_id: req.device_id
        });

        if (existing && existing.status === 'synced') {
          results.push({
            op_id: operation.op_id,
            status: 'already_synced',
            message: 'Operation already processed'
          });
          continue;
        }

        let result = { op_id: operation.op_id, status: 'failed' };

        switch (operation.type) {
          case 'sale':
            result = await processSaleSync(operation, req);
            break;
          case 'redemption':
            result = await processRedemptionSync(operation, req);
            break;
          case 'shift_open':
          case 'shift_close':
            result = await processShiftSync(operation, req);
            break;
          default:
            result = {
              op_id: operation.op_id,
              status: 'failed',
              error: 'E_UNSUPPORTED_OPERATION',
              message: 'Unsupported operation type'
            };
        }

        // Update or create outbox event
        if (existing) {
          existing.status = result.status === 'success' ? 'synced' : 'failed';
          existing.synced_at = result.status === 'success' ? new Date() : null;
          existing.error_message = result.error || null;
          await existing.save();
        } else {
          await OutboxEvent.create({
            device_id: req.device_id,
            operation_type: operation.type,
            operation_id: operation.op_id,
            payload: operation.data,
            status: result.status === 'success' ? 'synced' : 'failed',
            synced_at: result.status === 'success' ? new Date() : null,
            error_message: result.error || null
          });
        }

        results.push(result);

      } catch (error) {
        logger.error(`Sync operation failed: ${operation.op_id}`, error);
        results.push({
          op_id: operation.op_id,
          status: 'failed',
          error: 'E_SYNC_ERROR',
          message: error.message
        });
      }
    }

    res.json({
      results: results,
      processed: results.length,
      successful: results.filter(r => r.status === 'success').length,
      failed: results.filter(r => r.status === 'failed').length
    });

  } catch (error) {
    next(error);
  }
});

// Get bootstrap data for gate devices
router.get('/gate/bootstrap', [
  authMiddleware,
  query('window').optional().isInt({ min: 1, max: 1440 }) // minutes
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

    const windowMinutes = parseInt(req.query.window) || 60; // Default 1 hour
    const since = new Date(Date.now() - windowMinutes * 60 * 1000);

    // Get recently issued tickets
    const recentTickets = await Ticket.find({
      tenant_id: req.tenant_id,
      store_id: req.store_id,
      status: 'active',
      valid_from: { $lte: new Date() },
      valid_to: { $gte: new Date() },
      created_at: { $gte: since }
    }).select('ticket_id qr_token short_code type quota_or_minutes used valid_from valid_to signature');

    // Get device configuration
    const config = {
      offline_window_minutes: windowMinutes,
      max_offline_operations: 1000,
      sync_interval_minutes: 5,
      ticket_cache_hours: 24
    };

    res.json({
      tickets: recentTickets.map(ticket => ({
        ticket_id: ticket.ticket_id,
        qr_token: ticket.qr_token,
        short_code: ticket.short_code,
        type: ticket.type,
        quota_or_minutes: ticket.quota_or_minutes,
        used: ticket.used,
        valid_from: ticket.valid_from,
        valid_to: ticket.valid_to,
        signature: ticket.signature
      })),
      config: config,
      server_time: new Date().toISOString(),
      bootstrap_window: {
        from: since.toISOString(),
        to: new Date().toISOString()
      }
    });

  } catch (error) {
    next(error);
  }
});

// Helper functions for processing sync operations
async function processSaleSync(operation, req) {
  try {
    const saleData = operation.data;

    // Check if sale already exists
    const existingSale = await Sale.findOne({
      reference: operation.op_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (existingSale) {
      return {
        op_id: operation.op_id,
        status: 'success',
        sale_id: existingSale.sale_id,
        message: 'Sale already exists'
      };
    }

    // Create sale from sync data
    const sale = new Sale({
      ...saleData,
      tenant_id: req.tenant_id,
      store_id: req.store_id,
      device_id: req.device_id,
      reference: operation.op_id
    });

    await sale.save();

    return {
      op_id: operation.op_id,
      status: 'success',
      sale_id: sale.sale_id,
      message: 'Sale synced successfully'
    };

  } catch (error) {
    return {
      op_id: operation.op_id,
      status: 'failed',
      error: 'E_SALE_SYNC_FAILED',
      message: error.message
    };
  }
}

async function processRedemptionSync(operation, req) {
  try {
    const redemptionData = operation.data;

    // Check if redemption already exists
    const existingRedemption = await Redemption.findOne({
      redemption_id: operation.op_id
    });

    if (existingRedemption) {
      return {
        op_id: operation.op_id,
        status: 'success',
        redemption_id: existingRedemption.redemption_id,
        message: 'Redemption already exists'
      };
    }

    // Create redemption from sync data
    const redemption = new Redemption({
      ...redemptionData,
      redemption_id: operation.op_id,
      device_id: req.device_id
    });

    await redemption.save();

    // Update ticket if redemption was successful
    if (redemption.result === 'pass') {
      await Ticket.findOneAndUpdate(
        { ticket_id: redemption.ticket_id },
        { $inc: { used: 1 } }
      );
    }

    return {
      op_id: operation.op_id,
      status: 'success',
      redemption_id: redemption.redemption_id,
      message: 'Redemption synced successfully'
    };

  } catch (error) {
    return {
      op_id: operation.op_id,
      status: 'failed',
      error: 'E_REDEMPTION_SYNC_FAILED',
      message: error.message
    };
  }
}

async function processShiftSync(operation, req) {
  try {
    const shiftData = operation.data;

    // Check if shift already exists
    const existingShift = await Shift.findOne({
      shift_id: operation.op_id
    });

    if (existingShift) {
      return {
        op_id: operation.op_id,
        status: 'success',
        shift_id: existingShift.shift_id,
        message: 'Shift already exists'
      };
    }

    // Create or update shift from sync data
    const shift = new Shift({
      ...shiftData,
      shift_id: operation.op_id,
      store_id: req.store_id,
      device_id: req.device_id
    });

    await shift.save();

    return {
      op_id: operation.op_id,
      status: 'success',
      shift_id: shift.shift_id,
      message: 'Shift synced successfully'
    };

  } catch (error) {
    return {
      op_id: operation.op_id,
      status: 'failed',
      error: 'E_SHIFT_SYNC_FAILED',
      message: error.message
    };
  }
}

module.exports = router;
