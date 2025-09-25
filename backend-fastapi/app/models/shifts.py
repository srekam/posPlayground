"""
Shift Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class ShiftStatus(str, Enum):
    """Shift status"""
    OPEN = "open"
    CLOSED = "closed"


class ShiftTotals(BaseModel):
    """Shift totals model"""
    
    sales: Dict[str, Any] = Field(default_factory=lambda: {"count": 0, "amount": 0.0})
    refunds: Dict[str, Any] = Field(default_factory=lambda: {"count": 0, "amount": 0.0})
    reprints: Dict[str, Any] = Field(default_factory=lambda: {"count": 0})
    discounts: Dict[str, Any] = Field(default_factory=lambda: {"count": 0, "amount": 0.0})


class Shift(BaseDocument):
    """Shift model"""
    
    shift_id: str = Field(..., description="Unique shift identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    opened_by: str = Field(..., description="Opening employee ID")
    closed_by: Optional[str] = Field(default=None, description="Closing employee ID")
    open_at: datetime = Field(..., description="Opening timestamp")
    close_at: Optional[datetime] = Field(default=None, description="Closing timestamp")
    cash_open: float = Field(..., ge=0, description="Opening cash amount")
    cash_counted: Optional[float] = Field(default=None, ge=0, description="Counted cash amount")
    cash_expected: Optional[float] = Field(default=None, ge=0, description="Expected cash amount")
    cash_diff: Optional[float] = Field(default=None, description="Cash difference")
    status: ShiftStatus = Field(default=ShiftStatus.OPEN, description="Shift status")
    totals: ShiftTotals = Field(default_factory=ShiftTotals, description="Shift totals")
    notes: Optional[str] = Field(default=None, description="Shift notes")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Shift settings")
    
    class Config:
        collection = "shifts"


class ShiftOpenRequest(BaseModel):
    """Shift opening request"""
    
    employee_id: str = Field(..., description="Employee ID")
    cash_open: float = Field(..., ge=0, description="Opening cash amount")


class ShiftCloseRequest(BaseModel):
    """Shift closing request"""
    
    employee_id: str = Field(..., description="Employee ID")
    cash_counted: float = Field(..., ge=0, description="Counted cash amount")
    notes: Optional[str] = Field(default=None, description="Closing notes")


class ShiftResponse(BaseModel):
    """Shift response"""
    
    shift_id: str = Field(..., description="Shift ID")
    opened_by: str = Field(..., description="Opening employee ID")
    closed_by: Optional[str] = Field(..., description="Closing employee ID")
    open_at: datetime = Field(..., description="Opening timestamp")
    close_at: Optional[datetime] = Field(..., description="Closing timestamp")
    cash_open: float = Field(..., description="Opening cash amount")
    cash_counted: Optional[float] = Field(..., description="Counted cash amount")
    cash_expected: Optional[float] = Field(..., description="Expected cash amount")
    cash_diff: Optional[float] = Field(..., description="Cash difference")
    status: ShiftStatus = Field(..., description="Shift status")
    totals: ShiftTotals = Field(..., description="Shift totals")
    notes: Optional[str] = Field(..., description="Shift notes")


class ShiftSummary(BaseModel):
    """Shift summary model"""
    
    shift_id: str = Field(..., description="Shift ID")
    device_id: str = Field(..., description="Device ID")
    opened_by: str = Field(..., description="Opening employee ID")
    closed_by: Optional[str] = Field(..., description="Closing employee ID")
    open_at: datetime = Field(..., description="Opening timestamp")
    close_at: Optional[datetime] = Field(..., description="Closing timestamp")
    duration_minutes: Optional[int] = Field(default=None, description="Shift duration in minutes")
    status: ShiftStatus = Field(..., description="Shift status")
    totals: ShiftTotals = Field(..., description="Shift totals")


class CashDrawer(BaseDocument):
    """Cash drawer model"""
    
    drawer_id: str = Field(..., description="Unique drawer identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    shift_id: str = Field(..., description="Current shift ID")
    current_amount: float = Field(default=0, ge=0, description="Current cash amount")
    last_counted: Optional[datetime] = Field(default=None, description="Last count timestamp")
    last_counted_by: Optional[str] = Field(default=None, description="Last counter employee ID")
    status: str = Field(default="active", description="Drawer status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Drawer settings")
    
    class Config:
        collection = "cash_drawers"


class CashCount(BaseDocument):
    """Cash count model"""
    
    count_id: str = Field(..., description="Unique count identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    shift_id: str = Field(..., description="Shift ID")
    counted_by: str = Field(..., description="Counter employee ID")
    amount: float = Field(..., ge=0, description="Counted amount")
    expected: Optional[float] = Field(default=None, ge=0, description="Expected amount")
    difference: Optional[float] = Field(default=None, description="Amount difference")
    notes: Optional[str] = Field(default=None, description="Count notes")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Count timestamp")
    
    class Config:
        collection = "cash_counts"
