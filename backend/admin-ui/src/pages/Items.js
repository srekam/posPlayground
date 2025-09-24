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
  Switch,
  FormControlLabel,
} from '@mui/material';
import { Add, Edit, Delete } from '@mui/icons-material';
import axios from 'axios';

export default function Items() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [packages, setPackages] = useState([]);
  const [pricingRules, setPricingRules] = useState([]);
  const [accessZones, setAccessZones] = useState([]);
  const [activeTab, setActiveTab] = useState('packages');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [packagesRes, rulesRes, zonesRes] = await Promise.all([
        axios.get('/v1/catalog/packages'),
        axios.get('/v1/catalog/pricing-rules'),
        axios.get('/v1/catalog/access-zones')
      ]);

      setPackages(packagesRes.data.data || []);
      setPricingRules(rulesRes.data.data || []);
      setAccessZones(zonesRes.data.data || []);
    } catch (err) {
      console.error('Failed to fetch catalog data:', err);
      setError('Failed to load catalog data');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      await axios.delete(`/v1/catalog/${activeTab}/${id}`);
      fetchData();
    } catch (err) {
      console.error('Failed to delete item:', err);
      setError('Failed to delete item');
    }
  };

  const renderPackages = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Quota/Minutes</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {packages.map((pkg) => (
            <TableRow key={pkg.package_id}>
              <TableCell>{pkg.name}</TableCell>
              <TableCell>
                <Chip label={pkg.type} size="small" />
              </TableCell>
              <TableCell>฿{pkg.price}</TableCell>
              <TableCell>{pkg.quota_or_minutes}</TableCell>
              <TableCell>
                <Chip 
                  label={pkg.active ? 'Active' : 'Inactive'} 
                  color={pkg.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(pkg)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(pkg.package_id)}
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

  const renderPricingRules = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Scope</TableCell>
            <TableCell>Priority</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {pricingRules.map((rule) => (
            <TableRow key={rule.rule_id}>
              <TableCell>{rule.name}</TableCell>
              <TableCell>
                <Chip label={rule.kind} size="small" />
              </TableCell>
              <TableCell>{rule.scope}</TableCell>
              <TableCell>{rule.priority}</TableCell>
              <TableCell>
                <Chip 
                  label={rule.active ? 'Active' : 'Inactive'} 
                  color={rule.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(rule)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(rule.rule_id)}
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

  const renderAccessZones = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Device Binding</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {accessZones.map((zone) => (
            <TableRow key={zone.zone_id}>
              <TableCell>{zone.name}</TableCell>
              <TableCell>{zone.description}</TableCell>
              <TableCell>
                <Chip 
                  label={zone.device_binding ? 'Required' : 'Optional'} 
                  color={zone.device_binding ? 'warning' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Chip 
                  label={zone.active ? 'Active' : 'Inactive'} 
                  color={zone.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(zone)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(zone.zone_id)}
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
          Items & Catalog
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
        >
          Add {activeTab.slice(0, -1)}
        </Button>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex' }}>
            {[
              { key: 'packages', label: 'Packages' },
              { key: 'pricing-rules', label: 'Pricing Rules' },
              { key: 'access-zones', label: 'Access Zones' }
            ].map((tab) => (
              <Button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
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
          {activeTab === 'packages' && renderPackages()}
          {activeTab === 'pricing-rules' && renderPricingRules()}
          {activeTab === 'access-zones' && renderAccessZones()}
        </>
      )}

      {/* Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit' : 'Add'} {activeTab.slice(0, -1)}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Edit form would be implemented here with proper validation and API integration.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
