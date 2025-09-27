"""
Open Tickets Models (Cart/Park functionality)
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class OpenTicketStatus(str, Enum):
    """Open ticket status"""
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class OpenTicketItem(BaseModel):
    """Open ticket item"""
    
    package_id: str = Field(..., description="Package ID")
    package_name: str = Field(..., description="Package name")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: int = Field(..., ge=0, description="Unit price in satang")
    line_total: int = Field(..., ge=0, description="Line total in satang")


class OpenTicket(BaseDocument):
    """Open ticket model (parked cart)"""
    
    open_ticket_id: str = Field(..., description="Unique open ticket identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    cashier_id: str = Field(..., description="Cashier employee ID")
    items: List[OpenTicketItem] = Field(..., description="Open ticket items")
    subtotal: int = Field(..., ge=0, description="Subtotal in satang")
    discount_total: int = Field(default=0, ge=0, description="Total discount in satang")
    tax_total: int = Field(default=0, ge=0, description="Total tax in satang")
    grand_total: int = Field(..., ge=0, description="Grand total in satang")
    status: OpenTicketStatus = Field(default=OpenTicketStatus.ACTIVE, description="Open ticket status")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    notes: Optional[str] = Field(default=None, description="Open ticket notes")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "open_tickets"


class OpenTicketCreateRequest(BaseModel):
    """Open ticket creation request"""
    
    items: List[Dict[str, Any]] = Field(..., description="Open ticket items")
    expires_in_minutes: int = Field(default=30, ge=1, le=1440, description="Expiration in minutes")
    notes: Optional[str] = Field(default=None, description="Open ticket notes")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class OpenTicketUpdateRequest(BaseModel):
    """Open ticket update request"""
    
    items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Open ticket items")
    notes: Optional[str] = Field(default=None, description="Open ticket notes")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class OpenTicketCheckoutRequest(BaseModel):
    """Open ticket checkout request"""
    
    payment_method: str = Field(..., description="Payment method")
    amount_tendered: Optional[int] = Field(default=None, ge=0, description="Amount tendered in satang")
    notes: Optional[str] = Field(default=None, description="Sale notes")
    idempotency_key: Optional[str] = Field(default=None, description="Idempotency key")


class OpenTicketResponse(BaseModel):
    """Open ticket response"""
    
    open_ticket_id: str = Field(..., description="Open ticket ID")
    items: List[OpenTicketItem] = Field(..., description="Open ticket items")
    subtotal: int = Field(..., description="Subtotal in satang")
    discount_total: int = Field(..., description="Total discount in satang")
    tax_total: int = Field(..., description="Total tax in satang")
    grand_total: int = Field(..., description="Grand total in satang")
    status: OpenTicketStatus = Field(..., description="Open ticket status")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    notes: Optional[str] = Field(..., description="Open ticket notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class OpenTicketCheckoutResponse(BaseModel):
    """Open ticket checkout response"""
    
    open_ticket_id: str = Field(..., description="Open ticket ID")
    sale_id: str = Field(..., description="Generated sale ID")
    payment_id: str = Field(..., description="Generated payment ID")
    status: str = Field(..., description="Checkout status")
    tickets: List[Dict[str, Any]] = Field(default_factory=list, description="Generated tickets")
