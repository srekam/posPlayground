"""
Sales Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    QR = "qr"
    CARD = "card"
    OTHER = "other"


class SaleStatus(str, Enum):
    """Sale status"""
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PENDING = "pending"


class RefundStatus(str, Enum):
    """Refund status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


class ReprintStatus(str, Enum):
    """Reprint status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PRINTED = "printed"


class SaleItem(BaseModel):
    """Sale item model"""
    
    package_id: str = Field(..., description="Package ID")
    package_name: str = Field(..., description="Package name")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: float = Field(..., ge=0, description="Unit price")
    line_total: float = Field(..., ge=0, description="Line total")
    discounts: List[Dict[str, Any]] = Field(default_factory=list, description="Applied discounts")


class Sale(BaseDocument):
    """Sale model"""
    
    sale_id: str = Field(..., description="Unique sale identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    device_id: str = Field(..., description="Device ID")
    cashier_id: str = Field(..., description="Cashier employee ID")
    shift_id: str = Field(..., description="Shift ID")
    reference: str = Field(..., description="Sale reference (idempotency key)")
    items: List[SaleItem] = Field(..., description="Sale items")
    subtotal: float = Field(..., ge=0, description="Subtotal amount")
    discount_total: float = Field(default=0, ge=0, description="Total discount amount")
    tax_total: float = Field(default=0, ge=0, description="Total tax amount")
    grand_total: float = Field(..., ge=0, description="Grand total amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    amount_tendered: Optional[float] = Field(default=None, ge=0, description="Amount tendered")
    change: Optional[float] = Field(default=None, ge=0, description="Change amount")
    notes: Optional[str] = Field(default=None, description="Sale notes")
    status: SaleStatus = Field(default=SaleStatus.COMPLETED, description="Sale status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Sale timestamp")
    
    class Config:
        collection = "sales"


class SaleCreateRequest(BaseModel):
    """Sale creation request"""
    
    items: List[Dict[str, Any]] = Field(..., description="Sale items")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    amount_tendered: Optional[float] = Field(default=None, ge=0, description="Amount tendered")
    notes: Optional[str] = Field(default=None, description="Sale notes")
    idempotency_key: Optional[str] = Field(default=None, description="Idempotency key")


class SaleResponse(BaseModel):
    """Sale response"""
    
    sale_id: str = Field(..., description="Sale ID")
    reference: str = Field(..., description="Sale reference")
    status: SaleStatus = Field(..., description="Sale status")
    items: List[SaleItem] = Field(..., description="Sale items")
    subtotal: float = Field(..., description="Subtotal amount")
    discount_total: float = Field(..., description="Total discount amount")
    tax_total: float = Field(..., description="Total tax amount")
    grand_total: float = Field(..., description="Grand total amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    amount_tendered: Optional[float] = Field(..., description="Amount tendered")
    change: Optional[float] = Field(..., description="Change amount")
    notes: Optional[str] = Field(..., description="Sale notes")
    tickets: List[Dict[str, Any]] = Field(default_factory=list, description="Generated tickets")
    timestamp: datetime = Field(..., description="Sale timestamp")


class Refund(BaseDocument):
    """Refund model"""
    
    refund_id: str = Field(..., description="Unique refund identifier")
    sale_id: str = Field(..., description="Parent sale ID")
    ticket_ids: List[str] = Field(default_factory=list, description="Refunded ticket IDs")
    amount: float = Field(..., ge=0, description="Refund amount")
    method: PaymentMethod = Field(..., description="Refund method")
    requested_by: str = Field(..., description="Requestor employee ID")
    approved_by: Optional[str] = Field(default=None, description="Approver employee ID")
    reason_code: str = Field(..., description="Refund reason code")
    reason_text: Optional[str] = Field(default=None, description="Refund reason text")
    status: RefundStatus = Field(default=RefundStatus.PENDING, description="Refund status")
    processed_at: Optional[datetime] = Field(default=None, description="Processing date")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    
    class Config:
        collection = "refunds"


class RefundRequest(BaseModel):
    """Refund request"""
    
    sale_id: str = Field(..., description="Sale ID")
    ticket_ids: Optional[List[str]] = Field(default=None, description="Ticket IDs to refund")
    reason_code: str = Field(..., description="Refund reason code")
    reason_text: Optional[str] = Field(default=None, description="Refund reason text")


class RefundResponse(BaseModel):
    """Refund response"""
    
    refund_id: str = Field(..., description="Refund ID")
    sale_id: str = Field(..., description="Sale ID")
    amount: float = Field(..., description="Refund amount")
    status: RefundStatus = Field(..., description="Refund status")
    reason_code: str = Field(..., description="Refund reason code")
    reason_text: Optional[str] = Field(..., description="Refund reason text")
    requested_by: str = Field(..., description="Requestor employee ID")
    timestamp: datetime = Field(..., description="Request timestamp")


class Reprint(BaseDocument):
    """Reprint model"""
    
    reprint_id: str = Field(..., description="Unique reprint identifier")
    ticket_id: str = Field(..., description="Ticket ID")
    requested_by: str = Field(..., description="Requestor employee ID")
    approved_by: Optional[str] = Field(default=None, description="Approver employee ID")
    reason_code: str = Field(..., description="Reprint reason code")
    reason_text: Optional[str] = Field(default=None, description="Reprint reason text")
    status: ReprintStatus = Field(default=ReprintStatus.PENDING, description="Reprint status")
    printed_at: Optional[datetime] = Field(default=None, description="Printing date")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    
    class Config:
        collection = "reprints"


class ReprintRequest(BaseModel):
    """Reprint request"""
    
    ticket_id: str = Field(..., description="Ticket ID")
    reason_code: str = Field(..., description="Reprint reason code")
    reason_text: Optional[str] = Field(default=None, description="Reprint reason text")


class ReprintResponse(BaseModel):
    """Reprint response"""
    
    reprint_id: str = Field(..., description="Reprint ID")
    ticket_id: str = Field(..., description="Ticket ID")
    status: ReprintStatus = Field(..., description="Reprint status")
    reason_code: str = Field(..., description="Reprint reason code")
    reason_text: Optional[str] = Field(..., description="Reprint reason text")
    requested_by: str = Field(..., description="Requestor employee ID")
    timestamp: datetime = Field(..., description="Request timestamp")
