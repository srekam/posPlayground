# PlayPark POS API Quick Reference

**Version 1.15.1 - Developer Cheat Sheet**

---

## 🚀 Quick Start

```bash
# Base URL
BASE_URL="http://localhost:48080/api/v1"

# Authentication
curl -H "Authorization: Bearer YOUR_TOKEN" "$BASE_URL/media"

# Interactive Docs
open http://localhost:48080/docs
```

---

## 📸 Media API (NEW)

### Upload Flow
```bash
# 1. Get presigned URL
POST /api/v1/media/uploads/presign
{
  "filename": "image.jpg",
  "mime_type": "image/jpeg",
  "owner_type": "product",
  "owner_id": "prod_123"
}

# 2. Upload to S3 (direct)
# 3. Complete upload
POST /api/v1/media/complete
{
  "asset_id": "asset_id",
  "storage_key": "storage_key"
}
```

### Asset Management
```bash
# List assets
GET /api/v1/media?owner_type=product&owner_id=prod_123

# Get asset
GET /api/v1/media/{asset_id}

# Delete asset
DELETE /api/v1/media/{asset_id}

# Product images
GET /api/v1/media/products/{product_id}/images
POST /api/v1/media/products/{product_id}/images/order
POST /api/v1/media/products/{product_id}/images/primary
```

---

## 🏪 POS API Essentials

### Payments
```bash
# Create payment
POST /api/v1/payments
{
  "sale_id": "sale_123",
  "payment_type_id": "cash",
  "amount": 15000  # 150.00 THB in satang
}

# List payments
GET /api/v1/payments?start_date=2023-12-01&status=completed

# Payment stats
GET /api/v1/payments/summary/stats
```

### Pricing
```bash
# Pricing preview (deterministic)
POST /api/v1/pricing/preview
{
  "items": [
    {"product_id": "prod_123", "quantity": 2, "unit_price": 5000}
  ],
  "customer_id": "cust_456",
  "promo_code": "EARLY_BIRD"
}
```

### Redemptions
```bash
# Redeem ticket
POST /api/v1/redemptions
{
  "ticket_id": "ticket_123",
  "device_id": "device_456",
  "redemption_type": "entry"
}

# Check duplicates
GET /api/v1/redemptions/duplicate-check/ticket_123
```

### Open Tickets (Cart Parking)
```bash
# Park cart
POST /api/v1/open_tickets
{
  "items": [{"product_id": "prod_123", "quantity": 2, "unit_price": 5000}],
  "customer_id": "cust_456",
  "expires_at": "2023-12-01T15:00:00Z"
}

# Checkout to sale + payment
POST /api/v1/open_tickets/{open_ticket_id}/checkout
{
  "payment_method": "cash",
  "amount_paid": 9630
}
```

### Cash Drawers
```bash
# Open drawer
POST /api/v1/cash_drawers/open
{
  "opening_amount": 10000,
  "employee_id": "emp_123"
}

# Close drawer
POST /api/v1/cash_drawers/close
{
  "closing_amount": 25000,
  "employee_id": "emp_123"
}

# Summary
GET /api/v1/cash_drawers/summary
```

### Timecards
```bash
# Clock in/out
POST /api/v1/timecards/clock-in
POST /api/v1/timecards/clock-out

# Break management
POST /api/v1/timecards/break/start
POST /api/v1/timecards/break/end

# Current timecard
GET /api/v1/timecards/current
```

### Customers
```bash
# Create customer
POST /api/v1/customers
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+66812345678"
}

# Search customers
GET /api/v1/customers/search?q=john&limit=10

# Top customers
GET /api/v1/customers/top/spenders?period=month
```

### Settings
```bash
# Get settings
GET /api/v1/settings

# Set setting
PUT /api/v1/settings/keys/tax_rate
{
  "value": 0.07,
  "description": "Standard VAT rate"
}

# Feature flags
GET /api/v1/settings/feature-flags
PUT /api/v1/settings/feature-flags/new_feature
```

### Approvals
```bash
# Verify PIN
POST /api/v1/approvals/verify-pin
{
  "pin": "1234",
  "operation": "refund"
}

# Create approval
POST /api/v1/approvals
{
  "operation": "refund",
  "amount": 5000,
  "reason_code_id": "reason_1"
}
```

### Provider Health
```bash
# Device heartbeat
POST /api/v1/provider/heartbeats
{
  "device_id": "device_123",
  "status": "online",
  "version": "1.15.1"
}

# Overview
GET /api/v1/provider/overview

# Alerts
GET /api/v1/provider/alerts?status=active
```

### Usage Counters
```bash
# Billing usage
GET /api/v1/usage/billing/usage?month=2023-12

# Tenant stats
GET /api/v1/usage/stats/tenant?period=month

# Increment usage
POST /api/v1/usage/increment
{
  "route": "/api/v1/payments",
  "tenant_id": "tenant_1",
  "count": 1
}
```

---

## 🔐 Authentication

### JWT Token
```json
{
  "sub": "employee_id",
  "type": "access",
  "tenant_id": "tenant_1",
  "store_id": "store_1",
  "scopes": ["sales", "media"],
  "roles": ["cashier", "manager"],
  "permissions": ["read", "write"],
  "exp": 1234567890
}
```

### Headers
```http
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

---

## ❌ Error Codes

| Code | Description |
|------|-------------|
| `E_PERMISSION` | Permission denied |
| `E_NOT_FOUND` | Resource not found |
| `E_DUPLICATE` | Duplicate resource |
| `E_EXPIRED` | Resource expired |
| `E_USED` | Resource already used |
| `E_VALIDATION_ERROR` | Input validation failed |
| `E_RATE_LIMIT` | Rate limit exceeded |
| `E_STORAGE_ERROR` | Storage operation failed |
| `E_PROCESSING_ERROR` | Image processing failed |

---

## 🚦 Rate Limits

| Endpoint | Limit |
|----------|-------|
| Media Upload | 100/hour |
| Pricing Preview | 100/hour |
| Refunds/Reprints | 50/hour |
| General API | 1000/hour |
| Enrollment | 10/hour per IP |

---

## 🧪 Testing

```bash
# Media API tests
cd backend-fastapi
python test_media_api.py

# POS API tests
python test_pos_api.py

# Manual testing
curl -X GET "$BASE_URL/healthz"
curl -X GET "$BASE_URL/media" -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Response Formats

### Success Response
```json
{
  "data": {...},
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2023-12-01T12:00:00Z"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "E_NOT_FOUND",
    "message": "Resource not found",
    "details": {"resource": "payment", "id": "12345"},
    "request_id": "req_1234567890"
  }
}
```

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "pages": 3
  }
}
```

---

## 🎯 Common Use Cases

### 1. Product with Images
```bash
# 1. Create product
POST /api/v1/products
# 2. Upload images
POST /api/v1/media/uploads/presign
# 3. Set primary image
POST /api/v1/media/products/{id}/images/primary
```

### 2. Complete Sale Flow
```bash
# 1. Price preview
POST /api/v1/pricing/preview
# 2. Create open ticket (cart)
POST /api/v1/open_tickets
# 3. Checkout to sale + payment
POST /api/v1/open_tickets/{id}/checkout
```

### 3. Employee Operations
```bash
# 1. Clock in
POST /api/v1/timecards/clock-in
# 2. Open cash drawer
POST /api/v1/cash_drawers/open
# 3. Process sales
# 4. Close drawer
POST /api/v1/cash_drawers/close
# 5. Clock out
POST /api/v1/timecards/clock-out
```

---

## 🔗 Resources

- **Complete API Guide**: [API_REFERENCE_GUIDE.md](API_REFERENCE_GUIDE.md)
- **Media API Docs**: [MEDIA_API_DOCUMENTATION.md](backend-fastapi/MEDIA_API_DOCUMENTATION.md)
- **POS API Docs**: [POS_API_DOCUMENTATION.md](backend-fastapi/POS_API_DOCUMENTATION.md)
- **Interactive Docs**: http://localhost:48080/docs
- **Health Check**: http://localhost:48080/healthz

---

**🎉 Happy coding with PlayPark POS APIs!**
