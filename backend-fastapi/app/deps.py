"""
Dependency Injection for FastAPI
"""
from typing import Optional, List
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.config import settings
from app.db.mongo import get_database
from app.db.redis import get_redis, check_rate_limit
from app.models.auth import TokenPayload, TokenType
from app.utils.errors import PlayParkException, ErrorCode
from app.repositories.auth import AuthRepository
from app.repositories.users import UserRepository
from app.services.auth import AuthService

logger = structlog.get_logger(__name__)

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncIOMotorDatabase:
    """Get database dependency"""
    return await get_database()


async def get_redis_client():
    """Get Redis client dependency"""
    return await get_redis()


async def get_auth_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthRepository:
    """Get auth repository dependency"""
    return AuthRepository(db)


async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    """Get user repository dependency"""
    return UserRepository(db)


async def get_auth_service(
    auth_repo: AuthRepository = Depends(get_auth_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Get auth service dependency"""
    return AuthService(auth_repo, user_repo)


def verify_jwt_token(token: str) -> TokenPayload:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except ExpiredSignatureError:
        raise PlayParkException(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    except JWTError:
        raise PlayParkException(
            error_code=ErrorCode.INVALID_TOKEN,
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


async def get_current_user_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> TokenPayload:
    """Get current user token from Authorization header or cookies"""
    
    # Try Authorization header first
    if credentials:
        token = credentials.credentials
    else:
        # Try cookies for web clients
        token = request.cookies.get("access_token")
    
    if not token:
        raise PlayParkException(
            error_code=ErrorCode.MISSING_TOKEN,
            message="Authentication token required",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    return verify_jwt_token(token)


async def get_current_user(
    token: TokenPayload = Depends(get_current_user_token),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get current authenticated user"""
    
    if token.type != TokenType.ACCESS:
        raise PlayParkException(
            error_code=ErrorCode.INVALID_TOKEN_TYPE,
            message="Invalid token type",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get user from database
    user = await user_repo.get_by_id(token.sub)
    if not user:
        raise PlayParkException(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="User not found",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    return user


async def get_current_device(
    token: TokenPayload = Depends(get_current_user_token)
):
    """Get current authenticated device"""
    
    if token.type != TokenType.DEVICE:
        raise PlayParkException(
            error_code=ErrorCode.INVALID_TOKEN_TYPE,
            message="Invalid token type",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    return {
        "device_id": token.sub,
        "tenant_id": token.tenant_id,
        "store_id": token.store_id,
        "scopes": token.scopes
    }


def require_permissions(required_permissions: List[str]):
    """Require specific permissions"""
    
    async def permission_checker(
        user = Depends(get_current_user)
    ):
        user_permissions = getattr(user, 'permissions', [])
        
        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - set(user_permissions)
        if missing_permissions:
            raise PlayParkException(
                error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
                message=f"Missing permissions: {', '.join(missing_permissions)}",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return user
    
    return permission_checker


def require_roles(required_roles: List[str]):
    """Require specific roles"""
    
    async def role_checker(
        user = Depends(get_current_user)
    ):
        user_roles = getattr(user, 'roles', [])
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in required_roles):
            raise PlayParkException(
                error_code=ErrorCode.INSUFFICIENT_ROLES,
                message=f"Required roles: {', '.join(required_roles)}",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return user
    
    return role_checker


def require_scopes(required_scopes: List[str]):
    """Require specific scopes (for device tokens)"""
    
    async def scope_checker(
        device = Depends(get_current_device)
    ):
        device_scopes = device.get('scopes', [])
        
        # Check if device has all required scopes
        missing_scopes = set(required_scopes) - set(device_scopes)
        if missing_scopes:
            raise PlayParkException(
                error_code=ErrorCode.INSUFFICIENT_SCOPES,
                message=f"Missing scopes: {', '.join(missing_scopes)}",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return device
    
    return scope_checker


async def check_rate_limit_dependency(
    request: Request,
    redis = Depends(get_redis_client)
):
    """Rate limiting dependency"""
    
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # Get client identifier (IP address or user ID)
    client_ip = request.client.host
    user_id = getattr(request.state, 'user_id', None)
    identifier = user_id or client_ip
    
    # Check rate limit
    rate_limit_result = await check_rate_limit(
        identifier=identifier,
        limit=settings.RATE_LIMIT_REQUESTS,
        window=settings.RATE_LIMIT_WINDOW_MINUTES * 60
    )
    
    if not rate_limit_result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "E_RATE_LIMIT",
                "message": "Too many requests",
                "retry_after": rate_limit_result["reset"]
            },
            headers={
                "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                "X-RateLimit-Remaining": str(rate_limit_result["remaining"]),
                "X-RateLimit-Reset": str(rate_limit_result["reset"])
            }
        )
    
    # Add rate limit headers to response
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(rate_limit_result["limit"]),
        "X-RateLimit-Remaining": str(rate_limit_result["remaining"]),
        "X-RateLimit-Reset": str(rate_limit_result["reset"])
    }


async def get_idempotency_key(request: Request) -> Optional[str]:
    """Get idempotency key from request"""
    return request.headers.get("Idempotency-Key")


async def check_idempotency(
    request: Request,
    idempotency_key: Optional[str] = Depends(get_idempotency_key),
    redis = Depends(get_redis_client)
) -> Optional[str]:
    """Check idempotency and return key if valid"""
    
    if not settings.IDEMPOTENCY_ENABLED or not idempotency_key:
        return idempotency_key
    
    # Check if request already processed
    existing_response = await redis.get(
        key=idempotency_key,
        prefix="idempotency"
    )
    
    if existing_response:
        # Return cached response
        from fastapi import Response
        response = Response(
            content=existing_response,
            media_type="application/json"
        )
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Request already processed",
            headers={"X-Idempotency-Cached": "true"}
        )
    
    return idempotency_key


async def store_idempotency_response(
    idempotency_key: Optional[str],
    response_data: dict,
    redis = Depends(get_redis_client)
):
    """Store idempotency response"""
    
    if idempotency_key and settings.IDEMPOTENCY_ENABLED:
        import json
        await redis.redis_set(
            key=idempotency_key,
            value=json.dumps(response_data),
            expire=settings.IDEMPOTENCY_TTL_SECONDS,
            prefix="idempotency"
        )


# Common dependencies
CurrentUser = Depends(get_current_user)
CurrentDevice = Depends(get_current_device)
# RateLimit = Depends(check_rate_limit_dependency)  # Temporarily disabled
RateLimit = None  # Simplified for now
Idempotency = Depends(check_idempotency)

# Permission dependencies - these need to be called to get the actual dependency
def get_require_admin():
    return require_roles(["admin", "manager"])

def get_require_manager():
    return require_roles(["manager"])

def get_require_cashier():
    return require_roles(["cashier", "manager", "admin"])

# Scope dependencies - these need to be called to get the actual dependency
def get_require_sales_scope():
    return require_scopes(["sales"])

def get_require_ticket_scope():
    return require_scopes(["tickets"])

def get_require_report_scope():
    return require_scopes(["reports"])

# Dependency instances
RequireAdmin = Depends(get_require_admin)
RequireManager = Depends(get_require_manager)
RequireCashier = Depends(get_require_cashier)
RequireSalesScope = Depends(get_require_sales_scope)
RequireTicketScope = Depends(get_require_ticket_scope)
RequireReportScope = Depends(get_require_report_scope)
