"""
Discount Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class DiscountType(str, Enum):
    """Discount types"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    BUY_X_GET_Y = "buy_x_get_y"


class DiscountScope(str, Enum):
    """Discount scope"""
    GLOBAL = "global"
    PRODUCT = "product"
    CATEGORY = "category"
    CUSTOMER = "customer"


class Discount(BaseDocument):
    """Discount model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Discount name")
    code: str = Field(..., description="Discount code")
    type: DiscountType = Field(..., description="Discount type")
    value: float = Field(..., ge=0, description="Discount value")
    scope: DiscountScope = Field(default=DiscountScope.GLOBAL, description="Discount scope")
    scope_ids: list = Field(default_factory=list, description="Scope-specific IDs (products, categories, etc.)")
    min_amount: Optional[int] = Field(default=None, ge=0, description="Minimum amount in satang")
    max_amount: Optional[int] = Field(default=None, ge=0, description="Maximum amount in satang")
    active: bool = Field(default=True, description="Discount active status")
    description: Optional[str] = Field(default=None, description="Discount description")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions")
    
    class Config:
        collection = "discounts"


class DiscountCreateRequest(BaseModel):
    """Discount creation request"""
    
    name: str = Field(..., description="Discount name")
    code: str = Field(..., description="Discount code")
    type: DiscountType = Field(..., description="Discount type")
    value: float = Field(..., ge=0, description="Discount value")
    scope: DiscountScope = Field(default=DiscountScope.GLOBAL, description="Discount scope")
    scope_ids: list = Field(default_factory=list, description="Scope-specific IDs")
    min_amount: Optional[int] = Field(default=None, ge=0, description="Minimum amount in satang")
    max_amount: Optional[int] = Field(default=None, ge=0, description="Maximum amount in satang")
    active: bool = Field(default=True, description="Discount active status")
    description: Optional[str] = Field(default=None, description="Discount description")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions")


class DiscountUpdateRequest(BaseModel):
    """Discount update request"""
    
    name: Optional[str] = Field(default=None, description="Discount name")
    code: Optional[str] = Field(default=None, description="Discount code")
    type: Optional[DiscountType] = Field(default=None, description="Discount type")
    value: Optional[float] = Field(default=None, ge=0, description="Discount value")
    scope: Optional[DiscountScope] = Field(default=None, description="Discount scope")
    scope_ids: Optional[list] = Field(default=None, description="Scope-specific IDs")
    min_amount: Optional[int] = Field(default=None, ge=0, description="Minimum amount in satang")
    max_amount: Optional[int] = Field(default=None, ge=0, description="Maximum amount in satang")
    active: Optional[bool] = Field(default=None, description="Discount active status")
    description: Optional[str] = Field(default=None, description="Discount description")
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Additional conditions")


class DiscountResponse(BaseModel):
    """Discount response"""
    
    id: str = Field(..., description="Discount ID")
    name: str = Field(..., description="Discount name")
    code: str = Field(..., description="Discount code")
    type: DiscountType = Field(..., description="Discount type")
    value: float = Field(..., description="Discount value")
    scope: DiscountScope = Field(..., description="Discount scope")
    scope_ids: list = Field(..., description="Scope-specific IDs")
    min_amount: Optional[int] = Field(..., description="Minimum amount in satang")
    max_amount: Optional[int] = Field(..., description="Maximum amount in satang")
    active: bool = Field(..., description="Discount active status")
    description: Optional[str] = Field(..., description="Discount description")
    conditions: Dict[str, Any] = Field(..., description="Additional conditions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
