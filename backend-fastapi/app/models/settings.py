"""
Settings Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .core import BaseDocument


class Setting(BaseDocument):
    """Setting model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: Optional[str] = Field(default=None, description="Parent store ID (for store-specific settings)")
    key: str = Field(..., description="Setting key")
    value: Any = Field(..., description="Setting value")
    type: str = Field(default="string", description="Setting type")
    description: Optional[str] = Field(default=None, description="Setting description")
    category: Optional[str] = Field(default=None, description="Setting category")
    
    class Config:
        collection = "settings"


class FeatureFlag(BaseDocument):
    """Feature flag model"""
    
    key: str = Field(..., description="Feature flag key")
    enabled: bool = Field(default=False, description="Feature enabled status")
    tenant_id: Optional[str] = Field(default=None, description="Tenant-specific override")
    store_id: Optional[str] = Field(default=None, description="Store-specific override")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Feature conditions")
    description: Optional[str] = Field(default=None, description="Feature description")
    
    class Config:
        collection = "feature_flags"


class SettingCreateRequest(BaseModel):
    """Setting creation request"""
    
    key: str = Field(..., description="Setting key")
    value: Any = Field(..., description="Setting value")
    type: str = Field(default="string", description="Setting type")
    description: Optional[str] = Field(default=None, description="Setting description")
    category: Optional[str] = Field(default=None, description="Setting category")


class SettingUpdateRequest(BaseModel):
    """Setting update request"""
    
    value: Any = Field(..., description="Setting value")
    description: Optional[str] = Field(default=None, description="Setting description")
    category: Optional[str] = Field(default=None, description="Setting category")


class SettingResponse(BaseModel):
    """Setting response"""
    
    key: str = Field(..., description="Setting key")
    value: Any = Field(..., description="Setting value")
    type: str = Field(..., description="Setting type")
    description: Optional[str] = Field(..., description="Setting description")
    category: Optional[str] = Field(..., description="Setting category")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class FeatureFlagUpdateRequest(BaseModel):
    """Feature flag update request"""
    
    enabled: bool = Field(..., description="Feature enabled status")
    conditions: Optional[Dict[str, Any]] = Field(default=None, description="Feature conditions")
    description: Optional[str] = Field(default=None, description="Feature description")


class FeatureFlagResponse(BaseModel):
    """Feature flag response"""
    
    key: str = Field(..., description="Feature flag key")
    enabled: bool = Field(..., description="Feature enabled status")
    conditions: Dict[str, Any] = Field(..., description="Feature conditions")
    description: Optional[str] = Field(..., description="Feature description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
