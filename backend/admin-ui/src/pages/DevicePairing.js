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
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  IconButton,
  Tooltip,
  Snackbar,
} from '@mui/material';
import {
  Add,
  QrCode,
  Link,
  ContentCopy,
  Download,
  Refresh,
  Visibility,
  VisibilityOff,
  CheckCircle,
  Error,
  Warning,
  Info,
} from '@mui/icons-material';
import QRCode from 'qrcode';
import apiClient, { API_ENDPOINTS } from '../config/api';

export default function DevicePairing() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState('');
  const [deviceType, setDeviceType] = useState('POS');
  const [ttlMinutes, setTtlMinutes] = useState(15);
  const [generatedPairing, setGeneratedPairing] = useState(null);
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState('');
  const [showManualKey, setShowManualKey] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [pairingHistory, setPairingHistory] = useState([]);

  useEffect(() => {
    fetchStores();
    fetchPairingHistory();
  }, []);

  const fetchStores = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.STORES.LIST);
      setStores(response.data.data || response.data || []);
      const storesData = response.data.data || response.data || [];
      if (storesData.length > 0) {
        setSelectedStore(storesData[0].store_id);
      }
    } catch (err) {
      console.error('Failed to fetch stores:', err);
      setError('Failed to load stores');
    }
  };

  const fetchPairingHistory = async () => {
    try {
      // This would be a new endpoint to get pairing history
      // For now, we'll use a placeholder
      setPairingHistory([]);
    } catch (err) {
      console.error('Failed to fetch pairing history:', err);
    }
  };

  const generatePairing = async () => {
    if (!selectedStore) {
      setError('Please select a store');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await apiClient.post('/auth/device/pairing/generate', {
        store_id: selectedStore,
        device_type: deviceType,
        ttl_minutes: ttlMinutes,
      });

      const pairing = response.data;
      setGeneratedPairing(pairing);

      // Generate QR code
      try {
        const qrDataUrl = await QRCode.toDataURL(pairing.qr_payload, {
          width: 256,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#FFFFFF',
          },
        });
        setQrCodeDataUrl(qrDataUrl);
      } catch (qrError) {
        console.error('Failed to generate QR code:', qrError);
      }

      setSuccess('Pairing code generated successfully!');
      setOpenDialog(true);
    } catch (err) {
      console.error('Failed to generate pairing:', err);
      setError(err.response?.data?.message || 'Failed to generate pairing code');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccess(`${label} copied to clipboard!`);
    } catch (err) {
      console.error('Failed to copy:', err);
      setError('Failed to copy to clipboard');
    }
  };

  const downloadQRCode = () => {
    if (!qrCodeDataUrl) return;

    const link = document.createElement('a');
    link.download = `playpark-pairing-${deviceType.toLowerCase()}-${Date.now()}.png`;
    link.href = qrCodeDataUrl;
    link.click();
  };

  const revokePairing = async (token) => {
    try {
      await apiClient.post('/auth/device/pairing/revoke', null, {
        params: { token }
      });
      setSuccess('Pairing code revoked successfully');
      fetchPairingHistory();
    } catch (err) {
      console.error('Failed to revoke pairing:', err);
      setError('Failed to revoke pairing code');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'unused': return 'primary';
      case 'used': return 'success';
      case 'revoked': return 'error';
      case 'expired': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'unused': return <Info />;
      case 'used': return <CheckCircle />;
      case 'revoked': return <Error />;
      case 'expired': return <Warning />;
      default: return <Info />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Device Pairing
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={generatePairing}
          disabled={loading || !selectedStore}
        >
          {loading ? <CircularProgress size={20} /> : 'Generate Pairing Code'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Pairing Configuration */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Pairing Configuration
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Store</InputLabel>
                  <Select
                    value={selectedStore}
                    onChange={(e) => setSelectedStore(e.target.value)}
                    label="Store"
                  >
                    {stores.map((store) => (
                      <MenuItem key={store.store_id} value={store.store_id}>
                        {store.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Device Type</InputLabel>
                  <Select
                    value={deviceType}
                    onChange={(e) => setDeviceType(e.target.value)}
                    label="Device Type"
                  >
                    <MenuItem value="POS">POS Terminal</MenuItem>
                    <MenuItem value="GATE">Gate Device</MenuItem>
                    <MenuItem value="KIOSK">Kiosk</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Time to Live (minutes)"
                  type="number"
                  value={ttlMinutes}
                  onChange={(e) => setTtlMinutes(parseInt(e.target.value) || 15)}
                  inputProps={{ min: 5, max: 60 }}
                  helperText="How long the pairing code will be valid (5-60 minutes)"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Pairing Instructions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              How to Pair a Device
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  bgcolor: 'primary.main', 
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold'
                }}>
                  1
                </Box>
                <Typography>
                  Generate a pairing code using the form on the left
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  bgcolor: 'primary.main', 
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold'
                }}>
                  2
                </Box>
                <Typography>
                  On the device, open the PlayPark app and tap "Pair Device"
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  bgcolor: 'primary.main', 
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold'
                }}>
                  3
                </Box>
                <Typography>
                  Scan the QR code or enter the manual key
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  bgcolor: 'primary.main', 
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold'
                }}>
                  4
                </Box>
                <Typography>
                  The device will be automatically configured and ready to use
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Generated Pairing Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Pairing Code Generated
          <Typography variant="body2" color="text.secondary">
            Expires in {ttlMinutes} minutes
          </Typography>
        </DialogTitle>
        <DialogContent>
          {generatedPairing && (
            <Grid container spacing={3}>
              {/* QR Code */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" gutterBottom>
                      QR Code
                    </Typography>
                    {qrCodeDataUrl ? (
                      <Box sx={{ mb: 2 }}>
                        <img 
                          src={qrCodeDataUrl} 
                          alt="Pairing QR Code" 
                          style={{ maxWidth: '100%', height: 'auto' }}
                        />
                      </Box>
                    ) : (
                      <Box sx={{ height: 256, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <CircularProgress />
                      </Box>
                    )}
                    <Button
                      variant="outlined"
                      startIcon={<Download />}
                      onClick={downloadQRCode}
                      disabled={!qrCodeDataUrl}
                      fullWidth
                    >
                      Download QR Code
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              {/* Deep Link */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Deep Link
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Send this link via email, LINE, or other messaging apps
                    </Typography>
                    <TextField
                      fullWidth
                      value={generatedPairing.deep_link}
                      InputProps={{
                        readOnly: true,
                        endAdornment: (
                          <IconButton onClick={() => copyToClipboard(generatedPairing.deep_link, 'Deep link')}>
                            <ContentCopy />
                          </IconButton>
                        ),
                      }}
                      variant="outlined"
                      size="small"
                    />
                  </CardContent>
                </Card>
              </Grid>

              {/* Manual Key */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6">
                        Manual Key
                      </Typography>
                      <IconButton onClick={() => setShowManualKey(!showManualKey)}>
                        {showManualKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Enter this code manually if QR scanning is not available
                    </Typography>
                    <TextField
                      fullWidth
                      value={showManualKey ? generatedPairing.manual_key : '••••••••••••••••••••'}
                      InputProps={{
                        readOnly: true,
                        endAdornment: (
                          <IconButton onClick={() => copyToClipboard(generatedPairing.manual_key, 'Manual key')}>
                            <ContentCopy />
                          </IconButton>
                        ),
                      }}
                      variant="outlined"
                      size="small"
                    />
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>
            Close
          </Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setOpenDialog(false);
              generatePairing();
            }}
          >
            Generate New Code
          </Button>
        </DialogActions>
      </Dialog>

      {/* Pairing History */}
      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Pairing Codes
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        {pairingHistory.length === 0 ? (
          <Typography color="text.secondary">
            No pairing codes generated yet
          </Typography>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {pairingHistory.map((pairing, index) => (
              <Box key={index} sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                p: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip
                    icon={getStatusIcon(pairing.status)}
                    label={pairing.status}
                    color={getStatusColor(pairing.status)}
                    size="small"
                  />
                  <Typography variant="body2">
                    {pairing.device_type} • {pairing.store_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(pairing.created_at).toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title="Revoke">
                    <IconButton 
                      size="small" 
                      onClick={() => revokePairing(pairing.token)}
                      disabled={pairing.status !== 'unused'}
                    >
                      <Refresh />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  );
}
