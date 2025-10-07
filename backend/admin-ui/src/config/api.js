// API Configuration for FastAPI Backend
import axios from 'axios';

// FastAPI backend configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:50080';
const API_VERSION = 'v1';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Skip authentication for test endpoints
    const isTestEndpoint = config.url?.includes('/test') || config.url?.includes('/test-');
    
    if (!isTestEndpoint) {
      const token = localStorage.getItem('admin_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('admin_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    EMPLOYEE_LOGIN: '/auth/employees/login',
    EMPLOYEE_ME: '/auth/employees/me',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    VERIFY_PIN: '/auth/verify_pin',
  },
  
  // Sales
  SALES: {
    CREATE: '/sales',
    GET_BY_ID: (id) => `/sales/${id}`,
    LIST: '/sales',
    REFUNDS: '/sales/refunds',
    REPRINTS: '/sales/reprints',
  },
  
  // Reports
  REPORTS: {
    SALES: '/reports/sales',
    SHIFTS: '/reports/shifts',
    TICKETS: '/reports/tickets',
    FRAUD: '/reports/fraud',
  },
  
  // Catalog
  CATALOG: {
    PACKAGES: '/catalog/packages',
    PRICING_RULES: '/catalog/pricing/rules',
    CALCULATE_PRICING: '/catalog/pricing/calculate',
  },

  // Items Management (New Items Taxonomy API)
  ITEMS: {
    LIST: '/items/test-list',
    GET_BY_ID: (id) => `/items/${id}`,
    CREATE: '/items/test-create',
    UPDATE: (id) => `/items/${id}`,
    DELETE: (id) => `/items/${id}`,
    UPDATE_STATUS: (id) => `/items/${id}/status`,
  },

  // Inventory Management
  INVENTORY: {
    ITEMS: '/inventory/items',
    MOVEMENTS: '/inventory/movements',
    CREATE_MOVEMENT: '/inventory/movements',
  },

  // Categories
  CATEGORIES: {
    LIST: '/categories',
    GET_BY_ID: (id) => `/categories/${id}`,
    CREATE: '/categories',
    UPDATE: (id) => `/categories/${id}`,
    DELETE: (id) => `/categories/${id}`,
  },

  // Media Management
  MEDIA: {
    PRESIGN: '/media/uploads/test-presign',
    COMPLETE: '/media/test-complete',
    DELETE: '/media/assets',
    PRODUCT_IMAGES: (productId) => `/media/products/${productId}/images`,
    SET_PRIMARY: (productId) => `/media/products/${productId}/images/primary`,
    REORDER: (productId) => `/media/products/${productId}/images/order`,
  },

  // Cards (for Quick Actions)
  CARDS: {
    GET_BY_ID: (id) => `/cards/${id}`,
    ADD_ENTITLEMENT: (id) => `/cards/${id}/entitlements`,
    ADD_CREDITS: (id) => `/cards/${id}/credits/add`,
  },

  // Access Zones
  ACCESS_ZONES: {
    LIST: '/access/zones/test-list',
    GET_BY_ID: (id) => `/access/zones/test-get/${id}`,
    CREATE: '/access/zones/test-create',
    UPDATE: (id) => `/access/zones/test-update/${id}`,
    DELETE: (id) => `/access/zones/test-delete/${id}`,
  },
  
  // Shifts
  SHIFTS: {
    OPEN: '/shifts/open',
    CLOSE: '/shifts/close',
    CURRENT: '/shifts/current',
  },
  
  // Tickets
  TICKETS: {
    REDEEM: '/tickets/redeem',
    GET_BY_ID: (id) => `/tickets/${id}`,
  },
  
  // Users
  USERS: {
    LIST: '/users',
    GET_BY_ID: (id) => `/users/${id}`,
    CREATE: '/users',
    UPDATE: (id) => `/users/${id}`,
    DELETE: (id) => `/users/${id}`,
  },
  
  // Stores & Devices
  STORES: {
    LIST: '/stores',
    GET_BY_ID: (id) => `/stores/${id}`,
    CREATE: '/stores',
    UPDATE: (id) => `/stores/${id}`,
    DELETE: (id) => `/stores/${id}`,
  },
  
  DEVICES: {
    LIST: '/devices',
    GET_BY_ID: (id) => `/devices/${id}`,
    CREATE: '/devices',
    UPDATE: (id) => `/devices/${id}`,
    DELETE: (id) => `/devices/${id}`,
  },
  
  // Settings
  SETTINGS: {
    GET: '/settings',
    UPDATE: '/settings',
  },
};

export default apiClient;

