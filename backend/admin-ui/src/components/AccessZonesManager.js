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
  TextField,
  Stack,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  LocationOn,
  CheckCircle,
  Warning,
  Info,
} from '@mui/icons-material';
import apiClient, { API_ENDPOINTS } from '../config/api';

export default function AccessZonesManager() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [zones, setZones] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('add');
  const [selectedZone, setSelectedZone] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    capacity: '',
    active: true,
  });

  useEffect(() => {
    loadZones();
  }, []);

  const loadZones = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await apiClient.get(API_ENDPOINTS.ACCESS_ZONES.LIST);
      
      // Handle our API response structure
      if (response.data && response.data.data) {
        setZones(response.data.data || []);
      } else {
        setZones([]);
      }
    } catch (err) {
      console.error('Error loading access zones:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load access zones');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setDialogMode('add');
    setSelectedZone(null);
    setFormData({
      name: '',
      description: '',
      capacity: '',
      active: true,
    });
    setDialogOpen(true);
  };

  const handleEdit = (zone) => {
    setDialogMode('edit');
    setSelectedZone(zone);
    setFormData({
      name: zone.name,
      description: zone.description || '',
      capacity: zone.capacity || '',
      active: zone.active,
    });
    setDialogOpen(true);
  };

  const handleDelete = async (zone) => {
    if (window.confirm(`Are you sure you want to delete "${zone.name}"?`)) {
      try {
        await apiClient.delete(API_ENDPOINTS.ACCESS_ZONES.DELETE(zone.zone_id));
        setError(''); // Clear any previous errors
        setSuccess('Access zone deleted successfully!');
        loadZones(); // Reload the list
        
        // Auto-hide success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      } catch (err) {
        console.error('Error deleting access zone:', err);
        setError(err.response?.data?.message || err.message || 'Failed to delete access zone');
      }
    }
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    setSelectedZone(null);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Prepare data for API (remove location field as it's not in our API)
      const apiData = {
        name: formData.name,
        description: formData.description,
        capacity: formData.capacity || null,
        active: formData.active
      };

      let response;
      if (dialogMode === 'add') {
        response = await apiClient.post(API_ENDPOINTS.ACCESS_ZONES.CREATE, apiData);
      } else {
        response = await apiClient.put(API_ENDPOINTS.ACCESS_ZONES.UPDATE(selectedZone.zone_id), apiData);
      }

      // Handle our API response structure
      if (response.data && response.data.data) {
        setError(''); // Clear any previous errors
        setSuccess(dialogMode === 'add' ? 'Access zone created successfully!' : 'Access zone updated successfully!');
        loadZones(); // Reload the list
        handleDialogClose();
        
        // Auto-hide success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError('Unexpected response format');
      }
    } catch (err) {
      console.error('Error saving access zone:', err);
      setError(err.response?.data?.message || err.message || 'Failed to save access zone');
    } finally {
      setLoading(false);
    }
  };

  const renderZonesTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Zone Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Capacity</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {zones.map((zone) => (
            <TableRow key={zone.zone_id} hover>
              <TableCell>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <LocationOn color="primary" />
                  <Typography variant="body2" fontWeight="medium">
                    {zone.name}
                  </Typography>
                </Stack>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {zone.description || '-'}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {zone.capacity ? `${zone.capacity} people` : 'Unlimited'}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip 
                  label={zone.active ? 'Active' : 'Inactive'} 
                  color={zone.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Stack direction="row" spacing={1}>
                  <Tooltip title="Edit">
                    <IconButton 
                      size="small"
                      onClick={() => handleEdit(zone)}
                    >
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => handleDelete(zone)}
                    >
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderDialog = () => (
    <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {dialogMode === 'add' ? 'Add Access Zone' : 'Edit Access Zone'}
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Zone Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              required
              placeholder="e.g., Yellow Zone, Green Zone"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              multiline
              rows={3}
              placeholder="Describe what attractions or activities are in this zone"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Capacity"
              type="number"
              value={formData.capacity}
              onChange={(e) => handleInputChange('capacity', parseInt(e.target.value) || '')}
              placeholder="Maximum number of people"
              helperText="Leave empty for unlimited capacity"
            />
          </Grid>
          
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.active}
                  onChange={(e) => handleInputChange('active', e.target.checked)}
                />
              }
              label="Active"
            />
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleDialogClose}>Cancel</Button>
        <Button 
          variant="contained" 
          onClick={handleSave}
          disabled={loading || !formData.name}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Saving...' : dialogMode === 'add' ? 'Create Zone' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const renderSummaryCards = () => {
    const totalZones = zones.length;
    const activeZones = zones.filter(z => z.active).length;
    const totalCapacity = zones.reduce((sum, zone) => sum + (zone.capacity || 0), 0);
    const unlimitedZones = zones.filter(z => !z.capacity).length;

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ p: 1, bgcolor: 'primary.light', borderRadius: 1 }}>
                  <LocationOn color="primary" />
                </Box>
                <Box>
                  <Typography variant="h6">{totalZones}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Zones
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
                  <CheckCircle color="success" />
                </Box>
                <Box>
                  <Typography variant="h6">{activeZones}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Zones
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ p: 1, bgcolor: 'info.light', borderRadius: 1 }}>
                  <Info color="info" />
                </Box>
                <Box>
                  <Typography variant="h6">{totalCapacity}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Capacity
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box sx={{ p: 1, bgcolor: 'warning.light', borderRadius: 1 }}>
                  <Warning color="warning" />
                </Box>
                <Box>
                  <Typography variant="h6">{unlimitedZones}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Unlimited Zones
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box>
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

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Access Zones Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAdd}
        >
          Add Zone
        </Button>
      </Box>

      {renderSummaryCards()}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        renderZonesTable()
      )}

      {renderDialog()}
    </Box>
  );
}
