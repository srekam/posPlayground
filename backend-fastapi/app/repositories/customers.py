"""
Customer Repository
"""
from typing import List, Optional
from datetime import datetime

from .base import BaseRepository
from app.models.customers import Customer


class CustomerRepository(BaseRepository[Customer]):
    """Customer repository"""
    
    def __init__(self):
        super().__init__("customers", Customer)
    
    async def get_by_phone(self, tenant_id: str, phone: str) -> Optional[Customer]:
        """Get customer by phone"""
        query = {"tenant_id": tenant_id, "phone": phone}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def get_by_email(self, tenant_id: str, email: str) -> Optional[Customer]:
        """Get customer by email"""
        query = {"tenant_id": tenant_id, "email": email}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def search_customers(
        self,
        tenant_id: str,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Customer]:
        """Search customers by name, phone, or email"""
        search_query = {
            "tenant_id": tenant_id,
            "active": True,
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"phone": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]
        }
        
        sort = [("name", 1)]
        return await self.get_many(search_query, skip=skip, limit=limit, sort=sort)
    
    async def get_active_customers(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get active customers"""
        query = {"tenant_id": tenant_id, "active": True}
        sort = [("name", 1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def update_loyalty_points(
        self,
        customer_id: str,
        points: int,
        operation: str = "add"
    ) -> Optional[Customer]:
        """Update customer loyalty points"""
        customer = await self.get_by_field("customer_id", customer_id)
        if not customer:
            return None
        
        if operation == "add":
            new_points = customer.loyalty_points + points
        elif operation == "subtract":
            new_points = max(0, customer.loyalty_points - points)
        else:
            new_points = points
        
        return await self.update_by_id(customer_id, {"loyalty_points": new_points}, "customer_id")
    
    async def update_spending(
        self,
        customer_id: str,
        amount: int,
        operation: str = "add"
    ) -> Optional[Customer]:
        """Update customer spending"""
        customer = await self.get_by_field("customer_id", customer_id)
        if not customer:
            return None
        
        if operation == "add":
            new_total = customer.total_spent + amount
            new_visits = customer.visit_count + 1
        else:
            new_total = max(0, customer.total_spent - amount)
            new_visits = customer.visit_count
        
        update_data = {
            "total_spent": new_total,
            "visit_count": new_visits,
            "last_visit": datetime.utcnow()
        }
        
        return await self.update_by_id(customer_id, update_data, "customer_id")
    
    async def deactivate(self, customer_id: str) -> Optional[Customer]:
        """Deactivate customer"""
        return await self.update_by_id(customer_id, {"active": False}, "customer_id")
    
    async def activate(self, customer_id: str) -> Optional[Customer]:
        """Activate customer"""
        return await self.update_by_id(customer_id, {"active": True}, "customer_id")
    
    async def get_top_customers(
        self,
        tenant_id: str,
        limit: int = 10
    ) -> List[Customer]:
        """Get top customers by spending"""
        query = {"tenant_id": tenant_id, "active": True}
        sort = [("total_spent", -1)]
        return await self.get_many(query, limit=limit, sort=sort)
