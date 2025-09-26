import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  People,
  Inventory,
  Assessment,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import apiClient, { API_ENDPOINTS } from '../config/api';

const StatCard = ({ title, value, icon, color = 'primary' }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h4" component="h2">
            {value}
          </Typography>
        </Box>
        <Box color={`${color}.main`}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    todaySales: 0,
    activeShifts: 0,
    totalTickets: 0,
    redemptionRate: 0,
  });
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch today's sales
      const salesResponse = await apiClient.get(API_ENDPOINTS.REPORTS.SALES, {
        params: {
          start_date: new Date().toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0],
        }
      });

      // Fetch active shifts
      const shiftsResponse = await apiClient.get(API_ENDPOINTS.SHIFTS.CURRENT);

      // Fetch ticket stats
      const ticketsResponse = await apiClient.get(API_ENDPOINTS.REPORTS.TICKETS, {
        params: {
          start_date: new Date().toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0],
        }
      });

      // For now, use mock data for hourly sales since this endpoint doesn't exist yet
      const hourlyData = [
        { hour: '09:00', sales: 1500 },
        { hour: '10:00', sales: 2300 },
        { hour: '11:00', sales: 3200 },
        { hour: '12:00', sales: 4100 },
        { hour: '13:00', sales: 3800 },
        { hour: '14:00', sales: 2900 },
        { hour: '15:00', sales: 2100 },
        { hour: '16:00', sales: 1800 },
        { hour: '17:00', sales: 2500 },
        { hour: '18:00', sales: 3200 },
      ];

      setStats({
        todaySales: salesResponse.data.data.total_sales || 0,
        activeShifts: shiftsResponse.data.data.length || 0,
        totalTickets: ticketsResponse.data.data.total_issued || 0,
        redemptionRate: ticketsResponse.data.data.redemption_rate || 0,
      });

      setChartData(hourlyData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data');
      
      // Set fallback data for demo
      setStats({
        todaySales: 12500,
        activeShifts: 2,
        totalTickets: 45,
        redemptionRate: 78,
      });
      
      setChartData([
        { hour: '09:00', sales: 1500 },
        { hour: '10:00', sales: 2300 },
        { hour: '11:00', sales: 3200 },
        { hour: '12:00', sales: 4100 },
        { hour: '13:00', sales: 3800 },
        { hour: '14:00', sales: 2900 },
        { hour: '15:00', sales: 2100 },
        { hour: '16:00', sales: 1800 },
        { hour: '17:00', sales: 2500 },
        { hour: '18:00', sales: 3200 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Sales"
            value={`฿${stats.todaySales.toLocaleString()}`}
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Shifts"
            value={stats.activeShifts}
            icon={<People sx={{ fontSize: 40 }} />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Tickets Issued"
            value={stats.totalTickets}
            icon={<Inventory sx={{ fontSize: 40 }} />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Redemption Rate"
            value={`${stats.redemptionRate}%`}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>

        {/* Charts */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Hourly Sales Today
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip formatter={(value) => [`฿${value}`, 'Sales']} />
                <Line type="monotone" dataKey="sales" stroke="#1976d2" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Box>
              <Typography variant="body2" color="text.secondary">
                • POS Device 1: Sale completed
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Gate Device 1: Ticket redeemed
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Manager: Shift opened
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Kiosk Device 1: Package sold
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
