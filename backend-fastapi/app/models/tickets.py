"""
Ticket Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class TicketType(str, Enum):
    """Ticket types"""
    SINGLE = "single"
    MULTI = "multi"
    TIME_BASED = "time_based"


class TicketStatus(str, Enum):
    """Ticket status"""
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class RedemptionResult(str, Enum):
    """Redemption results"""
    PASS = "pass"
    FAIL = "fail"
    ALREADY_USED = "already_used"
    EXPIRED = "expired"
    NOT_STARTED = "not_started"
    QUOTA_EXHAUSTED = "quota_exhausted"
    INVALID_SIGNATURE = "invalid_signature"


class Ticket(BaseDocument):
    """Ticket model"""
    
    ticket_id: str = Field(..., description="Unique ticket identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    sale_id: str = Field(..., description="Parent sale ID")
    package_id: str = Field(..., description="Package ID")
    type: TicketType = Field(..., description="Ticket type")
    quota_or_minutes: int = Field(..., ge=1, description="Quota or minutes")
    used: int = Field(default=0, ge=0, description="Usage count")
    valid_from: datetime = Field(..., description="Valid from date")
    valid_to: datetime = Field(..., description="Valid to date")
    lot_no: str = Field(..., description="Lot number")
    shift_id: str = Field(..., description="Shift ID")
    issued_by: str = Field(..., description="Issuer employee ID")
    price: float = Field(..., ge=0, description="Ticket price")
    payment_method: str = Field(..., description="Payment method")
    qr_token: str = Field(..., description="QR token")
    qr_payload: Dict[str, Any] = Field(..., description="QR payload")
    short_code: str = Field(..., description="Short code")
    signature: str = Field(..., description="HMAC signature")
    status: TicketStatus = Field(default=TicketStatus.ACTIVE, description="Ticket status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Ticket settings")
    
    class Config:
        collection = "tickets"


class TicketRedeemRequest(BaseModel):
    """Ticket redemption request"""
    
    qr_token: str = Field(..., description="QR token")
    device_id: str = Field(..., description="Redemption device ID")


class TicketRedeemResponse(BaseModel):
    """Ticket redemption response"""
    
    result: RedemptionResult = Field(..., description="Redemption result")
    reason: str = Field(..., description="Result reason")
    remaining: Optional[int] = Field(default=None, description="Remaining uses")
    ticket: Optional[Dict[str, Any]] = Field(default=None, description="Ticket information")


class TicketResponse(BaseModel):
    """Ticket response"""
    
    ticket_id: str = Field(..., description="Ticket ID")
    package_name: str = Field(..., description="Package name")
    type: TicketType = Field(..., description="Ticket type")
    quota_or_minutes: int = Field(..., description="Quota or minutes")
    used: int = Field(..., description="Usage count")
    status: TicketStatus = Field(..., description="Ticket status")
    valid_from: datetime = Field(..., description="Valid from date")
    valid_to: datetime = Field(..., description="Valid to date")
    short_code: str = Field(..., description="Short code")
    qr_payload: Dict[str, Any] = Field(..., description="QR payload")
    redemptions: List[Dict[str, Any]] = Field(default_factory=list, description="Redemption history")


class Redemption(BaseDocument):
    """Redemption model"""
    
    redemption_id: str = Field(..., description="Unique redemption identifier")
    ticket_id: str = Field(..., description="Ticket ID")
    device_id: str = Field(..., description="Redemption device ID")
    employee_id: Optional[str] = Field(default=None, description="Redemption employee ID")
    result: RedemptionResult = Field(..., description="Redemption result")
    reason: str = Field(..., description="Result reason")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Redemption timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Redemption metadata")
    
    class Config:
        collection = "redemptions"


class TicketValidation(BaseModel):
    """Ticket validation model"""
    
    qr_token: str = Field(..., description="QR token")
    signature: str = Field(..., description="HMAC signature")
    timestamp: datetime = Field(..., description="Validation timestamp")
    device_id: Optional[str] = Field(default=None, description="Validation device ID")


class TicketGenerationRequest(BaseModel):
    """Ticket generation request"""
    
    sale_id: str = Field(..., description="Sale ID")
    package_id: str = Field(..., description="Package ID")
    quantity: int = Field(..., ge=1, description="Ticket quantity")
    valid_days: int = Field(default=30, ge=1, description="Validity in days")


class TicketGenerationResponse(BaseModel):
    """Ticket generation response"""
    
    tickets: List[TicketResponse] = Field(..., description="Generated tickets")
    count: int = Field(..., description="Generated ticket count")
