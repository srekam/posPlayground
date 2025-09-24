const jwt = require('jsonwebtoken');
const logger = require('../utils/logger');
const { Device, Employee } = require('../models/core');

// Error handler middleware
const errorHandler = (err, req, res, next) => {
  logger.error('Error:', err);

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(e => e.message);
    return res.status(400).json({
      error: 'E_VALIDATION',
      message: 'Validation failed',
      details: errors
    });
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    return res.status(400).json({
      error: 'E_DUPLICATE',
      message: `${field} already exists`,
      field: field
    });
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: 'E_INVALID_TOKEN',
      message: 'Invalid token'
    });
  }

  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      error: 'E_TOKEN_EXPIRED',
      message: 'Token expired'
    });
  }

  // Default error
  res.status(err.status || 500).json({
    error: err.code || 'E_INTERNAL_ERROR',
    message: err.message || 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

// Authentication middleware
const authMiddleware = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'E_NO_TOKEN',
        message: 'No token provided'
      });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Check if device exists and is active
    const device = await Device.findOne({ 
      device_id: decoded.device_id,
      status: 'active'
    }).populate('tenant_id store_id');

    if (!device) {
      return res.status(401).json({
        error: 'E_DEVICE_SUSPENDED',
        message: 'Device not found or suspended'
      });
    }

    // Update last seen
    device.last_seen = new Date();
    await device.save();

    req.device = device;
    req.tenant_id = device.tenant_id;
    req.store_id = device.store_id;
    req.device_id = device.device_id;
    
    next();
  } catch (error) {
    logger.error('Auth middleware error:', error);
    next(error);
  }
};

// Employee authentication middleware
const employeeAuthMiddleware = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'E_NO_TOKEN',
        message: 'No employee token provided'
      });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Check if employee exists and is active
    const employee = await Employee.findOne({ 
      employee_id: decoded.employee_id,
      status: 'active'
    });

    if (!employee) {
      return res.status(401).json({
        error: 'E_EMPLOYEE_SUSPENDED',
        message: 'Employee not found or suspended'
      });
    }

    req.employee = employee;
    req.employee_id = employee.employee_id;
    req.tenant_id = employee.tenant_id;
    
    next();
  } catch (error) {
    logger.error('Employee auth middleware error:', error);
    next(error);
  }
};

// Permission middleware
const requirePermission = (permission) => {
  return async (req, res, next) => {
    try {
      // This would check employee permissions
      // For now, we'll implement basic permission checking
      // In a full implementation, you'd check against the employee's roles
      
      if (!req.employee) {
        return res.status(401).json({
          error: 'E_NO_EMPLOYEE',
          message: 'Employee authentication required'
        });
      }

      // TODO: Implement proper permission checking based on employee roles
      // For now, allow all authenticated employees
      next();
    } catch (error) {
      logger.error('Permission middleware error:', error);
      next(error);
    }
  };
};

// Request ID middleware
const requestIdMiddleware = (req, res, next) => {
  req.request_id = require('ulid').ulid();
  res.setHeader('X-Request-ID', req.request_id);
  next();
};

// Response time middleware
const responseTimeMiddleware = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info(`${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`, {
      request_id: req.request_id,
      device_id: req.device_id,
      employee_id: req.employee_id
    });
  });
  
  next();
};

// Validation middleware
const validateRequest = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'E_VALIDATION',
        message: 'Request validation failed',
        details: error.details.map(d => d.message)
      });
    }
    next();
  };
};

// Idempotency middleware
const idempotencyMiddleware = (req, res, next) => {
  const idempotencyKey = req.headers['idempotency-key'];
  
  if (!idempotencyKey) {
    return res.status(400).json({
      error: 'E_NO_IDEMPOTENCY_KEY',
      message: 'Idempotency key required for this operation'
    });
  }
  
  req.idempotency_key = idempotencyKey;
  next();
};

module.exports = {
  errorHandler,
  authMiddleware,
  employeeAuthMiddleware,
  requirePermission,
  requestIdMiddleware,
  responseTimeMiddleware,
  validateRequest,
  idempotencyMiddleware
};
