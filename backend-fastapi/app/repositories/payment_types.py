"""
Payment Type Repository
"""
from typing import List, Optional

from .base import BaseRepository
from app.models.payment_types import PaymentType


class PaymentTypeRepository(BaseRepository[PaymentType]):
    """Payment type repository"""
    
    def __init__(self):
        super().__init__("payment_types", PaymentType)
    
    async def get_active_by_tenant(self, tenant_id: str) -> List[PaymentType]:
        """Get active payment types by tenant"""
        return await self.get_many({"tenant_id": tenant_id, "active": True})
    
    async def get_by_code(self, tenant_id: str, code: str) -> Optional[PaymentType]:
        """Get payment type by code"""
        query = {"tenant_id": tenant_id, "code": code}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def get_by_method(self, tenant_id: str, method: str) -> List[PaymentType]:
        """Get payment types by method"""
        return await self.get_many({"tenant_id": tenant_id, "method": method, "active": True})
    
    async def deactivate(self, payment_type_id: str) -> Optional[PaymentType]:
        """Deactivate payment type"""
        return await self.update_by_id(payment_type_id, {"active": False})
    
    async def activate(self, payment_type_id: str) -> Optional[PaymentType]:
        """Activate payment type"""
        return await self.update_by_id(payment_type_id, {"active": True})
