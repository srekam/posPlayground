"""
Tax Models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .core import BaseDocument


class Tax(BaseDocument):
    """Tax model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Tax name")
    rate: float = Field(..., ge=0, le=100, description="Tax rate percentage")
    type: str = Field(default="percentage", description="Tax type: percentage, fixed")
    active: bool = Field(default=True, description="Tax active status")
    description: Optional[str] = Field(default=None, description="Tax description")
    
    class Config:
        collection = "taxes"


class TaxCreateRequest(BaseModel):
    """Tax creation request"""
    
    name: str = Field(..., description="Tax name")
    rate: float = Field(..., ge=0, le=100, description="Tax rate percentage")
    type: str = Field(default="percentage", description="Tax type: percentage, fixed")
    active: bool = Field(default=True, description="Tax active status")
    description: Optional[str] = Field(default=None, description="Tax description")


class TaxUpdateRequest(BaseModel):
    """Tax update request"""
    
    name: Optional[str] = Field(default=None, description="Tax name")
    rate: Optional[float] = Field(default=None, ge=0, le=100, description="Tax rate percentage")
    type: Optional[str] = Field(default=None, description="Tax type: percentage, fixed")
    active: Optional[bool] = Field(default=None, description="Tax active status")
    description: Optional[str] = Field(default=None, description="Tax description")


class TaxResponse(BaseModel):
    """Tax response"""
    
    id: str = Field(..., description="Tax ID")
    name: str = Field(..., description="Tax name")
    rate: float = Field(..., description="Tax rate percentage")
    type: str = Field(..., description="Tax type")
    active: bool = Field(..., description="Tax active status")
    description: Optional[str] = Field(..., description="Tax description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
