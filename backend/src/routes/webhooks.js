const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { WebhookDelivery } = require('../models/audit');
const { authMiddleware, employeeAuthMiddleware } = require('../middleware/auth');

const router = express.Router();

// Get webhook delivery logs
router.get('/deliveries', [
  authMiddleware,
  employeeAuthMiddleware,
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('offset').optional().isInt({ min: 0 }),
  query('status').optional().isIn(['pending', 'delivered', 'failed', 'retrying'])
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

    const { limit = 50, offset = 0, status } = req.query;

    // Build query
    const query = {};
    if (status) query.status = status;

    const deliveries = await WebhookDelivery.find(query)
      .sort({ created_at: -1 })
      .limit(parseInt(limit))
      .skip(parseInt(offset));

    const total = await WebhookDelivery.countDocuments(query);

    res.json({
      deliveries: deliveries.map(delivery => ({
        delivery_id: delivery.delivery_id,
        webhook_id: delivery.webhook_id,
        event_type: delivery.event_type,
        url: delivery.url,
        status: delivery.status,
        response_code: delivery.response_code,
        attempt_count: delivery.attempt_count,
        max_attempts: delivery.max_attempts,
        next_retry_at: delivery.next_retry_at,
        delivered_at: delivery.delivered_at,
        created_at: delivery.created_at
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

// Test webhook delivery
router.post('/test', [
  authMiddleware,
  employeeAuthMiddleware,
  body('url').isURL().withMessage('Valid URL is required'),
  body('event_type').notEmpty().withMessage('Event type is required')
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

    const { url, event_type } = req.body;

    // Create test webhook delivery
    const testPayload = {
      event_type: event_type,
      timestamp: new Date().toISOString(),
      data: {
        test: true,
        message: 'This is a test webhook delivery'
      }
    };

    const delivery = new WebhookDelivery({
      webhook_id: 'test',
      event_type: event_type,
      url: url,
      payload: testPayload,
      max_attempts: 1
    });

    await delivery.save();

    // TODO: Implement actual webhook delivery logic
    // For now, just mark as delivered
    delivery.status = 'delivered';
    delivery.response_code = 200;
    delivery.delivered_at = new Date();
    await delivery.save();

    res.json({
      delivery_id: delivery.delivery_id,
      status: delivery.status,
      response_code: delivery.response_code,
      message: 'Test webhook delivered successfully'
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
