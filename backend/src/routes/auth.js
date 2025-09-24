const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const { body, validationResult } = require('express-validator');
const { Device, Employee, Tenant, Store } = require('../models/core');
const { AuditLog } = require('../models/audit');
const { authMiddleware, validateRequest } = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// Device registration
router.post('/device/register', [
  body('site_key').notEmpty().withMessage('Site key is required'),
  body('device_meta').isObject().withMessage('Device metadata is required'),
  body('device_meta.name').notEmpty().withMessage('Device name is required'),
  body('device_meta.type').isIn(['POS', 'GATE', 'KIOSK', 'ADMIN']).withMessage('Invalid device type')
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

    const { site_key, device_meta } = req.body;

    // Parse site key (format: tenant_id:store_id:secret)
    const siteKeyParts = site_key.split(':');
    if (siteKeyParts.length !== 3) {
      return res.status(400).json({
        error: 'E_INVALID_SITE_KEY',
        message: 'Invalid site key format'
      });
    }

    const [tenant_id, store_id, secret] = siteKeyParts;

    // Verify tenant and store exist
    const tenant = await Tenant.findOne({ tenant_id, status: 'active' });
    const store = await Store.findOne({ store_id, tenant_id, active: true });

    if (!tenant || !store) {
      return res.status(400).json({
        error: 'E_INVALID_SITE_KEY',
        message: 'Invalid tenant or store'
      });
    }

    // Generate device token
    const deviceToken = crypto.randomBytes(32).toString('hex');
    const deviceTokenHash = crypto.createHash('sha256').update(deviceToken).digest('hex');

    // Create device
    const device = new Device({
      tenant_id,
      store_id,
      type: device_meta.type,
      name: device_meta.name,
      device_token_hash: deviceTokenHash,
      capabilities: device_meta.capabilities || {},
      registered_by: req.ip
    });

    await device.save();

    // Log registration
    await AuditLog.logEvent({
      event_type: 'device.registered',
      device_id: device.device_id,
      payload: {
        device_type: device_meta.type,
        device_name: device_meta.name,
        tenant_id,
        store_id
      },
      ip_address: req.ip,
      store_id,
      tenant_id
    });

    logger.info(`Device registered: ${device.device_id}`, {
      device_id: device.device_id,
      tenant_id,
      store_id,
      type: device_meta.type
    });

    res.status(201).json({
      device_id: device.device_id,
      device_token: deviceToken,
      tenant_id,
      store_id,
      capabilities: device.capabilities
    });

  } catch (error) {
    next(error);
  }
});

// Device login
router.post('/device/login', [
  body('device_id').notEmpty().withMessage('Device ID is required'),
  body('device_token').notEmpty().withMessage('Device token is required')
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

    const { device_id, device_token } = req.body;

    // Find device
    const device = await Device.findOne({ device_id, status: 'active' })
      .populate('tenant_id store_id');

    if (!device) {
      return res.status(401).json({
        error: 'E_DEVICE_NOT_FOUND',
        message: 'Device not found or suspended'
      });
    }

    // Verify token
    const tokenHash = crypto.createHash('sha256').update(device_token).digest('hex');
    if (tokenHash !== device.device_token_hash) {
      return res.status(401).json({
        error: 'E_INVALID_TOKEN',
        message: 'Invalid device token'
      });
    }

    // Generate JWT
    const token = jwt.sign(
      {
        device_id: device.device_id,
        tenant_id: device.tenant_id,
        store_id: device.store_id,
        type: device.type,
        capabilities: device.capabilities
      },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );

    // Update last seen
    device.last_seen = new Date();
    await device.save();

    // Log login
    await AuditLog.logEvent({
      event_type: 'device.login',
      device_id: device.device_id,
      payload: {
        device_type: device.type,
        tenant_id: device.tenant_id,
        store_id: device.store_id
      },
      ip_address: req.ip,
      store_id: device.store_id,
      tenant_id: device.tenant_id
    });

    res.json({
      access_token: token,
      token_type: 'Bearer',
      expires_in: 24 * 60 * 60, // 24 hours in seconds
      device: {
        device_id: device.device_id,
        name: device.name,
        type: device.type,
        capabilities: device.capabilities,
        tenant: {
          tenant_id: device.tenant_id,
          name: device.tenant_id.name
        },
        store: {
          store_id: device.store_id,
          name: device.store_id.name
        }
      }
    });

  } catch (error) {
    next(error);
  }
});

// Employee login
router.post('/employees/login', [
  body('email').isEmail().withMessage('Valid email is required'),
  body('pin').isLength({ min: 4, max: 4 }).withMessage('PIN must be 4 digits')
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

    const { email, pin, device_id } = req.body;

    // Find employee
    const employee = await Employee.findOne({ 
      email: email.toLowerCase(), 
      status: 'active' 
    });

    if (!employee) {
      return res.status(401).json({
        error: 'E_INVALID_CREDENTIALS',
        message: 'Invalid email or PIN'
      });
    }

    // Verify PIN
    const isValidPin = await bcrypt.compare(pin, employee.pin_hash);
    if (!isValidPin) {
      // Log failed attempt
      await AuditLog.logEvent({
        event_type: 'employee.login_failed',
        actor_id: employee.employee_id,
        device_id,
        payload: {
          email,
          reason: 'invalid_pin'
        },
        ip_address: req.ip,
        tenant_id: employee.tenant_id,
        severity: 'medium'
      });

      return res.status(401).json({
        error: 'E_INVALID_CREDENTIALS',
        message: 'Invalid email or PIN'
      });
    }

    // Generate JWT
    const token = jwt.sign(
      {
        employee_id: employee.employee_id,
        tenant_id: employee.tenant_id,
        email: employee.email,
        name: employee.name
      },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );

    // Log successful login
    await AuditLog.logEvent({
      event_type: 'employee.login',
      actor_id: employee.employee_id,
      device_id,
      payload: {
        email,
        device_id
      },
      ip_address: req.ip,
      tenant_id: employee.tenant_id
    });

    res.json({
      access_token: token,
      token_type: 'Bearer',
      expires_in: 24 * 60 * 60, // 24 hours in seconds
      employee: {
        employee_id: employee.employee_id,
        name: employee.name,
        email: employee.email,
        tenant_id: employee.tenant_id
      }
    });

  } catch (error) {
    next(error);
  }
});

// PIN verification for approvals
router.post('/approvals/verify_pin', [
  authMiddleware,
  body('pin').isLength({ min: 4, max: 4 }).withMessage('PIN must be 4 digits'),
  body('action').notEmpty().withMessage('Action is required')
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

    const { pin, action } = req.body;
    const { employee_id } = req;

    // Find employee
    const employee = await Employee.findOne({ 
      employee_id, 
      status: 'active' 
    });

    if (!employee) {
      return res.status(401).json({
        error: 'E_EMPLOYEE_NOT_FOUND',
        message: 'Employee not found'
      });
    }

    // Verify PIN
    const isValidPin = await bcrypt.compare(pin, employee.pin_hash);
    if (!isValidPin) {
      // Log failed attempt
      await AuditLog.logEvent({
        event_type: 'approval.pin_failed',
        actor_id: employee.employee_id,
        device_id: req.device_id,
        payload: {
          action,
          reason: 'invalid_pin'
        },
        ip_address: req.ip,
        store_id: req.store_id,
        tenant_id: req.tenant_id,
        severity: 'high'
      });

      return res.status(401).json({
        error: 'E_INVALID_PIN',
        message: 'Invalid PIN'
      });
    }

    // Log successful verification
    await AuditLog.logEvent({
      event_type: 'approval.pin_verified',
      actor_id: employee.employee_id,
      device_id: req.device_id,
      payload: {
        action
      },
      ip_address: req.ip,
      store_id: req.store_id,
      tenant_id: req.tenant_id
    });

    res.json({
      verified: true,
      employee: {
        employee_id: employee.employee_id,
        name: employee.name
      }
    });

  } catch (error) {
    next(error);
  }
});

// Get current device info
router.get('/devices/me', authMiddleware, async (req, res, next) => {
  try {
    const device = await Device.findOne({ device_id: req.device_id })
      .populate('tenant_id store_id');

    if (!device) {
      return res.status(404).json({
        error: 'E_DEVICE_NOT_FOUND',
        message: 'Device not found'
      });
    }

    res.json({
      device_id: device.device_id,
      name: device.name,
      type: device.type,
      capabilities: device.capabilities,
      status: device.status,
      tenant: {
        tenant_id: device.tenant_id.tenant_id,
        name: device.tenant_id.name
      },
      store: {
        store_id: device.store_id.store_id,
        name: device.store_id.name
      },
      last_seen: device.last_seen
    });

  } catch (error) {
    next(error);
  }
});

module.exports = router;
