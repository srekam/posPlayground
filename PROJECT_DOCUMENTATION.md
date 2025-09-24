# PlayPark POS System - Complete Project Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Flutter Client App](#flutter-client-app)
4. [Backend Server](#backend-server)
5. [API Documentation](#api-documentation)
6. [RBAC System](#rbac-system)
7. [Adaptive Integration](#adaptive-integration)
8. [Development Guide](#development-guide)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

PlayPark is a comprehensive Point of Sale (POS) system designed for indoor playgrounds and entertainment venues. The system consists of a Flutter client application and a Node.js backend server with MongoDB database.

### Key Features

- **Multi-platform POS**: Flutter app for Android, iOS, and Web
- **Offline-First**: SQLite database with sync capabilities
- **Multi-tenant**: Support for multiple tenants and stores
- **RBAC Security**: Role-based access control with permissions
- **Real-time Sync**: Adaptive connectivity with backend
- **Comprehensive Reporting**: Sales, shifts, and analytics
- **QR Code System**: Ticket generation and redemption
- **Admin Dashboard**: Web-based administration panel

### Technology Stack

**Frontend (Flutter)**
- Flutter 3.x with Material 3 design
- Riverpod for state management
- Go Router for navigation
- SQLite for offline storage
- HTTP client for API communication

**Backend (Node.js)**
- Express.js REST API
- MongoDB with Mongoose ODM
- JWT authentication
- HMAC signature verification
- Docker containerization

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │   Backend API   │    │   MongoDB       │
│                 │    │                 │    │                 │
│ • POS Interface │◄──►│ • REST API      │◄──►│ • Data Storage  │
│ • Offline Mode  │    │ • Authentication│    │ • Multi-tenant  │
│ • QR Scanner    │    │ • RBAC System   │    │ • Audit Logs    │
│ • Sync Service  │    │ • Business Logic│    │ • Reports       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────┐            ┌─────────┐            ┌─────────┐
    │ SQLite  │            │ Docker  │            │ Admin   │
    │ Local   │            │ Compose │            │ UI      │
    │ Storage │            │ Services│            │ React   │
    └─────────┘            └─────────┘            └─────────┘
```

### Project Structure

```
posPlayground/
├── lib/                          # Flutter app source
│   ├── core/                     # Core functionality
│   │   ├── config/              # App configuration
│   │   ├── providers/           # Riverpod providers
│   │   ├── services/            # Core services
│   │   └── theme/               # UI theming
│   ├── data/                    # Data layer
│   │   ├── database/            # SQLite helpers
│   │   ├── models/              # Data models
│   │   ├── repositories/        # Data access
│   │   └── services/            # API services
│   ├── domain/                  # Business logic
│   │   └── models/              # Domain models
│   ├── features/                # Feature modules
│   │   ├── pos/                 # POS functionality
│   │   ├── gate/                # Gate scanning
│   │   ├── checkout/            # Checkout process
│   │   ├── reports/             # Reports & analytics
│   │   └── settings/            # Settings & config
│   └── widgets/                 # Reusable widgets
├── backend/                      # Node.js backend
│   ├── src/                     # Source code
│   │   ├── config/              # Configuration
│   │   ├── controllers/         # API controllers
│   │   ├── middleware/          # Express middleware
│   │   ├── models/              # Mongoose models
│   │   ├── routes/              # API routes
│   │   ├── services/            # Business services
│   │   └── utils/               # Utilities
│   ├── admin-ui/                # React admin dashboard
│   └── docker-compose.yml       # Docker configuration
└── docs/                        # Documentation files
```

---

## 📱 Flutter Client App

### Core Features

#### 1. Adaptive UI System
- **Online Mode**: Full functionality with real-time sync
- **Offline Mode**: Limited functionality with local data
- **Degraded Mode**: Partial connectivity with retry options
- **Unregistered Mode**: Demo mode for setup
- **Unauthenticated Mode**: Login prompts and limited access

#### 2. POS Functionality
- **Package Catalog**: Display available packages and pricing
- **Shopping Cart**: Add/remove items with quantity controls
- **Checkout Process**: Calculate totals, taxes, and discounts
- **Payment Processing**: Multiple payment methods
- **Receipt Generation**: QR code and receipt printing

#### 3. Gate Scanning
- **QR Code Scanner**: Real-time ticket validation
- **Pass/Fail Results**: Clear visual feedback
- **Ticket History**: Track redemption attempts
- **Offline Validation**: Local validation when offline

#### 4. Offline Support
- **SQLite Database**: Local data storage
- **Sync Service**: Bidirectional synchronization
- **Outbox Pattern**: Queue operations for later sync
- **Conflict Resolution**: Server-wins strategy

### Key Components

#### Adaptive UI Components
```dart
// Adaptive button that enables/disables based on capabilities
AdaptiveButton(
  onPressed: () => processSale(),
  requiredCapability: 'can_sell',
  child: Text('Process Sale'),
)

// Adaptive status banner
AdaptiveModeBanner(
  showBanner: true,
  child: MaterialApp(...),
)
```

#### State Management
```dart
// Riverpod providers for state management
final adaptiveProvider = StateNotifierProvider<AdaptiveModeNotifier, AdaptiveState>(
  (ref) => AdaptiveModeNotifier(ref),
);

final connectivityServiceProvider = Provider<ConnectivityService>(
  (ref) => ConnectivityService(),
);
```

#### Offline Data Storage
```dart
// SQLite database helpers
class DatabaseHelper {
  static Future<Database> get database async {
    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
    );
  }
}
```

### Configuration

#### Environment Configuration
```dart
class EnvironmentConfig {
  static const String defaultBackendUrl = 'http://localhost:48080/v1';
  static const String defaultDeviceId = 'pos-device-001';
  static const String defaultDeviceToken = 'pos-token-1';
  static const String defaultSiteKey = 'tenant_demo_01:store_demo_01:demo-secret-key';
}
```

#### Feature Flags
```dart
class FeatureFlags {
  static const bool enableOfflineMode = true;
  static const bool enableSyncStatus = true;
  static const bool enableBackendHealthCheck = true;
  static const bool enableAdaptiveUI = true;
}
```

---

## 🖥️ Backend Server

### Core Features

#### 1. Multi-tenant Architecture
- **Tenant Isolation**: Separate data for each tenant
- **Store Management**: Multiple stores per tenant
- **Device Registration**: Secure device enrollment
- **Site Key System**: Secure device registration

#### 2. RBAC Security System
- **User Management**: Employee accounts and profiles
- **Role Hierarchy**: Owner > Manager > Cashier > Gate Operator > Viewer
- **Permission System**: Granular permission control
- **API Key Management**: Device-based authentication

#### 3. Business Logic
- **Package Management**: Catalog and pricing rules
- **Ticket System**: Generation, validation, and redemption
- **Sales Processing**: Transaction handling and reporting
- **Shift Management**: Cash drawer and reconciliation

#### 4. Security Features
- **JWT Authentication**: Secure token-based auth
- **HMAC Signatures**: QR code verification
- **Rate Limiting**: API abuse prevention
- **Audit Logging**: Complete action tracking

### Database Models

#### Core Models
```javascript
// Tenant model
const TenantSchema = new mongoose.Schema({
  tenant_id: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  legal_name: String,
  timezone: { type: String, default: 'Asia/Bangkok' },
  currency: { type: String, default: 'THB' },
  billing_plan: { type: String, default: 'basic' },
  status: { type: String, enum: ['active', 'suspended'], default: 'active' },
  created_at: { type: Date, default: Date.now }
});

// Store model
const StoreSchema = new mongoose.Schema({
  store_id: { type: String, required: true, unique: true },
  tenant_id: { type: String, required: true },
  name: { type: String, required: true },
  address: String,
  timezone: { type: String, default: 'Asia/Bangkok' },
  tax_id: String,
  receipt_header: String,
  receipt_footer: String,
  logo_ref: String,
  active: { type: Boolean, default: true }
});

// Device model
const DeviceSchema = new mongoose.Schema({
  device_id: { type: String, required: true, unique: true },
  tenant_id: { type: String, required: true },
  store_id: { type: String, required: true },
  type: { type: String, enum: ['POS', 'GATE', 'KIOSK', 'ADMIN'], required: true },
  name: { type: String, required: true },
  registered_at: { type: Date, default: Date.now },
  registered_by: String,
  status: { type: String, enum: ['active', 'suspended', 'revoked'], default: 'active' },
  device_token_hash: { type: String, required: true },
  capabilities: [{ type: String }],
  notes: String
});
```

#### Business Models
```javascript
// Package model
const PackageSchema = new mongoose.Schema({
  package_id: { type: String, required: true, unique: true },
  tenant_id: { type: String, required: true },
  store_id: { type: String, required: true },
  name: { type: String, required: true },
  type: { type: String, enum: ['single', 'multi', 'timepass', 'credit', 'bundle'], required: true },
  price: { type: Number, required: true },
  tax_profile: { type: String, default: 'standard' },
  quota_or_minutes: { type: Number, required: true },
  allowed_devices: [{ type: String }],
  visible_on: [{ type: String, enum: ['POS', 'KIOSK'] }],
  active_window: {
    from: String,
    to: String
  },
  active: { type: Boolean, default: true }
});

// Ticket model
const TicketSchema = new mongoose.Schema({
  ticket_id: { type: String, required: true, unique: true },
  tenant_id: { type: String, required: true },
  store_id: { type: String, required: true },
  sale_id: { type: String, required: true },
  package_id: { type: String, required: true },
  short_code: { type: String, required: true, unique: true },
  qr_token: { type: String, required: true, unique: true },
  sig: { type: String, required: true },
  type: { type: String, enum: ['single', 'multi', 'timepass', 'credit', 'bundle'], required: true },
  quota_or_minutes: { type: Number, required: true },
  used: { type: Number, default: 0 },
  valid_from: { type: Date, required: true },
  valid_to: { type: Date, required: true },
  status: { type: String, enum: ['active', 'cancelled', 'refunded', 'expired'], default: 'active' },
  lot_no: { type: String, required: true },
  shift_id: { type: String, required: true },
  issued_by: { type: String, required: true },
  price: { type: Number, required: true },
  payment_method: { type: String, required: true },
  printed_count: { type: Number, default: 0 }
});
```

### API Endpoints

#### Authentication
```javascript
// Device registration
POST /v1/auth/device/register
{
  "device_id": "pos-device-001",
  "device_name": "Main POS Terminal",
  "device_type": "POS",
  "site_key": "tenant_demo_01:store_demo_01:demo-secret-key"
}

// Device login
POST /v1/auth/device/login
{
  "device_id": "pos-device-001",
  "device_token": "pos-token-1"
}

// Employee login
POST /v1/auth/employees/login
{
  "email": "manager@playpark.demo",
  "pin": "1234"
}
```

#### Catalog Management
```javascript
// Get packages
GET /v1/catalog/packages?store_id=store_demo_01

// Get pricing rules
GET /v1/catalog/pricing/rules?store_id=store_demo_01

// Calculate pricing
POST /v1/catalog/pricing/calculate
{
  "items": [
    {
      "package_id": "pkg_001",
      "quantity": 2,
      "price": 150
    }
  ],
  "discounts": []
}
```

#### Sales & Tickets
```javascript
// Create sale
POST /v1/sales
{
  "device_id": "pos-device-001",
  "cashier_id": "emp_001",
  "items": [...],
  "subtotal": 300,
  "discount_total": 30,
  "tax_total": 18.9,
  "grand_total": 288.9,
  "payment_method": "cash",
  "amount_tendered": 300,
  "change": 11.1,
  "idempotency_key": "sale_123456789"
}

// Redeem ticket
POST /v1/tickets/redeem
{
  "qr_token": "qr_token_001",
  "device_id": "gate-device-001"
}
```

---

## 📚 API Documentation

### Base Information

- **Base URL**: `http://localhost:48080/v1`
- **Content-Type**: `application/json`
- **Authentication**: Bearer Token (JWT) or Device Token

### Authentication Headers

```http
Authorization: Bearer <jwt_token>
X-Device-Token: <device_token>
X-API-Key: <api_key>
```

### Common Response Format

#### Success Response
```json
{
  "server_time": "2025-09-24T09:30:00.000Z",
  "request_id": "req_123456789",
  "data": {
    // Response data here
  }
}
```

#### Error Response
```json
{
  "server_time": "2025-09-24T09:30:00.000Z",
  "request_id": "req_123456789",
  "error": {
    "code": "E_ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `E_DEVICE_SUSPENDED` | Device is suspended |
| `E_PERMISSION` | Insufficient permissions |
| `E_SHIFT_CLOSED` | No active shift |
| `E_DUPLICATE_USE` | Ticket already used |
| `E_EXPIRED` | Ticket expired |
| `E_NOT_STARTED` | Ticket not yet valid |
| `E_EXHAUSTED` | Ticket quota exhausted |
| `E_INVALID_SIG` | Invalid ticket signature |
| `E_RATE_LIMIT` | Too many requests |
| `E_NOT_FOUND` | Resource not found |

### Demo Credentials

#### Device Tokens
- **POS Device**: `pos-token-1`
- **Gate Device**: `gate-token-1`
- **Kiosk Device**: `kiosk-token-1`

#### Employee Credentials
- **Email**: `manager@playpark.demo`
- **PIN**: `1234`

#### Site Key Format
- **Format**: `tenant_demo_01:store_demo_01:demo-secret-key`

---

## 🔐 RBAC System

### Permission System

```javascript
const PERMISSIONS = {
  READ: 'read',                    // Read access to data
  WRITE: 'write',                  // Write access to data
  DELETE: 'delete',                // Delete operations
  SELL: 'can_sell',               // POS selling operations
  REDEEM: 'can_redeem',           // Ticket redemption
  REFUND: 'can_refund',           // Refund operations
  REPORTS: 'can_access_reports',  // Report access
  MANAGE_USERS: 'can_manage_users', // User management
  MANAGE_DEVICES: 'can_manage_devices', // Device management
  ADMIN: 'can_admin',             // Administrative access
  MANAGE_SETTINGS: 'can_manage_settings' // Settings management
};
```

### Role Hierarchy

1. **Owner** (Level 10)
   - Full system access
   - All permissions
   - Cannot be deleted or modified by others

2. **Manager** (Level 7)
   - Store management
   - User management
   - Reports access
   - POS operations

3. **Cashier** (Level 3)
   - Basic POS operations
   - Selling and basic transactions

4. **Gate Operator** (Level 2)
   - Ticket redemption
   - Gate control operations

5. **Viewer** (Level 1)
   - Read-only access
   - Monitoring and reporting

### Security Features

#### 1. API Key Security
- Base64 encoding for storage
- Expiration support
- Usage tracking
- Device association

#### 2. Password Security
- bcrypt hashing with configurable rounds
- Account lockout after failed attempts
- Password strength requirements

#### 3. Token Security
- JWT tokens with expiration
- Refresh token support
- Secure storage in Flutter app

#### 4. Access Control
- Permission-based access control
- Role-based access control
- Owner privilege escalation
- Tenant isolation

---

## 🔄 Adaptive Integration

### Adaptive Modes

#### Online Mode
- **Capabilities**: Full functionality available
- **UI**: All buttons and features enabled
- **Data**: Real-time sync with backend
- **Status**: Green indicator with "Online" message

#### Offline Mode
- **Capabilities**: Limited to cached data and queued operations
- **UI**: Sync-dependent features disabled
- **Data**: Local SQLite database only
- **Status**: Orange indicator with "Offline Mode" message

#### Degraded Mode
- **Capabilities**: Partial connectivity, some features limited
- **UI**: Some features disabled with retry options
- **Data**: Attempts sync but falls back to local data
- **Status**: Yellow indicator with "Limited Connectivity" message

#### Unregistered Mode
- **Capabilities**: No backend access, demo mode only
- **UI**: Registration prompts and demo functionality
- **Data**: Mock data only
- **Status**: Red indicator with "Device Not Registered" message

#### Unauthenticated Mode
- **Capabilities**: Device registered but employee not logged in
- **UI**: Login prompts and limited functionality
- **Data**: Device-level access only
- **Status**: Red indicator with "Authentication Required" message

### Connectivity Detection

```dart
class ConnectivityService {
  // Network monitoring
  Stream<ConnectionStatus> get connectionStream;
  
  // Backend health checks
  Stream<BackendStatus> get backendStream;
  
  // Force health check
  void forceBackendHealthCheck();
  
  // Connection status
  bool get isConnected;
  bool get isBackendHealthy;
}
```

### Sync Service

```dart
class SyncService {
  // Sync packages from server
  Future<SyncResult> syncPackagesFromServer();
  
  // Sync local data to server
  Future<SyncResult> syncLocalDataToServer();
  
  // Process outbox events
  Future<SyncResult> processOutbox();
  
  // Add event to outbox
  Future<void> addEventToOutbox(OutboxEventType type, Map<String, dynamic> payload);
  
  // Get sync status
  Future<SyncStatus> getSyncStatus();
}
```

---

## 🛠️ Development Guide

### Prerequisites

#### Flutter Development
- Flutter 3.x SDK
- Dart 3.x
- Android Studio / VS Code
- Chrome (for web development)

#### Backend Development
- Node.js 18+
- MongoDB 6+
- Docker & Docker Compose
- Postman (for API testing)

### Setup Instructions

#### 1. Flutter App Setup

```bash
# Clone repository
git clone <repository-url>
cd posPlayground

# Install dependencies
flutter pub get

# Run on Chrome (for web development)
flutter run -d chrome --debug

# Run on Android
flutter run -d android --debug
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Start with Docker (Recommended)
docker-compose up -d

# Or start manually
npm run seed  # Seed database
npm run dev   # Start development server
```

#### 3. Environment Configuration

```bash
# Backend environment variables
JWT_SECRET=your-super-secret-jwt-key
HMAC_SECRET_V1=your-hmac-secret-key
BCRYPT_ROUNDS=12
MONGODB_URI=mongodb://admin:password@localhost:27017/playpark
API_PORT=48080
CORS_ORIGIN=http://localhost:3000,http://localhost:8080
```

### Development Workflow

#### 1. Feature Development
1. Create feature branch
2. Implement Flutter UI components
3. Add backend API endpoints
4. Implement offline sync logic
5. Add tests and documentation
6. Submit pull request

#### 2. Testing
```bash
# Flutter tests
flutter test

# Backend tests
npm test

# Integration tests
npm run test:integration
```

#### 3. Code Quality
```bash
# Flutter linting
flutter analyze

# Backend linting
npm run lint

# Format code
npm run format
```

---

## 🚀 Deployment

### Docker Deployment

#### Production Setup
```bash
# Set environment variables
export JWT_SECRET="your-production-jwt-secret"
export HMAC_SECRET_V1="your-production-hmac-secret"
export MONGODB_URI="mongodb://admin:password@mongo:27017/playpark"

# Deploy with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:48080/health
```

#### Docker Services
- **`mongo`** - MongoDB database (internal only)
- **`api`** - Node.js REST API (port 48080)
- **`admin`** - React admin UI (port 3000)

### Flutter App Deployment

#### Web Deployment
```bash
# Build for web
flutter build web

# Deploy to web server
# Copy build/web/* to your web server
```

#### Mobile Deployment
```bash
# Build for Android
flutter build apk --release

# Build for iOS
flutter build ios --release
```

### Environment Configuration

#### Development
- Backend URL: `http://localhost:48080/v1`
- Database: Local MongoDB
- Debug mode: Enabled

#### Production
- Backend URL: `https://api.playpark.com/v1`
- Database: MongoDB Atlas
- Debug mode: Disabled
- SSL/TLS: Required

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Not Running
**Problem**: Flutter app can't connect to backend
**Solution**:
```bash
# Check if backend is running
curl http://localhost:48080/health

# Check Docker containers
docker-compose ps

# View logs
docker-compose logs api
```

#### 2. Device Registration Fails
**Problem**: Device registration returns error
**Solution**:
- Verify site key format: `tenant_demo_01:store_demo_01:demo-secret-key`
- Check backend device registration endpoint
- Ensure backend is accessible

#### 3. Sync Not Working
**Problem**: Data not syncing between app and backend
**Solution**:
- Check network connectivity
- Verify backend health status
- Check outbox queue for failed operations
- Force sync from settings

#### 4. UI Not Adapting
**Problem**: Adaptive UI not responding to connectivity changes
**Solution**:
- Verify adaptive mode provider is working
- Check connectivity service initialization
- Ensure feature flags are enabled
- Restart app to reinitialize services

#### 5. SQLite Errors
**Problem**: Database errors on web platform
**Solution**:
- SQLite is not supported on web
- App automatically uses mock data on web
- Use Chrome/Android for full SQLite functionality

### Debug Tools

#### 1. Flutter Debug Tools
- **Offline Test Screen**: Test SQLite functionality
- **Backend Health Screen**: Monitor connection status
- **Device Registration Screen**: Test device registration
- **Sync Status Widget**: View sync status in real-time

#### 2. Backend Debug Tools
```bash
# Enable debug logging
export LOG_LEVEL=debug

# View detailed logs
docker-compose logs -f api

# Test API endpoints
curl -X GET http://localhost:48080/health
```

#### 3. Database Debug Tools
```bash
# Connect to MongoDB
docker exec -it posplayground_mongo_1 mongosh

# Check collections
db.getCollectionNames()

# View documents
db.tenants.find()
db.devices.find()
```

### Performance Optimization

#### 1. Flutter App
- Use `const` constructors where possible
- Implement lazy loading for large lists
- Optimize image loading and caching
- Use efficient state management with Riverpod

#### 2. Backend API
- Implement database indexing
- Use connection pooling
- Enable gzip compression
- Implement caching strategies

#### 3. Database
- Create appropriate indexes
- Optimize query performance
- Implement data archiving
- Monitor query execution plans

---

## 📞 Support

### Getting Help

1. **Check Documentation**: Review this comprehensive guide
2. **Check Issues**: Look for similar problems in GitHub issues
3. **Debug Mode**: Enable debug logging for detailed information
4. **Community**: Join the developer community for support

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📝 Changelog

### Version 1.0.0
- Initial release
- Flutter POS app with offline support
- Node.js backend with RBAC
- Docker deployment
- Comprehensive documentation

---

*This documentation is maintained and updated regularly. For the latest version, please check the project repository.*



