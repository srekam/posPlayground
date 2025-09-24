const { Tenant, Store, Device } = require('../models/core');
const { ProviderMetrics, UsageCounter, ProviderAlert } = require('../models/provider');
const { AnalyticsCache } = require('../models/reporting');
const moment = require('moment-timezone');

class AnalyticsEngine {
  constructor() {
    this.timezone = process.env.TZ || 'Asia/Bangkok';
    this.logger = require('../utils/logger');
  }

  /**
   * Get aggregated metrics based on type, period, and filters
   * @param {string} metricType - 'fleet', 'sales', 'usage', 'alerts', 'performance'
   * @param {object} params - Query parameters
   * @returns {Promise<Array>} Aggregated metrics
   */
  async getAggregatedMetrics(metricType, params = {}) {
    const cacheKey = `analytics_${metricType}_${JSON.stringify(params)}`;
    
    // Check cache first
    const cached = await this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const startDate = moment(params.start_date || moment().subtract(30, 'days'), this.timezone);
      const endDate = moment(params.end_date || moment(), this.timezone);
      
      const matchFilter = {
        date: {
          $gte: startDate.toDate(),
          $lte: endDate.toDate()
        }
      };

      if (params.tenant_id) {
        matchFilter.tenant_id = params.tenant_id;
      }

      const groupStage = this.buildGroupStage(params.group_by || 'day');
      const projectStage = this.buildProjectStage(params.group_by || 'day');
      const metricsToSum = this.getMetricsForType(metricType, params.metrics);

      // Add metrics to group stage
      metricsToSum.forEach(metric => {
        if (['refund_rate', 'reprint_rate', 'webhook_success_rate', 'uptime_percent', 'error_rate'].includes(metric)) {
          groupStage[metric] = { $avg: `$metrics.${metric}` };
        } else {
          groupStage[metric] = { $sum: `$metrics.${metric}` };
        }
        projectStage[metric] = 1;
      });

      const pipeline = [
        { $match: matchFilter },
        { $group: groupStage },
        { $project: projectStage }
      ];

      if (params.group_by === 'day' || params.group_by === 'month') {
        pipeline.push({ $sort: { date: 1 } });
      } else if (params.group_by === 'tenant') {
        pipeline.push({ $sort: { tenant_id: 1 } });
      }

      const results = await ProviderMetrics.aggregate(pipeline);

      // Format results
      const formattedResults = results.map(result => ({
        ...result,
        date: result.date ? moment(result.date).format('YYYY-MM-DD') : undefined,
        month: result.month ? moment(result.month).format('YYYY-MM') : undefined
      }));

      // Cache results
      await this.setCache(cacheKey, formattedResults, 300); // 5 minutes

      return formattedResults;
    } catch (error) {
      this.logger.error('AnalyticsEngine.getAggregatedMetrics error:', error);
      throw error;
    }
  }

  /**
   * Get raw data from a specific collection with filters and pagination
   * @param {string} collectionName - Collection name
   * @param {object} params - Query parameters
   * @returns {Promise<object>} Paginated data
   */
  async getRawData(collectionName, params = {}) {
    try {
      const Model = this.getModelForCollection(collectionName);
      if (!Model) {
        throw new Error(`Invalid collection: ${collectionName}`);
      }

      const filter = params.filter || {};
      const options = {
        skip: ((params.page || 1) - 1) * (params.limit || 10),
        limit: parseInt(params.limit || 10),
        sort: params.sort || { _id: -1 }
      };

      const data = await Model.find(filter, null, options).lean();
      const total = await Model.countDocuments(filter);

      return {
        data,
        total,
        page: params.page || 1,
        limit: params.limit || 10
      };
    } catch (error) {
      this.logger.error('AnalyticsEngine.getRawData error:', error);
      throw error;
    }
  }

  /**
   * Run custom aggregation pipeline
   * @param {string} collectionName - Collection name
   * @param {Array} pipeline - MongoDB aggregation pipeline
   * @returns {Promise<Array>} Aggregation results
   */
  async runCustomAggregation(collectionName, pipeline) {
    try {
      const Model = this.getModelForCollection(collectionName);
      if (!Model) {
        throw new Error(`Invalid collection: ${collectionName}`);
      }

      return await Model.aggregate(pipeline);
    } catch (error) {
      this.logger.error('AnalyticsEngine.runCustomAggregation error:', error);
      throw error;
    }
  }

  /**
   * Analyze trends in data
   * @param {Array} data - Time series data
   * @param {string} metricField - Field to analyze
   * @returns {object} Trend analysis
   */
  analyzeTrends(data, metricField) {
    if (!data || data.length < 2) {
      return { trend: 'insufficient_data', confidence: 0 };
    }

    const values = data.map(item => item[metricField]).filter(val => val != null);
    if (values.length < 2) {
      return { trend: 'insufficient_data', confidence: 0 };
    }

    // Simple linear regression
    const n = values.length;
    const x = Array.from({ length: n }, (_, i) => i);
    const y = values;

    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    // Calculate confidence based on R-squared
    const yMean = sumY / n;
    const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - yMean, 2), 0);
    const ssResidual = y.reduce((sum, yi, i) => {
      const predicted = slope * x[i] + intercept;
      return sum + Math.pow(yi - predicted, 2);
    }, 0);
    const rSquared = 1 - (ssResidual / ssTotal);

    let trend = 'stable';
    if (slope > 0.1) trend = 'increasing';
    else if (slope < -0.1) trend = 'decreasing';

    return {
      trend,
      slope,
      confidence: Math.max(0, Math.min(1, rSquared)),
      rSquared
    };
  }

  /**
   * Generate forecast based on historical data
   * @param {Array} data - Historical data
   * @param {string} metricField - Field to forecast
   * @param {number} periods - Number of periods to forecast
   * @returns {Array} Forecast values
   */
  generateForecast(data, metricField, periods = 7) {
    if (!data || data.length < 3) {
      return [];
    }

    const values = data.map(item => item[metricField]).filter(val => val != null);
    if (values.length < 3) {
      return [];
    }

    // Simple linear regression for forecasting
    const n = values.length;
    const x = Array.from({ length: n }, (_, i) => i);
    const y = values;

    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    // Generate forecast
    const forecast = [];
    for (let i = 0; i < periods; i++) {
      const predictedValue = slope * (n + i) + intercept;
      forecast.push(Math.max(0, predictedValue)); // Ensure non-negative values
    }

    return forecast;
  }

  /**
   * Generate insights from data
   * @param {Array} data - Data to analyze
   * @param {object} config - Insight configuration
   * @returns {Array} Generated insights
   */
  generateInsights(data, config = {}) {
    const insights = [];
    const { highThreshold = 1000, lowThreshold = 100 } = config;

    if (!data || data.length === 0) {
      return insights;
    }

    // Analyze trends
    Object.keys(data[0] || {}).forEach(field => {
      if (typeof data[0][field] === 'number') {
        const trendAnalysis = this.analyzeTrends(data, field);
        
        if (trendAnalysis.trend === 'increasing' && trendAnalysis.confidence > 0.7) {
          insights.push({
            type: 'trending_up',
            metric: field,
            message: `${field} is trending upward`,
            confidence: trendAnalysis.confidence
          });
        } else if (trendAnalysis.trend === 'decreasing' && trendAnalysis.confidence > 0.7) {
          insights.push({
            type: 'trending_down',
            metric: field,
            message: `${field} is trending downward`,
            confidence: trendAnalysis.confidence
          });
        }
      }
    });

    // Check for high/low values
    const latestData = data[data.length - 1];
    if (latestData) {
      Object.keys(latestData).forEach(field => {
        const value = latestData[field];
        if (typeof value === 'number') {
          if (value > highThreshold) {
            insights.push({
              type: 'high_value',
              metric: field,
              value,
              message: `High ${field} detected: ${value}`,
              threshold: highThreshold
            });
          } else if (value < lowThreshold) {
            insights.push({
              type: 'low_value',
              metric: field,
              value,
              message: `Low ${field} detected: ${value}`,
              threshold: lowThreshold
            });
          }
        }
      });
    }

    return insights;
  }

  // Helper methods
  buildGroupStage(groupBy) {
    const groupStage = { _id: null };

    switch (groupBy) {
      case 'day':
        groupStage._id = {
          year: { $year: '$date' },
          month: { $month: '$date' },
          day: { $dayOfMonth: '$date' }
        };
        break;
      case 'month':
        groupStage._id = {
          year: { $year: '$date' },
          month: { $month: '$date' }
        };
        break;
      case 'tenant':
        groupStage._id = '$tenant_id';
        break;
      default:
        groupStage._id = null;
    }

    return groupStage;
  }

  buildProjectStage(groupBy) {
    const projectStage = { _id: 0 };

    switch (groupBy) {
      case 'day':
        projectStage.date = {
          $dateFromParts: {
            year: '$_id.year',
            month: '$_id.month',
            day: '$_id.day',
            timezone: this.timezone
          }
        };
        break;
      case 'month':
        projectStage.month = {
          $dateFromParts: {
            year: '$_id.year',
            month: '$_id.month',
            day: 1,
            timezone: this.timezone
          }
        };
        break;
      case 'tenant':
        projectStage.tenant_id = '$_id';
        break;
    }

    return projectStage;
  }

  getMetricsForType(metricType, specificMetrics = []) {
    if (specificMetrics.length > 0) {
      return specificMetrics;
    }

    const metricsMap = {
      fleet: ['tenants_active', 'stores_active', 'devices_online', 'devices_total', 'uptime_percent'],
      sales: ['sales_24h', 'redemptions_24h', 'refund_rate', 'reprint_rate'],
      usage: ['api_calls_24h', 'webhook_calls_24h', 'webhook_success_rate'],
      alerts: ['incidents_open', 'critical_alerts', 'medium_alerts', 'low_alerts'],
      performance: ['sync_lag_p95', 'sync_lag_p99', 'response_time_p95', 'error_rate']
    };

    return metricsMap[metricType] || [];
  }

  getModelForCollection(collectionName) {
    const models = {
      tenants: Tenant,
      stores: Store,
      devices: Device,
      provider_alerts: ProviderAlert,
      usage_counters: UsageCounter,
      provider_metrics_daily: ProviderMetrics
    };

    return models[collectionName];
  }

  async getFromCache(key) {
    try {
      const cached = await AnalyticsCache.findOne({ 
        cache_key: key,
        expires_at: { $gt: new Date() }
      });
      
      if (cached) {
        await AnalyticsCache.updateOne(
          { _id: cached._id },
          { $inc: { hit_count: 1 } }
        );
        return cached.data;
      }
      return null;
    } catch (error) {
      this.logger.error('AnalyticsEngine.getFromCache error:', error);
      return null;
    }
  }

  async setCache(key, data, ttlSeconds = 300) {
    try {
      await AnalyticsCache.updateOne(
        { cache_key: key },
        {
          cache_key: key,
          data,
          expires_at: new Date(Date.now() + ttlSeconds * 1000),
          hit_count: 0
        },
        { upsert: true }
      );
    } catch (error) {
      this.logger.error('AnalyticsEngine.setCache error:', error);
    }
  }
}

module.exports = AnalyticsEngine;
