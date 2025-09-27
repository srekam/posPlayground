"""
Approval Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BaseRepository
from app.models.approvals import ReasonCode, Approval


class ReasonCodeRepository(BaseRepository[ReasonCode]):
    """Reason code repository"""
    
    def __init__(self):
        super().__init__("reason_codes", ReasonCode)
    
    async def get_by_tenant(self, tenant_id: str) -> List[ReasonCode]:
        """Get reason codes by tenant"""
        return await self.get_many({"tenant_id": tenant_id, "active": True})
    
    async def get_by_category(self, tenant_id: str, category: str) -> List[ReasonCode]:
        """Get reason codes by category"""
        return await self.get_many({
            "tenant_id": tenant_id,
            "category": category,
            "active": True
        })
    
    async def get_by_code(self, tenant_id: str, code: str) -> Optional[ReasonCode]:
        """Get reason code by code"""
        query = {"tenant_id": tenant_id, "code": code}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def deactivate(self, reason_code_id: str) -> Optional[ReasonCode]:
        """Deactivate reason code"""
        return await self.update_by_id(reason_code_id, {"active": False})
    
    async def activate(self, reason_code_id: str) -> Optional[ReasonCode]:
        """Activate reason code"""
        return await self.update_by_id(reason_code_id, {"active": True})


class ApprovalRepository(BaseRepository[Approval]):
    """Approval repository"""
    
    def __init__(self):
        super().__init__("approvals", Approval)
    
    async def get_pending_by_store(
        self,
        store_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Approval]:
        """Get pending approvals by store"""
        query = {"store_id": store_id, "status": "pending"}
        sort = [("requested_at", 1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_by_reference(
        self,
        reference_id: str,
        approval_type: str
    ) -> List[Approval]:
        """Get approvals by reference ID and type"""
        query = {"reference_id": reference_id, "type": approval_type}
        sort = [("requested_at", -1)]
        return await self.get_many(query, sort=sort)
    
    async def get_by_employee(
        self,
        employee_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Approval]:
        """Get approvals by employee"""
        query = {"$or": [
            {"requested_by": employee_id},
            {"approved_by": employee_id}
        ]}
        sort = [("requested_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def verify_pin(
        self,
        pin: str,
        reference_id: str,
        approval_type: str
    ) -> Optional[Approval]:
        """Verify approval PIN"""
        # This would typically hash the PIN and compare with stored hash
        # For now, we'll do a simple comparison as a placeholder
        
        query = {
            "reference_id": reference_id,
            "type": approval_type,
            "status": "pending"
        }
        
        approvals = await self.get_many(query, limit=1)
        if not approvals:
            return None
        
        approval = approvals[0]
        
        # Simple PIN verification (in production, use proper hashing)
        if approval.pin == pin:
            # Update approval status
            now = datetime.utcnow()
            update_data = {
                "status": "approved",
                "approved_at": now
            }
            
            return await self.update_by_id(approval.id, update_data)
        
        return None
    
    async def approve(
        self,
        approval_id: str,
        approved_by: str,
        notes: Optional[str] = None
    ) -> Optional[Approval]:
        """Approve an approval request"""
        now = datetime.utcnow()
        update_data = {
            "status": "approved",
            "approved_by": approved_by,
            "approved_at": now,
            "notes": notes
        }
        
        return await self.update_by_id(approval_id, update_data)
    
    async def reject(
        self,
        approval_id: str,
        rejected_by: str,
        notes: Optional[str] = None
    ) -> Optional[Approval]:
        """Reject an approval request"""
        now = datetime.utcnow()
        update_data = {
            "status": "rejected",
            "approved_by": rejected_by,
            "approved_at": now,
            "notes": notes
        }
        
        return await self.update_by_id(approval_id, update_data)
    
    async def create_approval_request(
        self,
        approval_id: str,
        tenant_id: str,
        store_id: str,
        approval_type: str,
        reference_id: str,
        requested_by: str,
        pin: str,
        reason_code: str,
        notes: Optional[str] = None
    ) -> Approval:
        """Create approval request"""
        now = datetime.utcnow()
        approval_data = {
            "approval_id": approval_id,
            "tenant_id": tenant_id,
            "store_id": store_id,
            "type": approval_type,
            "reference_id": reference_id,
            "requested_by": requested_by,
            "pin": pin,  # In production, hash this
            "status": "pending",
            "requested_at": now,
            "reason_code": reason_code,
            "notes": notes,
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(approval_data)
        approval_data["_id"] = result.inserted_id
        return Approval(**approval_data)
