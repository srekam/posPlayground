"""
Redemption Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class RedemptionResult(str, Enum):
    """Redemption result"""
    PASS = "pass"
    FAIL = "fail"


class RedemptionReason(str, Enum):
    """Redemption failure reason"""
    EXPIRED = "expired"
    DUPLICATE = "duplicate"
    EXHAUSTED = "exhausted"
    INVALID_SIG = "invalid_sig"
    WRONG_DEVICE = "wrong_device"
    NOT_STARTED = "not_started"


class Redemption(BaseDocument):
    """Redemption model"""
    
    redemption_id: str = Field(..., description="Unique redemption identifier")
    ticket_id: str = Field(..., description="Ticket ID")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID that processed redemption")
    result: RedemptionResult = Field(..., description="Redemption result")
    reason: Optional[RedemptionReason] = Field(default=None, description="Failure reason")
    redeemed_at: datetime = Field(default_factory=datetime.utcnow, description="Redemption timestamp")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "redemptions"


class RedemptionCreateRequest(BaseModel):
    """Redemption creation request"""
    
    ticket_id: str = Field(..., description="Ticket ID")
    device_id: str = Field(..., description="Device ID")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RedemptionResponse(BaseModel):
    """Redemption response"""
    
    redemption_id: str = Field(..., description="Redemption ID")
    ticket_id: str = Field(..., description="Ticket ID")
    result: RedemptionResult = Field(..., description="Redemption result")
    reason: Optional[RedemptionReason] = Field(..., description="Failure reason")
    redeemed_at: datetime = Field(..., description="Redemption timestamp")
    meta: Dict[str, Any] = Field(..., description="Additional metadata")
