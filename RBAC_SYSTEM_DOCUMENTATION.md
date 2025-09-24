# RBAC (Role-Based Access Control) System Documentation

## Overview

The PlayPark POS system implements a comprehensive Role-Based Access Control (RBAC) system that supports multiple users, roles, and permissions. This system ensures secure access control across the Flutter app and backend API.

## Architecture

### Backend Components

#### 1. Models

**User Model** (`backend/src/models/user.js`)
- Stores user credentials, profile information, and role assignments
- Supports password hashing with bcrypt
- Includes login attempt tracking and account locking
- Tenant isolation for multi-tenant support

**Role Model** (`backend/src/models/role.js`)
- Defines roles with permissions and hierarchical levels
- Supports system roles (predefined) and custom roles
- Color coding and icon support for UI representation
- Parent-child role relationships

**ApiKey Model** (`backend/src/models/api_key.js`)
- Manages API keys for device authentication
- Supports permission-based access control
- Expiration and usage tracking
- Device association

**Device Model** (`backend/src/models/device.js`)
- Tracks registered devices and their capabilities
- Online status monitoring
- API key association
- Platform and version tracking

#### 2. Middleware

**RBAC Middleware** (`backend/src/middleware/rbac.js`)
- `requirePermissions()`: Checks specific permissions
- `requireRole()`: Checks role membership
- `requireOwner()`: Owner-only access
- `requireTenantAccess()`: Tenant isolation
- `requireStoreAccess()`: Store isolation

#### 3. API Routes

**User Management** (`backend/src/routes/users.js`)
- CRUD operations for users
- Role assignment and management
- Password management
- Profile updates

**Role Management** (`backend/src/routes/roles.js`)
- CRUD operations for roles
- System role initialization
- Permission management
- Role hierarchy support

**Device Management** (`backend/src/routes/devices.js`)
- Device registration
- API key generation and validation
- Online device monitoring
- Device status management

## Permission System

### Permission Types

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

## Flutter App Integration

### Server Configuration

**ServerConfig Model** (`lib/core/models/server_config.dart`)
```dart
class ServerConfig {
  final String host;           // Server hostname/IP
  final int port;             // Server port
  final String protocol;      // HTTP/HTTPS
  final String? apiKey;       // API authentication key
  final bool useHttps;        // SSL/TLS support
  final Duration timeout;     // Request timeout
  final Map<String, String> headers; // Custom headers
}
```

**Server Configuration Service** (`lib/core/services/server_config_service.dart`)
- Configuration persistence
- Connection testing
- API key generation and validation
- Online device monitoring

### UI Components

**Server Configuration Screen** (`lib/features/settings/server_config_screen.dart`)
- Server host and port configuration
- API key management
- Connection testing
- HTTPS support

**User Management Screen** (`lib/features/settings/user_management_screen.dart`)
- User listing and management
- Role assignment visualization
- Permission overview
- User status management

**Online Devices Screen** (`lib/features/settings/online_devices_screen.dart`)
- Real-time device monitoring
- Device status tracking
- Permission display
- Last seen timestamps

## API Endpoints

### Authentication

```bash
# Generate API key for device
POST /v1/devices/api-key/generate
{
  "device_id": "flutter_pos_123",
  "device_name": "Flutter POS Device",
  "permissions": ["read", "write", "can_sell", "can_redeem"]
}

# Validate API key
POST /v1/devices/validate-api-key
Headers: X-API-Key: your_api_key_here

# Get online devices
GET /v1/devices/online
Headers: Authorization: Bearer jwt_token
```

### User Management

```bash
# Get all users
GET /v1/users
Headers: Authorization: Bearer jwt_token

# Create user
POST /v1/users
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "User Name",
  "roles": ["role_id_1", "role_id_2"],
  "permissions": ["can_sell"]
}

# Update user
PATCH /v1/users/:userId
{
  "name": "Updated Name",
  "roles": ["role_id_1"],
  "is_active": true
}

# Delete user
DELETE /v1/users/:userId
```

### Role Management

```bash
# Get all roles
GET /v1/roles
Headers: Authorization: Bearer jwt_token

# Create role
POST /v1/roles
{
  "name": "custom_role",
  "display_name": "Custom Role",
  "description": "Custom role description",
  "permissions": ["read", "write", "can_sell"],
  "level": 5,
  "color": "#1976d2"
}

# Initialize default roles
POST /v1/roles/initialize
Headers: Authorization: Bearer jwt_token
```

## Security Features

### 1. API Key Security
- Base64 encoding for storage
- Expiration support
- Usage tracking
- Device association

### 2. Password Security
- bcrypt hashing with configurable rounds
- Account lockout after failed attempts
- Password strength requirements

### 3. Token Security
- JWT tokens with expiration
- Refresh token support
- Secure storage in Flutter app

### 4. Access Control
- Permission-based access control
- Role-based access control
- Owner privilege escalation
- Tenant isolation

## Usage Examples

### 1. Device Registration Flow

```dart
// 1. Configure server
final config = ServerConfig(
  host: '192.168.1.100',
  port: 48080,
  protocol: 'http',
);

// 2. Generate API key
final result = await ServerConfigService.generateApiKey(
  config: config,
  deviceId: 'flutter_pos_${DateTime.now().millisecondsSinceEpoch}',
  deviceName: 'Flutter POS Device',
  permissions: ['read', 'write', 'can_sell', 'can_redeem'],
);

// 3. Save configuration
if (result.isSuccess) {
  await ServerConfigService.saveApiKey(result.apiKey!);
  await ServerConfigService.saveConfig(config);
}
```

### 2. Permission Checking

```dart
// Check if user has permission
if (user.hasPermission('can_sell')) {
  // Enable selling functionality
  enableSellingFeatures();
}

// Check multiple permissions
if (user.hasAnyPermission(['can_sell', 'can_redeem'])) {
  // Enable POS operations
  enablePOSOperations();
}
```

### 3. Backend Middleware Usage

```javascript
// Require specific permissions
router.get('/sales', auth, requirePermissions([PERMISSIONS.SELL]), (req, res) => {
  // Only users with 'can_sell' permission can access
});

// Require role
router.get('/reports', auth, requireRole('manager'), (req, res) => {
  // Only users with 'manager' role can access
});

// Owner only
router.delete('/tenant', auth, requireOwner, (req, res) => {
  // Only owners can delete tenant
});
```

## Configuration

### Environment Variables

```bash
# Backend configuration
JWT_SECRET=your-super-secret-jwt-key
HMAC_SECRET_V1=your-hmac-secret-key
BCRYPT_ROUNDS=12
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Database
MONGODB_URI=mongodb://admin:password@localhost:27017/playpark

# Security
CORS_ORIGIN=http://localhost:3000,http://localhost:8080
```

### Flutter Configuration

```dart
// Default server configuration
const defaultConfig = ServerConfig(
  host: '127.0.0.1',
  port: 48080,
  protocol: 'http',
  useHttps: false,
  timeout: Duration(seconds: 30),
);
```

## Best Practices

### 1. Security
- Always use HTTPS in production
- Implement proper API key rotation
- Use strong passwords and JWT secrets
- Enable rate limiting

### 2. User Management
- Follow principle of least privilege
- Regularly review user permissions
- Implement proper role hierarchies
- Use system roles for common operations

### 3. Device Management
- Register all devices properly
- Monitor device status regularly
- Implement device capability checks
- Use appropriate API key permissions

### 4. Monitoring
- Track API key usage
- Monitor failed login attempts
- Log permission changes
- Alert on suspicious activities

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Check if API key is properly encoded
   - Verify expiration date
   - Ensure correct headers are sent

2. **Permission Denied**
   - Verify user has required permissions
   - Check role assignments
   - Ensure proper authentication

3. **Device Not Found**
   - Register device first
   - Check device ID format
   - Verify tenant isolation

4. **Connection Issues**
   - Test server connectivity
   - Check firewall settings
   - Verify SSL certificates

### Debug Mode

Enable debug logging in the backend:

```javascript
// In server.js
process.env.LOG_LEVEL = 'debug';
```

Enable debug mode in Flutter:

```dart
// In main.dart
if (kDebugMode) {
  print('Debug mode enabled');
}
```

## Future Enhancements

1. **Advanced RBAC**
   - Dynamic permission assignment
   - Time-based permissions
   - Location-based access control

2. **Audit Logging**
   - Comprehensive audit trails
   - Permission change tracking
   - Security event monitoring

3. **Multi-Factor Authentication**
   - SMS verification
   - TOTP support
   - Biometric authentication

4. **Advanced Device Management**
   - Device fingerprinting
   - Remote device control
   - Bulk device operations

This RBAC system provides a robust foundation for secure multi-user access control in the PlayPark POS system, supporting both traditional user-based authentication and device-based API key authentication.
