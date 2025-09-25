# Security Documentation - PlayPark FastAPI Backend

## 🔒 Security Overview

The PlayPark FastAPI backend implements comprehensive security measures to protect against common vulnerabilities and ensure secure operation in production environments.

## 🛡️ Authentication & Authorization

### JWT Token Security

#### Token Structure
```json
{
  "sub": "user_id",
  "type": "access|refresh|device",
  "tenant_id": "tenant_123",
  "store_id": "store_456", 
  "device_id": "device_789",
  "scopes": ["sales", "tickets"],
  "iat": 1695540600,
  "exp": 1695544200
}
```

#### Security Features
- **Short-lived Access Tokens**: 20 minutes default
- **Refresh Token Rotation**: Automatic token refresh
- **Token Blacklisting**: Revoked tokens tracked in Redis
- **Scope-based Authorization**: Granular permission control
- **Device-specific Tokens**: Device authentication with capabilities

### Password Security

#### PIN Hashing
- **Algorithm**: bcrypt with salt rounds
- **Minimum Length**: 4-8 characters (configurable)
- **Validation**: Server-side validation required

```python
# PIN hashing example
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_pin = pwd_context.hash(pin)
```

### OAuth2 PKCE Support

#### Web Clients
- **Authorization Code Flow**: Standard OAuth2 flow
- **PKCE**: Proof Key for Code Exchange
- **State Parameter**: CSRF protection
- **Secure Cookies**: HttpOnly, SameSite attributes

#### Mobile Clients
- **Bearer Token**: Authorization header
- **Token Refresh**: Automatic refresh mechanism
- **Device Binding**: Device-specific tokens

## 🔐 Authorization & RBAC

### Role-Based Access Control

#### Roles Hierarchy
```
Provider-Admin > Manager > Cashier > Read-Only
```

#### Permission Matrix

| Role | Sales | Tickets | Reports | Settings | Admin |
|------|-------|---------|---------|----------|-------|
| Provider-Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manager | ✅ | ✅ | ✅ | ✅ | ❌ |
| Cashier | ✅ | ✅ | ❌ | ❌ | ❌ |
| Read-Only | ❌ | ❌ | ✅ | ❌ | ❌ |

### Scope-based Authorization

#### Device Scopes
- `sales`: Can process sales transactions
- `tickets`: Can redeem and validate tickets
- `reports`: Can access reporting endpoints
- `admin`: Administrative functions

#### API Endpoint Protection
```python
@router.post("/sales")
async def create_sale(
    current_user = Depends(CurrentUser),
    current_device = Depends(CurrentDevice),
    _ = Depends(RequireSalesScope)
):
    # Endpoint protected by multiple layers
```

## 🛡️ Input Validation & Sanitization

### Pydantic Validation

#### Request Validation
```python
class SaleCreateRequest(BaseModel):
    items: List[Dict[str, Any]] = Field(..., min_items=1)
    payment_method: PaymentMethod = Field(...)
    amount_tendered: Optional[float] = Field(None, ge=0)
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item required')
        return v
```

#### Response Sanitization
- **Data Filtering**: Remove sensitive fields
- **Type Conversion**: Ensure proper data types
- **Size Limits**: Prevent large payload attacks

### SQL Injection Prevention

#### MongoDB Query Safety
```python
# Safe query construction
query = {"tenant_id": tenant_id, "store_id": store_id}
sales = await sale_repo.get_many(query=query)

# Avoid string concatenation
# BAD: f"SELECT * FROM sales WHERE tenant_id = '{tenant_id}'"
```

## 🚫 Rate Limiting & DDoS Protection

### Rate Limiting Configuration

#### Default Limits
- **General API**: 100 requests per 15 minutes per IP
- **Authentication**: 10 requests per minute per IP
- **File Upload**: 5 requests per minute per user
- **Report Generation**: 10 requests per hour per user

#### Implementation
```python
# Redis-based rate limiting
rate_limit_result = await check_rate_limit(
    identifier=client_ip,
    limit=100,
    window=900  # 15 minutes
)
```

### DDoS Protection
- **Connection Limits**: Max concurrent connections
- **Request Size Limits**: 10MB max payload
- **Timeout Configuration**: 30s request timeout
- **Circuit Breaker**: Automatic service protection

## 🔒 Data Protection

### Encryption at Rest
- **Database**: MongoDB encryption at rest
- **Files**: Encrypted file storage
- **Backups**: Encrypted backup storage

### Encryption in Transit
- **HTTPS Only**: TLS 1.2+ required
- **Certificate Pinning**: Mobile app certificate validation
- **HSTS Headers**: HTTP Strict Transport Security

### Sensitive Data Handling

#### Data Classification
- **Public**: Package information, public settings
- **Internal**: Sales data, user information
- **Confidential**: Payment details, audit logs
- **Restricted**: API keys, system credentials

#### Data Masking
```python
def mask_sensitive_data(data: dict) -> dict:
    """Mask sensitive fields in logs"""
    sensitive_fields = ['pin', 'token', 'secret']
    for field in sensitive_fields:
        if field in data:
            data[field] = '***'
    return data
```

## 🕵️ Audit & Monitoring

### Audit Logging

#### Security Events
- **Authentication**: Login attempts, failures, successes
- **Authorization**: Permission denials, role changes
- **Data Access**: Sensitive data access
- **System Changes**: Configuration modifications

#### Audit Log Structure
```json
{
  "event_type": "auth.login.success",
  "actor_id": "user_123",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2025-01-24T10:30:00Z",
  "metadata": {
    "tenant_id": "tenant_123",
    "store_id": "store_456"
  }
}
```

### Security Monitoring

#### Real-time Alerts
- **Failed Login Attempts**: >5 failures in 5 minutes
- **Unusual API Usage**: >1000 requests in 1 minute
- **Permission Escalation**: Unauthorized role changes
- **Data Exfiltration**: Large data exports

#### Log Analysis
```python
# Security event detection
async def detect_security_threats():
    # Analyze audit logs for patterns
    suspicious_activities = await analyze_audit_logs()
    
    for activity in suspicious_activities:
        await send_security_alert(activity)
```

## 🔐 API Security

### Request Security

#### Headers Security
```python
# Security headers middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    force_https=True,
    hsts_max_age=31536000,
    content_type_nosniff=True,
    xss_protection=True
)
```

#### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://admin.playpark.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)
```

### Response Security

#### Data Sanitization
- **PII Removal**: Personal information filtering
- **Error Message Sanitization**: No sensitive data in errors
- **Response Size Limits**: Prevent information disclosure

#### Cache Control
```python
# Prevent sensitive data caching
response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
response.headers["Pragma"] = "no-cache"
```

## 🔑 Secret Management

### Environment Variables

#### Production Secrets
```bash
# Never commit these to version control
SECRET_KEY=your-super-secret-key-256-bits
JWT_SECRET=your-jwt-secret-key
MONGODB_PASSWORD=secure-database-password
REDIS_PASSWORD=secure-redis-password
```

#### Secret Rotation
- **Automated Rotation**: Monthly secret rotation
- **Zero Downtime**: Rolling secret updates
- **Backup Secrets**: Previous version support

### API Key Management

#### Key Lifecycle
1. **Generation**: Cryptographically secure random keys
2. **Storage**: Hashed storage in database
3. **Usage**: Rate limiting and usage tracking
4. **Rotation**: Regular key rotation
5. **Revocation**: Immediate key revocation capability

## 🚨 Incident Response

### Security Incident Types

#### Authentication Bypass
- **Detection**: Failed authentication monitoring
- **Response**: Account lockout, security alert
- **Recovery**: Password reset, security review

#### Data Breach
- **Detection**: Unusual data access patterns
- **Response**: Immediate access revocation
- **Recovery**: Data audit, security hardening

#### API Abuse
- **Detection**: Rate limiting triggers
- **Response**: IP blocking, request throttling
- **Recovery**: Pattern analysis, rule updates

### Response Procedures

#### Immediate Actions
1. **Contain**: Stop the attack vector
2. **Assess**: Determine scope and impact
3. **Notify**: Alert security team
4. **Document**: Record incident details

#### Recovery Steps
1. **Investigate**: Root cause analysis
2. **Remediate**: Fix vulnerabilities
3. **Test**: Verify security measures
4. **Monitor**: Enhanced monitoring

## 📋 Security Checklist

### Development
- [ ] Input validation on all endpoints
- [ ] Output sanitization implemented
- [ ] Authentication required for sensitive operations
- [ ] Authorization checks for all resources
- [ ] Error messages don't leak sensitive information
- [ ] Rate limiting configured
- [ ] Audit logging enabled

### Deployment
- [ ] HTTPS enforced in production
- [ ] Security headers configured
- [ ] Secrets properly managed
- [ ] Database encryption enabled
- [ ] Backup encryption configured
- [ ] Monitoring and alerting setup
- [ ] Incident response plan documented

### Operations
- [ ] Regular security updates
- [ ] Vulnerability scanning
- [ ] Penetration testing
- [ ] Security training for team
- [ ] Access review and cleanup
- [ ] Log monitoring and analysis
- [ ] Incident response testing

## 🔍 Security Testing

### Automated Security Tests

#### OWASP Top 10 Testing
```python
@pytest.mark.security
async def test_sql_injection_protection():
    # Test SQL injection attempts
    malicious_payload = "'; DROP TABLE users; --"
    response = await client.get(f"/api/v1/users?search={malicious_payload}")
    assert response.status_code == 400

@pytest.mark.security  
async def test_xss_protection():
    # Test XSS attempts
    xss_payload = "<script>alert('xss')</script>"
    response = await client.post("/api/v1/sales", json={"notes": xss_payload})
    assert "<script>" not in response.text
```

### Manual Security Testing

#### Penetration Testing
- **Authentication Testing**: Brute force, session management
- **Authorization Testing**: Privilege escalation, access control
- **Input Testing**: Injection attacks, buffer overflows
- **Configuration Testing**: Security misconfigurations

## 📚 Security Resources

### OWASP Guidelines
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

### Security Tools
- **Static Analysis**: Bandit, Safety
- **Dynamic Testing**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: Safety, Snyk
- **Container Scanning**: Trivy, Clair

---

**Security Contact**: security@playpark.com  
**Last Updated**: 2025-01-24  
**Next Review**: 2025-04-24
