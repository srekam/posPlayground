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
  Avatar,
  IconButton,
} from '@mui/material';
import { Add, Edit, Delete, Person } from '@mui/icons-material';
import axios from 'axios';

export default function Employees() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [employees, setEmployees] = useState([]);
  const [roles, setRoles] = useState([]);
  const [activeTab, setActiveTab] = useState('employees');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [employeesRes, rolesRes] = await Promise.all([
        axios.get('/v1/employees'),
        axios.get('/v1/roles')
      ]);

      setEmployees(employeesRes.data.data || []);
      setRoles(rolesRes.data.data || []);
    } catch (err) {
      console.error('Failed to fetch employee data:', err);
      setError('Failed to load employee data');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return;
    
    try {
      await axios.delete(`/v1/employees/${id}`);
      fetchData();
    } catch (err) {
      console.error('Failed to delete employee:', err);
      setError('Failed to delete employee');
    }
  };

  const handleSuspend = async (id, status) => {
    try {
      await axios.patch(`/v1/employees/${id}`, { status });
      fetchData();
    } catch (err) {
      console.error('Failed to update employee status:', err);
      setError('Failed to update employee status');
    }
  };

  const renderEmployees = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Employee</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Roles</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Last Login</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {employees.map((employee) => (
            <TableRow key={employee.employee_id}>
              <TableCell>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ mr: 2 }}>
                    {employee.name?.charAt(0) || <Person />}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2">{employee.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {employee.employee_id}
                    </Typography>
                  </Box>
                </Box>
              </TableCell>
              <TableCell>{employee.email}</TableCell>
              <TableCell>
                <Box>
                  {employee.roles?.map((role, index) => (
                    <Chip key={index} label={role} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </Box>
              </TableCell>
              <TableCell>
                <Chip 
                  label={employee.status} 
                  color={employee.status === 'active' ? 'success' : 'error'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                {employee.last_login ? new Date(employee.last_login).toLocaleDateString() : 'Never'}
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(employee)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color={employee.status === 'active' ? 'warning' : 'success'}
                  onClick={() => handleSuspend(employee.employee_id, 
                    employee.status === 'active' ? 'suspended' : 'active')}
                >
                  {employee.status === 'active' ? 'Suspend' : 'Activate'}
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(employee.employee_id)}
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

  const renderRoles = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Role Name</TableCell>
            <TableCell>Permissions</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {roles.map((role) => (
            <TableRow key={role.role_id}>
              <TableCell>
                <Typography variant="subtitle2">{role.name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  ID: {role.role_id}
                </Typography>
              </TableCell>
              <TableCell>
                <Box>
                  {role.permissions?.map((permission, index) => (
                    <Chip key={index} label={permission} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </Box>
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={() => handleEdit(role)}
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => handleDelete(role.role_id)}
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
          Employees & Roles
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
              { key: 'employees', label: 'Employees' },
              { key: 'roles', label: 'Roles' }
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
          {activeTab === 'employees' && renderEmployees()}
          {activeTab === 'roles' && renderRoles()}
        </>
      )}

      {/* Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit' : 'Add'} {activeTab.slice(0, -1)}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Employee/Role management form would be implemented here with proper validation and API integration.
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
