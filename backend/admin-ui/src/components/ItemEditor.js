import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  Box,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Typography,
  Card,
  CardContent,
  Chip,
  Stack,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Autocomplete,
  Checkbox,
  FormGroup,
  CircularProgress,
} from '@mui/material';
import {
  Close,
  Add,
  Delete,
  Image,
  Search,
  Warning,
  CheckCircle,
  Info,
  AttachMoney,
  Inventory,
  Timer,
  ShoppingCart,
  Upgrade,
  LocalShipping,
} from '@mui/icons-material';
import apiClient, { API_ENDPOINTS } from '../config/api';
import ImageUpload from './ImageUpload';

// Item type configurations
const ITEM_TYPES = {
  STOCKED_GOOD: { 
    label: 'Stocked Good', 
    icon: <LocalShipping />, 
    color: 'primary',
    description: 'Physical inventory items with SKU tracking'
  },
  NON_STOCKED_SERVICE: { 
    label: 'Service', 
    icon: <AttachMoney />, 
    color: 'secondary',
    description: 'Services without inventory tracking'
  },
  PASS_TIME: { 
    label: 'Pass (Time)', 
    icon: <Timer />, 
    color: 'success',
    description: 'Time-based access passes'
  },
  RIDE_CREDIT_BUNDLE: { 
    label: 'Ride Bundle', 
    icon: <ShoppingCart />, 
    color: 'info',
    description: 'Bundle of ride credits'
  },
  SINGLE_RIDE: { 
    label: 'Single Ride', 
    icon: <ShoppingCart />, 
    color: 'info',
    description: 'Individual ride credit'
  },
  BUNDLE: { 
    label: 'Bundle', 
    icon: <Inventory />, 
    color: 'warning',
    description: 'Composite items with Bill of Materials'
  },
  UPGRADE: { 
    label: 'Upgrade', 
    icon: <Upgrade />, 
    color: 'error',
    description: 'Entitlement upgrades'
  },
  FEE: { 
    label: 'Fee', 
    icon: <AttachMoney />, 
    color: 'default',
    description: 'Additional fees'
  },
  DISCOUNT: { 
    label: 'Discount', 
    icon: <AttachMoney />, 
    color: 'default',
    description: 'Discount items'
  },
};

const VALIDITY_SCOPES = [
  { value: 'same_day', label: 'Same Day' },
  { value: 'multi_day', label: 'Multi Day' },
  { value: 'date_range', label: 'Date Range' },
];

const PRICE_DIFF_STRATEGIES = [
  { value: 'pay_difference', label: 'Pay Difference' },
  { value: 'no_charge', label: 'No Charge' },
  { value: 'refund_difference', label: 'Refund Difference' },
];

const UOM_OPTIONS = [
  'piece', 'kg', 'g', 'liter', 'ml', 'hour', 'day', 'week', 'month'
];

export default function ItemEditor({ open, mode, item, categories, onClose, onSave }) {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    // Basic fields
    name: '',
    description: '',
    type: '',
    category_id: '',
    price_satang: 0,
    tax_class: 'STANDARD',
    active: true,
    images: [],
    
    // Type-specific fields
    stocked_good: null,
    pass_time: null,
    ride_credit_bundle: null,
    single_ride: null,
    bundle: null,
    upgrade: null,
  });
  
  const [availableItems, setAvailableItems] = useState([]);
  const [bundleItems, setBundleItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const steps = ['Basic Information', 'Type-Specific Fields', 'Preview & Save'];

  useEffect(() => {
    if (open) {
      if (mode === 'edit' && item) {
        setFormData(item);
      } else {
        resetForm();
      }
      setActiveStep(0);
      setError('');
      loadAvailableItems();
    }
  }, [open, mode, item]);

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      type: '',
      category_id: '',
      price_satang: 0,
      tax_class: 'STANDARD',
      active: true,
      images: [],
      stocked_good: null,
      pass_time: null,
      ride_credit_bundle: null,
      single_ride: null,
      bundle: null,
      upgrade: null,
    });
    setBundleItems([]);
  };

  const loadAvailableItems = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.ITEMS.LIST);
      if (response.data.success) {
        setAvailableItems(response.data.data.items || []);
      }
    } catch (err) {
      console.error('Error loading items:', err);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTypeSpecificChange = (type, field, value) => {
    setFormData(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        [field]: value
      }
    }));
  };

  const handleNext = () => {
    if (activeStep === 0) {
      // Validate basic fields
      if (!formData.name || !formData.type) {
        setError('Name and type are required');
        return;
      }
      if (formData.price_satang < 0) {
        setError('Price must be non-negative');
        return;
      }
    }
    
    if (activeStep === 1) {
      // Validate type-specific fields
      const typeValidation = validateTypeSpecificFields();
      if (!typeValidation.valid) {
        setError(typeValidation.message);
        return;
      }
    }
    
    setError('');
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const validateTypeSpecificFields = () => {
    switch (formData.type) {
      case 'STOCKED_GOOD':
        if (formData.stocked_good?.track_inventory && !formData.stocked_good?.sku) {
          return { valid: false, message: 'SKU is required when tracking inventory' };
        }
        break;
      case 'BUNDLE':
        if (!formData.bundle?.bom || formData.bundle.bom.length === 0) {
          return { valid: false, message: 'Bundle must have at least one item in BOM' };
        }
        break;
      case 'UPGRADE':
        if (!formData.upgrade?.from_entitlement || !formData.upgrade?.to_entitlement) {
          return { valid: false, message: 'Both from_entitlement and to_entitlement are required' };
        }
        break;
    }
    return { valid: true };
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    
    try {
      const payload = { ...formData };
      
      // Remove null type-specific fields
      Object.keys(ITEM_TYPES).forEach(type => {
        const typeKey = type.toLowerCase().replace(/_([a-z])/g, (match, letter) => letter);
        if (typeKey !== formData.type.toLowerCase().replace(/_([a-z])/g, (match, letter) => letter)) {
          delete payload[typeKey];
        }
      });

      let response;
      if (mode === 'add') {
        response = await apiClient.post(API_ENDPOINTS.ITEMS.CREATE, payload);
      } else {
        response = await apiClient.put(API_ENDPOINTS.ITEMS.UPDATE(item.item_id), payload);
      }

      // Handle our API response structure
      if (response.data && response.data.data) {
        onSave();
      } else {
        setError('Unexpected response format');
      }
    } catch (err) {
      console.error('Error saving item:', err);
      setError(err.response?.data?.message || err.message || 'Failed to save item');
    } finally {
      setLoading(false);
    }
  };

  const addBundleItem = (item) => {
    const existingIndex = bundleItems.findIndex(bi => bi.item_id === item.item_id);
    if (existingIndex >= 0) {
      // Update quantity
      const updated = [...bundleItems];
      updated[existingIndex].qty += 1;
      setBundleItems(updated);
    } else {
      // Add new item
      setBundleItems([...bundleItems, { item_id: item.item_id, qty: 1 }]);
    }
    setSearchTerm('');
  };

  const updateBundleItemQty = (itemId, qty) => {
    if (qty <= 0) {
      setBundleItems(prev => prev.filter(bi => bi.item_id !== itemId));
    } else {
      setBundleItems(prev => prev.map(bi => 
        bi.item_id === itemId ? { ...bi, qty } : bi
      ));
    }
  };

  const removeBundleItem = (itemId) => {
    setBundleItems(prev => prev.filter(bi => bi.item_id !== itemId));
  };

  const formatPrice = (satang) => {
    return `฿${(satang / 100).toFixed(2)}`;
  };

  const getFilteredItems = () => {
    return availableItems.filter(item => 
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      item.item_id !== formData.item_id && // Don't include self in bundles
      item.active
    );
  };

  const renderBasicFields = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Item Name"
          value={formData.name}
          onChange={(e) => handleInputChange('name', e.target.value)}
          required
          helperText="Enter a descriptive name for the item"
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth required>
          <InputLabel>Item Type</InputLabel>
          <Select
            value={formData.type}
            onChange={(e) => handleInputChange('type', e.target.value)}
            label="Item Type"
          >
            {Object.entries(ITEM_TYPES).map(([key, config]) => (
              <MenuItem key={key} value={key}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  {config.icon}
                  <Box>
                    <Typography variant="body2">{config.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {config.description}
                    </Typography>
                  </Box>
                </Stack>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12}>
        <TextField
          fullWidth
          label="Description"
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          multiline
          rows={3}
          helperText="Optional description of the item"
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Price (THB)"
          type="number"
          value={formData.price_satang / 100}
          onChange={(e) => handleInputChange('price_satang', Math.round(e.target.value * 100))}
          required
          inputProps={{ min: 0, step: 0.01 }}
          helperText={`Satang: ${formData.price_satang}`}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControl fullWidth>
          <InputLabel>Category</InputLabel>
          <Select
            value={formData.category_id}
            onChange={(e) => handleInputChange('category_id', e.target.value)}
            label="Category"
          >
            <MenuItem value="">No Category</MenuItem>
            {categories.map((category) => (
              <MenuItem key={category.category_id} value={category.category_id}>
                {category.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControl fullWidth>
          <InputLabel>Tax Class</InputLabel>
          <Select
            value={formData.tax_class}
            onChange={(e) => handleInputChange('tax_class', e.target.value)}
            label="Tax Class"
          >
            <MenuItem value="STANDARD">Standard</MenuItem>
            <MenuItem value="EXEMPT">Exempt</MenuItem>
            <MenuItem value="REDUCED">Reduced</MenuItem>
          </Select>
        </FormControl>
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
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom>
          Images
        </Typography>
        <ImageUpload
          images={formData.images || []}
          onImagesChange={(images) => handleInputChange('images', images)}
          ownerType="product"
          ownerId={formData.item_id || 'temp-' + Date.now()}
          maxImages={5}
          disabled={loading}
        />
      </Grid>
    </Grid>
  );

  const renderStockedGoodFields = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="SKU"
          value={formData.stocked_good?.sku || ''}
          onChange={(e) => handleTypeSpecificChange('stocked_good', 'sku', e.target.value)}
          helperText="Stock Keeping Unit identifier"
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Unit of Measure</InputLabel>
          <Select
            value={formData.stocked_good?.uom || 'piece'}
            onChange={(e) => handleTypeSpecificChange('stocked_good', 'uom', e.target.value)}
            label="Unit of Measure"
          >
            {UOM_OPTIONS.map(uom => (
              <MenuItem key={uom} value={uom}>{uom}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Cost (THB)"
          type="number"
          value={formData.stocked_good?.cost_satang ? formData.stocked_good.cost_satang / 100 : ''}
          onChange={(e) => handleTypeSpecificChange('stocked_good', 'cost_satang', Math.round(e.target.value * 100))}
          inputProps={{ min: 0, step: 0.01 }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Reorder Point"
          type="number"
          value={formData.stocked_good?.reorder_point || ''}
          onChange={(e) => handleTypeSpecificChange('stocked_good', 'reorder_point', parseInt(e.target.value) || 0)}
          inputProps={{ min: 0 }}
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Low Stock Threshold"
          type="number"
          value={formData.stocked_good?.low_stock_threshold || ''}
          onChange={(e) => handleTypeSpecificChange('stocked_good', 'low_stock_threshold', parseInt(e.target.value) || 0)}
          inputProps={{ min: 0 }}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Supplier"
          value={formData.stocked_good?.supplier || ''}
          onChange={(e) => handleTypeSpecificChange('stocked_good', 'supplier', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={formData.stocked_good?.track_inventory || false}
              onChange={(e) => handleTypeSpecificChange('stocked_good', 'track_inventory', e.target.checked)}
            />
          }
          label="Track Inventory"
        />
      </Grid>
    </Grid>
  );

  const renderPassTimeFields = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <TextField
          fullWidth
          label="Duration (Hours)"
          type="number"
          value={formData.pass_time?.duration_hours || ''}
          onChange={(e) => handleTypeSpecificChange('pass_time', 'duration_hours', parseInt(e.target.value) || 0)}
          inputProps={{ min: 1 }}
          required
        />
      </Grid>
      
      <Grid item xs={12} md={4}>
        <FormControl fullWidth>
          <InputLabel>Validity Scope</InputLabel>
          <Select
            value={formData.pass_time?.validity_scope || 'same_day'}
            onChange={(e) => handleTypeSpecificChange('pass_time', 'validity_scope', e.target.value)}
            label="Validity Scope"
          >
            {VALIDITY_SCOPES.map(scope => (
              <MenuItem key={scope.value} value={scope.value}>
                {scope.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      
      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Allowed Zones</InputLabel>
          <Select
            multiple
            value={formData.pass_time?.zones_allowed || []}
            onChange={(e) => handleTypeSpecificChange('pass_time', 'zones_allowed', e.target.value)}
            label="Allowed Zones"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip key={value} label={value} size="small" />
                ))}
              </Box>
            )}
          >
            <MenuItem value="YELLOW">Yellow Zone</MenuItem>
            <MenuItem value="GREEN">Green Zone</MenuItem>
            <MenuItem value="BLUE">Blue Zone</MenuItem>
            <MenuItem value="RED">Red Zone</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  const renderRideCreditFields = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Number of Credits"
          type="number"
          value={formData.ride_credit_bundle?.credits || formData.single_ride?.credits || ''}
          onChange={(e) => {
            const field = formData.type === 'RIDE_CREDIT_BUNDLE' ? 'ride_credit_bundle' : 'single_ride';
            handleTypeSpecificChange(field, 'credits', parseInt(e.target.value) || 1);
          }}
          inputProps={{ min: 1 }}
          required
        />
      </Grid>
    </Grid>
  );

  const renderBundleFields = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Bill of Materials (BOM)
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Add items to create a bundle. The bundle price should cover the cost of included items.
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={8}>
                <Autocomplete
                  options={getFilteredItems()}
                  getOptionLabel={(option) => option.name}
                  value={null}
                  onChange={(event, newValue) => {
                    if (newValue) {
                      addBundleItem(newValue);
                    }
                  }}
                  inputValue={searchTerm}
                  onInputChange={(event, newInputValue) => {
                    setSearchTerm(newInputValue);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Search items to add"
                      InputProps={{
                        ...params.InputProps,
                        startAdornment: <Search sx={{ mr: 1 }} />,
                      }}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  {getFilteredItems().length} items available
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {bundleItems.length > 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Price</TableCell>
                  <TableCell>Quantity</TableCell>
                  <TableCell>Total</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {bundleItems.map((bundleItem) => {
                  const item = availableItems.find(i => i.item_id === bundleItem.item_id);
                  if (!item) return null;
                  
                  return (
                    <TableRow key={bundleItem.item_id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {item.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={ITEM_TYPES[item.type]?.label || item.type}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{formatPrice(item.price_satang)}</TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={bundleItem.qty}
                          onChange={(e) => updateBundleItemQty(bundleItem.item_id, parseInt(e.target.value) || 0)}
                          inputProps={{ min: 1 }}
                          size="small"
                          sx={{ width: 80 }}
                        />
                      </TableCell>
                      <TableCell>
                        {formatPrice(item.price_satang * bundleItem.qty)}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => removeBundleItem(bundleItem.item_id)}
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Update bundle BOM */}
        {bundleItems.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={() => handleTypeSpecificChange('bundle', 'bom', bundleItems)}
            >
              Update BOM
            </Button>
          </Box>
        )}
      </Grid>
    </Grid>
  );

  const renderUpgradeFields = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="From Entitlement"
          value={formData.upgrade?.from_entitlement || ''}
          onChange={(e) => handleTypeSpecificChange('upgrade', 'from_entitlement', e.target.value)}
          required
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="To Entitlement"
          value={formData.upgrade?.to_entitlement || ''}
          onChange={(e) => handleTypeSpecificChange('upgrade', 'to_entitlement', e.target.value)}
          required
        />
      </Grid>
      
      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Price Difference Strategy</InputLabel>
          <Select
            value={formData.upgrade?.strategy || 'pay_difference'}
            onChange={(e) => handleTypeSpecificChange('upgrade', 'strategy', e.target.value)}
            label="Price Difference Strategy"
          >
            {PRICE_DIFF_STRATEGIES.map(strategy => (
              <MenuItem key={strategy.value} value={strategy.value}>
                {strategy.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  const renderTypeSpecificFields = () => {
    switch (formData.type) {
      case 'STOCKED_GOOD':
        return renderStockedGoodFields();
      case 'PASS_TIME':
        return renderPassTimeFields();
      case 'RIDE_CREDIT_BUNDLE':
      case 'SINGLE_RIDE':
        return renderRideCreditFields();
      case 'BUNDLE':
        return renderBundleFields();
      case 'UPGRADE':
        return renderUpgradeFields();
      default:
        return (
          <Alert severity="info">
            No additional fields required for this item type.
          </Alert>
        );
    }
  };

  const renderPreview = () => {
    const typeInfo = ITEM_TYPES[formData.type];
    const totalBundleCost = bundleItems.reduce((total, bi) => {
      const item = availableItems.find(i => i.item_id === bi.item_id);
      return total + (item ? item.price_satang * bi.qty : 0);
    }, 0);

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Item Preview
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                {typeInfo?.icon}
                <Typography variant="h6">{formData.name}</Typography>
                <Chip label={typeInfo?.label} color={typeInfo?.color} size="small" />
              </Stack>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {formData.description || 'No description provided'}
              </Typography>
              
              <Stack spacing={1}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Price:</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {formatPrice(formData.price_satang)}
                  </Typography>
                </Box>
                
                {formData.category_id && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Category:</Typography>
                    <Typography variant="body2">
                      {categories.find(c => c.category_id === formData.category_id)?.name || formData.category_id}
                    </Typography>
                  </Box>
                )}
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Status:</Typography>
                  <Chip 
                    label={formData.active ? 'Active' : 'Inactive'} 
                    color={formData.active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Image Preview */}
        {formData.images && formData.images.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Images ({formData.images.length})
                </Typography>
                <Grid container spacing={2}>
                  {formData.images.map((image, index) => (
                    <Grid item xs={6} sm={4} md={3} key={index}>
                      <Box sx={{ position: 'relative' }}>
                        <img
                          src={image.url}
                          alt={image.filename}
                          style={{
                            width: '100%',
                            height: '120px',
                            objectFit: 'cover',
                            borderRadius: '8px',
                          }}
                        />
                        {image.primary && (
                          <Chip
                            label="Primary"
                            color="primary"
                            size="small"
                            sx={{
                              position: 'absolute',
                              top: 4,
                              left: 4,
                            }}
                          />
                        )}
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Computed Effects
              </Typography>
              
              {formData.type === 'STOCKED_GOOD' && formData.stocked_good?.cost_satang && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Unit Margin:</Typography>
                  <Typography variant="body2" fontWeight="medium" color="success.main">
                    {formatPrice(formData.price_satang - formData.stocked_good.cost_satang)}
                  </Typography>
                </Box>
              )}
              
              {formData.type === 'BUNDLE' && bundleItems.length > 0 && (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Bundle Cost:</Typography>
                    <Typography variant="body2">{formatPrice(totalBundleCost)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Bundle Price:</Typography>
                    <Typography variant="body2">{formatPrice(formData.price_satang)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Bundle Margin:</Typography>
                    <Typography 
                      variant="body2" 
                      fontWeight="medium" 
                      color={formData.price_satang >= totalBundleCost ? 'success.main' : 'error.main'}
                    >
                      {formatPrice(formData.price_satang - totalBundleCost)}
                    </Typography>
                  </Box>
                </>
              )}
              
              {formData.type === 'PASS_TIME' && (
                <Typography variant="body2" color="info.main">
                  Will issue {formData.pass_time?.duration_hours || 0}h time-based entitlement
                </Typography>
              )}
              
              {formData.type === 'RIDE_CREDIT_BUNDLE' && (
                <Typography variant="body2" color="info.main">
                  Will add {formData.ride_credit_bundle?.credits || 0} ride credits to card
                </Typography>
              )}
              
              {formData.type === 'SINGLE_RIDE' && (
                <Typography variant="body2" color="info.main">
                  Will add {formData.single_ride?.credits || 1} ride credit to card
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {formData.type === 'BUNDLE' && bundleItems.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="info">
              Bundle contains {bundleItems.length} item(s). Make sure the bundle price covers the total cost of included items.
            </Alert>
          </Grid>
        )}
      </Grid>
    );
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBasicFields();
      case 1:
        return renderTypeSpecificFields();
      case 2:
        return renderPreview();
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {mode === 'add' ? 'Add New Item' : 'Edit Item'}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Stack>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Box sx={{ minHeight: 400 }}>
          {renderStepContent()}
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose}>
          Cancel
        </Button>
        
        {activeStep > 0 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button variant="contained" onClick={handleNext}>
            Next
          </Button>
        ) : (
          <Button 
            variant="contained" 
            onClick={handleSave}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckCircle />}
          >
            {loading ? 'Saving...' : mode === 'add' ? 'Create Item' : 'Save Changes'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
