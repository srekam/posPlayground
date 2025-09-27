"""
Redemption Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.redemptions import Redemption


class RedemptionRepository(BaseRepository[Redemption]):
    """Redemption repository"""
    
    def __init__(self):
        super().__init__("redemptions", Redemption)
    
    async def get_by_ticket_id(self, ticket_id: str) -> List[Redemption]:
        """Get redemptions by ticket ID"""
        return await self.get_many({"ticket_id": ticket_id})
    
    async def get_by_device_and_date_range(
        self,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Redemption]:
        """Get redemptions by device and date range"""
        query = {
            "device_id": device_id,
            "redeemed_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("redeemed_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_by_store_and_date_range(
        self,
        store_id: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Redemption]:
        """Get redemptions by store and date range"""
        query = {
            "store_id": store_id,
            "redeemed_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("redeemed_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_redemption_stats(
        self,
        store_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get redemption statistics"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "redeemed_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$result",
                    "count": {"$sum": 1},
                    "reasons": {
                        "$push": "$reason"
                    }
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        
        stats = {
            "total_redemptions": 0,
            "successful_redemptions": 0,
            "failed_redemptions": 0,
            "failure_reasons": {}
        }
        
        for result in results:
            count = result["count"]
            stats["total_redemptions"] += count
            
            if result["_id"] == "pass":
                stats["successful_redemptions"] += count
            else:
                stats["failed_redemptions"] += count
                
                # Count failure reasons
                for reason in result["reasons"]:
                    if reason:
                        stats["failure_reasons"][reason] = stats["failure_reasons"].get(reason, 0) + 1
        
        return stats
    
    async def check_duplicate_redemption(
        self,
        ticket_id: str,
        device_id: str,
        time_window_minutes: int = 5
    ) -> bool:
        """Check for duplicate redemption within time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        query = {
            "ticket_id": ticket_id,
            "device_id": device_id,
            "redeemed_at": {"$gte": cutoff_time},
            "result": "pass"
        }
        
        count = await self.count(query)
        return count > 0
