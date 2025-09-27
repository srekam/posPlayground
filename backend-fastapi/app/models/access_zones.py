"""
Access Zone Models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .core import BaseDocument


class AccessZone(BaseDocument):
    """Access zone model"""
    
    zone_id: str = Field(..., description="Unique zone identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(default=None, description="Zone description")
    active: bool = Field(default=True, description="Zone active status")
    capacity: Optional[int] = Field(default=None, ge=0, description="Zone capacity")
    current_count: int = Field(default=0, ge=0, description="Current occupancy")
    
    class Config:
        collection = "access_zones"


class PackageZoneMap(BaseDocument):
    """Package zone mapping model"""
    
    package_id: str = Field(..., description="Package ID")
    zone_id: str = Field(..., description="Zone ID")
    tenant_id: str = Field(..., description="Parent tenant ID")
    access_type: str = Field(default="allowed", description="Access type: allowed, denied, limited")
    max_uses: Optional[int] = Field(default=None, ge=1, description="Maximum uses per ticket")
    time_limit: Optional[int] = Field(default=None, ge=1, description="Time limit in minutes")
    
    class Config:
        collection = "package_zone_map"


class AccessZoneCreateRequest(BaseModel):
    """Access zone creation request"""
    
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(default=None, description="Zone description")
    active: bool = Field(default=True, description="Zone active status")
    capacity: Optional[int] = Field(default=None, ge=0, description="Zone capacity")


class AccessZoneUpdateRequest(BaseModel):
    """Access zone update request"""
    
    name: Optional[str] = Field(default=None, description="Zone name")
    description: Optional[str] = Field(default=None, description="Zone description")
    active: Optional[bool] = Field(default=None, description="Zone active status")
    capacity: Optional[int] = Field(default=None, ge=0, description="Zone capacity")


class AccessZoneResponse(BaseModel):
    """Access zone response"""
    
    zone_id: str = Field(..., description="Zone ID")
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(..., description="Zone description")
    active: bool = Field(..., description="Zone active status")
    capacity: Optional[int] = Field(..., description="Zone capacity")
    current_count: int = Field(..., description="Current occupancy")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class PackageZoneMapCreateRequest(BaseModel):
    """Package zone mapping creation request"""
    
    package_id: str = Field(..., description="Package ID")
    zone_id: str = Field(..., description="Zone ID")
    access_type: str = Field(default="allowed", description="Access type")
    max_uses: Optional[int] = Field(default=None, ge=1, description="Maximum uses per ticket")
    time_limit: Optional[int] = Field(default=None, ge=1, description="Time limit in minutes")


class PackageZoneMapResponse(BaseModel):
    """Package zone mapping response"""
    
    package_id: str = Field(..., description="Package ID")
    zone_id: str = Field(..., description="Zone ID")
    access_type: str = Field(..., description="Access type")
    max_uses: Optional[int] = Field(..., description="Maximum uses per ticket")
    time_limit: Optional[int] = Field(..., description="Time limit in minutes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
