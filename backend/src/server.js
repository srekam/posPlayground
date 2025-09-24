const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const logger = require('./utils/logger');
const errorHandler = require('./middleware/errorHandler');
const authMiddleware = require('./middleware/auth');

// Import routes
const authRoutes = require('./routes/auth');
const deviceRoutes = require('./routes/devices');
const userRoutes = require('./routes/users');
const roleRoutes = require('./routes/roles');
const catalogRoutes = require('./routes/catalog');
const salesRoutes = require('./routes/sales');
const ticketsRoutes = require('./routes/tickets');
const shiftsRoutes = require('./routes/shifts');
const reportsRoutes = require('./routes/reports');
const settingsRoutes = require('./routes/settings');
const webhooksRoutes = require('./routes/webhooks');
const syncRoutes = require('./routes/sync');

const app = express();
const PORT = process.env.PORT || 48080;

// Security middleware
app.use(helmet());
app.use(compression());

// CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3000', 'http://localhost:8080'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  message: {
    error: 'E_RATE_LIMIT',
    message: 'Too many requests from this IP, please try again later.'
  }
});
app.use(limiter);

// Logging
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.API_VERSION || 'v1',
    environment: process.env.NODE_ENV || 'development'
  });
});

// API routes
app.use(`/${process.env.API_VERSION || 'v1'}/auth`, authRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/devices`, deviceRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/users`, userRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/roles`, roleRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/catalog`, catalogRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/sales`, salesRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/tickets`, ticketsRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/shifts`, shiftsRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/reports`, reportsRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/settings`, settingsRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/webhooks`, webhooksRoutes);
app.use(`/${process.env.API_VERSION || 'v1'}/sync`, syncRoutes);

// Admin UI static files (if exists)
app.use('/admin', express.static('admin-ui/dist'));

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'E_NOT_FOUND',
    message: 'Endpoint not found',
    path: req.originalUrl
  });
});

// Database connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/playpark', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => {
  logger.info('Connected to MongoDB');
})
.catch((error) => {
  logger.error('MongoDB connection error:', error);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  mongoose.connection.close().then(() => {
    logger.info('MongoDB connection closed');
    process.exit(0);
  }).catch((error) => {
    logger.error('Error closing MongoDB connection:', error);
    process.exit(1);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  mongoose.connection.close().then(() => {
    logger.info('MongoDB connection closed');
    process.exit(0);
  }).catch((error) => {
    logger.error('Error closing MongoDB connection:', error);
    process.exit(1);
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`PlayPark Backend API running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`API Version: ${process.env.API_VERSION || 'v1'}`);
});

module.exports = app;
