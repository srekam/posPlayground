"""
Pricing Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class PricingRuleType(str, Enum):
    """Pricing rule types"""
    DISCOUNT = "discount"
    SURCHARGE = "surcharge"
    PRICE_OVERRIDE = "price_override"


class PricingRuleScope(str, Enum):
    """Pricing rule scope"""
    GLOBAL = "global"
    PRODUCT = "product"
    CATEGORY = "category"
    CUSTOMER = "customer"
    TIME = "time"


class PricingRule(BaseDocument):
    """Pricing rule model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Rule name")
    type: PricingRuleType = Field(..., description="Rule type")
    scope: PricingRuleScope = Field(..., description="Rule scope")
    scope_ids: List[str] = Field(default_factory=list, description="Scope-specific IDs")
    priority: int = Field(default=0, description="Rule priority (higher = more priority)")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Rule conditions")
    actions: Dict[str, Any] = Field(..., description="Rule actions")
    active: bool = Field(default=True, description="Rule active status")
    valid_from: Optional[datetime] = Field(default=None, description="Valid from date")
    valid_until: Optional[datetime] = Field(default=None, description="Valid until date")
    
    class Config:
        collection = "pricing_rules"


class PriceList(BaseDocument):
    """Price list model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Price list name")
    code: str = Field(..., description="Price list code")
    description: Optional[str] = Field(default=None, description="Price list description")
    active: bool = Field(default=True, description="Price list active status")
    priority: int = Field(default=0, description="Price list priority")
    valid_from: Optional[datetime] = Field(default=None, description="Valid from date")
    valid_until: Optional[datetime] = Field(default=None, description="Valid until date")
    
    class Config:
        collection = "price_lists"


class PriceListItem(BaseDocument):
    """Price list item model"""
    
    price_list_id: str = Field(..., description="Parent price list ID")
    product_id: str = Field(..., description="Product ID")
    package_id: Optional[str] = Field(default=None, description="Package ID")
    price: int = Field(..., ge=0, description="Price in satang")
    min_quantity: int = Field(default=1, ge=1, description="Minimum quantity")
    max_quantity: Optional[int] = Field(default=None, ge=1, description="Maximum quantity")
    active: bool = Field(default=True, description="Price list item active status")
    
    class Config:
        collection = "price_list_items"


class PricingPreviewRequest(BaseModel):
    """Pricing preview request"""
    
    items: List[Dict[str, Any]] = Field(..., description="Items to price")
    customer_id: Optional[str] = Field(default=None, description="Customer ID")
    store_id: Optional[str] = Field(default=None, description="Store ID")
    timestamp: Optional[datetime] = Field(default=None, description="Pricing timestamp")


class PricingPreviewItem(BaseModel):
    """Pricing preview item"""
    
    product_id: str = Field(..., description="Product ID")
    package_id: Optional[str] = Field(default=None, description="Package ID")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: int = Field(..., ge=0, description="Unit price in satang")
    line_total: int = Field(..., ge=0, description="Line total in satang")
    discounts: List[Dict[str, Any]] = Field(default_factory=list, description="Applied discounts")
    taxes: List[Dict[str, Any]] = Field(default_factory=list, description="Applied taxes")


class PricingPreviewResponse(BaseModel):
    """Pricing preview response"""
    
    items: List[PricingPreviewItem] = Field(..., description="Priced items")
    subtotal: int = Field(..., ge=0, description="Subtotal in satang")
    discount_total: int = Field(..., ge=0, description="Total discount in satang")
    tax_total: int = Field(..., ge=0, description="Total tax in satang")
    grand_total: int = Field(..., ge=0, description="Grand total in satang")
    applied_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Applied pricing rules")
    price_list: Optional[str] = Field(default=None, description="Applied price list")
