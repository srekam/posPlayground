const express = require('express');
const router = express.Router();
const { Device } = require('../models/core');
const ApiKey = require('../models/api_key');
const { authMiddleware } = require('../middleware/auth');
const { body, validationResult } = require('express-validator');

// Generate API key for device
router.post('/api-key/generate', [
  body('device_id').notEmpty().withMessage('Device ID is required'),
  body('device_name').notEmpty().withMessage('Device name is required'),
  body('permissions').isArray().withMessage('Permissions must be an array'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_VALIDATION',
          message: 'Validation failed',
          details: errors.array()
        }
      });
    }

    const { device_id, device_name, permissions = ['read', 'write'] } = req.body;

    // Check if device already has an API key
    const existingApiKey = await ApiKey.findOne({ device_id });
    if (existingApiKey && !existingApiKey.expires_at) {
      return res.status(409).json({
        success: false,
        error: {
          code: 'E_API_KEY_EXISTS',
          message: 'Device already has an active API key'
        }
      });
    }

    // Generate new API key
    const apiKeyValue = generateApiKey();
    const expiresAt = new Date();
    expiresAt.setFullYear(expiresAt.getFullYear() + 1); // Expires in 1 year

    const apiKey = new ApiKey({
      api_key: apiKeyValue,
      device_id,
      device_name,
      permissions,
      expires_at: expiresAt,
      created_by: 'system',
      tenant_id: 'default', // TODO: Get from auth context
    });

    await apiKey.save();

    // Update device status
    await Device.findOneAndUpdate(
      { device_id },
      { 
        status: 'active',
        last_seen: new Date()
      },
      { upsert: true }
    );

    res.status(201).json({
      success: true,
      data: {
        api_key: apiKeyValue,
        device_id,
        device_name,
        permissions,
        created_at: apiKey.created_at,
        expires_at: apiKey.expires_at,
      }
    });
  } catch (error) {
    console.error('Error generating API key:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Validate API key
router.post('/validate-api-key', [
  body('api_key').optional(),
], async (req, res) => {
  try {
    const apiKey = req.headers['x-api-key'] || req.body.api_key;
    
    if (!apiKey) {
      return res.status(401).json({
        success: false,
        error: {
          code: 'E_NO_TOKEN',
          message: 'No API key provided'
        }
      });
    }

    const apiKeyDoc = await ApiKey.findOne({ api_key: apiKey });
    
    if (!apiKeyDoc) {
      return res.status(401).json({
        success: false,
        error: {
          code: 'E_INVALID_TOKEN',
          message: 'Invalid API key'
        }
      });
    }

    if (apiKeyDoc.expires_at && new Date() > apiKeyDoc.expires_at) {
      return res.status(401).json({
        success: false,
        error: {
          code: 'E_TOKEN_EXPIRED',
          message: 'API key has expired'
        }
      });
    }

    // Update last used timestamp
    apiKeyDoc.last_used = new Date();
    await apiKeyDoc.save();

    res.json({
      success: true,
      data: {
        device_id: apiKeyDoc.device_id,
        device_name: apiKeyDoc.device_name,
        permissions: apiKeyDoc.permissions,
        expires_at: apiKeyDoc.expires_at,
      }
    });
  } catch (error) {
    console.error('Error validating API key:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get online devices
router.get('/online', authMiddleware, async (req, res) => {
  try {
    const onlineDevices = await Device.find({
      status: 'active',
      last_seen: { $gte: new Date(Date.now() - 5 * 60 * 1000) } // Last 5 minutes
    });

    const devices = onlineDevices.map(device => ({
      device_id: device.device_id,
      device_name: device.name || 'Unknown Device',
      device_type: device.type?.toLowerCase() || 'pos',
      status: 'online',
      last_seen: device.last_seen,
      ip_address: null, // Not available in existing schema
      permissions: [], // Will be populated from API keys separately
    }));

    res.json({
      success: true,
      data: devices
    });
  } catch (error) {
    console.error('Error fetching online devices:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Get all devices
router.get('/', authMiddleware, async (req, res) => {
  try {
    const devices = await Device.find();
    
    const deviceList = devices.map(device => ({
      device_id: device.device_id,
      device_name: device.name || 'Unknown Device',
      device_type: device.type?.toLowerCase() || 'pos',
      status: device.status,
      last_seen: device.last_seen,
      ip_address: null, // Not available in existing schema
      permissions: [], // Will be populated from API keys separately
      created_at: device.created_at,
    }));

    res.json({
      success: true,
      data: deviceList
    });
  } catch (error) {
    console.error('Error fetching devices:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Register device
router.post('/register', [
  body('device_id').notEmpty().withMessage('Device ID is required'),
  body('device_name').notEmpty().withMessage('Device name is required'),
  body('device_type').optional().isIn(['POS', 'GATE', 'KIOSK', 'ADMIN']),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'E_VALIDATION',
          message: 'Validation failed',
          details: errors.array()
        }
      });
    }

    const { device_id, device_name, device_type = 'POS' } = req.body;

    const device = await Device.findOneAndUpdate(
      { device_id },
      {
        device_id,
        name: device_name,
        type: device_type,
        status: 'active',
        last_seen: new Date(),
        tenant_id: 'default', // TODO: Get from auth context
        store_id: 'default', // TODO: Get from auth context
        device_token_hash: 'temp_hash', // TODO: Generate proper hash
      },
      { upsert: true, new: true }
    );

    res.status(201).json({
      success: true,
      data: {
        device_id: device.device_id,
        device_name: device.name,
        device_type: device.type,
        status: device.status,
        created_at: device.created_at,
      }
    });
  } catch (error) {
    console.error('Error registering device:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Update device status
router.patch('/:deviceId/status', authMiddleware, [
  body('status').isIn(['active', 'suspended', 'revoked']),
], async (req, res) => {
  try {
    const { deviceId } = req.params;
    const { status } = req.body;

    const device = await Device.findOneAndUpdate(
      { device_id: deviceId },
      { 
        status,
        last_seen: new Date(),
      },
      { new: true }
    );

    if (!device) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'Device not found'
        }
      });
    }

    res.json({
      success: true,
      data: {
        device_id: device.device_id,
        device_name: device.name,
        status: device.status,
        last_seen: device.last_seen,
      }
    });
  } catch (error) {
    console.error('Error updating device status:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Revoke API key
router.delete('/api-key/:deviceId', authMiddleware, async (req, res) => {
  try {
    const { deviceId } = req.params;

    const apiKey = await ApiKey.findOne({ device_id: deviceId });
    if (!apiKey) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'E_NOT_FOUND',
          message: 'API key not found'
        }
      });
    }

    await ApiKey.findByIdAndDelete(apiKey._id);

    // Update device to suspended status
    await Device.findOneAndUpdate(
      { device_id: deviceId },
      { 
        status: 'suspended',
      }
    );

    res.json({
      success: true,
      message: 'API key revoked successfully'
    });
  } catch (error) {
    console.error('Error revoking API key:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'E_INTERNAL',
        message: 'Internal server error'
      }
    });
  }
});

// Helper function to generate API key
function generateApiKey() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

module.exports = router;