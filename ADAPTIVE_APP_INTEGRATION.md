# Adaptive App Integration - Flutter + Backend

## Overview

This document explains how the Flutter POS app integrates with the backend system to provide adaptive, offline-capable functionality. The app automatically adapts its behavior based on backend connectivity and capabilities.

## Architecture

### Backend Integration
- **Base URL**: `http://localhost:48080/v1` (configurable)
- **Authentication**: Device tokens + JWT for employees
- **API Contract**: RESTful JSON API with standardized responses
- **Offline Support**: SQLite database with sync capabilities

### Flutter App Structure
```
lib/
├── core/
│   ├── config/           # App configuration and environment settings
│   ├── providers/        # Riverpod providers for state management
│   └── services/         # Core services (connectivity, auth)
├── data/
│   ├── database/         # SQLite database helpers
│   ├── models/           # Database and API models
│   ├── repositories/     # Data access layer
│   └── services/         # API and sync services
├── features/             # Feature-based modules
├── widgets/
│   └── adaptive_ui/      # Adaptive UI components
└── main.dart            # App entry point
```

## Key Features

### 1. Adaptive Configuration System
- **Environment-based configuration**: Development, staging, production
- **Runtime configuration**: Backend URL, device credentials
- **Feature flags**: Enable/disable features dynamically
- **Fallback defaults**: Always works with demo data

### 2. Connectivity Detection
- **Network monitoring**: Real-time internet connectivity
- **Backend health checks**: Periodic API health monitoring
- **Automatic retry**: Exponential backoff for failed connections
- **Connection quality**: Multiple connection status levels

### 3. Device Registration & Authentication
- **Device registration**: Register with backend using site key
- **Token-based auth**: Secure device authentication
- **Employee login**: PIN-based employee authentication
- **Session management**: Automatic token refresh

### 4. Adaptive UI System
- **Capability-based UI**: Buttons/features adapt to backend capabilities
- **Visual indicators**: Clear status indicators for connection state
- **Offline mode**: UI elements show offline state
- **Graceful degradation**: Features disable gracefully when unavailable

### 5. Offline-First Data Storage
- **SQLite database**: Local data storage
- **Sync service**: Bidirectional data synchronization
- **Outbox pattern**: Queue operations for later sync
- **Conflict resolution**: Server-wins conflict resolution

### 6. Backend Health Monitoring
- **Real-time monitoring**: Continuous health checks
- **Detailed diagnostics**: Connection info and capabilities
- **Manual testing**: Force connection tests and sync
- **Status dashboard**: Comprehensive health overview

## Backend API Integration

### Authentication Flow
1. **Device Registration**: `POST /auth/device/register`
2. **Device Login**: `POST /auth/device/login`
3. **Employee Login**: `POST /employees/login`
4. **Token Refresh**: Automatic token refresh

### Core Endpoints
- **Packages**: `GET /catalog/packages`
- **Sales**: `POST /sales`
- **Tickets**: `GET /tickets/{id}`, `POST /tickets/redeem`
- **Shifts**: `POST /shifts/open`, `POST /shifts/close`
- **Reports**: `GET /reports/sales`, `GET /reports/tickets`
- **Health**: `GET /health`

### Sync Endpoints
- **Batch Sync**: `POST /sync/batch`
- **Gate Bootstrap**: `GET /gate/bootstrap`

## Adaptive Modes

### Online Mode
- **Capabilities**: Full functionality available
- **UI**: All buttons and features enabled
- **Data**: Real-time sync with backend
- **Status**: Green indicator with "Online" message

### Offline Mode
- **Capabilities**: Limited to cached data and queued operations
- **UI**: Sync-dependent features disabled
- **Data**: Local SQLite database only
- **Status**: Orange indicator with "Offline Mode" message

### Degraded Mode
- **Capabilities**: Partial connectivity, some features limited
- **UI**: Some features disabled with retry options
- **Data**: Attempts sync but falls back to local data
- **Status**: Yellow indicator with "Limited Connectivity" message

### Unregistered Mode
- **Capabilities**: No backend access, demo mode only
- **UI**: Registration prompts and demo functionality
- **Data**: Mock data only
- **Status**: Red indicator with "Device Not Registered" message

### Unauthenticated Mode
- **Capabilities**: Device registered but employee not logged in
- **UI**: Login prompts and limited functionality
- **Data**: Device-level access only
- **Status**: Red indicator with "Authentication Required" message

## Usage Guide

### Initial Setup
1. **Start Backend**: Ensure backend is running on `localhost:48080`
2. **Run Flutter App**: App will initialize with default demo configuration
3. **Register Device**: Go to Settings > Device Management > Device Registration
4. **Test Connection**: Use Backend Health screen to verify connectivity

### Device Registration
1. Navigate to **Settings > Device Management > Device Registration**
2. Enter **Site Key**: `tenant_demo_01:store_demo_01:demo-secret-key`
3. Enter **Device Name**: e.g., "Main POS Terminal"
4. Click **Register Device**
5. Device will be registered and authenticated automatically

### Backend Health Monitoring
1. Navigate to **Settings > Device Management > Backend Health**
2. View real-time connection status and capabilities
3. Use **Test Connection** to force health check
4. Use **Force Sync** to manually trigger synchronization
5. View **Detailed Info** for technical diagnostics

### Offline Testing
1. **Disconnect Network**: Turn off WiFi/mobile data
2. **Observe UI Changes**: Notice adaptive UI elements disable
3. **Test Offline Features**: POS sales still work with local data
4. **Reconnect Network**: Watch automatic sync when connection restored

## Configuration

### Environment Variables
```dart
// Backend Configuration
static const String defaultBackendUrl = 'http://localhost:48080/v1';
static const String stagingBackendUrl = 'http://staging.playpark.local:48080/v1';
static const String productionBackendUrl = 'https://api.playpark.com/v1';

// Device Configuration
static const String defaultDeviceId = 'pos-device-001';
static const String defaultDeviceToken = 'pos-token-1';
static const String defaultSiteKey = 'tenant_demo_01:store_demo_01:demo-secret-key';
```

### Feature Flags
```dart
// Enable/disable features
static const bool enableOfflineMode = true;
static const bool enableSyncStatus = true;
static const bool enableBackendHealthCheck = true;
static const bool enableAdaptiveUI = true;
```

## Demo Credentials

### Device Tokens
- **POS Device**: `pos-token-1`
- **Gate Device**: `gate-token-1`
- **Kiosk Device**: `kiosk-token-1`

### Employee Credentials
- **Email**: `manager@playpark.demo`
- **PIN**: `1234`

### Site Key Format
- **Format**: `tenant_demo_01:store_demo_01:demo-secret-key`

## Troubleshooting

### Common Issues

1. **Backend Not Running**
   - Check if backend is running on `localhost:48080`
   - Verify Docker containers are up
   - Check backend health endpoint

2. **Device Registration Fails**
   - Verify site key format
   - Check backend device registration endpoint
   - Ensure backend is accessible

3. **Sync Not Working**
   - Check network connectivity
   - Verify backend health status
   - Check outbox queue for failed operations

4. **UI Not Adapting**
   - Verify adaptive mode provider is working
   - Check connectivity service initialization
   - Ensure feature flags are enabled

### Debug Tools

1. **Offline Test Screen**: Test SQLite functionality
2. **Backend Health Screen**: Monitor connection status
3. **Device Registration Screen**: Test device registration
4. **Sync Status Widget**: View sync status in real-time

## Development

### Adding New Adaptive Features
1. Define capability in `AdaptiveMode` class
2. Add UI component with capability requirement
3. Update backend integration as needed
4. Test offline/online scenarios

### Extending Backend Integration
1. Add new API endpoint to `ApiService`
2. Create corresponding repository method
3. Add sync support for offline operations
4. Update adaptive capabilities

## Security Considerations

- Device tokens are hashed at rest
- JWT tokens have expiration times
- All API calls use HTTPS in production
- Local SQLite database is encrypted
- Audit logs track all sensitive operations

## Performance

- **Connection checks**: Every 5 minutes
- **Sync operations**: Batched for efficiency
- **Database queries**: Optimized with indexes
- **UI updates**: Minimal re-renders with Riverpod
- **Memory usage**: Efficient with lazy loading

This adaptive system ensures the Flutter app works seamlessly whether online or offline, providing a robust POS experience that adapts to backend availability and capabilities.
