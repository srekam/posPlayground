"""
Customer Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic import EmailStr

from .core import BaseDocument


class Customer(BaseDocument):
    """Customer model"""
    
    customer_id: str = Field(..., description="Unique customer identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Customer name")
    email: Optional[EmailStr] = Field(default=None, description="Customer email")
    phone: Optional[str] = Field(default=None, description="Customer phone")
    address: Optional[str] = Field(default=None, description="Customer address")
    date_of_birth: Optional[datetime] = Field(default=None, description="Date of birth")
    gender: Optional[str] = Field(default=None, description="Gender")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Customer preferences")
    loyalty_points: int = Field(default=0, ge=0, description="Loyalty points")
    total_spent: int = Field(default=0, ge=0, description="Total spent in satang")
    visit_count: int = Field(default=0, ge=0, description="Visit count")
    last_visit: Optional[datetime] = Field(default=None, description="Last visit timestamp")
    notes: Optional[str] = Field(default=None, description="Customer notes")
    active: bool = Field(default=True, description="Customer active status")
    
    class Config:
        collection = "customers"


class CustomerCreateRequest(BaseModel):
    """Customer creation request"""
    
    name: str = Field(..., description="Customer name")
    email: Optional[EmailStr] = Field(default=None, description="Customer email")
    phone: Optional[str] = Field(default=None, description="Customer phone")
    address: Optional[str] = Field(default=None, description="Customer address")
    date_of_birth: Optional[datetime] = Field(default=None, description="Date of birth")
    gender: Optional[str] = Field(default=None, description="Gender")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Customer preferences")
    notes: Optional[str] = Field(default=None, description="Customer notes")


class CustomerUpdateRequest(BaseModel):
    """Customer update request"""
    
    name: Optional[str] = Field(default=None, description="Customer name")
    email: Optional[EmailStr] = Field(default=None, description="Customer email")
    phone: Optional[str] = Field(default=None, description="Customer phone")
    address: Optional[str] = Field(default=None, description="Customer address")
    date_of_birth: Optional[datetime] = Field(default=None, description="Date of birth")
    gender: Optional[str] = Field(default=None, description="Gender")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Customer preferences")
    notes: Optional[str] = Field(default=None, description="Customer notes")
    active: Optional[bool] = Field(default=None, description="Customer active status")


class CustomerResponse(BaseModel):
    """Customer response"""
    
    customer_id: str = Field(..., description="Customer ID")
    name: str = Field(..., description="Customer name")
    email: Optional[str] = Field(..., description="Customer email")
    phone: Optional[str] = Field(..., description="Customer phone")
    address: Optional[str] = Field(..., description="Customer address")
    date_of_birth: Optional[datetime] = Field(..., description="Date of birth")
    gender: Optional[str] = Field(..., description="Gender")
    preferences: Dict[str, Any] = Field(..., description="Customer preferences")
    loyalty_points: int = Field(..., description="Loyalty points")
    total_spent: int = Field(..., description="Total spent in satang")
    visit_count: int = Field(..., description="Visit count")
    last_visit: Optional[datetime] = Field(..., description="Last visit timestamp")
    notes: Optional[str] = Field(..., description="Customer notes")
    active: bool = Field(..., description="Customer active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class CustomerSearchRequest(BaseModel):
    """Customer search request"""
    
    query: str = Field(..., description="Search query")
    limit: int = Field(default=20, ge=1, le=100, description="Result limit")
    offset: int = Field(default=0, ge=0, description="Result offset")
