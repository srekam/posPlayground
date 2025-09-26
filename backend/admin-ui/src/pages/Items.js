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
  Tab,
  Tabs,
} from '@mui/material';
import { Add, Edit, Delete, Inventory, AttachMoney, LocationOn } from '@mui/icons-material';

export default function Items() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [packages, setPackages] = useState([]);
  const [pricingRules, setPricingRules] = useState([]);
  const [accessZones, setAccessZones] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('add');
  const [selectedItem, setSelectedItem] = useState(null);

  // Mock data for demonstration
  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    // Mock packages data
    const mockPackages = [
      {
        id: '1',
        name: 'Day Pass',
        description: 'Full day access to all attractions',
        price: 25.99,
        duration: 8,
        status: 'active',
        category: 'Day Passes'
      },
      {
        id: '2',
        name: 'Weekend Pass',
        description: 'Access for Saturday and Sunday',
        price: 45.99,
        duration: 16,
        status: 'active',
        category: 'Weekend Passes'
      },
      {
        id: '3',
        name: 'Season Pass',
        description: 'Unlimited access for 3 months',
        price: 199.99,
        duration: 2160,
        status: 'active',
        category: 'Season Passes'
      }
    ];

    // Mock pricing rules data
    const mockPricingRules = [
      {
        id: '1',
        name: 'Student Discount',
        description: '20% off for students',
        discount_type: 'percentage',
        discount_value: 20,
        conditions: 'Student ID required',
        status: 'active'
      },
      {
        id: '2',
        name: 'Family Package',
        description: 'Buy 3 get 1 free',
        discount_type: 'free_item',
        discount_value: 1,
        conditions: 'Minimum 4 people',
        status: 'active'
      }
    ];

    // Mock access zones data
    const mockAccessZones = [
      {
        id: '1',
        name: 'Main Playground',
        description: 'Primary play area with slides and swings',
        capacity: 100,
        status: 'active',
        location: 'Zone A'
      },
      {
        id: '2',
        name: 'Water Play Area',
        description: 'Splash pads and water features',
        capacity: 50,
        status: 'active',
        location: 'Zone B'
      }
    ];

    setPackages(mockPackages);
    setPricingRules(mockPricingRules);
    setAccessZones(mockAccessZones);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleAdd = () => {
    setDialogMode('add');
    setSelectedItem(null);
    setDialogOpen(true);
  };

  const handleEdit = (item) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setDialogOpen(true);
  };

  const handleDelete = (item) => {
    if (window.confirm(`Are you sure you want to delete ${item.name}?`)) {
      // Mock delete - in real app, this would call API
      console.log('Deleting item:', item);
    }
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    setSelectedItem(null);
  };

  const renderPackagesTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Duration (hrs)</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {packages.map((pkg) => (
            <TableRow key={pkg.id}>
              <TableCell>{pkg.name}</TableCell>
              <TableCell>{pkg.description}</TableCell>
              <TableCell>${pkg.price}</TableCell>
              <TableCell>{pkg.duration}</TableCell>
              <TableCell>{pkg.category}</TableCell>
              <TableCell>
                <Chip 
                  label={pkg.status} 
                  color={pkg.status === 'active' ? 'success' : 'default'}
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
                  startIcon={<Delete />}
                  color="error"
                  onClick={() => handleDelete(pkg)}
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

  const renderPricingRulesTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Value</TableCell>
            <TableCell>Conditions</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {pricingRules.map((rule) => (
            <TableRow key={rule.id}>
              <TableCell>{rule.name}</TableCell>
              <TableCell>{rule.description}</TableCell>
              <TableCell>{rule.discount_type}</TableCell>
              <TableCell>
                {rule.discount_type === 'percentage' 
                  ? `${rule.discount_value}%` 
                  : `${rule.discount_value} item(s)`
                }
              </TableCell>
              <TableCell>{rule.conditions}</TableCell>
              <TableCell>
                <Chip 
                  label={rule.status} 
                  color={rule.status === 'active' ? 'success' : 'default'}
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
                  startIcon={<Delete />}
                  color="error"
                  onClick={() => handleDelete(rule)}
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

  const renderAccessZonesTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Capacity</TableCell>
            <TableCell>Location</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {accessZones.map((zone) => (
            <TableRow key={zone.id}>
              <TableCell>{zone.name}</TableCell>
              <TableCell>{zone.description}</TableCell>
              <TableCell>{zone.capacity}</TableCell>
              <TableCell>{zone.location}</TableCell>
              <TableCell>
                <Chip 
                  label={zone.status} 
                  color={zone.status === 'active' ? 'success' : 'default'}
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
                  startIcon={<Delete />}
                  color="error"
                  onClick={() => handleDelete(zone)}
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

  const getTabIcon = (index) => {
    const icons = [<Inventory />, <AttachMoney />, <LocationOn />];
    return icons[index] || <Inventory />;
  };

  const getTabLabel = (index) => {
    const labels = ['Packages', 'Pricing Rules', 'Access Zones'];
    return labels[index] || 'Unknown';
  };

  const getTabCount = (index) => {
    const counts = [packages.length, pricingRules.length, accessZones.length];
    return counts[index] || 0;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Items Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAdd}
        >
          Add {getTabLabel(activeTab).slice(0, -1)}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab 
            icon={getTabIcon(0)} 
            label={`${getTabLabel(0)} (${getTabCount(0)})`}
            iconPosition="start"
          />
          <Tab 
            icon={getTabIcon(1)} 
            label={`${getTabLabel(1)} (${getTabCount(1)})`}
            iconPosition="start"
          />
          <Tab 
            icon={getTabIcon(2)} 
            label={`${getTabLabel(2)} (${getTabCount(2)})`}
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              {activeTab === 0 && renderPackagesTable()}
              {activeTab === 1 && renderPricingRulesTable()}
              {activeTab === 2 && renderAccessZonesTable()}
            </>
          )}
        </Grid>
      </Grid>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add' : 'Edit'} {getTabLabel(activeTab).slice(0, -1)}
        </DialogTitle>
        <DialogContent>
          <Typography>
            {dialogMode === 'add' 
              ? `Add a new ${getTabLabel(activeTab).slice(0, -1).toLowerCase()}` 
              : `Edit ${selectedItem?.name || 'item'}`
            }
          </Typography>
          {/* Form fields would go here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button variant="contained">
            {dialogMode === 'add' ? 'Add' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}