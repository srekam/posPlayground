const express = require('express');
const { body, query, validationResult } = require('express-validator');
const { Package, PricingRule, AccessZone } = require('../models/catalog');
const { authMiddleware } = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// Get packages for a store
router.get('/packages', [
  authMiddleware,
  query('store_id').optional().isString(),
  query('type').optional().isIn(['single', 'multi', 'timepass', 'credit', 'bundle']),
  query('active').optional().isBoolean()
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

    const { type, active } = req.query;
    const store_id = req.query.store_id || req.store_id;

    // Build query
    const query = {
      tenant_id: req.tenant_id,
      store_id: store_id
    };

    if (type) query.type = type;
    if (active !== undefined) query.active = active === 'true';

    const packages = await Package.find(query)
      .sort({ name: 1 });

    // Filter by active window if needed
    const filteredPackages = packages.filter(pkg => {
      if (!pkg.active) return false;
      
      if (pkg.active_window && pkg.active_window.from && pkg.active_window.to) {
        const now = new Date();
        const currentTime = now.getHours() * 60 + now.getMinutes();
        const fromTime = pkg.parseTime(pkg.active_window.from);
        const toTime = pkg.parseTime(pkg.active_window.to);
        
        return currentTime >= fromTime && currentTime <= toTime;
      }
      
      return true;
    });

    res.json({
      packages: filteredPackages.map(pkg => ({
        package_id: pkg.package_id,
        name: pkg.name,
        type: pkg.type,
        price: pkg.price,
        price_text: pkg.price_text,
        quota_or_minutes: pkg.quota_or_minutes,
        description: pkg.description,
        image_url: pkg.image_url,
        allowed_devices: pkg.allowed_devices,
        visible_on: pkg.visible_on,
        active_window: pkg.active_window
      }))
    });

  } catch (error) {
    next(error);
  }
});

// Get pricing rules for a store
router.get('/pricing/rules', [
  authMiddleware,
  query('store_id').optional().isString(),
  query('active').optional().isBoolean()
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

    const { active } = req.query;
    const store_id = req.query.store_id || req.store_id;

    // Build query for both store and tenant rules
    const query = {
      $or: [
        { scope: 'store', scope_id: store_id },
        { scope: 'tenant', scope_id: req.tenant_id }
      ]
    };

    if (active !== undefined) query.active = active === 'true';

    const rules = await PricingRule.find(query)
      .sort({ priority: -1, created_at: 1 });

    // Filter by active window
    const now = new Date();
    const activeRules = rules.filter(rule => {
      if (!rule.active) return false;
      
      if (rule.active_window) {
        const from = rule.active_window.from;
        const to = rule.active_window.to;
        
        if (from && to) {
          return now >= from && now <= to;
        }
      }
      
      return true;
    });

    res.json({
      rules: activeRules.map(rule => ({
        rule_id: rule.rule_id,
        name: rule.name,
        description: rule.description,
        kind: rule.kind,
        scope: rule.scope,
        scope_id: rule.scope_id,
        params: rule.params,
        priority: rule.priority,
        active_window: rule.active_window
      }))
    });

  } catch (error) {
    next(error);
  }
});

// Calculate pricing for a cart
router.post('/pricing/calculate', [
  authMiddleware,
  body('items').isArray().withMessage('Items array is required'),
  body('items.*.package_id').notEmpty().withMessage('Package ID is required'),
  body('items.*.quantity').isInt({ min: 1 }).withMessage('Quantity must be at least 1')
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

    const { items, promo_code } = req.body;

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

    // Get pricing rules
    const rules = await PricingRule.find({
      $or: [
        { scope: 'store', scope_id: req.store_id },
        { scope: 'tenant', scope_id: req.tenant_id }
      ],
      active: true
    }).sort({ priority: -1 });

    // Calculate line items
    const lineItems = items.map(item => {
      const pkg = packageMap[item.package_id];
      if (!pkg) {
        throw new Error(`Package ${item.package_id} not found`);
      }

      const lineTotal = pkg.price * item.quantity;
      const discounts = [];

      // Apply line-level discounts
      rules.forEach(rule => {
        if (rule.kind === 'line_percent' && 
            (!rule.params.target_packages || rule.params.target_packages.includes(item.package_id))) {
          const discountAmount = lineTotal * (rule.params.percentage / 100);
          discounts.push({
            type: 'percent',
            value: rule.params.percentage,
            amount: discountAmount,
            description: rule.name,
            rule_id: rule.rule_id
          });
        } else if (rule.kind === 'line_amount' && 
                   (!rule.params.target_packages || rule.params.target_packages.includes(item.package_id))) {
          const discountAmount = Math.min(rule.params.amount, lineTotal);
          discounts.push({
            type: 'amount',
            value: rule.params.amount,
            amount: discountAmount,
            description: rule.name,
            rule_id: rule.rule_id
          });
        }
      });

      const lineDiscountTotal = discounts.reduce((sum, discount) => sum + discount.amount, 0);
      const lineSubtotal = lineTotal - lineDiscountTotal;

      return {
        package_id: item.package_id,
        package_name: pkg.name,
        quantity: item.quantity,
        unit_price: pkg.price,
        line_total: lineTotal,
        discounts: discounts,
        line_discount_total: lineDiscountTotal,
        line_subtotal: lineSubtotal
      };
    });

    // Calculate cart totals
    const subtotal = lineItems.reduce((sum, item) => sum + item.line_subtotal, 0);
    const lineDiscountTotal = lineItems.reduce((sum, item) => sum + item.line_discount_total, 0);

    // Apply cart-level discounts
    const cartDiscounts = [];
    let cartDiscountTotal = 0;

    rules.forEach(rule => {
      if (rule.kind === 'cart_percent') {
        const discountAmount = subtotal * (rule.params.percentage / 100);
        cartDiscounts.push({
          type: 'percent',
          value: rule.params.percentage,
          amount: discountAmount,
          description: rule.name,
          rule_id: rule.rule_id
        });
        cartDiscountTotal += discountAmount;
      } else if (rule.kind === 'cart_amount') {
        const discountAmount = Math.min(rule.params.amount, subtotal);
        cartDiscounts.push({
          type: 'amount',
          value: rule.params.amount,
          amount: discountAmount,
          description: rule.name,
          rule_id: rule.rule_id
        });
        cartDiscountTotal += discountAmount;
      } else if (rule.kind === 'promo_code' && promo_code === rule.params.promo_code) {
        const discountAmount = rule.params.amount || (subtotal * (rule.params.percentage / 100));
        cartDiscounts.push({
          type: 'promo_code',
          value: rule.params.amount || rule.params.percentage,
          amount: discountAmount,
          description: rule.name,
          rule_id: rule.rule_id
        });
        cartDiscountTotal += discountAmount;
      }
    });

    const finalSubtotal = subtotal - cartDiscountTotal;
    const taxTotal = finalSubtotal * 0.07; // 7% VAT (configurable)
    const grandTotal = finalSubtotal + taxTotal;

    res.json({
      line_items: lineItems,
      subtotal: subtotal,
      line_discount_total: lineDiscountTotal,
      cart_discounts: cartDiscounts,
      cart_discount_total: cartDiscountTotal,
      final_subtotal: finalSubtotal,
      tax_total: taxTotal,
      grand_total: grandTotal,
      currency: 'THB'
    });

  } catch (error) {
    next(error);
  }
});

// Get access zones
router.get('/zones', [
  authMiddleware,
  query('store_id').optional().isString()
], async (req, res, next) => {
  try {
    const store_id = req.query.store_id || req.store_id;

    const zones = await AccessZone.find({
      tenant_id: req.tenant_id,
      store_id: store_id,
      active: true
    }).populate('devices packages');

    res.json({
      zones: zones.map(zone => ({
        zone_id: zone.zone_id,
        name: zone.name,
        description: zone.description,
        devices: zone.devices,
        packages: zone.packages
      }))
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
