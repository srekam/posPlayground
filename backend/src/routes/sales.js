const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { Sale, Shift, Refund, Reprint } = require('../models/sales');
const { Ticket } = require('../models/tickets');
const { Package } = require('../models/catalog');
const { authMiddleware, employeeAuthMiddleware, idempotencyMiddleware } = require('../middleware/auth');
const { AuditLog } = require('../models/audit');
const logger = require('../utils/logger');

const router = express.Router();

// Create a new sale
router.post('/', [
  authMiddleware,
  employeeAuthMiddleware,
  idempotencyMiddleware,
  body('items').isArray().withMessage('Items array is required'),
  body('items.*.package_id').notEmpty().withMessage('Package ID is required'),
  body('items.*.quantity').isInt({ min: 1 }).withMessage('Quantity must be at least 1'),
  body('payment_method').isIn(['cash', 'qr', 'card', 'other']).withMessage('Invalid payment method'),
  body('amount_tendered').optional().isNumeric().withMessage('Amount tendered must be numeric')
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

    const { items, payment_method, amount_tendered, notes } = req.body;
    const idempotency_key = req.idempotency_key;

    // Check for existing sale with same idempotency key
    const existingSale = await Sale.findOne({ reference: idempotency_key });
    if (existingSale) {
      return res.json({
        sale_id: existingSale.sale_id,
        reference: existingSale.reference,
        status: existingSale.status,
        message: 'Sale already processed'
      });
    }

    // Get current shift
    const currentShift = await Shift.findOne({
      store_id: req.store_id,
      device_id: req.device_id,
      status: 'open'
    });

    if (!currentShift) {
      return res.status(400).json({
        error: 'E_NO_OPEN_SHIFT',
        message: 'No open shift found for this device'
      });
    }

    // Get packages
    const packageIds = items.map(item => item.package_id);
    const packages = await Package.find({
      package_id: { $in: packageIds },
      tenant_id: req.tenant_id,
      store_id: req.store_id,
      active: true
    });

    const packageMap = {};
    packages.forEach(pkg => {
      packageMap[pkg.package_id] = pkg;
    });

    // Calculate totals
    let subtotal = 0;
    const saleItems = items.map(item => {
      const pkg = packageMap[item.package_id];
      if (!pkg) {
        throw new Error(`Package ${item.package_id} not found`);
      }

      const lineTotal = pkg.price * item.quantity;
      subtotal += lineTotal;

      return {
        package_id: item.package_id,
        package_name: pkg.name,
        quantity: item.quantity,
        unit_price: pkg.price,
        line_total: lineTotal,
        discounts: []
      };
    });

    const discountTotal = 0; // TODO: Apply discounts
    const taxTotal = subtotal * 0.07; // 7% VAT
    const grandTotal = subtotal - discountTotal + taxTotal;

    // Calculate change
    let change = 0;
    if (payment_method === 'cash' && amount_tendered) {
      change = amount_tendered - grandTotal;
      if (change < 0) {
        return res.status(400).json({
          error: 'E_INSUFFICIENT_PAYMENT',
          message: 'Amount tendered is less than grand total'
        });
      }
    }

    // Create sale
    const sale = new Sale({
      tenant_id: req.tenant_id,
      store_id: req.store_id,
      device_id: req.device_id,
      cashier_id: req.employee_id,
      shift_id: currentShift.shift_id,
      items: saleItems,
      subtotal: subtotal,
      discount_total: discountTotal,
      tax_total: taxTotal,
      grand_total: grandTotal,
      payment_method: payment_method,
      amount_tendered: amount_tendered,
      change: change,
      reference: idempotency_key,
      notes: notes
    });

    await sale.save();

    // Generate tickets
    const tickets = [];
    for (const item of saleItems) {
      const pkg = packageMap[item.package_id];
      
      for (let i = 0; i < item.quantity; i++) {
        const ticket = new Ticket({
          tenant_id: req.tenant_id,
          store_id: req.store_id,
          sale_id: sale.sale_id,
          package_id: item.package_id,
          type: pkg.type,
          quota_or_minutes: pkg.quota_or_minutes,
          valid_from: new Date(),
          valid_to: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
          lot_no: `LOT-${Date.now()}`,
          shift_id: currentShift.shift_id,
          issued_by: req.employee_id,
          price: pkg.price,
          payment_method: payment_method
        });

        await ticket.save();
        tickets.push(ticket);
      }
    }

    // Update shift totals
    currentShift.totals.sales.count += 1;
    currentShift.totals.sales.amount += grandTotal;
    await currentShift.save();

    // Log sale creation
    await AuditLog.logEvent({
      event_type: 'sale.created',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        sale_id: sale.sale_id,
        items_count: items.length,
        grand_total: grandTotal,
        payment_method: payment_method,
        ticket_count: tickets.length
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id
    });

    logger.info(`Sale created: ${sale.sale_id}`, {
      sale_id: sale.sale_id,
      device_id: req.device_id,
      employee_id: req.employee_id,
      grand_total: grandTotal
    });

    res.status(201).json({
      sale_id: sale.sale_id,
      reference: sale.reference,
      status: sale.status,
      items: sale.items,
      subtotal: sale.subtotal,
      discount_total: sale.discount_total,
      tax_total: sale.tax_total,
      grand_total: sale.grand_total,
      payment_method: sale.payment_method,
      amount_tendered: sale.amount_tendered,
      change: sale.change,
      tickets: tickets.map(ticket => ({
        ticket_id: ticket.ticket_id,
        short_code: ticket.short_code,
        qr_token: ticket.qr_token,
        qr_payload: ticket.qr_payload,
        type: ticket.type,
        quota_or_minutes: ticket.quota_or_minutes,
        valid_from: ticket.valid_from,
        valid_to: ticket.valid_to
      })),
      timestamp: sale.timestamp
    });

  } catch (error) {
    next(error);
  }
});

// Get sale by ID
router.get('/:sale_id', [
  authMiddleware,
  employeeAuthMiddleware
], async (req, res, next) => {
  try {
    const { sale_id } = req.params;

    const sale = await Sale.findOne({
      sale_id: sale_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!sale) {
      return res.status(404).json({
        error: 'E_SALE_NOT_FOUND',
        message: 'Sale not found'
      });
    }

    // Get tickets for this sale
    const tickets = await Ticket.find({ sale_id: sale_id });

    res.json({
      sale_id: sale.sale_id,
      reference: sale.reference,
      status: sale.status,
      items: sale.items,
      subtotal: sale.subtotal,
      discount_total: sale.discount_total,
      tax_total: sale.tax_total,
      grand_total: sale.grand_total,
      payment_method: sale.payment_method,
      amount_tendered: sale.amount_tendered,
      change: sale.change,
      notes: sale.notes,
      tickets: tickets.map(ticket => ({
        ticket_id: ticket.ticket_id,
        short_code: ticket.short_code,
        type: ticket.type,
        quota_or_minutes: ticket.quota_or_minutes,
        used: ticket.used,
        status: ticket.status,
        valid_from: ticket.valid_from,
        valid_to: ticket.valid_to
      })),
      timestamp: sale.timestamp,
      created_at: sale.created_at
    });

  } catch (error) {
    next(error);
  }
});

// Get sales list
router.get('/', [
  authMiddleware,
  employeeAuthMiddleware,
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('offset').optional().isInt({ min: 0 }),
  query('from_date').optional().isISO8601(),
  query('to_date').optional().isISO8601(),
  query('status').optional().isIn(['completed', 'cancelled', 'refunded'])
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
      tenant_id: req.tenant_id,
      store_id: req.store_id
    };

    if (status) query.status = status;

    if (from_date || to_date) {
      query.timestamp = {};
      if (from_date) query.timestamp.$gte = new Date(from_date);
      if (to_date) query.timestamp.$lte = new Date(to_date);
    }

    const sales = await Sale.find(query)
      .sort({ timestamp: -1 })
      .limit(parseInt(limit))
      .skip(parseInt(offset));

    const total = await Sale.countDocuments(query);

    res.json({
      sales: sales.map(sale => ({
        sale_id: sale.sale_id,
        reference: sale.reference,
        status: sale.status,
        items_count: sale.items.length,
        grand_total: sale.grand_total,
        payment_method: sale.payment_method,
        cashier_id: sale.cashier_id,
        timestamp: sale.timestamp
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

// Request refund
router.post('/refunds', [
  authMiddleware,
  employeeAuthMiddleware,
  body('sale_id').notEmpty().withMessage('Sale ID is required'),
  body('ticket_ids').optional().isArray().withMessage('Ticket IDs must be array'),
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

    const { sale_id, ticket_ids, reason_code, reason_text } = req.body;

    // Find sale
    const sale = await Sale.findOne({
      sale_id: sale_id,
      tenant_id: req.tenant_id,
      store_id: req.store_id
    });

    if (!sale) {
      return res.status(404).json({
        error: 'E_SALE_NOT_FOUND',
        message: 'Sale not found'
      });
    }

    // Calculate refund amount
    let refundAmount = sale.grand_total;
    if (ticket_ids && ticket_ids.length > 0) {
      const tickets = await Ticket.find({
        ticket_id: { $in: ticket_ids },
        sale_id: sale_id
      });
      refundAmount = tickets.reduce((sum, ticket) => sum + ticket.price, 0);
    }

    // Create refund request
    const refund = new Refund({
      sale_id: sale_id,
      ticket_ids: ticket_ids || [],
      amount: refundAmount,
      method: sale.payment_method,
      requested_by: req.employee_id,
      reason_code: reason_code,
      reason_text: reason_text
    });

    await refund.save();

    // Log refund request
    await AuditLog.logEvent({
      event_type: 'refund.requested',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        refund_id: refund.refund_id,
        sale_id: sale_id,
        amount: refundAmount,
        reason_code: reason_code
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id,
      severity: 'high'
    });

    res.status(201).json({
      refund_id: refund.refund_id,
      sale_id: sale_id,
      amount: refundAmount,
      status: refund.status,
      reason_code: reason_code,
      reason_text: reason_text,
      requested_by: req.employee_id,
      timestamp: refund.timestamp
    });

  } catch (error) {
    next(error);
  }
});

// Request reprint
router.post('/reprints', [
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

    // Create reprint request
    const reprint = new Reprint({
      ticket_id: ticket_id,
      requested_by: req.employee_id,
      reason_code: reason_code,
      reason_text: reason_text
    });

    await reprint.save();

    // Log reprint request
    await AuditLog.logEvent({
      event_type: 'reprint.requested',
      actor_id: req.employee_id,
      device_id: req.device_id,
      payload: {
        reprint_id: reprint.reprint_id,
        ticket_id: ticket_id,
        reason_code: reason_code
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id,
      severity: 'medium'
    });

    res.status(201).json({
      reprint_id: reprint.reprint_id,
      ticket_id: ticket_id,
      status: reprint.status,
      reason_code: reason_code,
      reason_text: reason_text,
      requested_by: req.employee_id,
      timestamp: reprint.timestamp
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
