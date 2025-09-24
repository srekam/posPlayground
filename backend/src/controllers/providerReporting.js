const { ReportTemplate, ReportInstance, DashboardWidget, ExportFile } = require('../models/reporting');
const AnalyticsEngine = require('../services/analyticsEngine');
const logger = require('../utils/logger');
const { ulid } = require('ulid');
const fs = require('fs').promises;
const path = require('path');

class ProviderReportingController {
  constructor() {
    this.analyticsEngine = new AnalyticsEngine();
    this.exportPath = process.env.EXPORT_STORAGE_PATH || '/tmp/exports';
  }

  // Report Template Management
  async getReportTemplates(req, res) {
    try {
      const { category, type, scope, page = 1, limit = 10 } = req.query;
      
      const filter = {};
      if (category) filter.category = category;
      if (type) filter.type = type;
      if (scope) filter.scope = scope;

      const templates = await ReportTemplate.find(filter)
        .sort({ created_at: -1 })
        .skip((page - 1) * limit)
        .limit(parseInt(limit))
        .lean();

      const total = await ReportTemplate.countDocuments(filter);

      res.json({
        success: true,
        data: {
          templates,
          pagination: {
            page: parseInt(page),
            limit: parseInt(limit),
            total,
            pages: Math.ceil(total / limit)
          }
        }
      });
    } catch (error) {
      logger.error('ProviderReportingController.getReportTemplates error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORT_TEMPLATES_FETCH_FAILED',
        message: 'Failed to fetch report templates'
      });
    }
  }

  async createReportTemplate(req, res) {
    try {
      const { name, description, category, type, scope, config, permissions, tags } = req.body;
      const createdBy = req.user?.user_id;

      const template = new ReportTemplate({
        name,
        description,
        category,
        type,
        scope,
        config,
        permissions,
        tags,
        created_by: createdBy
      });

      await template.save();

      res.status(201).json({
        success: true,
        data: template
      });
    } catch (error) {
      logger.error('ProviderReportingController.createReportTemplate error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORT_TEMPLATE_CREATE_FAILED',
        message: 'Failed to create report template'
      });
    }
  }

  async getReportTemplate(req, res) {
    try {
      const { template_id } = req.params;

      const template = await ReportTemplate.findOne({ template_id });
      if (!template) {
        return res.status(404).json({
          success: false,
          error: 'E_REPORT_TEMPLATE_NOT_FOUND',
          message: 'Report template not found'
        });
      }

      res.json({
        success: true,
        data: template
      });
    } catch (error) {
      logger.error('ProviderReportingController.getReportTemplate error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORT_TEMPLATE_FETCH_FAILED',
        message: 'Failed to fetch report template'
      });
    }
  }

  // Report Generation
  async generateReport(req, res) {
    try {
      const { template_id } = req.params;
      const { parameters } = req.body;
      const generatedBy = req.user?.user_id;

      const template = await ReportTemplate.findOne({ template_id });
      if (!template) {
        return res.status(404).json({
          success: false,
          error: 'E_REPORT_TEMPLATE_NOT_FOUND',
          message: 'Report template not found'
        });
      }

      const instance = new ReportInstance({
        template_id,
        parameters,
        generated_by: generatedBy,
        status: 'generating'
      });

      await instance.save();

      // Start background report generation (in real implementation, this would be queued)
      this.generateReportData(instance.instance_id, template, parameters)
        .catch(error => {
          logger.error(`Report generation failed for instance ${instance.instance_id}:`, error);
        });

      res.status(202).json({
        success: true,
        data: {
          instance_id: instance.instance_id,
          status: 'generating',
          message: 'Report generation started'
        }
      });
    } catch (error) {
      logger.error('ProviderReportingController.generateReport error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORT_GENERATION_FAILED',
        message: 'Failed to start report generation'
      });
    }
  }

  async getReportStatus(req, res) {
    try {
      const { instance_id } = req.params;

      const instance = await ReportInstance.findOne({ instance_id });
      if (!instance) {
        return res.status(404).json({
          success: false,
          error: 'E_REPORT_INSTANCE_NOT_FOUND',
          message: 'Report instance not found'
        });
      }

      res.json({
        success: true,
        data: instance
      });
    } catch (error) {
      logger.error('ProviderReportingController.getReportStatus error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORT_STATUS_FETCH_FAILED',
        message: 'Failed to fetch report status'
      });
    }
  }

  async getReportData(req, res) {
    try {
      const { instance_id } = req.params;

      const instance = await ReportInstance.findOne({ instance_id });
      if (!instance) {
        return res.status(404).json({
          success: false,
          error: 'E_REPORT_INSTANCE_NOT_FOUND',
          message: 'Report instance not found'
        });
      }

      if (instance.status !== 'completed') {
        return res.status(400).json({
          success: false,
          error: 'E_REPORT_NOT_COMPLETED',
          message: `Report status: ${instance.status}`
        });
      }

      // In a real implementation, this would fetch from the actual data storage
      const reportData = {
        instance_id: instance.instance_id,
        template_id: instance.template_id,
        parameters: instance.parameters,
        generated_at: instance.generated_at,
        data: instance.report_data_ref || 'Report data would be here'
      };

      res.json({
        success: true,
        data: reportData
      });
    } catch (error) {
      logger.error('ProviderReportingController.getReportData error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORT_DATA_FETCH_FAILED',
        message: 'Failed to fetch report data'
      });
    }
  }

  // Dashboard Management
  async getDashboards(req, res) {
    try {
      const { page = 1, limit = 10 } = req.query;

      const dashboards = await ReportTemplate.find({ type: 'dashboard' })
        .sort({ created_at: -1 })
        .skip((page - 1) * limit)
        .limit(parseInt(limit))
        .lean();

      const total = await ReportTemplate.countDocuments({ type: 'dashboard' });

      res.json({
        success: true,
        data: {
          dashboards,
          pagination: {
            page: parseInt(page),
            limit: parseInt(limit),
            total,
            pages: Math.ceil(total / limit)
          }
        }
      });
    } catch (error) {
      logger.error('ProviderReportingController.getDashboards error:', error);
      res.status(500).json({
        success: false,
        error: 'E_DASHBOARDS_FETCH_FAILED',
        message: 'Failed to fetch dashboards'
      });
    }
  }

  async createDashboard(req, res) {
    try {
      const { name, description, config, permissions, tags } = req.body;
      const createdBy = req.user?.user_id;

      const dashboard = new ReportTemplate({
        name,
        description,
        category: 'fleet',
        type: 'dashboard',
        scope: 'global',
        config,
        permissions,
        tags,
        created_by: createdBy
      });

      await dashboard.save();

      res.status(201).json({
        success: true,
        data: dashboard
      });
    } catch (error) {
      logger.error('ProviderReportingController.createDashboard error:', error);
      res.status(500).json({
        success: false,
        error: 'E_DASHBOARD_CREATE_FAILED',
        message: 'Failed to create dashboard'
      });
    }
  }

  async getDashboard(req, res) {
    try {
      const { template_id } = req.params;
      const { tenant_id, filters } = req.query;

      const dashboard = await ReportTemplate.findOne({ template_id, type: 'dashboard' });
      if (!dashboard) {
        return res.status(404).json({
          success: false,
          error: 'E_DASHBOARD_NOT_FOUND',
          message: 'Dashboard not found'
        });
      }

      // Get widgets for this dashboard
      const widgets = await DashboardWidget.find({ dashboard_id: template_id })
        .sort({ order: 1 })
        .lean();

      // Build dashboard data
      const dashboardData = {
        dashboard_id: template_id,
        name: dashboard.name,
        config: dashboard.config,
        widgets: []
      };

      // Fetch data for each widget
      for (const widget of widgets) {
        try {
          const widgetData = await this.fetchWidgetData(widget, { tenant_id, ...filters });
          dashboardData.widgets.push({
            widget_id: widget.widget_id,
            name: widget.name,
            type: widget.type,
            config: widget.config,
            data: widgetData
          });
        } catch (error) {
          logger.error(`Failed to fetch data for widget ${widget.widget_id}:`, error);
          dashboardData.widgets.push({
            widget_id: widget.widget_id,
            name: widget.name,
            type: widget.type,
            config: widget.config,
            data: { error: 'Failed to load data' }
          });
        }
      }

      res.json({
        success: true,
        data: dashboardData
      });
    } catch (error) {
      logger.error('ProviderReportingController.getDashboard error:', error);
      res.status(500).json({
        success: false,
        error: 'E_DASHBOARD_FETCH_FAILED',
        message: 'Failed to fetch dashboard data'
      });
    }
  }

  // Widget Management
  async getWidgets(req, res) {
    try {
      const { dashboard_id, type, page = 1, limit = 10 } = req.query;

      const filter = {};
      if (dashboard_id) filter.dashboard_id = dashboard_id;
      if (type) filter.type = type;

      const widgets = await DashboardWidget.find(filter)
        .sort({ order: 1 })
        .skip((page - 1) * limit)
        .limit(parseInt(limit))
        .lean();

      const total = await DashboardWidget.countDocuments(filter);

      res.json({
        success: true,
        data: {
          widgets,
          pagination: {
            page: parseInt(page),
            limit: parseInt(limit),
            total,
            pages: Math.ceil(total / limit)
          }
        }
      });
    } catch (error) {
      logger.error('ProviderReportingController.getWidgets error:', error);
      res.status(500).json({
        success: false,
        error: 'E_WIDGETS_FETCH_FAILED',
        message: 'Failed to fetch widgets'
      });
    }
  }

  async createWidget(req, res) {
    try {
      const { dashboard_id, name, type, title, config, data_source, position, order } = req.body;
      const createdBy = req.user?.user_id;

      const widget = new DashboardWidget({
        dashboard_id,
        name,
        type,
        title,
        config,
        data_source,
        position,
        order,
        created_by: createdBy
      });

      await widget.save();

      res.status(201).json({
        success: true,
        data: widget
      });
    } catch (error) {
      logger.error('ProviderReportingController.createWidget error:', error);
      res.status(500).json({
        success: false,
        error: 'E_WIDGET_CREATE_FAILED',
        message: 'Failed to create widget'
      });
    }
  }

  // Analytics
  async getAnalytics(req, res) {
    try {
      const { template_id } = req.params;
      const { tenant_id, filters } = req.query;

      const template = await ReportTemplate.findOne({ template_id });
      if (!template) {
        return res.status(404).json({
          success: false,
          error: 'E_ANALYTICS_TEMPLATE_NOT_FOUND',
          message: 'Analytics template not found'
        });
      }

      const params = { tenant_id, ...filters };
      const analyticsData = await this.analyticsEngine.getAggregatedMetrics(
        template.category,
        params
      );

      // Generate insights
      const insights = this.analyticsEngine.generateInsights(analyticsData);

      // Generate trends
      const trends = {};
      if (analyticsData.length > 0) {
        Object.keys(analyticsData[0] || {}).forEach(field => {
          if (typeof analyticsData[0][field] === 'number') {
            trends[field] = this.analyticsEngine.analyzeTrends(analyticsData, field);
          }
        });
      }

      // Generate forecasts
      const forecasts = {};
      if (analyticsData.length > 0) {
        Object.keys(analyticsData[0] || {}).forEach(field => {
          if (typeof analyticsData[0][field] === 'number') {
            forecasts[field] = this.analyticsEngine.generateForecast(analyticsData, field, 7);
          }
        });
      }

      res.json({
        success: true,
        data: {
          template_id,
          data: analyticsData,
          insights,
          trends,
          forecasts,
          generated_at: new Date().toISOString()
        }
      });
    } catch (error) {
      logger.error('ProviderReportingController.getAnalytics error:', error);
      res.status(500).json({
        success: false,
        error: 'E_ANALYTICS_FETCH_FAILED',
        message: 'Failed to fetch analytics data'
      });
    }
  }

  // Export Management
  async exportReport(req, res) {
    try {
      const { instance_id } = req.params;
      const { format = 'csv' } = req.body;
      const requestedBy = req.user?.user_id;

      const instance = await ReportInstance.findOne({ instance_id });
      if (!instance) {
        return res.status(404).json({
          success: false,
          error: 'E_REPORT_INSTANCE_NOT_FOUND',
          message: 'Report instance not found'
        });
      }

      if (instance.status !== 'completed') {
        return res.status(400).json({
          success: false,
          error: 'E_REPORT_NOT_COMPLETED',
          message: `Report status: ${instance.status}`
        });
      }

      // Update export status
      instance.export_status = 'exporting';
      await instance.save();

      // Generate export file (simplified implementation)
      const exportFile = await this.generateExportFile(instance, format, requestedBy);

      res.status(202).json({
        success: true,
        data: {
          export_file_id: exportFile.file_id,
          format,
          status: 'exporting',
          message: 'Export generation started'
        }
      });
    } catch (error) {
      logger.error('ProviderReportingController.exportReport error:', error);
      res.status(500).json({
        success: false,
        error: 'E_EXPORT_GENERATION_FAILED',
        message: 'Failed to start export generation'
      });
    }
  }

  async downloadExport(req, res) {
    try {
      const { file_id } = req.params;

      const exportFile = await ExportFile.findOne({ file_id });
      if (!exportFile) {
        return res.status(404).json({
          success: false,
          error: 'E_EXPORT_FILE_NOT_FOUND',
          message: 'Export file not found'
        });
      }

      if (exportFile.expires_at < new Date()) {
        return res.status(410).json({
          success: false,
          error: 'E_EXPORT_FILE_EXPIRED',
          message: 'Export file has expired'
        });
      }

      // Update download count
      await ExportFile.updateOne(
        { _id: exportFile._id },
        { $inc: { download_count: 1 } }
      );

      // Set appropriate headers
      res.setHeader('Content-Type', exportFile.mime_type);
      res.setHeader('Content-Disposition', `attachment; filename="export_${file_id}.${exportFile.format}"`);
      res.setHeader('Content-Length', exportFile.size);

      // Stream file (in real implementation, this would stream from storage)
      res.send(`Mock export file content for ${file_id}`);

    } catch (error) {
      logger.error('ProviderReportingController.downloadExport error:', error);
      res.status(500).json({
        success: false,
        error: 'E_EXPORT_DOWNLOAD_FAILED',
        message: 'Failed to download export file'
      });
    }
  }

  // Statistics
  async getReportingStatistics(req, res) {
    try {
      const [
        totalTemplates,
        totalInstances,
        totalWidgets,
        totalExports,
        recentTemplates,
        recentInstances
      ] = await Promise.all([
        ReportTemplate.countDocuments(),
        ReportInstance.countDocuments(),
        DashboardWidget.countDocuments(),
        ExportFile.countDocuments(),
        ReportTemplate.find().sort({ created_at: -1 }).limit(5).lean(),
        ReportInstance.find().sort({ created_at: -1 }).limit(5).lean()
      ]);

      const stats = {
        templates: {
          total: totalTemplates,
          by_category: await ReportTemplate.aggregate([
            { $group: { _id: '$category', count: { $sum: 1 } } }
          ]),
          by_type: await ReportTemplate.aggregate([
            { $group: { _id: '$type', count: { $sum: 1 } } }
          ])
        },
        instances: {
          total: totalInstances,
          by_status: await ReportInstance.aggregate([
            { $group: { _id: '$status', count: { $sum: 1 } } }
          ])
        },
        widgets: {
          total: totalWidgets,
          by_type: await DashboardWidget.aggregate([
            { $group: { _id: '$type', count: { $sum: 1 } } }
          ])
        },
        exports: {
          total: totalExports,
          by_format: await ExportFile.aggregate([
            { $group: { _id: '$format', count: { $sum: 1 } } }
          ])
        },
        recent: {
          templates: recentTemplates,
          instances: recentInstances
        }
      };

      res.json({
        success: true,
        data: stats
      });
    } catch (error) {
      logger.error('ProviderReportingController.getReportingStatistics error:', error);
      res.status(500).json({
        success: false,
        error: 'E_REPORTING_STATISTICS_FETCH_FAILED',
        message: 'Failed to fetch reporting statistics'
      });
    }
  }

  // Helper methods
  async generateReportData(instanceId, template, parameters) {
    try {
      const startTime = Date.now();
      
      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const reportData = {
        template_id: template.template_id,
        parameters,
        generated_at: new Date(),
        data: 'Mock report data'
      };

      await ReportInstance.updateOne(
        { instance_id: instanceId },
        {
          status: 'completed',
          completed_at: new Date(),
          report_data_ref: JSON.stringify(reportData),
          'metadata.generation_time_ms': Date.now() - startTime
        }
      );

      logger.info(`Report generation completed for instance ${instanceId}`);
    } catch (error) {
      await ReportInstance.updateOne(
        { instance_id: instanceId },
        {
          status: 'failed',
          completed_at: new Date(),
          error_message: error.message
        }
      );
      throw error;
    }
  }

  async fetchWidgetData(widget, filters = {}) {
    const { data_source } = widget;
    
    switch (data_source.type) {
      case 'database':
        return await this.analyticsEngine.getAggregatedMetrics(
          data_source.query.metric_type || 'fleet',
          { ...filters, ...data_source.query }
        );
      case 'api':
        // In real implementation, this would call internal APIs
        return { message: 'API data would be fetched here' };
      case 'calculated':
        // In real implementation, this would evaluate formulas
        return { message: 'Calculated data would be computed here' };
      default:
        throw new Error(`Unknown data source type: ${data_source.type}`);
    }
  }

  async generateExportFile(instance, format, requestedBy) {
    const fileId = ulid();
    const fileName = `export_${fileId}.${format}`;
    const filePath = path.join(this.exportPath, fileName);
    
    // Ensure export directory exists
    await fs.mkdir(this.exportPath, { recursive: true });
    
    // Generate mock file content
    const content = `Mock export content for instance ${instance.instance_id} in ${format} format`;
    await fs.writeFile(filePath, content);
    
    const stats = await fs.stat(filePath);
    
    const exportFile = new ExportFile({
      file_id: fileId,
      instance_id: instance.instance_id,
      format,
      file_path: filePath,
      mime_type: this.getMimeType(format),
      size: stats.size,
      requested_by: requestedBy
    });

    await exportFile.save();

    // Update instance with export file reference
    await ReportInstance.updateOne(
      { instance_id: instance.instance_id },
      {
        export_status: 'completed',
        export_file_id: fileId
      }
    );

    return exportFile;
  }

  getMimeType(format) {
    const mimeTypes = {
      csv: 'text/csv',
      excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      pdf: 'application/pdf',
      json: 'application/json'
    };
    return mimeTypes[format] || 'application/octet-stream';
  }
}

module.exports = new ProviderReportingController();
