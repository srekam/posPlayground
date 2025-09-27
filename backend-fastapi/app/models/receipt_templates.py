"""
Receipt Template Models
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from .core import BaseDocument


class ReceiptTemplate(BaseDocument):
    """Receipt template model"""
    
    template_id: str = Field(..., description="Unique template identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: Optional[str] = Field(default=None, description="Parent store ID")
    name: str = Field(..., description="Template name")
    type: str = Field(default="sale", description="Template type: sale, refund, reprint")
    template: Dict[str, Any] = Field(..., description="Template configuration")
    active: bool = Field(default=True, description="Template active status")
    description: Optional[str] = Field(default=None, description="Template description")
    
    class Config:
        collection = "receipt_templates"


class Printer(BaseDocument):
    """Printer model"""
    
    printer_id: str = Field(..., description="Unique printer identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    name: str = Field(..., description="Printer name")
    type: str = Field(..., description="Printer type: thermal, inkjet, laser")
    connection: str = Field(..., description="Connection type: usb, network, bluetooth")
    address: str = Field(..., description="Printer address/IP")
    port: Optional[int] = Field(default=None, description="Printer port")
    capabilities: List[str] = Field(default_factory=list, description="Printer capabilities")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Printer settings")
    active: bool = Field(default=True, description="Printer active status")
    
    class Config:
        collection = "printers"


class ReceiptTemplateCreateRequest(BaseModel):
    """Receipt template creation request"""
    
    name: str = Field(..., description="Template name")
    type: str = Field(default="sale", description="Template type")
    template: Dict[str, Any] = Field(..., description="Template configuration")
    active: bool = Field(default=True, description="Template active status")
    description: Optional[str] = Field(default=None, description="Template description")


class ReceiptTemplateUpdateRequest(BaseModel):
    """Receipt template update request"""
    
    name: Optional[str] = Field(default=None, description="Template name")
    template: Optional[Dict[str, Any]] = Field(default=None, description="Template configuration")
    active: Optional[bool] = Field(default=None, description="Template active status")
    description: Optional[str] = Field(default=None, description="Template description")


class PrinterCreateRequest(BaseModel):
    """Printer creation request"""
    
    name: str = Field(..., description="Printer name")
    type: str = Field(..., description="Printer type")
    connection: str = Field(..., description="Connection type")
    address: str = Field(..., description="Printer address/IP")
    port: Optional[int] = Field(default=None, description="Printer port")
    capabilities: List[str] = Field(default_factory=list, description="Printer capabilities")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Printer settings")
    active: bool = Field(default=True, description="Printer active status")


class PrinterUpdateRequest(BaseModel):
    """Printer update request"""
    
    name: Optional[str] = Field(default=None, description="Printer name")
    type: Optional[str] = Field(default=None, description="Printer type")
    connection: Optional[str] = Field(default=None, description="Connection type")
    address: Optional[str] = Field(default=None, description="Printer address/IP")
    port: Optional[int] = Field(default=None, description="Printer port")
    capabilities: Optional[List[str]] = Field(default=None, description="Printer capabilities")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="Printer settings")
    active: Optional[bool] = Field(default=None, description="Printer active status")


class ReceiptTemplateResponse(BaseModel):
    """Receipt template response"""
    
    template_id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    type: str = Field(..., description="Template type")
    template: Dict[str, Any] = Field(..., description="Template configuration")
    active: bool = Field(..., description="Template active status")
    description: Optional[str] = Field(..., description="Template description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class PrinterResponse(BaseModel):
    """Printer response"""
    
    printer_id: str = Field(..., description="Printer ID")
    name: str = Field(..., description="Printer name")
    type: str = Field(..., description="Printer type")
    connection: str = Field(..., description="Connection type")
    address: str = Field(..., description="Printer address/IP")
    port: Optional[int] = Field(..., description="Printer port")
    capabilities: List[str] = Field(..., description="Printer capabilities")
    settings: Dict[str, Any] = Field(..., description="Printer settings")
    active: bool = Field(..., description="Printer active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
