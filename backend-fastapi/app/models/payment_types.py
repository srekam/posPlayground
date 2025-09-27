"""
Payment Type Models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .core import BaseDocument


class PaymentType(BaseDocument):
    """Payment type model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Payment type name")
    code: str = Field(..., description="Payment type code")
    method: str = Field(..., description="Payment method: cash, qr, card, other")
    active: bool = Field(default=True, description="Payment type active status")
    description: Optional[str] = Field(default=None, description="Payment type description")
    requires_reference: bool = Field(default=False, description="Requires transaction reference")
    
    class Config:
        collection = "payment_types"


class PaymentTypeCreateRequest(BaseModel):
    """Payment type creation request"""
    
    name: str = Field(..., description="Payment type name")
    code: str = Field(..., description="Payment type code")
    method: str = Field(..., description="Payment method: cash, qr, card, other")
    active: bool = Field(default=True, description="Payment type active status")
    description: Optional[str] = Field(default=None, description="Payment type description")
    requires_reference: bool = Field(default=False, description="Requires transaction reference")


class PaymentTypeUpdateRequest(BaseModel):
    """Payment type update request"""
    
    name: Optional[str] = Field(default=None, description="Payment type name")
    code: Optional[str] = Field(default=None, description="Payment type code")
    method: Optional[str] = Field(default=None, description="Payment method")
    active: Optional[bool] = Field(default=None, description="Payment type active status")
    description: Optional[str] = Field(default=None, description="Payment type description")
    requires_reference: Optional[bool] = Field(default=None, description="Requires transaction reference")


class PaymentTypeResponse(BaseModel):
    """Payment type response"""
    
    id: str = Field(..., description="Payment type ID")
    name: str = Field(..., description="Payment type name")
    code: str = Field(..., description="Payment type code")
    method: str = Field(..., description="Payment method")
    active: bool = Field(..., description="Payment type active status")
    description: Optional[str] = Field(..., description="Payment type description")
    requires_reference: bool = Field(..., description="Requires transaction reference")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
