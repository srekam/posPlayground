# PlayPark Backend API

A complete Loyverse-style backend for the PlayPark POS system, implementing all 15 specifications from the backend.md document.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- Docker & Docker Compose
- MongoDB (or use Docker)

### Installation

1. **Clone and setup:**
```bash
cd backend
npm install
```

2. **Environment setup:**
```bash
cp env.example .env
# Edit .env with your configuration
```

3. **Start with Docker (Recommended):**
```bash
docker-compose up -d
```

4. **Or start manually:**
```bash
# Start MongoDB first
mongod

# Seed the database
npm run seed

# Start the server
npm start
# or for development
npm run dev
```

## 📋 Demo Credentials

After seeding, use these credentials:

- **Tenant ID:** `tenant_demo_01`
- **Store ID:** `store_demo_01`
- **Manager Email:** `manager@playpark.demo`
- **Manager PIN:** `1234`

### Site Key for Device Registration:
```
tenant_demo_01:store_demo_01:demo-secret-key
```

### Device Tokens:
- **POS Token:** `pos-token-1`
- **Gate Token:** `gate-token-1`
- **Kiosk Token:** `kiosk-token-1`

## 🌐 API Endpoints

The API runs on port **48080** and follows the `/v1` versioning.

### Health Check
```
GET /health
```

### Authentication
```
POST /v1/auth/device/register
POST /v1/auth/device/login
POST /v1/auth/employees/login
POST /v1/auth/approvals/verify_pin
```

### Catalog
```
GET  /v1/catalog/packages
GET  /v1/catalog/pricing/rules
POST /v1/catalog/pricing/calculate
```

### Sales & Tickets
```
POST /v1/sales
GET  /v1/sales/{id}
POST /v1/tickets/redeem
POST /v1/tickets/reprint
POST /v1/tickets/refund
```

### Shifts
```
POST /v1/shifts/open
POST /v1/shifts/close
GET  /v1/shifts/current
```

### Reports
```
GET /v1/reports/sales
GET /v1/reports/shifts
GET /v1/reports/tickets
GET /v1/reports/fraud
```

### Sync (Offline Support)
```
POST /v1/sync/batch
GET  /v1/sync/gate/bootstrap
```

## 🏗️ Architecture

### Core Features Implemented:

1. **✅ Multi-tenant System** - Tenants, Stores, Devices
2. **✅ RBAC Security** - Employees, Roles, Permissions  
3. **✅ Catalog Management** - Packages, Pricing Rules
4. **✅ Ticket System** - Issuance, Redemption, Validation
5. **✅ Sales & Payments** - Shifts, Cash Drawer
6. **✅ Audit & Compliance** - Reprints, Refunds, Logs
7. **✅ Offline Support** - Sync, Outbox Pattern
8. **✅ Reports & Analytics** - Sales, Fraud Watch
9. **✅ Security Controls** - HMAC, JWT, Rate Limiting
10. **✅ API Versioning** - RESTful endpoints

### Database Models:

- **Core:** Tenants, Stores, Devices, Employees, Roles
- **Catalog:** Packages, Pricing Rules, Access Zones  
- **Tickets:** Tickets, Redemptions
- **Sales:** Sales, Shifts, Refunds, Reprints
- **Audit:** Audit Logs, Settings, Webhooks, Outbox Events

## 🐋 Docker Deployment

The system uses Docker Compose with 3 services:

- **`mongo`** - MongoDB database (internal only)
- **`api`** - Node.js REST API (port 48080)
- **`admin`** - React admin UI (port 3000)

### Production Deployment:
```bash
# Set environment variables
export JWT_SECRET="your-production-jwt-secret"
export HMAC_SECRET_V1="your-production-hmac-secret"

# Deploy
docker-compose up -d

# Check health
curl http://localhost:48080/health
```

## 🔒 Security Features

- **JWT Authentication** with device tokens
- **HMAC Signature** verification for QR codes
- **PIN-based approvals** for sensitive operations
- **Rate limiting** and IP tracking
- **Audit logging** for all critical actions
- **Offline fraud detection** patterns

## 📊 Reports & Analytics

- **Sales Reports** - Revenue, discounts, payment methods
- **Shift Reports** - Cash reconciliation, performance
- **Ticket Reports** - Redemption rates, usage patterns
- **Fraud Watch** - Suspicious activity detection

## 🛠️ Development

### Scripts:
```bash
npm start          # Start production server
npm run dev        # Start with nodemon
npm run seed       # Seed database with demo data
npm test           # Run tests
```

### Environment Variables:
See `env.example` for all configuration options.

## 🔧 Troubleshooting

### Common Issues:

1. **Database Connection**: Ensure MongoDB is running
2. **Port Conflicts**: Check if port 48080 is available
3. **Token Issues**: Verify JWT_SECRET is set
4. **CORS Errors**: Update CORS_ORIGIN in environment

### Logs:
```bash
# View logs
docker-compose logs api
docker-compose logs mongo

# Follow logs
docker-compose logs -f api
```

## 📚 API Documentation

For complete API documentation with request/response examples, see the generated Swagger docs at:
```
http://localhost:48080/docs
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.
