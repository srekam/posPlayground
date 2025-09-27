"""
Cash Drawer Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class CashDrawerStatus(str, Enum):
    """Cash drawer status"""
    OPEN = "open"
    CLOSED = "closed"
    SUSPENDED = "suspended"


class CashMovementType(str, Enum):
    """Cash movement type"""
    OPEN = "open"
    CLOSE = "close"
    DROP = "drop"
    PICKUP = "pickup"
    SALE = "sale"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class CashDrawer(BaseDocument):
    """Cash drawer model"""
    
    drawer_id: str = Field(..., description="Unique drawer identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    employee_id: str = Field(..., description="Employee ID")
    status: CashDrawerStatus = Field(..., description="Drawer status")
    opened_at: datetime = Field(..., description="Opening timestamp")
    closed_at: Optional[datetime] = Field(default=None, description="Closing timestamp")
    opening_amount: int = Field(..., ge=0, description="Opening amount in satang")
    closing_amount: Optional[int] = Field(default=None, ge=0, description="Closing amount in satang")
    expected_amount: Optional[int] = Field(default=None, description="Expected amount in satang")
    variance: Optional[int] = Field(default=None, description="Variance in satang")
    notes: Optional[str] = Field(default=None, description="Drawer notes")
    
    class Config:
        collection = "cash_drawers"


class CashMovement(BaseDocument):
    """Cash movement model"""
    
    movement_id: str = Field(..., description="Unique movement identifier")
    drawer_id: str = Field(..., description="Parent drawer ID")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    type: CashMovementType = Field(..., description="Movement type")
    amount: int = Field(..., description="Amount in satang")
    employee_id: str = Field(..., description="Employee ID")
    sale_id: Optional[str] = Field(default=None, description="Related sale ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Movement timestamp")
    notes: Optional[str] = Field(default=None, description="Movement notes")
    
    class Config:
        collection = "cash_movements"


class CashDrawerOpenRequest(BaseModel):
    """Cash drawer open request"""
    
    opening_amount: int = Field(..., ge=0, description="Opening amount in satang")
    notes: Optional[str] = Field(default=None, description="Opening notes")


class CashDrawerCloseRequest(BaseModel):
    """Cash drawer close request"""
    
    closing_amount: int = Field(..., ge=0, description="Closing amount in satang")
    notes: Optional[str] = Field(default=None, description="Closing notes")


class CashMovementCreateRequest(BaseModel):
    """Cash movement creation request"""
    
    type: CashMovementType = Field(..., description="Movement type")
    amount: int = Field(..., description="Amount in satang")
    sale_id: Optional[str] = Field(default=None, description="Related sale ID")
    notes: Optional[str] = Field(default=None, description="Movement notes")


class CashDrawerSummary(BaseModel):
    """Cash drawer summary"""
    
    drawer_id: str = Field(..., description="Drawer ID")
    status: CashDrawerStatus = Field(..., description="Drawer status")
    opened_at: datetime = Field(..., description="Opening timestamp")
    closed_at: Optional[datetime] = Field(..., description="Closing timestamp")
    opening_amount: int = Field(..., description="Opening amount in satang")
    closing_amount: Optional[int] = Field(..., description="Closing amount in satang")
    expected_amount: Optional[int] = Field(..., description="Expected amount in satang")
    variance: Optional[int] = Field(..., description="Variance in satang")
    total_sales: int = Field(..., description="Total sales in satang")
    total_refunds: int = Field(..., description="Total refunds in satang")
    total_drops: int = Field(..., description="Total drops in satang")
    total_pickups: int = Field(..., description="Total pickups in satang")
    movement_count: int = Field(..., description="Total movement count")
    reconciliation_rule: str = Field(..., description="Applied reconciliation rule")


class CashDrawerResponse(BaseModel):
    """Cash drawer response"""
    
    drawer_id: str = Field(..., description="Drawer ID")
    status: CashDrawerStatus = Field(..., description="Drawer status")
    opened_at: datetime = Field(..., description="Opening timestamp")
    closed_at: Optional[datetime] = Field(..., description="Closing timestamp")
    opening_amount: int = Field(..., description="Opening amount in satang")
    closing_amount: Optional[int] = Field(..., description="Closing amount in satang")
    expected_amount: Optional[int] = Field(..., description="Expected amount in satang")
    variance: Optional[int] = Field(..., description="Variance in satang")
    notes: Optional[str] = Field(..., description="Drawer notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
