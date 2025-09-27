import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
import apiClient, { API_ENDPOINTS } from '../config/api';

export default function Settings() {
  const { t } = useTranslation('settings');
  
  // Helper functions for enum mappings
  const feeTypeLabel = (value) => {
    return t(`payment.feeTypes.${value}`);
  };
  
  const paymentMethodLabel = (method) => {
    return t(`payment.${method}`);
  };
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Default settings object to ensure all properties exist
  const defaultSettings = {
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
  };
  
  const [settings, setSettings] = useState(defaultSettings);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(API_ENDPOINTS.SETTINGS.GET);
      // Merge with default settings to ensure all properties exist
      const apiSettings = response.data.data || {};
      setSettings({
        ...defaultSettings,
        ...apiSettings,
        features: { ...defaultSettings.features, ...apiSettings.features },
        billing: { ...defaultSettings.billing, ...apiSettings.billing },
        payment_types: { ...defaultSettings.payment_types, ...apiSettings.payment_types },
        taxes: { ...defaultSettings.taxes, ...apiSettings.taxes },
        receipt: { ...defaultSettings.receipt, ...apiSettings.receipt },
      });
    } catch (err) {
      console.error('Failed to fetch settings:', err);
      setError('Failed to load settings');
      // Keep default settings if API fails
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      await apiClient.put(API_ENDPOINTS.SETTINGS.UPDATE, settings);
      setSuccess(t('messages.saved'));
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError(t('messages.error'));
    } finally {
      setSaving(false);
    }
  };

  const handleFeatureChange = (feature, value) => {
    setSettings(prev => ({
      ...prev,
      features: {
        ...(prev.features || {}),
        [feature]: value
      }
    }));
  };

  const handlePaymentChange = (method, field, value) => {
    setSettings(prev => ({
      ...prev,
      payment_types: {
        ...(prev.payment_types || {}),
        [method]: {
          ...(prev.payment_types?.[method] || {}),
          [field]: value
        }
      }
    }));
  };

  const handleTaxChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      taxes: {
        ...(prev.taxes || {}),
        [field]: value
      }
    }));
  };

  const handleReceiptChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      receipt: {
        ...(prev.receipt || {}),
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
          {t('title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Save />}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? <CircularProgress size={24} /> : t('actions.save')}
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
              {t('sections.features')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features?.kiosk || false}
                    onChange={(e) => handleFeatureChange('kiosk', e.target.checked)}
                  />
                }
                label={t('features.kioskMode')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features?.gate_binding || false}
                    onChange={(e) => handleFeatureChange('gate_binding', e.target.checked)}
                  />
                }
                label={t('features.gateBinding')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features?.multi_price || false}
                    onChange={(e) => handleFeatureChange('multi_price', e.target.checked)}
                  />
                }
                label={t('features.multiPrice')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features?.webhooks || false}
                    onChange={(e) => handleFeatureChange('webhooks', e.target.checked)}
                  />
                }
                label={t('features.webhooks')}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.features?.offline_sync || false}
                    onChange={(e) => handleFeatureChange('offline_sync', e.target.checked)}
                  />
                }
                label={t('features.offlineSync')}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Billing */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('sections.billing')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>{t('billing.plan')}</InputLabel>
              <Select
                value={settings.billing?.plan || 'basic'}
                label={t('billing.plan')}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  billing: { ...(prev.billing || {}), plan: e.target.value }
                }))}
              >
                <MenuItem value="basic">Basic</MenuItem>
                <MenuItem value="premium">Premium</MenuItem>
                <MenuItem value="enterprise">Enterprise</MenuItem>
              </Select>
            </FormControl>
            
            <Typography variant="body2" color="text.secondary">
              {t('billing.trialEnd')}: {settings.billing?.trial_end ? new Date(settings.billing.trial_end).toLocaleDateString() : 'N/A'}
            </Typography>
          </Paper>
        </Grid>

        {/* Payment Types */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('sections.paymentTypes')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              {Object.entries(settings.payment_types || {}).map(([method, config]) => (
                <Grid item xs={12} sm={6} md={3} key={method}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        {paymentMethodLabel(method)}
                      </Typography>
                      
                      <FormControlLabel
                        control={
                          <Switch
                            checked={config.enabled}
                            onChange={(e) => handlePaymentChange(method, 'enabled', e.target.checked)}
                          />
                        }
                        label={t('payment.enabled')}
                      />
                      
                      <FormControl fullWidth sx={{ mt: 1 }}>
                        <InputLabel>{t('payment.feeType')}</InputLabel>
                        <Select
                          value={config.fee_type}
                          label={t('payment.feeType')}
                          onChange={(e) => handlePaymentChange(method, 'fee_type', e.target.value)}
                        >
                          <MenuItem value="none">{feeTypeLabel('none')}</MenuItem>
                          <MenuItem value="percentage">{feeTypeLabel('percentage')}</MenuItem>
                          <MenuItem value="fixed">{feeTypeLabel('fixed')}</MenuItem>
                        </Select>
                      </FormControl>
                      
                      <TextField
                        fullWidth
                        label={t('payment.feeAmount')}
                        type="number"
                        value={config.fee_amount}
                        onChange={(e) => handlePaymentChange(method, 'fee_amount', parseFloat(e.target.value))}
                        placeholder={t('placeholders.enterNumber')}
                        inputProps={{ 'aria-label': t('payment.feeAmount') }}
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
              {t('sections.tax')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.taxes?.inclusive || false}
                  onChange={(e) => handleTaxChange('inclusive', e.target.checked)}
                />
              }
              label={t('tax.inclusive')}
            />
            
            <TextField
              fullWidth
              label={t('tax.defaultRate')}
              type="number"
              value={settings.taxes?.default_rate || 0}
              onChange={(e) => handleTaxChange('default_rate', parseFloat(e.target.value))}
              placeholder={t('placeholders.enterNumber')}
              inputProps={{ 'aria-label': t('tax.defaultRate') }}
              sx={{ mt: 2 }}
            />
          </Paper>
        </Grid>

        {/* Receipt */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('sections.receipt')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <TextField
              fullWidth
              label={t('receipt.header')}
              multiline
              rows={2}
              value={settings.receipt?.header || ''}
              onChange={(e) => handleReceiptChange('header', e.target.value)}
              placeholder={t('placeholders.enterText')}
              inputProps={{ 'aria-label': t('receipt.header') }}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label={t('receipt.footer')}
              multiline
              rows={2}
              value={settings.receipt?.footer || ''}
              onChange={(e) => handleReceiptChange('footer', e.target.value)}
              placeholder={t('placeholders.enterText')}
              inputProps={{ 'aria-label': t('receipt.footer') }}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label={t('receipt.paperWidth')}
              type="number"
              value={settings.receipt?.paper_width || 80}
              onChange={(e) => handleReceiptChange('paper_width', parseInt(e.target.value))}
              placeholder={t('placeholders.enterNumber')}
              inputProps={{ 'aria-label': t('receipt.paperWidth') }}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
