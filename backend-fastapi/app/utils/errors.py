"""
Error Handling Utilities
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorCode:
    """Error code constants"""
    
    # Authentication errors
    MISSING_TOKEN = "E_MISSING_TOKEN"
    INVALID_TOKEN = "E_INVALID_TOKEN"
    TOKEN_EXPIRED = "E_TOKEN_EXPIRED"
    INVALID_TOKEN_TYPE = "E_INVALID_TOKEN_TYPE"
    INVALID_CREDENTIALS = "E_INVALID_CREDENTIALS"
    ACCOUNT_DISABLED = "E_ACCOUNT_DISABLED"
    ACCOUNT_LOCKED = "E_ACCOUNT_LOCKED"
    
    # Authorization errors
    INSUFFICIENT_PERMISSIONS = "E_INSUFFICIENT_PERMISSIONS"
    INSUFFICIENT_ROLES = "E_INSUFFICIENT_ROLES"
    INSUFFICIENT_SCOPES = "E_INSUFFICIENT_SCOPES"
    ACCESS_DENIED = "E_ACCESS_DENIED"
    
    # User errors
    USER_NOT_FOUND = "E_USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "E_USER_ALREADY_EXISTS"
    INVALID_USER_DATA = "E_INVALID_USER_DATA"
    
    # Device errors
    DEVICE_NOT_FOUND = "E_DEVICE_NOT_FOUND"
    DEVICE_SUSPENDED = "E_DEVICE_SUSPENDED"
    DEVICE_ALREADY_REGISTERED = "E_DEVICE_ALREADY_REGISTERED"
    INVALID_DEVICE_TOKEN = "E_INVALID_DEVICE_TOKEN"
    
    # Sale errors
    SALE_NOT_FOUND = "E_SALE_NOT_FOUND"
    SALE_ALREADY_PROCESSED = "E_SALE_ALREADY_PROCESSED"
    INVALID_SALE_DATA = "E_INVALID_SALE_DATA"
    NO_OPEN_SHIFT = "E_NO_OPEN_SHIFT"
    INSUFFICIENT_PAYMENT = "E_INSUFFICIENT_PAYMENT"
    
    # Ticket errors
    TICKET_NOT_FOUND = "E_TICKET_NOT_FOUND"
    TICKET_ALREADY_USED = "E_TICKET_ALREADY_USED"
    TICKET_EXPIRED = "E_TICKET_EXPIRED"
    TICKET_NOT_STARTED = "E_TICKET_NOT_STARTED"
    TICKET_QUOTA_EXHAUSTED = "E_TICKET_QUOTA_EXHAUSTED"
    INVALID_TICKET_SIGNATURE = "E_INVALID_TICKET_SIGNATURE"
    DUPLICATE_USE = "E_DUPLICATE_USE"
    EXHAUSTED = "E_EXHAUSTED"
    NOT_STARTED = "E_NOT_STARTED"
    EXPIRED = "E_EXPIRED"
    INVALID_SIG = "E_INVALID_SIG"
    
    # Shift errors
    SHIFT_NOT_FOUND = "E_SHIFT_NOT_FOUND"
    SHIFT_ALREADY_OPEN = "E_SHIFT_ALREADY_OPEN"
    SHIFT_ALREADY_CLOSED = "E_SHIFT_ALREADY_CLOSED"
    NO_ACTIVE_SHIFT = "E_NO_ACTIVE_SHIFT"
    SHIFT_CLOSED = "E_SHIFT_CLOSED"
    
    # Package errors
    PACKAGE_NOT_FOUND = "E_PACKAGE_NOT_FOUND"
    PACKAGE_INACTIVE = "E_PACKAGE_INACTIVE"
    INVALID_PACKAGE_DATA = "E_INVALID_PACKAGE_DATA"
    
    # Validation errors
    VALIDATION_ERROR = "E_VALIDATION_ERROR"
    INVALID_REQUEST_DATA = "E_INVALID_REQUEST_DATA"
    MISSING_REQUIRED_FIELD = "E_MISSING_REQUIRED_FIELD"
    
    # Rate limiting
    RATE_LIMIT = "E_RATE_LIMIT"
    
    # System errors
    INTERNAL_ERROR = "E_INTERNAL_ERROR"
    DATABASE_ERROR = "E_DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "E_EXTERNAL_SERVICE_ERROR"
    SERVICE_UNAVAILABLE = "E_SERVICE_UNAVAILABLE"
    
    # Not found errors
    NOT_FOUND = "E_NOT_FOUND"
    RESOURCE_NOT_FOUND = "E_RESOURCE_NOT_FOUND"
    
    # Permission errors
    PERMISSION = "E_PERMISSION"


class PlayParkException(Exception):
    """Custom PlayPark exception"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create standardized error response"""
    
    error_data = {
        "error": error_code,
        "message": message
    }
    
    if details:
        error_data["details"] = details
    
    if request_id:
        error_data["request_id"] = request_id
    
    return HTTPException(
        status_code=status_code,
        detail=error_data
    )


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    
    field: str
    message: str
    code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    
    error: str = "E_VALIDATION_ERROR"
    message: str = "Validation failed"
    details: list[ValidationErrorDetail] = []


def create_validation_error_response(
    validation_errors: list[ValidationErrorDetail],
    request_id: Optional[str] = None
) -> HTTPException:
    """Create validation error response"""
    
    error_data = {
        "error": ErrorCode.VALIDATION_ERROR,
        "message": "Validation failed",
        "details": [error.dict() for error in validation_errors]
    }
    
    if request_id:
        error_data["request_id"] = request_id
    
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=error_data
    )


# Common error responses
def not_found_error(
    resource: str,
    identifier: str,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create not found error response"""
    return create_error_response(
        error_code=ErrorCode.NOT_FOUND,
        message=f"{resource} not found: {identifier}",
        status_code=status.HTTP_404_NOT_FOUND,
        request_id=request_id
    )


def unauthorized_error(
    message: str = "Authentication required",
    request_id: Optional[str] = None
) -> HTTPException:
    """Create unauthorized error response"""
    return create_error_response(
        error_code=ErrorCode.MISSING_TOKEN,
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
        request_id=request_id
    )


def forbidden_error(
    message: str = "Access denied",
    request_id: Optional[str] = None
) -> HTTPException:
    """Create forbidden error response"""
    return create_error_response(
        error_code=ErrorCode.ACCESS_DENIED,
        message=message,
        status_code=status.HTTP_403_FORBIDDEN,
        request_id=request_id
    )


def conflict_error(
    message: str = "Resource conflict",
    request_id: Optional[str] = None
) -> HTTPException:
    """Create conflict error response"""
    return create_error_response(
        error_code=ErrorCode.USER_ALREADY_EXISTS,
        message=message,
        status_code=status.HTTP_409_CONFLICT,
        request_id=request_id
    )


def rate_limit_error(
    retry_after: int = 60,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create rate limit error response"""
    return create_error_response(
        error_code=ErrorCode.RATE_LIMIT,
        message="Too many requests",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        details={"retry_after": retry_after},
        request_id=request_id
    )


def internal_error(
    message: str = "Internal server error",
    request_id: Optional[str] = None
) -> HTTPException:
    """Create internal error response"""
    return create_error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id
    )


def service_unavailable_error(
    message: str = "Service temporarily unavailable",
    request_id: Optional[str] = None
) -> HTTPException:
    """Create service unavailable error response"""
    return create_error_response(
        error_code=ErrorCode.SERVICE_UNAVAILABLE,
        message=message,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        request_id=request_id
    )
