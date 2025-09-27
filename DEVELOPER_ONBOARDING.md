# Developer Onboarding Guide

**PlayPark POS v1.15.1 - Getting Started with APIs**

Welcome to the PlayPark POS system! This guide will help you understand how to work with our APIs and build amazing features.

---

## 🎯 What You Can Build

### Media-Rich Applications
- **Product Catalogs** - Rich product galleries with multiple images
- **Category Management** - Visual category browsing with banner images
- **Brand Experiences** - Consistent branding across all touchpoints
- **User Profiles** - Avatar and profile image management

### Complete POS Operations
- **Sales Processing** - End-to-end sales with pricing, taxes, discounts
- **Payment Handling** - Multiple payment methods with reconciliation
- **Customer Management** - CRM with loyalty programs and analytics
- **Employee Operations** - Time tracking, approvals, cash management
- **Inventory Control** - Stock tracking and management
- **Reporting & Analytics** - Business intelligence and insights

---

## 🚀 Quick Start (5 Minutes)

### 1. Setup Infrastructure
```bash
cd backend-fastapi
./setup_media.sh
```

### 2. Start the API Server
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 48080
```

### 3. Test the APIs
```bash
# Health check
curl http://localhost:48080/healthz

# Interactive documentation
open http://localhost:48080/docs
```

### 4. Get Your First Token
```bash
curl -X POST "http://localhost:48080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@playpark.com", "password": "demo123"}'
```

---

## 📸 Media API - Your First Integration

### Understanding the Upload Flow

The Media API uses a **3-step upload process** for security and performance:

1. **Presign** - Get secure upload URL
2. **Upload** - Upload directly to S3 (bypasses API server)
3. **Complete** - Finalize and trigger processing

### Step-by-Step Example

#### 1. Request Upload Permission
```javascript
const presignResponse = await fetch('/api/v1/media/uploads/presign', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    filename: 'product-image.jpg',
    mime_type: 'image/jpeg',
    owner_type: 'product',
    owner_id: 'prod_123'
  })
});

const { upload_url, headers, asset_id } = await presignResponse.json();
```

#### 2. Upload File to S3
```javascript
const formData = new FormData();
Object.entries(headers).forEach(([key, value]) => {
  formData.append(key, value);
});
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch(upload_url, {
  method: 'POST',
  body: formData
});
```

#### 3. Complete Upload
```javascript
await fetch('/api/v1/media/complete', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    asset_id,
    storage_key: headers.key
  })
});
```

#### 4. Get Processed Images
```javascript
const assetResponse = await fetch(`/api/v1/media/${asset_id}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

const asset = await assetResponse.json();
console.log('Available variants:', asset.variants);
// thumb, sm, md, lg variants are now available!
```

### Real-World Use Cases

#### Product Gallery
```javascript
// Get all product images
const images = await fetch(`/api/v1/media/products/${productId}/images`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Display in UI
images.forEach(image => {
  const img = document.createElement('img');
  img.src = image.variants.find(v => v.variant === 'md').url;
  img.alt = image.alt_text;
  gallery.appendChild(img);
});
```

#### Category Banner
```javascript
// Set category banner
const bannerAsset = await uploadImage(file, 'category', categoryId);
await fetch(`/api/v1/categories/${categoryId}`, {
  method: 'PATCH',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    banner_image_id: bannerAsset.asset_id
  })
});
```

---

## 🏪 POS API - Building Sales Features

### Understanding the Sales Flow

The POS API follows a **deterministic pricing model** that ensures consistency between preview and final calculations:

1. **Preview** - Calculate pricing with all rules
2. **Create Cart** - Park items for checkout
3. **Checkout** - Create sale + payment atomically

### Step-by-Step Sales Example

#### 1. Calculate Pricing
```javascript
const pricingResponse = await fetch('/api/v1/pricing/preview', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    items: [
      {
        product_id: 'prod_123',
        quantity: 2,
        unit_price: 5000  // 50.00 THB in satang
      }
    ],
    customer_id: 'cust_456',
    promo_code: 'EARLY_BIRD'
  })
});

const pricing = await pricingResponse.json();
console.log(`Total: ${pricing.total / 100} THB`);
```

#### 2. Create Open Ticket (Cart)
```javascript
const cartResponse = await fetch('/api/v1/open_tickets', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    items: [
      {
        product_id: 'prod_123',
        quantity: 2,
        unit_price: 5000
      }
    ],
    customer_id: 'cust_456',
    expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString() // 30 min
  })
});

const cart = await cartResponse.json();
```

#### 3. Checkout to Sale + Payment
```javascript
const checkoutResponse = await fetch(`/api/v1/open_tickets/${cart.open_ticket_id}/checkout`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    payment_method: 'cash',
    amount_paid: pricing.total,
    customer_id: 'cust_456'
  })
});

const { sale, payment } = await checkoutResponse.json();
console.log(`Sale ${sale.sale_id} completed with payment ${payment.payment_id}`);
```

### Advanced POS Features

#### Cash Drawer Management
```javascript
// Open drawer
await fetch('/api/v1/cash_drawers/open', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    opening_amount: 10000,  // 100.00 THB
    employee_id: employeeId
  })
});

// Process sales...

// Close drawer
await fetch('/api/v1/cash_drawers/close', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    closing_amount: 25000,  // 250.00 THB
    employee_id: employeeId
  })
});
```

#### Employee Time Tracking
```javascript
// Clock in
const timecard = await fetch('/api/v1/timecards/clock-in', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    employee_id: employeeId,
    device_id: deviceId
  })
});

// Take break
await fetch('/api/v1/timecards/break/start', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    timecard_id: timecard.timecard_id,
    break_type: 'lunch'
  })
});

// End break
await fetch('/api/v1/timecards/break/end', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    timecard_id: timecard.timecard_id
  })
});
```

---

## 🔐 Authentication & Security

### Understanding Scopes and Permissions

The API uses **JWT tokens** with **scoped access**:

```json
{
  "sub": "employee_123",
  "type": "access",
  "tenant_id": "tenant_1",
  "store_id": "store_1",
  "scopes": ["sales", "media", "reports"],
  "roles": ["cashier", "manager"],
  "permissions": ["read", "write", "admin"]
}
```

### Common Scopes
- `sales` - Sales and payment operations
- `media` - Media upload and management
- `reports` - Reporting and analytics
- `admin` - Administrative functions
- `provider` - Provider-specific operations

### Role-Based Access
- **Cashier** - Basic sales operations
- **Manager** - Approvals, refunds, reports
- **Admin** - Full system access
- **Provider** - Device and health monitoring

---

## 🧪 Testing Your Integration

### Unit Testing
```javascript
// Test media upload flow
describe('Media API', () => {
  test('should upload image successfully', async () => {
    const presign = await presignUpload('test.jpg', 'product', 'prod_123');
    expect(presign.upload_url).toBeDefined();
    
    const upload = await uploadToS3(presign.upload_url, presign.headers, file);
    expect(upload.status).toBe(200);
    
    const complete = await completeUpload(presign.asset_id, presign.storage_key);
    expect(complete.success).toBe(true);
  });
});
```

### Integration Testing
```javascript
// Test complete sales flow
describe('POS Integration', () => {
  test('should complete sale with pricing', async () => {
    const pricing = await getPricing(items, customerId);
    const cart = await createCart(items, customerId);
    const sale = await checkout(cart.id, pricing.total);
    
    expect(sale.sale_id).toBeDefined();
    expect(sale.payment_id).toBeDefined();
    expect(sale.total).toBe(pricing.total);
  });
});
```

### Load Testing
```bash
# Test media upload performance
ab -n 100 -c 10 -T 'application/json' \
  -p presign_request.json \
  http://localhost:48080/api/v1/media/uploads/presign

# Test pricing calculation
ab -n 1000 -c 50 -T 'application/json' \
  -p pricing_request.json \
  http://localhost:48080/api/v1/pricing/preview
```

---

## 🚀 Building Advanced Features

### Real-Time Updates with WebSockets
```javascript
const ws = new WebSocket('ws://localhost:48080/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'sale_completed') {
    updateSalesDisplay(data.sale);
  }
  if (data.type === 'media_processed') {
    updateImageDisplay(data.asset);
  }
};
```

### Offline-First with Sync
```javascript
// Store operations offline
const offlineOperations = [];
offlineOperations.push({
  type: 'create_sale',
  data: saleData,
  timestamp: Date.now()
});

// Sync when online
if (navigator.onLine) {
  await syncOfflineOperations(offlineOperations);
}
```

### Background Processing
```javascript
// Upload multiple images
const uploadPromises = files.map(async (file) => {
  const presign = await presignUpload(file.name, 'product', productId);
  await uploadToS3(presign.upload_url, presign.headers, file);
  return await completeUpload(presign.asset_id, presign.storage_key);
});

const results = await Promise.all(uploadPromises);
console.log(`${results.length} images uploaded successfully`);
```

---

## 📊 Monitoring & Debugging

### Request Logging
```javascript
// Add request ID to all requests
const requestId = generateRequestId();
fetch('/api/v1/media', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Request-ID': requestId
  }
});

// Log errors with context
try {
  await apiCall();
} catch (error) {
  console.error('API Error:', {
    requestId,
    endpoint: '/api/v1/media',
    error: error.message,
    timestamp: new Date().toISOString()
  });
}
```

### Performance Monitoring
```javascript
// Measure API response times
const startTime = performance.now();
const response = await fetch('/api/v1/pricing/preview', options);
const endTime = performance.now();

console.log(`API call took ${endTime - startTime} milliseconds`);

// Track usage metrics
analytics.track('api_call', {
  endpoint: '/api/v1/pricing/preview',
  duration: endTime - startTime,
  success: response.ok
});
```

---

## 🎯 Best Practices

### 1. Error Handling
```javascript
async function apiCall(endpoint, options) {
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.error.code, error.error.message);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      handleApiError(error);
    } else {
      handleNetworkError(error);
    }
  }
}
```

### 2. Caching Strategy
```javascript
// Cache frequently accessed data
const cache = new Map();

async function getCachedData(key, fetcher) {
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const data = await fetcher();
  cache.set(key, data);
  
  // Expire cache after 5 minutes
  setTimeout(() => cache.delete(key), 5 * 60 * 1000);
  
  return data;
}
```

### 3. Rate Limiting
```javascript
// Implement client-side rate limiting
const rateLimiter = {
  requests: new Map(),
  
  canMakeRequest(endpoint) {
    const now = Date.now();
    const requests = this.requests.get(endpoint) || [];
    
    // Remove requests older than 1 hour
    const recentRequests = requests.filter(time => now - time < 3600000);
    
    if (recentRequests.length >= 1000) { // 1000/hour limit
      return false;
    }
    
    recentRequests.push(now);
    this.requests.set(endpoint, recentRequests);
    return true;
  }
};
```

---

## 🔗 Resources & Next Steps

### Documentation
- **[Complete API Reference](API_REFERENCE_GUIDE.md)** - Comprehensive guide
- **[API Quick Reference](API_QUICK_REFERENCE.md)** - Developer cheat sheet
- **[Media API Docs](backend-fastapi/MEDIA_API_DOCUMENTATION.md)** - Media-specific
- **[POS API Docs](backend-fastapi/POS_API_DOCUMENTATION.md)** - POS-specific

### Development Tools
- **Interactive Docs**: http://localhost:48080/docs
- **Test Suite**: `test_media_api.py`, `test_pos_api.py`
- **Setup Script**: `setup_media.sh`

### Community & Support
- **GitHub Issues**: Report bugs and request features
- **Discord/Slack**: Developer community
- **Email Support**: dev-support@playpark.com

### What to Build Next
1. **Mobile App** - React Native or Flutter integration
2. **Admin Dashboard** - React/Vue.js web interface
3. **Analytics Platform** - Business intelligence dashboard
4. **E-commerce Integration** - Shopify/WooCommerce sync
5. **Payment Gateway** - Stripe/PayPal integration
6. **AI Features** - Image recognition, predictive analytics

---

## 🎉 Congratulations!

You now have everything you need to build amazing features with the PlayPark POS APIs! 

### Quick Checklist
- ✅ Infrastructure setup complete
- ✅ API server running
- ✅ Authentication working
- ✅ Media upload flow tested
- ✅ POS operations tested
- ✅ Error handling implemented
- ✅ Monitoring in place

**Happy coding!** 🚀

---

*Need help? Check the [API Quick Reference](API_QUICK_REFERENCE.md) or join our developer community!*
