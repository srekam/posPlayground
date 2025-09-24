const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { Shift } = require('../models/sales');
const { authMiddleware, employeeAuthMiddleware } = require('../middleware/auth');
const { AuditLog } = require('../models/audit');
const logger = require('../utils/logger');

const router = express.Router();

// Open shift
router.post('/open', [
  authMiddleware,
  employeeAuthMiddleware,
  body('cash_open').isNumeric().withMessage('Cash open amount is required')
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

    const { cash_open, notes } = req.body;

    // Check if there's already an open shift for this device
    const existingShift = await Shift.findOne({
      store_id: req.store_id,
      device_id: req.device_id,
      status: 'open'
    });

    if (existingShift) {
      return res.status(400).json({
        error: 'E_SHIFT_ALREADY_OPEN',
        message: 'Shift is already open for this device'
      });
    }

    // Create new shift
    const shift = new Shift({
      store_id: req.store_id,
      device_id: req.device_id,
      opened_by: req.employee_id,
      cash_open: cash_open,
      notes: notes
    });

    await shift.save();

    // Log shift opening
    await AuditLog.logEvent({
      event_type: 'shift.opened',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        shift_id: shift.shift_id,
        cash_open: cash_open,
        notes: notes
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id
    });

    logger.info(`Shift opened: ${shift.shift_id}`, {
      shift_id: shift.shift_id,
      device_id: req.device_id,
      employee_id: req.employee_id,
      cash_open: cash_open
    });

    res.status(201).json({
      shift_id: shift.shift_id,
      store_id: shift.store_id,
      device_id: shift.device_id,
      opened_by: shift.opened_by,
      open_at: shift.open_at,
      cash_open: shift.cash_open,
      status: shift.status,
      totals: shift.totals
    });

  } catch (error) {
    next(error);
  }
});

// Close shift
router.post('/close', [
  authMiddleware,
  employeeAuthMiddleware,
  body('cash_counted').isNumeric().withMessage('Cash counted amount is required')
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

    const { cash_counted, notes } = req.body;

    // Find open shift
    const shift = await Shift.findOne({
      store_id: req.store_id,
      device_id: req.device_id,
      status: 'open'
    });

    if (!shift) {
      return res.status(400).json({
        error: 'E_NO_OPEN_SHIFT',
        message: 'No open shift found for this device'
      });
    }

    // Close shift
    shift.closeShift(req.employee_id, cash_counted);
    if (notes) shift.notes = notes;
    await shift.save();

    // Log shift closing
    await AuditLog.logEvent({
      event_type: 'shift.closed',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        shift_id: shift.shift_id,
        cash_open: shift.cash_open,
        cash_counted: cash_counted,
        cash_expected: shift.cash_expected,
        cash_diff: shift.cash_diff,
        totals: shift.totals,
        notes: notes
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id
    });

    logger.info(`Shift closed: ${shift.shift_id}`, {
      shift_id: shift.shift_id,
      device_id: req.device_id,
      employee_id: req.employee_id,
      cash_diff: shift.cash_diff
    });

    res.json({
      shift_id: shift.shift_id,
      store_id: shift.store_id,
      device_id: shift.device_id,
      opened_by: shift.opened_by,
      closed_by: shift.closed_by,
      open_at: shift.open_at,
      close_at: shift.close_at,
      cash_open: shift.cash_open,
      cash_counted: shift.cash_counted,
      cash_expected: shift.cash_expected,
      cash_diff: shift.cash_diff,
      status: shift.status,
      totals: shift.totals,
      notes: shift.notes
    });

  } catch (error) {
    next(error);
  }
});

// Get current shift
router.get('/current', [
  authMiddleware,
  employeeAuthMiddleware
], async (req, res, next) => {
  try {
    const shift = await Shift.findOne({
      store_id: req.store_id,
      device_id: req.device_id,
      status: 'open'
    });

    if (!shift) {
      return res.status(404).json({
        error: 'E_NO_OPEN_SHIFT',
        message: 'No open shift found for this device'
      });
    }

    res.json({
      shift_id: shift.shift_id,
      store_id: shift.store_id,
      device_id: shift.device_id,
      opened_by: shift.opened_by,
      open_at: shift.open_at,
      cash_open: shift.cash_open,
      status: shift.status,
      totals: shift.totals,
      notes: shift.notes
    });

  } catch (error) {
    next(error);
  }
});

// Get shifts list
router.get('/', [
  authMiddleware,
  employeeAuthMiddleware,
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('offset').optional().isInt({ min: 0 }),
  query('from_date').optional().isISO8601(),
  query('to_date').optional().isISO8601(),
  query('status').optional().isIn(['open', 'closed'])
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

    const { limit = 50, offset = 0, from_date, to_date, status } = req.query;

    // Build query
    const query = {
      store_id: req.store_id
    };

    if (status) query.status = status;

    if (from_date || to_date) {
      query.open_at = {};
      if (from_date) query.open_at.$gte = new Date(from_date);
      if (to_date) query.open_at.$lte = new Date(to_date);
    }

    const shifts = await Shift.find(query)
      .sort({ open_at: -1 })
      .limit(parseInt(limit))
      .skip(parseInt(offset));

    const total = await Shift.countDocuments(query);

    res.json({
      shifts: shifts.map(shift => ({
        shift_id: shift.shift_id,
        device_id: shift.device_id,
        opened_by: shift.opened_by,
        closed_by: shift.closed_by,
        open_at: shift.open_at,
        close_at: shift.close_at,
        cash_open: shift.cash_open,
        cash_counted: shift.cash_counted,
        cash_expected: shift.cash_expected,
        cash_diff: shift.cash_diff,
        status: shift.status,
        totals: shift.totals
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

// Get shift by ID
router.get('/:shift_id', [
  authMiddleware,
  employeeAuthMiddleware
], async (req, res, next) => {
  try {
    const { shift_id } = req.params;

    const shift = await Shift.findOne({
      shift_id: shift_id,
      store_id: req.store_id
    });

    if (!shift) {
      return res.status(404).json({
        error: 'E_SHIFT_NOT_FOUND',
        message: 'Shift not found'
      });
    }

    res.json({
      shift_id: shift.shift_id,
      store_id: shift.store_id,
      device_id: shift.device_id,
      opened_by: shift.opened_by,
      closed_by: shift.closed_by,
      open_at: shift.open_at,
      close_at: shift.close_at,
      cash_open: shift.cash_open,
      cash_counted: shift.cash_counted,
      cash_expected: shift.cash_expected,
      cash_diff: shift.cash_diff,
      status: shift.status,
      totals: shift.totals,
      notes: shift.notes,
      created_at: shift.created_at,
      updated_at: shift.updated_at
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
