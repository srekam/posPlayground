"""
Tax Repository
"""
from typing import List, Optional

from .base import BaseRepository
from app.models.taxes import Tax


class TaxRepository(BaseRepository[Tax]):
    """Tax repository"""
    
    def __init__(self):
        super().__init__("taxes", Tax)
    
    async def get_active_by_tenant(self, tenant_id: str) -> List[Tax]:
        """Get active taxes by tenant"""
        return await self.get_many({"tenant_id": tenant_id, "active": True})
    
    async def get_by_code(self, tenant_id: str, code: str) -> Optional[Tax]:
        """Get tax by code"""
        return await self.get_by_field("code", code)
    
    async def deactivate(self, tax_id: str) -> Optional[Tax]:
        """Deactivate tax"""
        return await self.update_by_id(tax_id, {"active": False})
    
    async def activate(self, tax_id: str) -> Optional[Tax]:
        """Activate tax"""
        return await self.update_by_id(tax_id, {"active": True})
