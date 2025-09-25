"""
Catalog Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class PackageType(str, Enum):
    """Package types"""
    SINGLE = "single"
    MULTI = "multi"
    TIME_BASED = "time_based"


class PricingRuleKind(str, Enum):
    """Pricing rule kinds"""
    LINE_PERCENT = "line_percent"
    LINE_AMOUNT = "line_amount"
    CART_PERCENT = "cart_percent"
    CART_AMOUNT = "cart_amount"
    BULK_DISCOUNT = "bulk_discount"


class AccessZone(BaseDocument):
    """Access zone model"""
    
    zone_id: str = Field(..., description="Unique zone identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(default=None, description="Zone description")
    capacity: Optional[int] = Field(default=None, description="Zone capacity")
    status: str = Field(default="active", description="Zone status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Zone settings")
    
    class Config:
        collection = "access_zones"


class Package(BaseDocument):
    """Package model"""
    
    package_id: str = Field(..., description="Unique package identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Package name")
    description: Optional[str] = Field(default=None, description="Package description")
    type: PackageType = Field(..., description="Package type")
    price: float = Field(..., ge=0, description="Package price")
    quota_or_minutes: int = Field(..., ge=1, description="Quota or minutes")
    active: bool = Field(default=True, description="Package active status")
    visible_on: List[str] = Field(default_factory=list, description="Visible on devices")
    access_zones: List[str] = Field(default_factory=list, description="Access zones")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Package settings")
    
    class Config:
        collection = "packages"


class PricingRule(BaseDocument):
    """Pricing rule model"""
    
    rule_id: str = Field(..., description="Unique rule identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(default=None, description="Rule description")
    kind: PricingRuleKind = Field(..., description="Rule kind")
    params: Dict[str, Any] = Field(..., description="Rule parameters")
    priority: int = Field(default=0, description="Rule priority")
    active: bool = Field(default=True, description="Rule active status")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Rule conditions")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Rule settings")
    
    class Config:
        collection = "pricing_rules"


class PricingCalculationRequest(BaseModel):
    """Pricing calculation request"""
    
    items: List[Dict[str, Any]] = Field(..., description="Items to calculate pricing for")
    customer_id: Optional[str] = Field(default=None, description="Customer ID")
    store_id: str = Field(..., description="Store ID")


class PricingCalculationResponse(BaseModel):
    """Pricing calculation response"""
    
    subtotal: float = Field(..., description="Subtotal amount")
    discount_total: float = Field(..., description="Total discount amount")
    tax_total: float = Field(..., description="Total tax amount")
    grand_total: float = Field(..., description="Grand total amount")
    applied_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Applied rules")
    breakdown: Dict[str, Any] = Field(default_factory=dict, description="Price breakdown")


class Category(BaseDocument):
    """Category model"""
    
    category_id: str = Field(..., description="Unique category identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(default=None, description="Category description")
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
    sort_order: int = Field(default=0, description="Sort order")
    active: bool = Field(default=True, description="Category active status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Category settings")
    
    class Config:
        collection = "categories"


class Product(BaseDocument):
    """Product model"""
    
    product_id: str = Field(..., description="Unique product identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    category_id: Optional[str] = Field(default=None, description="Category ID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(default=None, description="Product description")
    sku: Optional[str] = Field(default=None, description="Product SKU")
    price: float = Field(..., ge=0, description="Product price")
    cost: Optional[float] = Field(default=None, ge=0, description="Product cost")
    active: bool = Field(default=True, description="Product active status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Product settings")
    
    class Config:
        collection = "products"
