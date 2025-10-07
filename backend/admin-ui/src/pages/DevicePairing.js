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
} from '@mui/material';
import {
  Add,
  ContentCopy,
  Download,
  Refresh,
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
  const [ttlMinutes, setTtlMinutes] = useState(1); // Changed to 1 minute (60 seconds)
  const [generatedPairing, setGeneratedPairing] = useState(null);
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [pairingHistory, setPairingHistory] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState(60); // 60 seconds countdown
  const [pairingSuccess, setPairingSuccess] = useState(false);
  const [recentDevices, setRecentDevices] = useState([]);

  useEffect(() => {
    fetchStores();
    fetchPairingHistory();
    fetchRecentDevices();
    
    // Check for pairing success every 2 seconds when dialog is open
    const interval = setInterval(() => {
      if (openDialog && generatedPairing) {
        checkPairingSuccess();
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [openDialog, generatedPairing, checkPairingSuccess]);

  // Countdown timer effect
  useEffect(() => {
    let interval = null;
    if (openDialog && generatedPairing && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(timeRemaining => {
          if (timeRemaining <= 1) {
            setOpenDialog(false);
            setGeneratedPairing(null);
            setTimeRemaining(60);
            return 0;
          }
          return timeRemaining - 1;
        });
      }, 1000);
    } else if (timeRemaining === 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [openDialog, generatedPairing, timeRemaining]);

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

  const fetchRecentDevices = async () => {
    try {
      const response = await apiClient.get('/api/v1/devices?limit=5');
      if (response.data.success) {
        setRecentDevices(response.data.data || []);
      }
    } catch (error) {
      console.error('Error fetching recent devices:', error);
    }
  };

  const checkPairingSuccess = async () => {
    try {
      const response = await apiClient.get('/api/v1/devices?limit=10');
      if (response.data.success) {
        const devices = response.data.data || [];
        const newDevices = devices.filter(device => {
          const createdTime = new Date(device.created_at);
          const now = new Date();
          const timeDiff = now - createdTime;
          return timeDiff < 120000; // Created within last 2 minutes
        });
        
        if (newDevices.length > recentDevices.length) {
          setPairingSuccess(true);
          setSuccess('🎉 Device paired successfully! New device added to your device list.');
          fetchRecentDevices(); // Refresh the device list
          
          // Close dialog IMMEDIATELY upon success
          setOpenDialog(false);
          setPairingSuccess(false);
          
          // Clear success message after 5 seconds
          setTimeout(() => {
            setSuccess('');
          }, 5000);
        }
      }
    } catch (error) {
      console.error('Error checking pairing success:', error);
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
      console.log('Generated pairing response:', pairing);
      console.log('Manual key generated:', pairing.manual_key);
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
      setTimeRemaining(60); // Reset countdown to 60 seconds
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
                  onChange={(e) => setTtlMinutes(parseInt(e.target.value) || 1)}
                  inputProps={{ min: 1, max: 5 }}
                  helperText="Quick pairing - code expires in 60 seconds for fast pairing"
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
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="h6">Pairing Code Generated</Typography>
              <Typography variant="body2" color="text.secondary">
                Quick pairing - expires in 60 seconds
              </Typography>
            </Box>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              px: 2, 
              py: 1, 
              borderRadius: 2,
              bgcolor: timeRemaining <= 10 ? 'error.main' : timeRemaining <= 30 ? 'warning.main' : 'success.main',
              color: 'white'
            }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {timeRemaining}s
              </Typography>
            </Box>
          </Box>
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

              {/* Deep Link removed per request */}

              {/* Manual Key - Big Font Display */}
              <Grid item xs={12}>
                <Card sx={{ bgcolor: 'primary.50', border: '2px solid', borderColor: 'primary.main' }}>
                  <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      Manual Pairing Code
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Enter this 5-digit code in your mobile app
                    </Typography>
                    
                    {/* Big 5-digit display */}
                    <Box sx={{ 
                      display: 'flex', 
                      justifyContent: 'center', 
                      gap: 2, 
                      mb: 3,
                      flexWrap: 'wrap'
                    }}>
                      {generatedPairing.manual_key.split('').map((digit, index) => (
                        <Box
                          key={index}
                          sx={{
                            width: 60,
                            height: 80,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            bgcolor: 'white',
                            border: '3px solid',
                            borderColor: 'primary.main',
                            borderRadius: 2,
                            boxShadow: 2
                          }}
                        >
                          <Typography 
                            variant="h3" 
                            sx={{ 
                              fontWeight: 'bold', 
                              color: 'primary.main',
                              fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
                            }}
                          >
                            {digit}
                          </Typography>
                        </Box>
                      ))}
                    </Box>

                    {/* Action buttons */}
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                      <Button
                        variant="outlined"
                        startIcon={<ContentCopy />}
                        onClick={() => copyToClipboard(generatedPairing.manual_key, 'Pairing code')}
                        size="large"
                      >
                        Copy Code
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<Refresh />}
                        onClick={() => {
                          setOpenDialog(false);
                          generatePairing();
                        }}
                        size="large"
                        sx={{ bgcolor: 'success.main', '&:hover': { bgcolor: 'success.dark' } }}
                      >
                        Generate New Code
                      </Button>
                    </Box>
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

      {/* Recent Devices */}
      <Paper sx={{ mt: 3, p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Recent Paired Devices
          </Typography>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Refresh />}
            onClick={fetchRecentDevices}
          >
            Refresh
          </Button>
        </Box>
        <Divider sx={{ mb: 2 }} />
        
        {recentDevices.length === 0 ? (
          <Typography color="text.secondary">
            No devices paired yet
          </Typography>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {recentDevices.map((device) => (
              <Box key={device.device_id} sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                p: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                bgcolor: pairingSuccess ? 'success.50' : 'background.paper'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip
                    icon={getStatusIcon(device.status)}
                    label={device.status}
                    color={getStatusColor(device.status)}
                    size="small"
                  />
                  <Box>
                    <Typography variant="body2" fontWeight="medium">
                      {device.name || 'Unnamed Device'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {device.device_id} • {device.type} • {device.store_id}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(device.created_at).toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    label={device.last_seen ? 'Online' : 'Offline'}
                    color={device.last_seen ? 'success' : 'default'}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Paper>

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
