"""
Pairing Log Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .core import BaseDocument


class PairingLog(BaseDocument):
    """Pairing log model"""
    
    pairing_id: str = Field(..., description="Unique pairing identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    user_id: str = Field(..., description="User ID who performed pairing")
    action: str = Field(..., description="Pairing action: pair, unpair, update")
    used_at: datetime = Field(default_factory=datetime.utcnow, description="Pairing timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Pairing details")
    
    class Config:
        collection = "pairing_logs"


class PairingLogCreateRequest(BaseModel):
    """Pairing log creation request"""
    
    device_id: str = Field(..., description="Device ID")
    action: str = Field(..., description="Pairing action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Pairing details")


class PairingLogResponse(BaseModel):
    """Pairing log response"""
    
    pairing_id: str = Field(..., description="Pairing ID")
    device_id: str = Field(..., description="Device ID")
    user_id: str = Field(..., description="User ID")
    action: str = Field(..., description="Pairing action")
    used_at: datetime = Field(..., description="Pairing timestamp")
    details: Dict[str, Any] = Field(..., description="Pairing details")
    created_at: datetime = Field(..., description="Creation timestamp")


class PairingLogsRequest(BaseModel):
    """Pairing logs request"""
    
    from_date: Optional[str] = Field(default=None, description="From date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(default=None, description="To date (YYYY-MM-DD)")
    store_id: Optional[str] = Field(default=None, description="Store ID filter")
    device_id: Optional[str] = Field(default=None, description="Device ID filter")
    limit: int = Field(default=100, ge=1, le=1000, description="Result limit")
    offset: int = Field(default=0, ge=0, description="Result offset")
