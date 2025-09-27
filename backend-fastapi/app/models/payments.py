"""
Payment Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    QR = "qr"
    CARD = "card"
    OTHER = "other"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(BaseDocument):
    """Payment model"""
    
    payment_id: str = Field(..., description="Unique payment identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    sale_id: str = Field(..., description="Parent sale ID")
    method: PaymentMethod = Field(..., description="Payment method")
    amount: int = Field(..., ge=0, description="Amount in satang (minor units)")
    currency: str = Field(default="THB", description="Currency code")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    txn_ref: Optional[str] = Field(default=None, description="Transaction reference")
    gateway: Optional[str] = Field(default=None, description="Payment gateway")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "payments"


class PaymentCreateRequest(BaseModel):
    """Payment creation request"""
    
    sale_id: str = Field(..., description="Sale ID")
    method: PaymentMethod = Field(..., description="Payment method")
    amount: int = Field(..., ge=0, description="Amount in satang")
    txn_ref: Optional[str] = Field(default=None, description="Transaction reference")
    gateway: Optional[str] = Field(default=None, description="Payment gateway")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PaymentUpdateRequest(BaseModel):
    """Payment update request"""
    
    status: PaymentStatus = Field(..., description="Payment status")
    txn_ref: Optional[str] = Field(default=None, description="Transaction reference")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PaymentResponse(BaseModel):
    """Payment response"""
    
    payment_id: str = Field(..., description="Payment ID")
    sale_id: str = Field(..., description="Sale ID")
    method: PaymentMethod = Field(..., description="Payment method")
    amount: int = Field(..., description="Amount in satang")
    currency: str = Field(..., description="Currency code")
    status: PaymentStatus = Field(..., description="Payment status")
    txn_ref: Optional[str] = Field(..., description="Transaction reference")
    gateway: Optional[str] = Field(..., description="Payment gateway")
    meta: Dict[str, Any] = Field(..., description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
