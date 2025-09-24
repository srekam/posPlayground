const express = require('express');
const router = express.Router();

// Import controllers
const providerReportingController = require('../controllers/providerReporting');

// Middleware imports (you'll need to create these)
// const providerAuth = require('../middleware/providerAuth');
// const requirePermission = require('../middleware/requirePermission');

// Mock middleware for now - replace with actual implementation
const providerAuth = (req, res, next) => {
  // Mock authentication - replace with actual JWT verification
  req.user = { user_id: 'provider_user_01', role: 'Provider-Admin' };
  next();
};

const requirePermission = (permission) => {
  return (req, res, next) => {
    // Mock permission check - replace with actual RBAC
    if (req.user && req.user.role === 'Provider-Admin') {
      next();
    } else {
      res.status(403).json({
        success: false,
        error: 'E_INSUFFICIENT_PERMISSIONS',
        message: `Permission required: ${permission}`
      });
    }
  };
};

// Apply provider authentication to all routes
router.use(providerAuth);

// Report Template Management
router.get('/reports/templates', 
  requirePermission('provider.reports.read'),
  providerReportingController.getReportTemplates
);

router.post('/reports/templates', 
  requirePermission('provider.reports.create'),
  providerReportingController.createReportTemplate
);

router.get('/reports/templates/:template_id', 
  requirePermission('provider.reports.read'),
  providerReportingController.getReportTemplate
);

// Report Generation
router.post('/reports/templates/:template_id/generate', 
  requirePermission('provider.reports.generate'),
  providerReportingController.generateReport
);

router.get('/reports/instances/:instance_id/status', 
  requirePermission('provider.reports.read'),
  providerReportingController.getReportStatus
);

router.get('/reports/instances/:instance_id/data', 
  requirePermission('provider.reports.read'),
  providerReportingController.getReportData
);

// Dashboard Management
router.get('/dashboards', 
  requirePermission('provider.dashboards.read'),
  providerReportingController.getDashboards
);

router.post('/dashboards', 
  requirePermission('provider.dashboards.create'),
  providerReportingController.createDashboard
);

router.get('/dashboards/:template_id', 
  requirePermission('provider.dashboards.read'),
  providerReportingController.getDashboard
);

// Widget Management
router.get('/widgets', 
  requirePermission('provider.widgets.read'),
  providerReportingController.getWidgets
);

router.post('/widgets', 
  requirePermission('provider.widgets.create'),
  providerReportingController.createWidget
);

// Analytics
router.get('/analytics/:template_id', 
  requirePermission('provider.analytics.read'),
  providerReportingController.getAnalytics
);

// Export Management
router.post('/reports/instances/:instance_id/export', 
  requirePermission('provider.reports.export'),
  providerReportingController.exportReport
);

router.get('/exports/download/:file_id', 
  requirePermission('provider.exports.download'),
  providerReportingController.downloadExport
);

// Reporting Statistics
router.get('/reporting/statistics', 
  requirePermission('provider.reports.read'),
  providerReportingController.getReportingStatistics
);

module.exports = router;
