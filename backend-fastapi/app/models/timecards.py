"""
Timecard Models
"""
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class TimecardStatus(str, Enum):
    """Timecard status"""
    CLOCKED_IN = "clocked_in"
    CLOCKED_OUT = "clocked_out"
    BREAK = "break"


class Timecard(BaseDocument):
    """Timecard model"""
    
    timecard_id: str = Field(..., description="Unique timecard identifier")
    employee_id: str = Field(..., description="Employee ID")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    clock_in: datetime = Field(..., description="Clock in timestamp")
    clock_out: Optional[datetime] = Field(default=None, description="Clock out timestamp")
    break_start: Optional[datetime] = Field(default=None, description="Break start timestamp")
    break_end: Optional[datetime] = Field(default=None, description="Break end timestamp")
    total_break_time: int = Field(default=0, ge=0, description="Total break time in minutes")
    total_work_time: Optional[int] = Field(default=None, ge=0, description="Total work time in minutes")
    status: TimecardStatus = Field(default=TimecardStatus.CLOCKED_IN, description="Timecard status")
    notes: Optional[str] = Field(default=None, description="Timecard notes")
    
    class Config:
        collection = "timecards"


class TimecardClockInRequest(BaseModel):
    """Timecard clock in request"""
    
    notes: Optional[str] = Field(default=None, description="Clock in notes")


class TimecardClockOutRequest(BaseModel):
    """Timecard clock out request"""
    
    notes: Optional[str] = Field(default=None, description="Clock out notes")


class TimecardBreakRequest(BaseModel):
    """Timecard break request"""
    
    break_type: str = Field(default="break", description="Break type")
    notes: Optional[str] = Field(default=None, description="Break notes")


class TimecardResponse(BaseModel):
    """Timecard response"""
    
    timecard_id: str = Field(..., description="Timecard ID")
    employee_id: str = Field(..., description="Employee ID")
    clock_in: datetime = Field(..., description="Clock in timestamp")
    clock_out: Optional[datetime] = Field(..., description="Clock out timestamp")
    break_start: Optional[datetime] = Field(..., description="Break start timestamp")
    break_end: Optional[datetime] = Field(..., description="Break end timestamp")
    total_break_time: int = Field(..., description="Total break time in minutes")
    total_work_time: Optional[int] = Field(..., description="Total work time in minutes")
    status: TimecardStatus = Field(..., description="Timecard status")
    notes: Optional[str] = Field(..., description="Timecard notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class TimecardSummary(BaseModel):
    """Timecard summary"""
    
    employee_id: str = Field(..., description="Employee ID")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    clock_in: datetime = Field(..., description="Clock in timestamp")
    clock_out: Optional[datetime] = Field(..., description="Clock out timestamp")
    total_break_time: int = Field(..., description="Total break time in minutes")
    total_work_time: int = Field(..., description="Total work time in minutes")
    status: TimecardStatus = Field(..., description="Current status")
