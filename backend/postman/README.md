# PlayPark API Postman Collections

This directory contains Postman collections and environments for testing the PlayPark Backend API.

## Files

- **PlayPark_API_Collection.json** - Complete API collection with all endpoints
- **PlayPark_Environment.json** - Development environment variables
- **README.md** - This documentation

## Setup Instructions

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select `PlayPark_API_Collection.json`
4. Click "Import"

### 2. Import Environment
1. In Postman, click the gear icon (⚙️) in the top right
2. Click "Import"
3. Select `PlayPark_Environment.json`
4. Click "Import"
5. Select "PlayPark Development" environment from the dropdown

### 3. Start Backend Services
```bash
cd backend
docker-compose up -d
```

### 4. Test API
1. Run "Health Check" → "API Health" to verify backend is running
2. Run "Authentication" → "Device Login" to get auth token
3. Test other endpoints

## Collection Structure

### Authentication
- **Device Login** - Authenticate POS/Gate/Kiosk devices
- **Employee Login** - Authenticate employees with email/PIN

### Health Check
- **API Health** - Check API status and uptime

### Catalog
- **Get Packages** - Fetch available packages
- **Get Pricing Rules** - Fetch pricing rules

### Sales
- **Create Sale** - Process a sale transaction

### Tickets
- **Redeem Ticket** - Redeem ticket at gate
- **Get Ticket Details** - Fetch ticket information

### Shifts
- **Open Shift** - Start a new shift
- **Close Shift** - End current shift
- **Get Current Shift** - Fetch active shift

### Reports
- **Sales Report** - Generate sales analytics
- **Ticket Report** - Generate ticket analytics

## Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `baseUrl` | API base URL | `http://localhost:48080/v1` |
| `authToken` | JWT authentication token | (auto-set after login) |
| `deviceToken` | POS device token | `pos-token-1` |
| `gateToken` | Gate device token | `gate-token-1` |
| `kioskToken` | Kiosk device token | `kiosk-token-1` |
| `storeId` | Store identifier | `store_demo_01` |
| `tenantId` | Tenant identifier | `tenant_demo_01` |
| `employeeEmail` | Employee email | `manager@playpark.demo` |
| `employeePin` | Employee PIN | `1234` |
| `siteKey` | Site key for device registration | `tenant_demo_01:store_demo_01:demo-secret-key` |

## Demo Credentials

### Device Tokens
- **POS Device**: `pos-token-1`
- **Gate Device**: `gate-token-1`
- **Kiosk Device**: `kiosk-token-1`

### Employee Credentials
- **Email**: `manager@playpark.demo`
- **PIN**: `1234`

## Testing Workflow

### 1. Basic Health Check
```
Health Check → API Health
```

### 2. Authentication Flow
```
Authentication → Device Login
Authentication → Employee Login
```

### 3. Catalog Operations
```
Catalog → Get Packages
Catalog → Get Pricing Rules
```

### 4. Sales Flow
```
Shifts → Open Shift
Sales → Create Sale
Shifts → Close Shift
```

### 5. Ticket Operations
```
Tickets → Redeem Ticket
Tickets → Get Ticket Details
```

### 6. Reporting
```
Reports → Sales Report
Reports → Ticket Report
```

## Error Handling

The API returns standardized error responses:

```json
{
  "error": {
    "code": "E_ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

Common error codes:
- `E_DEVICE_SUSPENDED` - Device is suspended
- `E_PERMISSION` - Insufficient permissions
- `E_SHIFT_CLOSED` - No active shift
- `E_DUPLICATE_USE` - Ticket already used
- `E_EXPIRED` - Ticket expired
- `E_RATE_LIMIT` - Too many requests

## Rate Limiting

- **Window**: 15 minutes
- **Limit**: 100 requests per IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Idempotency

Use `Idempotency-Key` header for POST requests to prevent duplicate operations:

```
Idempotency-Key: sale_123456789
```

## Troubleshooting

### Connection Issues
1. Verify backend is running: `docker ps`
2. Check API health: `curl http://localhost:48080/health`
3. Verify environment variables

### Authentication Issues
1. Check if auth token is set in environment
2. Verify device tokens are correct
3. Check employee credentials

### Permission Issues
1. Ensure proper authentication
2. Check user roles and permissions
3. Verify device capabilities

## Support

For issues or questions:
1. Check API documentation: `backend/API_CONTRACT.md`
2. Review backend logs: `docker-compose logs api`
3. Check health status: `./scripts/monitor.sh`
