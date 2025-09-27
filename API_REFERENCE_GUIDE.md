# PlayPark POS API Reference Guide

**Version 1.15.1 - Complete API Documentation**

This comprehensive guide covers all available APIs in the PlayPark POS system, including the new media storage backbone and the complete POS functionality.

---

## 📚 Table of Contents

1. [Quick Start](#-quick-start)
2. [API Overview](#-api-overview)
3. [Media API (NEW in v1.15.1)](#-media-api-new-in-v1151)
4. [Complete POS API](#-complete-pos-api)
5. [Authentication & Authorization](#-authentication--authorization)
6. [Error Handling](#-error-handling)
7. [Rate Limiting](#-rate-limiting)
8. [Testing & Examples](#-testing--examples)
9. [Future API Development](#-future-api-development)

---

## 🚀 Quick Start

### Base URLs
- **Development**: `http://localhost:48080/api/v1`
- **Production**: `https://api.playpark.com/api/v1`

### Authentication
```bash
# Get access token
curl -X POST "http://localhost:48080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:48080/api/v1/media"
```

### Interactive Documentation
- **Swagger UI**: http://localhost:48080/docs
- **ReDoc**: http://localhost:48080/redoc

---

## 🎯 API Overview

### Version Breakdown (v1.15.1)
- **App (1)**: Flutter mobile application
- **API (15)**: Complete POS + Media storage backbone
- **Web UI (1)**: Web administration interface

### API Categories
1. **Media Management** (NEW) - File uploads, image processing, CDN delivery
2. **Sales & Payments** - Transactions, pricing, checkout
3. **Inventory & Catalog** - Products, categories, pricing rules
4. **Customer Management** - CRM, loyalty, analytics
5. **Employee Operations** - Time tracking, approvals, permissions
6. **System Management** - Settings, health monitoring, usage tracking

---

## 📸 Media API (NEW in v1.15.1)

### Overview
The Media API provides comprehensive file storage and image processing capabilities using S3/MinIO with CDN integration.

### Core Features
- ✅ **Direct S3 Uploads** - Presigned URLs bypass API server
- ✅ **Image Processing** - Automatic WebP variants (thumb, sm, md, lg)
- ✅ **Security** - MIME validation, EXIF stripping, deduplication
- ✅ **CDN Integration** - Fast global delivery with caching
- ✅ **Multi-tenant** - Isolated storage paths per tenant

### Endpoints

#### 1. Upload Flow
```bash
# Step 1: Get presigned upload URL
POST /api/v1/media/uploads/presign
{
  "filename": "product-image.jpg",
  "mime_type": "image/jpeg",
  "owner_type": "product",
  "owner_id": "prod_123"
}

# Response:
{
  "upload_url": "https://storage.example.com/...",
  "storage_key": "tenants/tenant1/products/prod_123/asset_id/orig.jpg",
  "headers": {...},
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W"
}

# Step 2: Upload directly to S3 using presigned URL
# Step 3: Complete upload
POST /api/v1/media/complete
{
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W",
  "storage_key": "tenants/tenant1/products/prod_123/asset_id/orig.jpg"
}
```

#### 2. Asset Management
```bash
# List assets with filtering
GET /api/v1/media?owner_type=product&owner_id=prod_123

# Get specific asset
GET /api/v1/media/{asset_id}

# Delete asset (soft delete + storage cleanup)
DELETE /api/v1/media/{asset_id}
```

#### 3. Product Images
```bash
# Get all product images (ordered)
GET /api/v1/media/products/{product_id}/images

# Reorder product images
POST /api/v1/media/products/{product_id}/images/order
{
  "asset_ids": ["asset1", "asset2", "asset3"]
}

# Set primary image
POST /api/v1/media/products/{product_id}/images/primary
{
  "asset_id": "asset1"
}
```

### Response Format
```json
{
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W",
  "tenant_id": "tenant1",
  "owner_type": "product",
  "owner_id": "prod_123",
  "filename_original": "product-image.jpg",
  "mime_type": "image/jpeg",
  "bytes": 2048576,
  "width": 1200,
  "height": 800,
  "acl": "public",
  "variants": [
    {
      "variant": "thumb",
      "url": "https://cdn.example.com/.../thumb.webp",
      "width": 150,
      "height": 150,
      "bytes": 15432,
      "format": "webp"
    }
  ],
  "processing_status": "completed",
  "created_at": "2023-12-01T12:00:00Z"
}
```

### Use Cases
- **Product Galleries** - Multiple images with ordering and primary designation
- **Category Images** - Banner images and category icons
- **Brand Assets** - Logos and brand materials
- **User Profiles** - Profile pictures and avatars
- **Receipt Templates** - Custom receipt designs

---

## 🏪 Complete POS API

### 1. Payments API (`/api/v1/payments`)

#### Create Payment
```bash
POST /api/v1/payments
{
  "sale_id": "sale_123",
  "payment_type_id": "payment_type_1",
  "amount": 15000,  // 150.00 THB in satang
  "currency": "THB",
  "metadata": {
    "transaction_id": "txn_456",
    "card_last4": "1234"
  }
}
```

#### List Payments
```bash
GET /api/v1/payments?start_date=2023-12-01&end_date=2023-12-31&status=completed
```

#### Payment Statistics
```bash
GET /api/v1/payments/summary/stats
```

### 2. Pricing API (`/api/v1/pricing`)

#### Deterministic Pricing Preview
```bash
POST /api/v1/pricing/preview
{
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 2,
      "unit_price": 5000  // 50.00 THB
    }
  ],
  "customer_id": "cust_456",
  "promo_code": "EARLY_BIRD"
}
```

#### Response
```json
{
  "subtotal": 10000,
  "discounts": [
    {
      "type": "percentage",
      "amount": 1000,
      "description": "Early Bird 10%"
    }
  ],
  "taxes": [
    {
      "tax_id": "tax_1",
      "rate": 0.07,
      "amount": 630
    }
  ],
  "total": 9630,
  "breakdown": {
    "subtotal": 10000,
    "discount_total": 1000,
    "tax_total": 630,
    "final_total": 9630
  }
}
```

### 3. Redemptions API (`/api/v1/redemptions`)

#### Redeem Ticket
```bash
POST /api/v1/redemptions
{
  "ticket_id": "ticket_123",
  "device_id": "device_456",
  "redemption_type": "entry"
}
```

#### Check Duplicate Redemption
```bash
GET /api/v1/redemptions/duplicate-check/ticket_123
```

### 4. Open Tickets API (`/api/v1/open_tickets`)

#### Park Cart
```bash
POST /api/v1/open_tickets
{
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 2,
      "unit_price": 5000
    }
  ],
  "customer_id": "cust_456",
  "expires_at": "2023-12-01T15:00:00Z"
}
```

#### Checkout to Sale + Payment
```bash
POST /api/v1/open_tickets/{open_ticket_id}/checkout
{
  "payment_method": "cash",
  "amount_paid": 9630,
  "customer_id": "cust_456"
}
```

### 5. Cash Drawers API (`/api/v1/cash_drawers`)

#### Open Cash Drawer
```bash
POST /api/v1/cash_drawers/open
{
  "opening_amount": 10000,  // 100.00 THB
  "employee_id": "emp_123"
}
```

#### Close Cash Drawer
```bash
POST /api/v1/cash_drawers/close
{
  "closing_amount": 25000,  // 250.00 THB
  "employee_id": "emp_123"
}
```

#### Drawer Summary
```bash
GET /api/v1/cash_drawers/summary
```

### 6. Timecards API (`/api/v1/timecards`)

#### Clock In/Out
```bash
POST /api/v1/timecards/clock-in
{
  "employee_id": "emp_123",
  "device_id": "device_456"
}

POST /api/v1/timecards/clock-out
{
  "timecard_id": "timecard_789"
}
```

#### Break Management
```bash
POST /api/v1/timecards/break/start
{
  "timecard_id": "timecard_789",
  "break_type": "lunch"
}

POST /api/v1/timecards/break/end
{
  "timecard_id": "timecard_789"
}
```

### 7. Customers API (`/api/v1/customers`)

#### Create Customer
```bash
POST /api/v1/customers
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+66812345678",
  "loyalty_points": 0,
  "metadata": {
    "birth_date": "1990-01-01",
    "preferred_language": "en"
  }
}
```

#### Search Customers
```bash
GET /api/v1/customers/search?q=john&limit=10
```

#### Top Customers
```bash
GET /api/v1/customers/top/spenders?period=month&limit=10
```

### 8. Settings API (`/api/v1/settings`)

#### Get Merged Settings
```bash
GET /api/v1/settings
```

#### Set Setting
```bash
PUT /api/v1/settings/keys/tax_rate
{
  "value": 0.07,
  "description": "Standard VAT rate"
}
```

#### Feature Flags
```bash
GET /api/v1/settings/feature-flags

PUT /api/v1/settings/feature-flags/new_checkout_flow
{
  "enabled": true,
  "conditions": {
    "tenant_id": "tenant_1",
    "rollout_percentage": 50
  }
}
```

### 9. Approvals API (`/api/v1/approvals`)

#### Verify PIN
```bash
POST /api/v1/approvals/verify-pin
{
  "pin": "1234",
  "operation": "refund"
}
```

#### Create Approval Request
```bash
POST /api/v1/approvals
{
  "operation": "refund",
  "amount": 5000,
  "reason_code_id": "reason_1",
  "requested_by": "emp_123",
  "metadata": {
    "sale_id": "sale_456",
    "description": "Customer complaint"
  }
}
```

### 10. Provider Health API (`/api/v1/provider`)

#### Device Heartbeat
```bash
POST /api/v1/provider/heartbeats
{
  "device_id": "device_123",
  "status": "online",
  "version": "1.15.1",
  "last_seen": "2023-12-01T12:00:00Z"
}
```

#### Provider Overview
```bash
GET /api/v1/provider/overview
```

#### Alerts
```bash
GET /api/v1/provider/alerts?status=active

POST /api/v1/provider/alerts/{alert_id}/acknowledge
{
  "acknowledged_by": "admin_123",
  "notes": "Investigating issue"
}
```

### 11. Usage Counters API (`/api/v1/usage`)

#### Billing Usage
```bash
GET /api/v1/usage/billing/usage?month=2023-12
```

#### Tenant Statistics
```bash
GET /api/v1/usage/stats/tenant?period=month
```

#### Increment Usage
```bash
POST /api/v1/usage/increment
{
  "route": "/api/v1/payments",
  "tenant_id": "tenant_1",
  "count": 1
}
```

---

## 🔐 Authentication & Authorization

### JWT Token Structure
```json
{
  "sub": "employee_id_or_device_id",
  "type": "access|device|refresh",
  "tenant_id": "tenant_identifier",
  "store_id": "store_identifier",
  "scopes": ["sales", "tickets", "reports", "media"],
  "roles": ["cashier", "manager", "admin"],
  "permissions": ["read", "write", "admin"],
  "exp": 1234567890
}
```

### Scoping Rules
- **Tenant Scope**: All `/api/v1/*` endpoints require tenant access
- **Store Scope**: Store-specific operations require store access
- **Media Scope**: Media operations require `media` scope
- **Provider Scope**: `/api/v1/provider/*` requires provider access

### Token Usage
```bash
# Include in headers
Authorization: Bearer YOUR_JWT_TOKEN

# Or as query parameter (for webhooks)
?token=YOUR_JWT_TOKEN
```

---

## ❌ Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "E_NOT_FOUND",
    "message": "Resource not found",
    "details": {
      "resource": "payment",
      "id": "12345"
    },
    "request_id": "req_1234567890"
  }
}
```

### Common Error Codes
- `E_PERMISSION` - Permission denied
- `E_NOT_FOUND` - Resource not found
- `E_DUPLICATE` - Duplicate resource
- `E_EXPIRED` - Resource expired
- `E_USED` - Resource already used
- `E_REVOKED` - Resource revoked
- `E_SCOPE_MISMATCH` - Scope mismatch
- `E_RATE_LIMIT` - Rate limit exceeded
- `E_VALIDATION_ERROR` - Input validation failed
- `E_STORAGE_ERROR` - Storage operation failed
- `E_PROCESSING_ERROR` - Image processing failed

---

## 🚦 Rate Limiting

### Limits by Endpoint
- **Media Upload**: 100 requests/hour per user
- **Pricing Preview**: 100 requests/hour per user
- **Refunds/Reprints**: 50 requests/hour per user
- **General API**: 1000 requests/hour per user
- **Enrollment**: 10 requests/hour per IP

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

---

## 🧪 Testing & Examples

### Media API Testing
```bash
# Run the test suite
cd backend-fastapi
python test_media_api.py

# Test upload flow
curl -X POST "http://localhost:48080/api/v1/media/uploads/presign" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.jpg", "mime_type": "image/jpeg", "owner_type": "product", "owner_id": "test123"}'
```

### POS API Testing
```bash
# Test pricing preview
curl -X POST "http://localhost:48080/api/v1/pricing/preview" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": "prod1", "quantity": 1, "unit_price": 5000}]}'

# Test payment creation
curl -X POST "http://localhost:48080/api/v1/payments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sale_id": "sale1", "payment_type_id": "cash", "amount": 5000}'
```

---

## 🚀 Future API Development

### Planned Features

#### 1. Advanced Media Features
- **Video Support** - Video upload and processing
- **Document Management** - PDF and document handling
- **AI Integration** - Automatic image tagging and optimization
- **Advanced Editing** - Crop, resize, filter operations

#### 2. Enhanced POS Features
- **Loyalty Programs** - Points, tiers, rewards
- **Inventory Management** - Stock tracking, alerts, reordering
- **Advanced Analytics** - Sales trends, customer insights
- **Multi-location Support** - Chain store management

#### 3. Integration APIs
- **Payment Gateways** - Stripe, PayPal, local payment methods
- **Accounting Systems** - QuickBooks, Xero integration
- **CRM Systems** - Salesforce, HubSpot integration
- **E-commerce** - Shopify, WooCommerce sync

#### 4. Mobile-First APIs
- **Offline Sync** - Conflict resolution, data synchronization
- **Push Notifications** - Real-time alerts and updates
- **Mobile Payments** - NFC, QR code payments
- **Location Services** - GPS tracking, geofencing

### Development Guidelines

#### 1. API Design Principles
- **RESTful** - Follow REST conventions
- **Consistent** - Use consistent naming and structure
- **Versioned** - Maintain backward compatibility
- **Documented** - Comprehensive OpenAPI documentation

#### 2. Security Best Practices
- **Authentication** - JWT tokens with proper scoping
- **Authorization** - Role-based access control
- **Validation** - Input validation and sanitization
- **Rate Limiting** - Protect against abuse

#### 3. Performance Considerations
- **Caching** - Redis caching for frequently accessed data
- **Pagination** - Limit result sets for large queries
- **Async Processing** - Background jobs for heavy operations
- **CDN Integration** - Fast delivery of static assets

#### 4. Monitoring & Observability
- **Structured Logging** - JSON logs with request IDs
- **Metrics** - Prometheus metrics for monitoring
- **Health Checks** - Kubernetes-ready health endpoints
- **Error Tracking** - Comprehensive error reporting

### Adding New APIs

#### 1. Create Model
```python
# app/models/new_feature.py
from beanie import Document
from pydantic import Field
from ulid import ULID

class NewFeature(Document):
    feature_id: str = Field(default_factory=lambda: str(ULID()))
    name: str = Field(..., description="Feature name")
    # ... other fields
```

#### 2. Create Repository
```python
# app/repositories/new_feature.py
from ..models.new_feature import NewFeature
from ..utils.errors import NotFoundError

class NewFeatureRepository:
    async def create(self, feature: NewFeature) -> NewFeature:
        await feature.insert()
        return feature
    
    async def get_by_id(self, feature_id: str) -> NewFeature:
        feature = await NewFeature.find_one(NewFeature.feature_id == feature_id)
        if not feature:
            raise NotFoundError(f"Feature {feature_id} not found")
        return feature
```

#### 3. Create Router
```python
# app/routers/new_feature.py
from fastapi import APIRouter, Depends, HTTPException
from ..models.new_feature import NewFeature
from ..repositories.new_feature import NewFeatureRepository

router = APIRouter(prefix="/api/v1/new-features", tags=["New Features"])

@router.post("/", response_model=NewFeature)
async def create_feature(
    feature: NewFeature,
    repo: NewFeatureRepository = Depends(get_new_feature_repository)
):
    return await repo.create(feature)
```

#### 4. Add to Main App
```python
# app/main.py
from app.routers.new_feature import router as new_feature_router

app.include_router(new_feature_router)
```

#### 5. Add Tests
```python
# test_new_feature_api.py
async def test_create_feature():
    response = await client.post(
        "/api/v1/new-features/",
        json={"name": "Test Feature"}
    )
    assert response.status_code == 201
```

### API Versioning Strategy

#### 1. URL Versioning
```
/api/v1/media/     # Current version
/api/v2/media/     # Future version
```

#### 2. Header Versioning
```http
Accept: application/vnd.playpark.v2+json
API-Version: v2
```

#### 3. Backward Compatibility
- Maintain old endpoints for at least 6 months
- Use deprecation warnings
- Provide migration guides

---

## 📞 Support & Resources

### Documentation
- **API Reference**: This document
- **Media API**: [MEDIA_API_DOCUMENTATION.md](backend-fastapi/MEDIA_API_DOCUMENTATION.md)
- **POS API**: [POS_API_DOCUMENTATION.md](backend-fastapi/POS_API_DOCUMENTATION.md)
- **Interactive Docs**: http://localhost:48080/docs

### Development Tools
- **Test Suite**: `test_media_api.py`, `test_pos_api.py`
- **Setup Script**: `setup_media.sh`
- **Docker**: `docker-compose.media.yml`

### Monitoring
- **Health Checks**: `/healthz`, `/readyz`
- **Metrics**: Prometheus endpoints
- **Logs**: Structured JSON logging

---

**🎉 This comprehensive API reference provides everything you need to work with the PlayPark POS system, from basic operations to advanced features and future development!**
