import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Snackbar,
} from '@mui/material';
import { Add, Edit, Delete, Devices, Store, Refresh } from '@mui/icons-material';
import apiClient, { API_ENDPOINTS } from '../config/api';

export default function Stores() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stores, setStores] = useState([]);
  const [devices, setDevices] = useState([]);
  const [activeTab, setActiveTab] = useState('stores');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    timezone: 'UTC',
    currency: 'THB',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch stores and devices separately to handle errors independently
      try {
        const storesRes = await apiClient.get(API_ENDPOINTS.STORES.LIST);
        setStores(storesRes.data.data || storesRes.data || []);
      } catch (err) {
        console.error('Failed to fetch stores:', err);
        setStores([]);
      }
      
      try {
        const devicesRes = await apiClient.get(API_ENDPOINTS.DEVICES.LIST);
        setDevices(devicesRes.data.data || devicesRes.data || []);
      } catch (err) {
        console.error('Failed to fetch devices:', err);
        setDevices([]);
      }
      
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData({
      name: item.name || '',
      address: item.address || '',
      timezone: item.timezone || 'UTC',
      currency: item.currency || 'THB',
    });
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      setLoading(true);
      await apiClient.delete(API_ENDPOINTS.STORES.DELETE(id));
      setSnackbar({ open: true, message: 'Store deleted successfully', severity: 'success' });
      fetchData();
    } catch (err) {
      console.error('Failed to delete store:', err);
      setSnackbar({ open: true, message: 'Failed to delete store', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      if (editingItem) {
        // Update existing store
        await apiClient.put(API_ENDPOINTS.STORES.UPDATE(editingItem.store_id), formData);
        setSnackbar({ open: true, message: 'Store updated successfully', severity: 'success' });
      } else {
        // Create new store
        await apiClient.post(API_ENDPOINTS.STORES.CREATE, formData);
        setSnackbar({ open: true, message: 'Store created successfully', severity: 'success' });
      }
      
      setOpenDialog(false);
      setEditingItem(null);
      setFormData({ name: '', address: '', timezone: 'UTC', currency: 'THB' });
      fetchData();
    } catch (err) {
      console.error('Failed to save store:', err);
      setSnackbar({ open: true, message: 'Failed to save store', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setFormData({ name: '', address: '', timezone: 'UTC', currency: 'THB' });
  };

  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleDeviceAction = async (deviceId, action) => {
    try {
      await apiClient.patch(API_ENDPOINTS.DEVICES.UPDATE(deviceId), { action });
      fetchData();
    } catch (err) {
      console.error(`Failed to ${action} device:`, err);
      setError(`Failed to ${action} device`);
    }
  };

  const renderStores = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Store Name</TableCell>
            <TableCell>Address</TableCell>
            <TableCell>Timezone</TableCell>
            <TableCell>Devices</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {stores.map((store) => (
            <TableRow key={store.store_id}>
              <TableCell>
                <Box>
                  <Typography variant="subtitle2">{store.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    ID: {store.store_id}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Typography variant="body2">{store.address}</Typography>
              </TableCell>
              <TableCell>{store.tz}</TableCell>
              <TableCell>
                {devices.filter(d => d.store_id === store.store_id).length}
              </TableCell>
              <TableCell>
                <Chip 
                  label={store.active ? 'Active' : 'Inactive'} 
                  color={store.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(store)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(store.store_id)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const getDeviceStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'warning';
      case 'revoked': return 'error';
      default: return 'default';
    }
  };

  const renderDevices = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Device Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Store</TableCell>
            <TableCell>Capabilities</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Last Seen</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {devices.map((device) => (
            <TableRow key={device.device_id}>
              <TableCell>
                <Box>
                  <Typography variant="subtitle2">{device.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    ID: {device.device_id}
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Chip label={device.type} size="small" />
              </TableCell>
              <TableCell>
                {stores.find(s => s.store_id === device.store_id)?.name || 'Unknown'}
              </TableCell>
              <TableCell>
                <Box>
                  {device.caps?.map((cap, index) => (
                    <Chip key={index} label={cap} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </Box>
              </TableCell>
              <TableCell>
                <Chip 
                  label={device.status} 
                  color={getDeviceStatusColor(device.status)}
                  size="small"
                />
              </TableCell>
              <TableCell>
                {device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Never'}
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(device)}
                >
                  Edit
                </Button>
                {device.status === 'active' ? (
                  <Button
                    size="small"
                    color="warning"
                    onClick={() => handleDeviceAction(device.device_id, 'suspend')}
                  >
                    Suspend
                  </Button>
                ) : (
                  <Button
                    size="small"
                    color="success"
                    onClick={() => handleDeviceAction(device.device_id, 'activate')}
                  >
                    Activate
                  </Button>
                )}
                <Button
                  size="small"
                  color="info"
                  startIcon={<Refresh />}
                  onClick={() => handleDeviceAction(device.device_id, 'rotate-token')}
                >
                  Rotate Token
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(device.device_id)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Stores & Devices
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            setEditingItem(null);
            setFormData({ name: '', address: '', timezone: 'UTC', currency: 'THB' });
            setOpenDialog(true);
          }}
        >
          Add {activeTab.slice(0, -1)}
        </Button>
      </Box>

      {/* Store/Device Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Stores
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {stores.length}
                  </Typography>
                </Box>
                <Store sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Devices
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {devices.length}
                  </Typography>
                </Box>
                <Devices sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Active Devices
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {devices.filter(d => d.status === 'active').length}
                  </Typography>
                </Box>
                <Devices sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Issues
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {devices.filter(d => d.status !== 'active').length}
                  </Typography>
                </Box>
                <Devices sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex' }}>
            {[
              { key: 'stores', label: 'Stores', icon: <Store /> },
              { key: 'devices', label: 'POS Devices', icon: <Devices /> }
            ].map((tab) => (
              <Button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                startIcon={tab.icon}
                sx={{
                  borderBottom: activeTab === tab.key ? 2 : 0,
                  borderColor: 'primary.main',
                  borderRadius: 0,
                }}
              >
                {tab.label}
              </Button>
            ))}
          </Box>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      ) : (
        <>
          {activeTab === 'stores' && renderStores()}
          {activeTab === 'devices' && renderDevices()}
        </>
      )}

      {/* Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingItem ? 'Edit Store' : 'Add Store'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Store Name"
              value={formData.name}
              onChange={(e) => handleFormChange('name', e.target.value)}
              margin="normal"
              required
              error={!formData.name.trim()}
              helperText={!formData.name.trim() ? 'Store name is required' : ''}
            />
            
            <TextField
              fullWidth
              label="Address"
              value={formData.address}
              onChange={(e) => handleFormChange('address', e.target.value)}
              margin="normal"
              multiline
              rows={3}
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Timezone</InputLabel>
              <Select
                value={formData.timezone}
                onChange={(e) => handleFormChange('timezone', e.target.value)}
                label="Timezone"
              >
                <MenuItem value="UTC">UTC</MenuItem>
                <MenuItem value="Asia/Bangkok">Asia/Bangkok</MenuItem>
                <MenuItem value="Asia/Tokyo">Asia/Tokyo</MenuItem>
                <MenuItem value="America/New_York">America/New_York</MenuItem>
                <MenuItem value="Europe/London">Europe/London</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Currency</InputLabel>
              <Select
                value={formData.currency}
                onChange={(e) => handleFormChange('currency', e.target.value)}
                label="Currency"
              >
                <MenuItem value="THB">THB (Thai Baht)</MenuItem>
                <MenuItem value="USD">USD (US Dollar)</MenuItem>
                <MenuItem value="EUR">EUR (Euro)</MenuItem>
                <MenuItem value="JPY">JPY (Japanese Yen)</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={loading}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleSubmit}
            disabled={loading || !formData.name.trim()}
          >
            {loading ? <CircularProgress size={20} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
