"""
Usage Counter Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.usage_counters import UsageCounter


class UsageCounterRepository(BaseRepository[UsageCounter]):
    """Usage counter repository"""
    
    def __init__(self):
        super().__init__("usage_counters", UsageCounter)
    
    async def increment_usage(
        self,
        tenant_id: str,
        route: str,
        method: str,
        period: str
    ) -> UsageCounter:
        """Increment usage counter"""
        query = {
            "tenant_id": tenant_id,
            "route": route,
            "method": method,
            "period": period
        }
        
        # Try to find existing counter
        existing = await self.get_many(query, limit=1)
        
        if existing:
            # Update existing counter
            counter = existing[0]
            update_data = {
                "count": counter.count + 1,
                "last_reset": datetime.utcnow()
            }
            return await self.update_by_id(counter.id, update_data)
        else:
            # Create new counter
            now = datetime.utcnow()
            counter_data = {
                "tenant_id": tenant_id,
                "route": route,
                "method": method,
                "period": period,
                "count": 1,
                "last_reset": now,
                "meta": {},
                "created_at": now,
                "updated_at": now
            }
            
            result = await self.collection.insert_one(counter_data)
            counter_data["_id"] = result.inserted_id
            return UsageCounter(**counter_data)
    
    async def get_tenant_usage(
        self,
        tenant_id: str,
        period: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UsageCounter]:
        """Get usage counters for tenant and period"""
        query = {"tenant_id": tenant_id, "period": period}
        sort = [("count", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_usage_summary(
        self,
        tenant_id: str,
        from_date: str,
        to_date: str
    ) -> Dict[str, Any]:
        """Get usage summary for date range"""
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "period": {
                        "$gte": from_date,
                        "$lte": to_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$route",
                    "total_requests": {"$sum": "$count"},
                    "methods": {"$addToSet": "$method"}
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        
        route_usage = {}
        total_requests = 0
        
        for result in results:
            route = result["_id"]
            count = result["total_requests"]
            route_usage[route] = count
            total_requests += count
        
        return {
            "tenant_id": tenant_id,
            "period": f"{from_date} to {to_date}",
            "total_requests": total_requests,
            "route_usage": route_usage,
            "generated_at": datetime.utcnow()
        }
    
    async def cleanup_old_counters(self, days: int = 90) -> int:
        """Clean up old usage counters"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_period = cutoff_date.strftime("%Y-%m")
        
        query = {"period": {"$lt": cutoff_period}}
        result = await self.collection.delete_many(query)
        return result.deleted_count
    
    async def reset_period_counters(self, period: str) -> int:
        """Reset counters for a specific period"""
        query = {"period": period}
        update_data = {"count": 0, "last_reset": datetime.utcnow()}
        
        result = await self.collection.update_many(query, {"$set": update_data})
        return result.modified_count
