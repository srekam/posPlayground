"""
Core Database Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from ulid import ULID


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class BaseDocument(BaseModel):
    """Base document model with common fields"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class Tenant(BaseDocument):
    """Tenant model"""
    
    tenant_id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Tenant name")
    status: str = Field(default="active", description="Tenant status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Tenant settings")
    created_by: Optional[str] = Field(default=None, description="Creator user ID")
    
    class Config:
        collection = "tenants"


class Store(BaseDocument):
    """Store model"""
    
    store_id: str = Field(..., description="Unique store identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Store name")
    address: Optional[str] = Field(default=None, description="Store address")
    timezone: str = Field(default="UTC", description="Store timezone")
    currency: str = Field(default="THB", description="Store currency")
    status: str = Field(default="active", description="Store status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Store settings")
    
    class Config:
        collection = "stores"


class Device(BaseDocument):
    """Device model"""
    
    device_id: str = Field(..., description="Unique device identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Device name")
    type: str = Field(..., description="Device type: POS, GATE, KIOSK")
    capabilities: List[str] = Field(default_factory=list, description="Device capabilities")
    status: str = Field(default="active", description="Device status")
    last_seen: Optional[datetime] = Field(default=None, description="Last heartbeat")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Device settings")
    
    class Config:
        collection = "devices"


class Employee(BaseDocument):
    """Employee model"""
    
    employee_id: str = Field(..., description="Unique employee identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    name: str = Field(..., description="Employee name")
    email: str = Field(..., description="Employee email")
    pin: str = Field(..., description="Employee PIN (hashed)")
    roles: List[str] = Field(default_factory=list, description="Employee roles")
    status: str = Field(default="active", description="Employee status")
    permissions: List[str] = Field(default_factory=list, description="Employee permissions")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Employee settings")
    
    class Config:
        collection = "employees"


class Role(BaseDocument):
    """Role model"""
    
    role_id: str = Field(..., description="Unique role identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(default=None, description="Role description")
    permissions: List[str] = Field(default_factory=list, description="Role permissions")
    is_system: bool = Field(default=False, description="System role flag")
    status: str = Field(default="active", description="Role status")
    
    class Config:
        collection = "roles"


class ApiKey(BaseDocument):
    """API Key model"""
    
    key_id: str = Field(..., description="Unique key identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    name: str = Field(..., description="Key name")
    key_hash: str = Field(..., description="Hashed API key")
    permissions: List[str] = Field(default_factory=list, description="Key permissions")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration date")
    last_used: Optional[datetime] = Field(default=None, description="Last usage date")
    status: str = Field(default="active", description="Key status")
    
    class Config:
        collection = "api_keys"
