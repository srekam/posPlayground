const logger = require('../utils/logger');

// Error handler middleware
const errorHandler = (err, req, res, next) => {
  logger.error('Error:', {
    message: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    user_agent: req.get('User-Agent'),
    request_id: req.request_id,
    device_id: req.device_id,
    employee_id: req.employee_id
  });

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(e => e.message);
    return res.status(400).json({
      error: 'E_VALIDATION',
      message: 'Validation failed',
      details: errors,
      request_id: req.request_id
    });
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    return res.status(400).json({
      error: 'E_DUPLICATE',
      message: `${field} already exists`,
      field: field,
      request_id: req.request_id
    });
  }

  // Mongoose cast error
  if (err.name === 'CastError') {
    return res.status(400).json({
      error: 'E_INVALID_ID',
      message: 'Invalid ID format',
      field: err.path,
      request_id: req.request_id
    });
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: 'E_INVALID_TOKEN',
      message: 'Invalid token',
      request_id: req.request_id
    });
  }

  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      error: 'E_TOKEN_EXPIRED',
      message: 'Token expired',
      request_id: req.request_id
    });
  }

  // Custom application errors
  if (err.code) {
    return res.status(err.status || 400).json({
      error: err.code,
      message: err.message,
      ...(err.details && { details: err.details }),
      request_id: req.request_id
    });
  }

  // Default error
  res.status(err.status || 500).json({
    error: err.code || 'E_INTERNAL_ERROR',
    message: err.message || 'Internal server error',
    request_id: req.request_id,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

module.exports = errorHandler;
