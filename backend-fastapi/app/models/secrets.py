"""
Secrets Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class SecretKind(str, Enum):
    """Secret kinds"""
    HMAC_QR = "hmac_qr"
    API_KEY = "api_key"
    ENCRYPTION = "encryption"
    SIGNING = "signing"


class Secret(BaseDocument):
    """Secret model"""
    
    secret_id: str = Field(..., description="Unique secret identifier")
    kind: SecretKind = Field(..., description="Secret kind")
    version: int = Field(..., description="Secret version")
    key_hash: str = Field(..., description="Hashed secret key")
    active: bool = Field(default=True, description="Secret active status")
    created_by: str = Field(..., description="Creator user ID")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "secrets"


class SecretCreateRequest(BaseModel):
    """Secret creation request"""
    
    kind: SecretKind = Field(..., description="Secret kind")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SecretResponse(BaseModel):
    """Secret response"""
    
    secret_id: str = Field(..., description="Secret ID")
    kind: SecretKind = Field(..., description="Secret kind")
    version: int = Field(..., description="Secret version")
    active: bool = Field(..., description="Secret active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(..., description="Expiration timestamp")
    meta: Dict[str, Any] = Field(..., description="Additional metadata")
