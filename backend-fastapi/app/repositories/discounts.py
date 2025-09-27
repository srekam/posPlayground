"""
Discount Repository
"""
from typing import List, Optional

from .base import BaseRepository
from app.models.discounts import Discount


class DiscountRepository(BaseRepository[Discount]):
    """Discount repository"""
    
    def __init__(self):
        super().__init__("discounts", Discount)
    
    async def get_active_by_tenant(self, tenant_id: str) -> List[Discount]:
        """Get active discounts by tenant"""
        return await self.get_many({"tenant_id": tenant_id, "active": True})
    
    async def get_by_code(self, tenant_id: str, code: str) -> Optional[Discount]:
        """Get discount by code"""
        query = {"tenant_id": tenant_id, "code": code}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def get_by_scope(
        self,
        tenant_id: str,
        scope: str,
        scope_ids: Optional[List[str]] = None
    ) -> List[Discount]:
        """Get discounts by scope"""
        query = {"tenant_id": tenant_id, "scope": scope, "active": True}
        if scope_ids:
            query["scope_ids"] = {"$in": scope_ids}
        
        return await self.get_many(query)
    
    async def deactivate(self, discount_id: str) -> Optional[Discount]:
        """Deactivate discount"""
        return await self.update_by_id(discount_id, {"active": False})
    
    async def activate(self, discount_id: str) -> Optional[Discount]:
        """Activate discount"""
        return await self.update_by_id(discount_id, {"active": True})
    
    async def validate_discount(
        self,
        tenant_id: str,
        discount_code: str,
        amount: int,
        items: List[dict]
    ) -> Optional[Discount]:
        """Validate discount application"""
        discount = await self.get_by_code(tenant_id, discount_code)
        if not discount or not discount.active:
            return None
        
        # Check minimum amount
        if discount.min_amount and amount < discount.min_amount:
            return None
        
        # Check maximum amount
        if discount.max_amount and amount > discount.max_amount:
            return None
        
        # Check scope-specific validation
        if discount.scope != "global":
            item_ids = [item.get("package_id") or item.get("product_id") for item in items]
            if not any(item_id in discount.scope_ids for item_id in item_ids):
                return None
        
        return discount
