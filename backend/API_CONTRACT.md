# PlayPark Backend API Contract Documentation

## Base Information

- **Base URL**: `http://localhost:48080/v1`
- **Content-Type**: `application/json`
- **Authentication**: Bearer Token (JWT) or Device Token

## Authentication Headers

```http
Authorization: Bearer <jwt_token>
X-Device-Token: <device_token>
```

## Common Response Format

### Success Response
```json
{
  "server_time": "2025-09-24T09:30:00.000Z",
  "request_id": "req_123456789",
  "data": {
    // Response data here
  }
}
```

### Error Response
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

## Error Codes

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

---

## Authentication Endpoints

### Device Login
**POST** `/auth/device/login`

**Request:**
```json
{
  "device_id": "pos-device-001",
  "device_token": "pos-token-1"
}
```

**Response:**
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "device": {
      "device_id": "pos-device-001",
      "type": "POS",
      "capabilities": ["can_sell", "can_redeem"],
      "store_id": "store_demo_01"
    }
  }
}
```

### Employee Login
**POST** `/employees/login`

**Request:**
```json
{
  "email": "manager@playpark.demo",
  "pin": "1234"
}
```

**Response:**
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "employee": {
      "employee_id": "emp_001",
      "name": "Manager",
      "email": "manager@playpark.demo",
      "roles": ["manager"],
      "permissions": ["sell", "redeem", "refund", "reprint"]
    }
  }
}
```

---

## Catalog Endpoints

### Get Packages
**GET** `/catalog/packages?store_id=store_demo_01`

**Response:**
```json
{
  "data": [
    {
      "package_id": "pkg_001",
      "name": "Single Entry",
      "type": "single",
      "price": 150,
      "quota_or_minutes": 1,
      "active": true,
      "visible_on": ["POS", "KIOSK"]
    },
    {
      "package_id": "pkg_002",
      "name": "5-Entry Pass",
      "type": "multi",
      "price": 600,
      "quota_or_minutes": 5,
      "active": true,
      "visible_on": ["POS", "KIOSK"]
    }
  ]
}
```

### Get Pricing Rules
**GET** `/catalog/pricing-rules?store_id=store_demo_01`

**Response:**
```json
{
  "data": [
    {
      "rule_id": "rule_001",
      "name": "Early Bird Discount",
      "kind": "line_percent",
      "params": {
        "discount_percent": 10,
        "time_window": "06:00-10:00"
      },
      "priority": 1,
      "active": true
    }
  ]
}
```

---

## Sales Endpoints

### Create Sale
**POST** `/sales`

**Request:**
```json
{
  "device_id": "pos-device-001",
  "cashier_id": "emp_001",
  "items": [
    {
      "package_id": "pkg_001",
      "qty": 2,
      "price": 150,
      "discounts": [
        {
          "type": "percentage",
          "amount": 10,
          "reason": "Early bird"
        }
      ]
    }
  ],
  "subtotal": 300,
  "discount_total": 30,
  "tax_total": 18.9,
  "grand_total": 288.9,
  "payment_method": "cash",
  "amount_tendered": 300,
  "change": 11.1,
  "idempotency_key": "sale_123456789"
}
```

**Response:**
```json
{
  "data": {
    "sale_id": "sale_123456789",
    "tickets": [
      {
        "ticket_id": "tkt_001",
        "qr_token": "qr_token_001",
        "short_code": "ABC123",
        "package_id": "pkg_001",
        "valid_from": "2025-09-24T09:30:00.000Z",
        "valid_to": "2025-09-24T23:59:59.000Z"
      }
    ],
    "receipt_data": {
      "receipt_number": "R001",
      "printed_at": "2025-09-24T09:30:00.000Z"
    }
  }
}
```

---

## Ticket Endpoints

### Redeem Ticket
**POST** `/tickets/redeem`

**Request:**
```json
{
  "qr_token": "qr_token_001",
  "device_id": "gate-device-001"
}
```

**Response:**
```json
{
  "data": {
    "result": "pass",
    "reason": "valid",
    "remaining": 4,
    "ticket": {
      "ticket_id": "tkt_001",
      "package_name": "5-Entry Pass",
      "valid_until": "2025-09-24T23:59:59.000Z"
    }
  }
}
```

### Get Ticket Details
**GET** `/tickets/{ticket_id}`

**Response:**
```json
{
  "data": {
    "ticket_id": "tkt_001",
    "package_name": "Single Entry",
    "status": "active",
    "used": 0,
    "quota_or_minutes": 1,
    "valid_from": "2025-09-24T09:30:00.000Z",
    "valid_to": "2025-09-24T23:59:59.000Z",
    "redemptions": [
      {
        "redemption_id": "red_001",
        "device_id": "gate-device-001",
        "timestamp": "2025-09-24T10:00:00.000Z",
        "result": "pass"
      }
    ]
  }
}
```

---

## Shift Endpoints

### Open Shift
**POST** `/shifts/open`

**Request:**
```json
{
  "employee_id": "emp_001",
  "cash_open": 1000.0
}
```

**Response:**
```json
{
  "data": {
    "shift_id": "shift_001",
    "opened_by": "emp_001",
    "open_at": "2025-09-24T09:00:00.000Z",
    "cash_open": 1000.0,
    "is_active": true
  }
}
```

### Close Shift
**POST** `/shifts/close`

**Request:**
```json
{
  "employee_id": "emp_001",
  "cash_counted": 1250.0
}
```

**Response:**
```json
{
  "data": {
    "shift_id": "shift_001",
    "closed_by": "emp_001",
    "close_at": "2025-09-24T17:00:00.000Z",
    "cash_counted": 1250.0,
    "cash_expected": 1200.0,
    "cash_diff": 50.0,
    "totals": {
      "sales": 15,
      "refunds": 2,
      "reprints": 1,
      "total_amount": 3750.0
    }
  }
}
```

### Get Current Shift
**GET** `/shifts/current`

**Response:**
```json
{
  "data": [
    {
      "shift_id": "shift_001",
      "opened_by": "emp_001",
      "open_at": "2025-09-24T09:00:00.000Z",
      "cash_open": 1000.0,
      "is_active": true
    }
  ]
}
```

---

## Reports Endpoints

### Sales Report
**GET** `/reports/sales?start_date=2025-09-24&end_date=2025-09-24`

**Response:**
```json
{
  "data": {
    "total_sales": 3750.0,
    "total_transactions": 15,
    "payment_methods": [
      {
        "method": "cash",
        "amount": 2500.0,
        "count": 10
      },
      {
        "method": "qr",
        "amount": 1250.0,
        "count": 5
      }
    ],
    "daily_trend": [
      {
        "date": "2025-09-24",
        "sales": 3750.0,
        "transactions": 15
      }
    ]
  }
}
```

### Ticket Report
**GET** `/reports/tickets?start_date=2025-09-24&end_date=2025-09-24`

**Response:**
```json
{
  "data": {
    "total_issued": 15,
    "total_redeemed": 12,
    "redemption_rate": 80.0,
    "status_distribution": [
      {
        "status": "active",
        "count": 3
      },
      {
        "status": "redeemed",
        "count": 12
      }
    ],
    "package_performance": [
      {
        "package_name": "Single Entry",
        "issued": 10,
        "redeemed": 8,
        "redemption_rate": 80.0
      }
    ]
  }
}
```

---

## Health Check

### Health Status
**GET** `/health`

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2025-09-24T09:30:00.000Z",
  "uptime": 3600,
  "version": "v1",
  "environment": "development"
}
```

---

## Demo Credentials

### Device Tokens
- **POS Device**: `pos-token-1`
- **Gate Device**: `gate-token-1`
- **Kiosk Device**: `kiosk-token-1`

### Employee Credentials
- **Email**: `manager@playpark.demo`
- **PIN**: `1234`

### Site Key
- **Format**: `tenant_demo_01:store_demo_01:demo-secret-key`

---

## Rate Limiting

- **Window**: 15 minutes
- **Limit**: 100 requests per IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Idempotency

- Use `idempotency_key` header for POST requests
- Prevents duplicate operations
- Required for sales and sensitive operations
