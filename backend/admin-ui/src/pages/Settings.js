import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save } from '@mui/icons-material';
import axios from 'axios';

export default function Settings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [settings, setSettings] = useState({
    features: {
      kiosk: true,
      gate_binding: true,
      multi_price: true,
      webhooks: true,
      offline_sync: true,
    },
    billing: {
      plan: 'basic',
      trial_end: null,
    },
    payment_types: {
      cash: { enabled: true, fee_type: 'none', fee_amount: 0 },
      qr: { enabled: true, fee_type: 'percentage', fee_amount: 2.5 },
      card: { enabled: true, fee_type: 'percentage', fee_amount: 3.0 },
      other: { enabled: false, fee_type: 'none', fee_amount: 0 },
    },
    taxes: {
      inclusive: true,
      default_rate: 7,
    },
    receipt: {
      header: 'PlayPark Entertainment Center',
      footer: 'Thank you for your visit!',
      paper_width: 80,
    },
    access_zones: [],
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/v1/settings');
      setSettings(response.data.data);
    } catch (err) {
      console.error('Failed to fetch settings:', err);
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      await axios.put('/v1/settings', settings);
      setSuccess('Settings saved successfully');
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleFeatureChange = (feature, value) => {
    setSettings(prev => ({
      ...prev,
      features: {
        ...prev.features,
        [feature]: value
      }
    }));
  };

  const handlePaymentChange = (method, field, value) => {
    setSettings(prev => ({
      ...prev,
      payment_types: {
        ...prev.payment_types,
        [method]: {
          ...prev.payment_types[method],
          [field]: value
        }
      }
    }));
  };

  const handleTaxChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      taxes: {
        ...prev.taxes,
        [field]: value
      }
    }));
  };

  const handleReceiptChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      receipt: {
        ...prev.receipt,
        [field]: value
      }
    }));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Settings
        </Typography>
        <Button
          variant="contained"
          startIcon={<Save />}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? <CircularProgress size={24} /> : 'Save Settings'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Features */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Features
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features.kiosk}
                    onChange={(e) => handleFeatureChange('kiosk', e.target.checked)}
                  />
                }
                label="Enable Kiosk Mode"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features.gate_binding}
                    onChange={(e) => handleFeatureChange('gate_binding', e.target.checked)}
                  />
                }
                label="Enable Gate Device Binding"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features.multi_price}
                    onChange={(e) => handleFeatureChange('multi_price', e.target.checked)}
                  />
                }
                label="Enable Multi-Price Packages"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features.webhooks}
                    onChange={(e) => handleFeatureChange('webhooks', e.target.checked)}
                  />
                }
                label="Enable Webhooks"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features.offline_sync}
                    onChange={(e) => handleFeatureChange('offline_sync', e.target.checked)}
                  />
                }
                label="Enable Offline Sync"
              />
            </Box>
          </Paper>
        </Grid>

        {/* Billing */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Billing & Subscription
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Plan</InputLabel>
              <Select
                value={settings.billing.plan}
                label="Plan"
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  billing: { ...prev.billing, plan: e.target.value }
                }))}
              >
                <MenuItem value="basic">Basic</MenuItem>
                <MenuItem value="premium">Premium</MenuItem>
                <MenuItem value="enterprise">Enterprise</MenuItem>
              </Select>
            </FormControl>
            
            <Typography variant="body2" color="text.secondary">
              Trial End: {settings.billing.trial_end ? new Date(settings.billing.trial_end).toLocaleDateString() : 'N/A'}
            </Typography>
          </Paper>
        </Grid>

        {/* Payment Types */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Payment Types
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              {Object.entries(settings.payment_types).map(([method, config]) => (
                <Grid item xs={12} sm={6} md={3} key={method}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                        {method}
                      </Typography>
                      
                      <FormControlLabel
                        control={
                          <Switch
                            checked={config.enabled}
                            onChange={(e) => handlePaymentChange(method, 'enabled', e.target.checked)}
                          />
                        }
                        label="Enabled"
                      />
                      
                      <FormControl fullWidth sx={{ mt: 1 }}>
                        <InputLabel>Fee Type</InputLabel>
                        <Select
                          value={config.fee_type}
                          label="Fee Type"
                          onChange={(e) => handlePaymentChange(method, 'fee_type', e.target.value)}
                        >
                          <MenuItem value="none">No Fee</MenuItem>
                          <MenuItem value="percentage">Percentage</MenuItem>
                          <MenuItem value="fixed">Fixed Amount</MenuItem>
                        </Select>
                      </FormControl>
                      
                      <TextField
                        fullWidth
                        label="Fee Amount"
                        type="number"
                        value={config.fee_amount}
                        onChange={(e) => handlePaymentChange(method, 'fee_amount', parseFloat(e.target.value))}
                        sx={{ mt: 1 }}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Taxes */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Tax Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.taxes.inclusive}
                  onChange={(e) => handleTaxChange('inclusive', e.target.checked)}
                />
              }
              label="Tax Inclusive Pricing"
            />
            
            <TextField
              fullWidth
              label="Default Tax Rate (%)"
              type="number"
              value={settings.taxes.default_rate}
              onChange={(e) => handleTaxChange('default_rate', parseFloat(e.target.value))}
              sx={{ mt: 2 }}
            />
          </Paper>
        </Grid>

        {/* Receipt */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Receipt Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <TextField
              fullWidth
              label="Receipt Header"
              multiline
              rows={2}
              value={settings.receipt.header}
              onChange={(e) => handleReceiptChange('header', e.target.value)}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Receipt Footer"
              multiline
              rows={2}
              value={settings.receipt.footer}
              onChange={(e) => handleReceiptChange('footer', e.target.value)}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Paper Width (mm)"
              type="number"
              value={settings.receipt.paper_width}
              onChange={(e) => handleReceiptChange('paper_width', parseInt(e.target.value))}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
