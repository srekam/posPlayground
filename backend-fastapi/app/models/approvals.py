"""
Approval Models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .core import BaseDocument


class ReasonCode(BaseDocument):
    """Reason code model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    code: str = Field(..., description="Reason code")
    name: str = Field(..., description="Reason name")
    category: str = Field(..., description="Reason category")
    description: Optional[str] = Field(default=None, description="Reason description")
    requires_approval: bool = Field(default=True, description="Requires approval")
    active: bool = Field(default=True, description="Reason code active status")
    
    class Config:
        collection = "reason_codes"


class Approval(BaseDocument):
    """Approval model"""
    
    approval_id: str = Field(..., description="Unique approval identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    type: str = Field(..., description="Approval type")
    reference_id: str = Field(..., description="Reference ID (sale, refund, etc.)")
    requested_by: str = Field(..., description="Requestor employee ID")
    approved_by: Optional[str] = Field(default=None, description="Approver employee ID")
    pin: str = Field(..., description="Approval PIN (hashed)")
    status: str = Field(default="pending", description="Approval status")
    requested_at: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    approved_at: Optional[datetime] = Field(default=None, description="Approval timestamp")
    reason_code: str = Field(..., description="Reason code")
    notes: Optional[str] = Field(default=None, description="Approval notes")
    
    class Config:
        collection = "approvals"


class ReasonCodeCreateRequest(BaseModel):
    """Reason code creation request"""
    
    code: str = Field(..., description="Reason code")
    name: str = Field(..., description="Reason name")
    category: str = Field(..., description="Reason category")
    description: Optional[str] = Field(default=None, description="Reason description")
    requires_approval: bool = Field(default=True, description="Requires approval")
    active: bool = Field(default=True, description="Reason code active status")


class ReasonCodeUpdateRequest(BaseModel):
    """Reason code update request"""
    
    name: Optional[str] = Field(default=None, description="Reason name")
    category: Optional[str] = Field(default=None, description="Reason category")
    description: Optional[str] = Field(default=None, description="Reason description")
    requires_approval: Optional[bool] = Field(default=None, description="Requires approval")
    active: Optional[bool] = Field(default=None, description="Reason code active status")


class ApprovalVerifyRequest(BaseModel):
    """Approval verification request"""
    
    pin: str = Field(..., description="Approval PIN")
    reference_id: str = Field(..., description="Reference ID")


class ReasonCodeResponse(BaseModel):
    """Reason code response"""
    
    id: str = Field(..., description="Reason code ID")
    code: str = Field(..., description="Reason code")
    name: str = Field(..., description="Reason name")
    category: str = Field(..., description="Reason category")
    description: Optional[str] = Field(..., description="Reason description")
    requires_approval: bool = Field(..., description="Requires approval")
    active: bool = Field(..., description="Reason code active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class ApprovalResponse(BaseModel):
    """Approval response"""
    
    approval_id: str = Field(..., description="Approval ID")
    type: str = Field(..., description="Approval type")
    reference_id: str = Field(..., description="Reference ID")
    status: str = Field(..., description="Approval status")
    requested_by: str = Field(..., description="Requestor employee ID")
    approved_by: Optional[str] = Field(..., description="Approver employee ID")
    requested_at: datetime = Field(..., description="Request timestamp")
    approved_at: Optional[datetime] = Field(..., description="Approval timestamp")
    reason_code: str = Field(..., description="Reason code")
    notes: Optional[str] = Field(..., description="Approval notes")
