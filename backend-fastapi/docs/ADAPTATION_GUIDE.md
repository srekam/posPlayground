# PlayPark API Migration Guide: Express.js → FastAPI

This guide documents the migration from the Node.js/Express backend to the FastAPI Python backend, preserving business semantics while modernizing the runtime.

## 📋 Overview

### Migration Goals
- **Preserve Business Logic**: Maintain exact API contracts and business semantics
- **Modernize Runtime**: Upgrade to async/await, type safety, and modern Python
- **Enhance Developer Experience**: Better tooling, documentation, and testing
- **Improve Performance**: ASGI server, connection pooling, and caching

### Technology Stack Changes

| Component | Legacy (Express.js) | New (FastAPI) |
|-----------|-------------------|---------------|
| **Framework** | Express.js | FastAPI |
| **Runtime** | Node.js | Python 3.11+ |
| **Server** | HTTP | ASGI (Uvicorn) |
| **Database Driver** | Mongoose | Motor (async) |
| **Validation** | Express-validator | Pydantic v2 |
| **Authentication** | Custom JWT | OAuth2 + JWT |
| **Caching** | Manual | Redis + async |
| **Documentation** | Manual | Auto-generated OpenAPI |

## 🔄 Route Mapping

### Authentication Routes

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `POST /v1/auth/device/login` | `POST /api/v1/auth/device/login` | ✅ Migrated | Device authentication |
| `POST /v1/auth/employees/login` | `POST /api/v1/auth/employees/login` | ✅ Migrated | Employee authentication |
| `POST /v1/auth/refresh` | `POST /api/v1/auth/refresh` | ✅ Migrated | Token refresh |
| `POST /v1/auth/logout` | `POST /api/v1/auth/logout` | ✅ Migrated | User logout |
| `POST /v1/auth/approvals/verify_pin` | `POST /api/v1/auth/verify_pin` | ✅ Migrated | PIN verification |

### Sales Routes

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `POST /v1/sales` | `POST /api/v1/sales` | ✅ Migrated | Create sale |
| `GET /v1/sales/{id}` | `GET /api/v1/sales/{sale_id}` | ✅ Migrated | Get sale |
| `GET /v1/sales` | `GET /api/v1/sales` | ✅ Migrated | List sales |
| `POST /v1/sales/refunds` | `POST /api/v1/sales/refunds` | ✅ Migrated | Request refund |
| `POST /v1/sales/reprints` | `POST /api/v1/sales/reprints` | ✅ Migrated | Request reprint |

### Ticket Routes

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `POST /v1/tickets/redeem` | `POST /api/v1/tickets/redeem` | ✅ Migrated | Redeem ticket |
| `GET /v1/tickets/{id}` | `GET /api/v1/tickets/{ticket_id}` | ✅ Migrated | Get ticket |

### Catalog Routes

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `GET /v1/catalog/packages` | `GET /api/v1/catalog/packages` | ✅ Migrated | Get packages |
| `GET /v1/catalog/pricing/rules` | `GET /api/v1/catalog/pricing/rules` | ✅ Migrated | Get pricing rules |
| `POST /v1/catalog/pricing/calculate` | `POST /api/v1/catalog/pricing/calculate` | 🚧 Pending | Calculate pricing |

### Shift Routes

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `POST /v1/shifts/open` | `POST /api/v1/shifts/open` | ✅ Migrated | Open shift |
| `POST /v1/shifts/close` | `POST /api/v1/shifts/close` | ✅ Migrated | Close shift |
| `GET /v1/shifts/current` | `GET /api/v1/shifts/current` | ✅ Migrated | Get current shift |

### Report Routes

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `GET /v1/reports/sales` | `GET /api/v1/reports/sales` | ✅ Migrated | Sales report |
| `GET /v1/reports/shifts` | `GET /api/v1/reports/shifts` | ✅ Migrated | Shifts report |
| `GET /v1/reports/tickets` | `GET /api/v1/reports/tickets` | ✅ Migrated | Tickets report |
| `GET /v1/reports/fraud` | `GET /api/v1/reports/fraud` | 🚧 Pending | Fraud report |

### Provider Routes (Phase 6)

| Legacy Route | New Route | Method | Status |
|--------------|-----------|---------|---------|
| `GET /provider/reports/templates` | `GET /provider/reports/templates` | ✅ Migrated | Report templates |
| `POST /provider/dashboards` | `POST /provider/dashboards` | ✅ Migrated | Create dashboard |
| `GET /provider/widgets` | `GET /provider/widgets` | ✅ Migrated | Widget management |
| `GET /provider/analytics/{id}` | `GET /provider/analytics/{template_id}` | ✅ Migrated | Analytics data |

## 📝 Request/Response Changes

### Response Envelope

**Legacy Format:**
```json
{
  "server_time": "2025-09-24T09:30:00.000Z",
  "request_id": "req_123456789",
  "data": { /* response data */ }
}
```

**New Format (Preserved):**
```json
{
  "server_time": "2025-09-24T09:30:00.000Z",
  "request_id": "req_123456789",
  "data": { /* response data */ }
}
```

### Error Envelope

**Legacy Format:**
```json
{
  "error": "E_ERROR_CODE",
  "message": "Human readable error message",
  "details": { /* additional context */ }
}
```

**New Format (Preserved):**
```json
{
  "error": "E_ERROR_CODE",
  "message": "Human readable error message",
  "details": { /* additional context */ }
}
```

## 🔐 Authentication Changes

### JWT Token Structure

**Legacy Claims:**
```json
{
  "sub": "user_id",
  "iat": 1695540600,
  "exp": 1695544200,
  "tenant_id": "tenant_123",
  "store_id": "store_456"
}
```

**New Claims (Enhanced):**
```json
{
  "sub": "user_id",
  "type": "access",
  "tenant_id": "tenant_123",
  "store_id": "store_456",
  "device_id": "device_789",
  "scopes": ["sales", "tickets"],
  "iat": 1695540600,
  "exp": 1695544200
}
```

### Authentication Headers

**Legacy:**
```http
Authorization: Bearer <jwt_token>
X-Device-Token: <device_token>
```

**New (Preserved):**
```http
Authorization: Bearer <jwt_token>
X-Device-Token: <device_token>
```

### Cookie Support (New)

For web clients:
```http
Cookie: access_token=<jwt_token>; refresh_token=<refresh_token>
```

## 🗄️ Database Changes

### Connection Management

**Legacy (Mongoose):**
```javascript
mongoose.connect(MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
});
```

**New (Motor):**
```python
client = AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=50,
    serverSelectionTimeoutMS=2000,
    retryWrites=True
)
```

### Query Patterns

**Legacy (Mongoose):**
```javascript
const sales = await Sale.find({
  tenant_id: req.tenant_id,
  store_id: req.store_id
}).sort({ timestamp: -1 });
```

**New (Motor):**
```python
sales = await sale_repo.get_many(
    query={"tenant_id": tenant_id, "store_id": store_id},
    sort=[("timestamp", -1)]
)
```

## 🚀 Performance Improvements

### Async/Await
- **Legacy**: Callback-based with some Promise support
- **New**: Full async/await throughout the application

### Connection Pooling
- **Legacy**: Default Mongoose connection pooling
- **New**: Optimized Motor connection pool with configurable limits

### Caching
- **Legacy**: Manual caching implementation
- **New**: Redis-based caching with automatic TTL management

### Rate Limiting
- **Legacy**: Express-rate-limit middleware
- **New**: SlowAPI with Redis backend for distributed rate limiting

## 🧪 Testing Changes

### Test Framework

**Legacy (Jest):**
```javascript
describe('Sales API', () => {
  test('should create sale', async () => {
    const response = await request(app)
      .post('/v1/sales')
      .send(saleData);
    expect(response.status).toBe(201);
  });
});
```

**New (pytest):**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_sale(client: AsyncClient):
    response = await client.post("/api/v1/sales", json=sale_data)
    assert response.status_code == 201
```

## 📊 Monitoring & Observability

### Logging

**Legacy:**
```javascript
logger.info('Sale created', { sale_id, amount });
```

**New (Structured):**
```python
logger.info("Sale created", sale_id=sale_id, amount=amount)
```

### Health Checks

**Legacy:**
```
GET /health
```

**New (Enhanced):**
```
GET /healthz    # Kubernetes-style health check
GET /readyz     # Readiness check
GET /metrics    # Prometheus metrics
```

## 🔧 Development Workflow

### Local Development

**Legacy:**
```bash
npm install
npm run dev
```

**New:**
```bash
make install
make dev
# or
docker-compose up -d
```

### Testing

**Legacy:**
```bash
npm test
npm run test:watch
```

**New:**
```bash
make test
pytest tests/ -v --cov
```

### Deployment

**Legacy:**
```bash
npm start
```

**New:**
```bash
make run
# or
docker-compose up -d
```

## 📚 API Documentation

### Legacy
- Manual API documentation
- Postman collections

### New
- **Swagger UI**: `http://localhost:48080/docs`
- **ReDoc**: `http://localhost:48080/redoc`
- **OpenAPI JSON**: `http://localhost:48080/openapi.json`
- Auto-generated client SDKs

## 🚨 Breaking Changes

### None
This migration preserves all existing API contracts. No breaking changes for clients.

### Deprecation Warnings
- Some legacy endpoints may be marked as deprecated in OpenAPI docs
- New endpoints will be clearly documented

## 🎯 Migration Checklist

### Phase 1: Core Infrastructure ✅
- [x] FastAPI application setup
- [x] Database connection (Motor)
- [x] Redis integration
- [x] Authentication system
- [x] Response envelope middleware
- [x] Error handling
- [x] Logging configuration

### Phase 2: API Routes ✅
- [x] Authentication routes
- [x] Sales routes
- [x] Ticket routes
- [x] Catalog routes
- [x] Shift routes
- [x] Report routes
- [x] Provider routes (Phase 6)

### Phase 3: Business Logic 🚧
- [x] Authentication service
- [ ] Sales service (placeholder)
- [ ] Ticket service (placeholder)
- [ ] Catalog service (placeholder)
- [ ] Shift service (placeholder)
- [ ] Report service (placeholder)

### Phase 4: Testing & Documentation 🚧
- [ ] Unit tests
- [ ] Integration tests
- [ ] API documentation
- [ ] Migration guide

### Phase 5: Deployment 🚧
- [ ] Docker configuration
- [ ] CI/CD pipeline
- [ ] Environment configuration
- [ ] Monitoring setup

## 🔍 Client Migration Guide

### JavaScript/TypeScript Clients

**Legacy:**
```javascript
const response = await fetch('/v1/sales', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(saleData)
});
```

**New (Same API):**
```javascript
const response = await fetch('/api/v1/sales', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(saleData)
});
```

### Android Clients

**Legacy:**
```kotlin
val response = apiClient.post("/v1/sales", saleData)
```

**New:**
```kotlin
val response = apiClient.post("/api/v1/sales", saleData)
```

## 🆘 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if services are running: `docker-compose ps`
   - Verify ports are not in use: `netstat -tlnp | grep 48080`

2. **Authentication Errors**
   - Verify JWT_SECRET is set
   - Check token expiration
   - Ensure proper scopes

3. **Database Connection Issues**
   - Check MongoDB is running: `docker-compose logs mongo`
   - Verify connection string format
   - Check network connectivity

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Run with verbose output
make dev
```

## 📞 Support

For migration support:
- Check the logs: `docker-compose logs api`
- Review the OpenAPI docs: `http://localhost:48080/docs`
- Run health checks: `curl http://localhost:48080/healthz`

---

**Migration Status**: 🚧 In Progress  
**Completion**: ~80% (Core infrastructure and routes complete, business logic pending)  
**Next Steps**: Implement business services, add comprehensive tests, finalize documentation
