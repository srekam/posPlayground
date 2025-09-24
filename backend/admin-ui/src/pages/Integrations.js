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
  Card,
  CardContent,
} from '@mui/material';
import { Add, Edit, Delete, Webhook, Payment, Print } from '@mui/icons-material';
import axios from 'axios';

export default function Integrations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [webhooks, setWebhooks] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [printers, setPrinters] = useState([]);
  const [activeTab, setActiveTab] = useState('webhooks');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [webhooksRes, paymentRes, printersRes] = await Promise.all([
        axios.get('/v1/webhooks'),
        axios.get('/v1/settings/payment-methods'),
        axios.get('/v1/settings/printers')
      ]);

      setWebhooks(webhooksRes.data.data || []);
      setPaymentMethods(paymentRes.data.data || []);
      setPrinters(printersRes.data.data || []);
    } catch (err) {
      console.error('Failed to fetch integration data:', err);
      setError('Failed to load integration data');
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
      await axios.delete(`/v1/${activeTab}/${id}`);
      fetchData();
    } catch (err) {
      console.error('Failed to delete item:', err);
      setError('Failed to delete item');
    }
  };

  const handleTestWebhook = async (id) => {
    try {
      await axios.post(`/v1/webhooks/${id}/test`);
      alert('Test webhook sent successfully');
    } catch (err) {
      console.error('Failed to test webhook:', err);
      alert('Failed to test webhook');
    }
  };

  const renderWebhooks = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>URL</TableCell>
            <TableCell>Events</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Last Delivery</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {webhooks.map((webhook) => (
            <TableRow key={webhook.webhook_id}>
              <TableCell>{webhook.name}</TableCell>
              <TableCell>
                <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {webhook.url}
                </Typography>
              </TableCell>
              <TableCell>
                <Box>
                  {webhook.events?.map((event, index) => (
                    <Chip key={index} label={event} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </Box>
              </TableCell>
              <TableCell>
                <Chip 
                  label={webhook.active ? 'Active' : 'Inactive'} 
                  color={webhook.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                {webhook.last_delivery ? new Date(webhook.last_delivery).toLocaleString() : 'Never'}
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(webhook)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="info"
                  onClick={() => handleTestWebhook(webhook.webhook_id)}
                >
                  Test
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(webhook.webhook_id)}
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

  const renderPaymentMethods = () => (
    <Grid container spacing={2}>
      {paymentMethods.map((method) => (
        <Grid item xs={12} sm={6} md={4} key={method.method_id}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h6">{method.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {method.type}
                  </Typography>
                </Box>
                <Payment />
              </Box>
              <Box mt={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={method.enabled}
                      onChange={(e) => {
                        // Handle enable/disable
                      }}
                    />
                  }
                  label="Enabled"
                />
              </Box>
              <Box mt={1}>
                <Typography variant="body2">
                  Fee: {method.fee_type === 'percentage' ? `${method.fee_amount}%` : `฿${method.fee_amount}`}
                </Typography>
              </Box>
              <Box mt={2}>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(method)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(method.method_id)}
                >
                  Delete
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  const renderPrinters = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Device</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {printers.map((printer) => (
            <TableRow key={printer.printer_id}>
              <TableCell>{printer.name}</TableCell>
              <TableCell>
                <Chip label={printer.type} size="small" />
              </TableCell>
              <TableCell>{printer.device_name || 'All Devices'}</TableCell>
              <TableCell>
                <Chip 
                  label={printer.active ? 'Active' : 'Inactive'} 
                  color={printer.active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(printer)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(printer.printer_id)}
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
          Integrations
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
              { key: 'webhooks', label: 'Webhooks', icon: <Webhook /> },
              { key: 'payment-methods', label: 'Payment Methods', icon: <Payment /> },
              { key: 'printers', label: 'Printers', icon: <Print /> }
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
          {activeTab === 'webhooks' && renderWebhooks()}
          {activeTab === 'payment-methods' && renderPaymentMethods()}
          {activeTab === 'printers' && renderPrinters()}
        </>
      )}

      {/* Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit' : 'Add'} {activeTab.slice(0, -1)}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Integration configuration form would be implemented here with proper validation and API integration.
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
