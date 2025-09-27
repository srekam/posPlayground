"""
Pricing Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BaseRepository
from app.models.pricing import PricingRule, PriceList, PriceListItem


class PricingRuleRepository(BaseRepository[PricingRule]):
    """Pricing rule repository"""
    
    def __init__(self):
        super().__init__("pricing_rules", PricingRule)
    
    async def get_active_by_tenant(self, tenant_id: str) -> List[PricingRule]:
        """Get active pricing rules by tenant"""
        now = datetime.utcnow()
        query = {
            "tenant_id": tenant_id,
            "active": True,
            "$or": [
                {"valid_from": {"$lte": now}, "valid_until": {"$gte": now}},
                {"valid_from": {"$lte": now}, "valid_until": None},
                {"valid_from": None, "valid_until": {"$gte": now}},
                {"valid_from": None, "valid_until": None}
            ]
        }
        sort = [("priority", -1), ("created_at", 1)]
        return await self.get_many(query, sort=sort)
    
    async def get_by_scope(
        self,
        tenant_id: str,
        scope: str,
        scope_ids: Optional[List[str]] = None
    ) -> List[PricingRule]:
        """Get pricing rules by scope"""
        query = {"tenant_id": tenant_id, "scope": scope, "active": True}
        if scope_ids:
            query["scope_ids"] = {"$in": scope_ids}
        
        sort = [("priority", -1)]
        return await self.get_many(query, sort=sort)
    
    async def deactivate(self, rule_id: str) -> Optional[PricingRule]:
        """Deactivate pricing rule"""
        return await self.update_by_id(rule_id, {"active": False})
    
    async def activate(self, rule_id: str) -> Optional[PricingRule]:
        """Activate pricing rule"""
        return await self.update_by_id(rule_id, {"active": True})


class PriceListRepository(BaseRepository[PriceList]):
    """Price list repository"""
    
    def __init__(self):
        super().__init__("price_lists", PriceList)
    
    async def get_active_by_tenant(self, tenant_id: str) -> List[PriceList]:
        """Get active price lists by tenant"""
        now = datetime.utcnow()
        query = {
            "tenant_id": tenant_id,
            "active": True,
            "$or": [
                {"valid_from": {"$lte": now}, "valid_until": {"$gte": now}},
                {"valid_from": {"$lte": now}, "valid_until": None},
                {"valid_from": None, "valid_until": {"$gte": now}},
                {"valid_from": None, "valid_until": None}
            ]
        }
        sort = [("priority", -1), ("created_at", 1)]
        return await self.get_many(query, sort=sort)
    
    async def get_by_code(self, tenant_id: str, code: str) -> Optional[PriceList]:
        """Get price list by code"""
        query = {"tenant_id": tenant_id, "code": code}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None


class PriceListItemRepository(BaseRepository[PriceListItem]):
    """Price list item repository"""
    
    def __init__(self):
        super().__init__("price_list_items", PriceListItem)
    
    async def get_by_price_list(self, price_list_id: str) -> List[PriceListItem]:
        """Get price list items by price list ID"""
        return await self.get_many({"price_list_id": price_list_id, "active": True})
    
    async def get_product_price(
        self,
        price_list_id: str,
        product_id: str,
        package_id: Optional[str] = None,
        quantity: int = 1
    ) -> Optional[PriceListItem]:
        """Get product price from price list"""
        query = {
            "price_list_id": price_list_id,
            "product_id": product_id,
            "active": True,
            "min_quantity": {"$lte": quantity}
        }
        
        if package_id:
            query["package_id"] = package_id
        
        # Sort by quantity descending to get the best price
        sort = [("min_quantity", -1)]
        items = await self.get_many(query, sort=sort, limit=1)
        
        return items[0] if items else None
    
    async def deactivate(self, item_id: str) -> Optional[PriceListItem]:
        """Deactivate price list item"""
        return await self.update_by_id(item_id, {"active": False})
    
    async def activate(self, item_id: str) -> Optional[PriceListItem]:
        """Activate price list item"""
        return await self.update_by_id(item_id, {"active": True})
