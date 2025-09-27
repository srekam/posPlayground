"""
Pairing Log Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.pairing_logs import PairingLog


class PairingLogRepository(BaseRepository[PairingLog]):
    """Pairing log repository"""
    
    def __init__(self):
        super().__init__("pairing_logs", PairingLog)
    
    async def log_pairing_action(
        self,
        pairing_id: str,
        tenant_id: str,
        store_id: str,
        device_id: str,
        user_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> PairingLog:
        """Log pairing action"""
        now = datetime.utcnow()
        log_data = {
            "pairing_id": pairing_id,
            "tenant_id": tenant_id,
            "store_id": store_id,
            "device_id": device_id,
            "user_id": user_id,
            "action": action,
            "used_at": now,
            "details": details or {},
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(log_data)
        log_data["_id"] = result.inserted_id
        return PairingLog(**log_data)
    
    async def get_pairing_logs(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        store_id: Optional[str] = None,
        device_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PairingLog]:
        """Get pairing logs with filters"""
        query = {}
        
        if store_id:
            query["store_id"] = store_id
        if device_id:
            query["device_id"] = device_id
        
        if from_date or to_date:
            query["used_at"] = {}
            if from_date:
                from_dt = datetime.fromisoformat(from_date)
                query["used_at"]["$gte"] = from_dt
            if to_date:
                to_dt = datetime.fromisoformat(to_date)
                query["used_at"]["$lte"] = to_dt
        
        sort = [("used_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_device_pairing_history(
        self,
        device_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[PairingLog]:
        """Get device pairing history"""
        query = {"device_id": device_id}
        sort = [("used_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_store_pairing_summary(
        self,
        store_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get pairing summary for store"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "used_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                    "unique_devices": {"$addToSet": "$device_id"},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        
        summary = {
            "store_id": store_id,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_actions": 0,
            "action_breakdown": {},
            "unique_devices": set(),
            "unique_users": set()
        }
        
        for result in results:
            action = result["_id"]
            count = result["count"]
            summary["total_actions"] += count
            summary["action_breakdown"][action] = count
            summary["unique_devices"].update(result["unique_devices"])
            summary["unique_users"].update(result["unique_users"])
        
        summary["unique_devices"] = len(summary["unique_devices"])
        summary["unique_users"] = len(summary["unique_users"])
        
        return summary
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Clean up old pairing logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = {"used_at": {"$lt": cutoff_date}}
        
        result = await self.collection.delete_many(query)
        return result.deleted_count
