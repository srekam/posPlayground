"""
Usage Counter Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .core import BaseDocument


class UsageCounter(BaseDocument):
    """Usage counter model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    route: str = Field(..., description="API route")
    method: str = Field(..., description="HTTP method")
    period: str = Field(..., description="Period (YYYY-MM)")
    count: int = Field(default=0, ge=0, description="Usage count")
    last_reset: datetime = Field(default_factory=datetime.utcnow, description="Last reset timestamp")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "usage_counters"


class UsageCounterResponse(BaseModel):
    """Usage counter response"""
    
    tenant_id: str = Field(..., description="Tenant ID")
    route: str = Field(..., description="API route")
    method: str = Field(..., description="HTTP method")
    period: str = Field(..., description="Period")
    count: int = Field(..., description="Usage count")
    last_reset: datetime = Field(..., description="Last reset timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class UsageBillingRequest(BaseModel):
    """Usage billing request"""
    
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID")
    from_date: str = Field(..., description="From date (YYYY-MM-DD)")
    to_date: str = Field(..., description="To date (YYYY-MM-DD)")


class UsageBillingResponse(BaseModel):
    """Usage billing response"""
    
    tenant_id: str = Field(..., description="Tenant ID")
    period: str = Field(..., description="Period")
    total_requests: int = Field(..., description="Total requests")
    route_usage: Dict[str, int] = Field(..., description="Route usage breakdown")
    generated_at: datetime = Field(..., description="Report generation timestamp")
