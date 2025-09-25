"""
Authentication Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

from .core import BaseDocument


class TokenType(str, Enum):
    """Token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    DEVICE = "device"


class AuthProvider(str, Enum):
    """Authentication providers"""
    LOCAL = "local"
    OAUTH2 = "oauth2"


class DeviceLoginRequest(BaseModel):
    """Device login request"""
    
    device_id: str = Field(..., description="Device identifier")
    device_token: str = Field(..., description="Device token")


class EmployeeLoginRequest(BaseModel):
    """Employee login request"""
    
    email: EmailStr = Field(..., description="Employee email")
    pin: str = Field(..., min_length=4, max_length=8, description="Employee PIN")


class OAuth2LoginRequest(BaseModel):
    """OAuth2 login request"""
    
    code: str = Field(..., description="Authorization code")
    state: Optional[str] = Field(default=None, description="State parameter")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    """Token response"""
    
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class DeviceAuthResponse(BaseModel):
    """Device authentication response"""
    
    token: str = Field(..., description="JWT token")
    device: Dict[str, Any] = Field(..., description="Device information")


class EmployeeAuthResponse(BaseModel):
    """Employee authentication response"""
    
    token: str = Field(..., description="JWT token")
    employee: Dict[str, Any] = Field(..., description="Employee information")


class TokenPayload(BaseModel):
    """JWT token payload"""
    
    sub: str = Field(..., description="Subject (user/device ID)")
    type: TokenType = Field(..., description="Token type")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID")
    store_id: Optional[str] = Field(default=None, description="Store ID")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    scopes: List[str] = Field(default_factory=list, description="Token scopes")
    iat: int = Field(..., description="Issued at")
    exp: int = Field(..., description="Expires at")


class RefreshToken(BaseDocument):
    """Refresh token model"""
    
    token_id: str = Field(..., description="Unique token identifier")
    user_id: str = Field(..., description="User ID")
    token_hash: str = Field(..., description="Hashed refresh token")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID")
    store_id: Optional[str] = Field(default=None, description="Store ID")
    scopes: List[str] = Field(default_factory=list, description="Token scopes")
    expires_at: datetime = Field(..., description="Expiration date")
    last_used: Optional[datetime] = Field(default=None, description="Last usage date")
    is_revoked: bool = Field(default=False, description="Revocation flag")
    
    class Config:
        collection = "refresh_tokens"


class Session(BaseDocument):
    """User session model"""
    
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID")
    store_id: Optional[str] = Field(default=None, description="Store ID")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    expires_at: datetime = Field(..., description="Expiration date")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity")
    is_active: bool = Field(default=True, description="Session active flag")
    
    class Config:
        collection = "sessions"


class PasswordReset(BaseDocument):
    """Password reset model"""
    
    reset_id: str = Field(..., description="Unique reset identifier")
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    token_hash: str = Field(..., description="Hashed reset token")
    expires_at: datetime = Field(..., description="Expiration date")
    is_used: bool = Field(default=False, description="Usage flag")
    used_at: Optional[datetime] = Field(default=None, description="Usage date")
    
    class Config:
        collection = "password_resets"
