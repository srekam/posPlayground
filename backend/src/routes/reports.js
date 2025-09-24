const express = require('express');
const { query, validationResult } = require('express-validator');
const { Sale, Shift, Refund, Reprint } = require('../models/sales');
const { Ticket, Redemption } = require('../models/tickets');
const { AuditLog } = require('../models/audit');
const { authMiddleware, employeeAuthMiddleware } = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// Sales report
router.get('/sales', [
  authMiddleware,
  employeeAuthMiddleware,
  query('from_date').isISO8601().withMessage('Valid from date is required'),
  query('to_date').isISO8601().withMessage('Valid to date is required'),
  query('store_id').optional().isString(),
  query('device_id').optional().isString(),
  query('cashier_id').optional().isString()
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

    const { from_date, to_date, store_id, device_id, cashier_id } = req.query;

    // Build query
    const query = {
      tenant_id: req.tenant_id,
      store_id: store_id || req.store_id,
      timestamp: {
        $gte: new Date(from_date),
        $lte: new Date(to_date)
      }
    };

    if (device_id) query.device_id = device_id;
    if (cashier_id) query.cashier_id = cashier_id;

    const sales = await Sale.find(query);

    // Calculate totals
    const totalSales = sales.length;
    const grossRevenue = sales.reduce((sum, sale) => sum + sale.subtotal, 0);
    const discountTotal = sales.reduce((sum, sale) => sum + sale.discount_total, 0);
    const netRevenue = sales.reduce((sum, sale) => sum + sale.grand_total, 0);
    const taxTotal = sales.reduce((sum, sale) => sum + sale.tax_total, 0);

    // Group by payment method
    const paymentMethods = {};
    sales.forEach(sale => {
      if (!paymentMethods[sale.payment_method]) {
        paymentMethods[sale.payment_method] = { count: 0, amount: 0 };
      }
      paymentMethods[sale.payment_method].count += 1;
      paymentMethods[sale.payment_method].amount += sale.grand_total;
    });

    // Group by hour for hourly breakdown
    const hourlyBreakdown = {};
    sales.forEach(sale => {
      const hour = sale.timestamp.getHours();
      if (!hourlyBreakdown[hour]) {
        hourlyBreakdown[hour] = { count: 0, amount: 0 };
      }
      hourlyBreakdown[hour].count += 1;
      hourlyBreakdown[hour].amount += sale.grand_total;
    });

    res.json({
      period: {
        from: from_date,
        to: to_date
      },
      summary: {
        total_sales: totalSales,
        gross_revenue: grossRevenue,
        discount_total: discountTotal,
        net_revenue: netRevenue,
        tax_total: taxTotal,
        average_sale: totalSales > 0 ? netRevenue / totalSales : 0
      },
      payment_methods: paymentMethods,
      hourly_breakdown: hourlyBreakdown
    });

  } catch (error) {
    next(error);
  }
});

// Shifts report
router.get('/shifts', [
  authMiddleware,
  employeeAuthMiddleware,
  query('from_date').isISO8601().withMessage('Valid from date is required'),
  query('to_date').isISO8601().withMessage('Valid to date is required'),
  query('store_id').optional().isString(),
  query('device_id').optional().isString()
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

    const { from_date, to_date, store_id, device_id } = req.query;

    // Build query
    const query = {
      store_id: store_id || req.store_id,
      open_at: {
        $gte: new Date(from_date),
        $lte: new Date(to_date)
      }
    };

    if (device_id) query.device_id = device_id;

    const shifts = await Shift.find(query);

    // Calculate totals
    const totalShifts = shifts.length;
    const totalCashOpen = shifts.reduce((sum, shift) => sum + shift.cash_open, 0);
    const totalCashCounted = shifts.reduce((sum, shift) => sum + (shift.cash_counted || 0), 0);
    const totalCashExpected = shifts.reduce((sum, shift) => sum + (shift.cash_expected || 0), 0);
    const totalCashDiff = shifts.reduce((sum, shift) => sum + (shift.cash_diff || 0), 0);

    const totalSalesCount = shifts.reduce((sum, shift) => sum + shift.totals.sales.count, 0);
    const totalSalesAmount = shifts.reduce((sum, shift) => sum + shift.totals.sales.amount, 0);
    const totalRefundsCount = shifts.reduce((sum, shift) => sum + shift.totals.refunds.count, 0);
    const totalRefundsAmount = shifts.reduce((sum, shift) => sum + shift.totals.refunds.amount, 0);

    // Group by device
    const deviceBreakdown = {};
    shifts.forEach(shift => {
      if (!deviceBreakdown[shift.device_id]) {
        deviceBreakdown[shift.device_id] = {
          shift_count: 0,
          sales_count: 0,
          sales_amount: 0,
          cash_diff_total: 0
        };
      }
      deviceBreakdown[shift.device_id].shift_count += 1;
      deviceBreakdown[shift.device_id].sales_count += shift.totals.sales.count;
      deviceBreakdown[shift.device_id].sales_amount += shift.totals.sales.amount;
      deviceBreakdown[shift.device_id].cash_diff_total += (shift.cash_diff || 0);
    });

    res.json({
      period: {
        from: from_date,
        to: to_date
      },
      summary: {
        total_shifts: totalShifts,
        total_cash_open: totalCashOpen,
        total_cash_counted: totalCashCounted,
        total_cash_expected: totalCashExpected,
        total_cash_diff: totalCashDiff,
        total_sales_count: totalSalesCount,
        total_sales_amount: totalSalesAmount,
        total_refunds_count: totalRefundsCount,
        total_refunds_amount: totalRefundsAmount
      },
      device_breakdown: deviceBreakdown,
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
      }))
    });

  } catch (error) {
    next(error);
  }
});

// Tickets report
router.get('/tickets', [
  authMiddleware,
  employeeAuthMiddleware,
  query('from_date').isISO8601().withMessage('Valid from date is required'),
  query('to_date').isISO8601().withMessage('Valid to date is required'),
  query('store_id').optional().isString()
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

    const { from_date, to_date, store_id } = req.query;

    // Build query
    const query = {
      tenant_id: req.tenant_id,
      store_id: store_id || req.store_id,
      created_at: {
        $gte: new Date(from_date),
        $lte: new Date(to_date)
      }
    };

    const tickets = await Ticket.find(query);
    const redemptions = await Redemption.find({
      ticket_id: { $in: tickets.map(t => t.ticket_id) }
    });

    // Calculate metrics
    const totalTicketsIssued = tickets.length;
    const totalTicketsRedeemed = new Set(redemptions.filter(r => r.result === 'pass').map(r => r.ticket_id)).size;
    const redemptionRate = totalTicketsIssued > 0 ? (totalTicketsRedeemed / totalTicketsIssued) * 100 : 0;

    // Group by type
    const typeBreakdown = {};
    tickets.forEach(ticket => {
      if (!typeBreakdown[ticket.type]) {
        typeBreakdown[ticket.type] = {
          issued: 0,
          redeemed: 0,
          total_quota: 0,
          total_used: 0
        };
      }
      typeBreakdown[ticket.type].issued += 1;
      typeBreakdown[ticket.type].total_quota += ticket.quota_or_minutes;
      typeBreakdown[ticket.type].total_used += ticket.used;
    });

    // Count redemptions per type
    redemptions.forEach(redemption => {
      const ticket = tickets.find(t => t.ticket_id === redemption.ticket_id);
      if (ticket && redemption.result === 'pass') {
        if (!typeBreakdown[ticket.type]) return;
        typeBreakdown[ticket.type].redeemed += 1;
      }
    });

    // Failure reasons
    const failureReasons = {};
    redemptions.filter(r => r.result === 'fail').forEach(redemption => {
      if (!failureReasons[redemption.reason]) {
        failureReasons[redemption.reason] = 0;
      }
      failureReasons[redemption.reason] += 1;
    });

    res.json({
      period: {
        from: from_date,
        to: to_date
      },
      summary: {
        total_tickets_issued: totalTicketsIssued,
        total_tickets_redeemed: totalTicketsRedeemed,
        redemption_rate: redemptionRate,
        total_redemption_attempts: redemptions.length,
        successful_redemptions: redemptions.filter(r => r.result === 'pass').length,
        failed_redemptions: redemptions.filter(r => r.result === 'fail').length
      },
      type_breakdown: typeBreakdown,
      failure_reasons: failureReasons
    });

  } catch (error) {
    next(error);
  }
});

// Fraud watch report
router.get('/fraud', [
  authMiddleware,
  employeeAuthMiddleware,
  query('from_date').isISO8601().withMessage('Valid from date is required'),
  query('to_date').isISO8601().withMessage('Valid to date is required'),
  query('store_id').optional().isString()
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

    const { from_date, to_date, store_id } = req.query;

    // Get audit logs for suspicious activities
    const auditQuery = {
      tenant_id: req.tenant_id,
      store_id: store_id || req.store_id,
      timestamp: {
        $gte: new Date(from_date),
        $lte: new Date(to_date)
      },
      event_type: {
        $in: [
          'reprint.requested', 'refund.requested', 'ticket.redeemed.fail',
          'employee.login_failed', 'approval.pin_failed'
        ]
      }
    };

    const auditLogs = await AuditLog.find(auditQuery);

    // Get reprints and refunds
    const reprints = await Reprint.find({
      timestamp: {
        $gte: new Date(from_date),
        $lte: new Date(to_date)
      }
    });

    const refunds = await Refund.find({
      timestamp: {
        $gte: new Date(from_date),
        $lte: new Date(to_date)
      }
    });

    // Analyze patterns
    const reprintsByEmployee = {};
    reprints.forEach(reprint => {
      if (!reprintsByEmployee[reprint.requested_by]) {
        reprintsByEmployee[reprint.requested_by] = 0;
      }
      reprintsByEmployee[reprint.requested_by] += 1;
    });

    const refundsByEmployee = {};
    refunds.forEach(refund => {
      if (!refundsByEmployee[refund.requested_by]) {
        refundsByEmployee[refund.requested_by] = 0;
      }
      refundsByEmployee[refund.requested_by] += 1;
    });

    // Failed login attempts by employee
    const failedLoginsByEmployee = {};
    auditLogs.filter(log => log.event_type === 'employee.login_failed').forEach(log => {
      if (!failedLoginsByEmployee[log.actor_id]) {
        failedLoginsByEmployee[log.actor_id] = 0;
      }
      failedLoginsByEmployee[log.actor_id] += 1;
    });

    // After-hours activities (activities outside 9 AM - 10 PM)
    const afterHoursActivities = auditLogs.filter(log => {
      const hour = log.timestamp.getHours();
      return hour < 9 || hour > 22;
    });

    res.json({
      period: {
        from: from_date,
        to: to_date
      },
      summary: {
        total_reprints: reprints.length,
        total_refunds: refunds.length,
        total_failed_logins: auditLogs.filter(log => log.event_type === 'employee.login_failed').length,
        total_failed_redemptions: auditLogs.filter(log => log.event_type === 'ticket.redeemed.fail').length,
        after_hours_activities: afterHoursActivities.length
      },
      reprints_by_employee: reprintsByEmployee,
      refunds_by_employee: refundsByEmployee,
      failed_logins_by_employee: failedLoginsByEmployee,
      after_hours_activities: afterHoursActivities.map(log => ({
        timestamp: log.timestamp,
        event_type: log.event_type,
        actor_id: log.actor_id,
        device_id: log.device_id,
        payload: log.payload
      })),
      high_risk_events: auditLogs.filter(log => log.severity === 'high' || log.severity === 'critical').map(log => ({
        timestamp: log.timestamp,
        event_type: log.event_type,
        actor_id: log.actor_id,
        device_id: log.device_id,
        severity: log.severity,
        payload: log.payload
      }))
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
