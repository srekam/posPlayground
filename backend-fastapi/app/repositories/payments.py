"""
Payment Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from .base import BaseRepository
from app.models.payments import Payment


class PaymentRepository(BaseRepository[Payment]):
    """Payment repository"""
    
    def __init__(self):
        super().__init__("payments", Payment)
    
    async def get_by_sale_id(self, sale_id: str) -> List[Payment]:
        """Get payments by sale ID"""
        return await self.get_many({"sale_id": sale_id})
    
    async def get_by_store_and_date_range(
        self,
        store_id: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """Get payments by store and date range"""
        query = {
            "store_id": store_id,
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("created_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_by_status_and_date(
        self,
        status: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """Get payments by status and date range"""
        query = {
            "status": status,
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("created_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def update_status(
        self,
        payment_id: str,
        status: str,
        txn_ref: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Optional[Payment]:
        """Update payment status"""
        update_data = {"status": status}
        if txn_ref:
            update_data["txn_ref"] = txn_ref
        if meta:
            update_data["meta"] = meta
        
        return await self.update_by_id(payment_id, update_data, "payment_id")
    
    async def get_payment_summary(
        self,
        store_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get payment summary for date range"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$method",
                    "total_amount": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "succeeded_count": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "succeeded"]}, 1, 0]
                        }
                    },
                    "failed_count": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "failed"]}, 1, 0]
                        }
                    }
                }
            }
        ]
        
        results = await self.aggregate(pipeline)
        return {
            "summary": results,
            "total_payments": sum(r["count"] for r in results),
            "total_amount": sum(r["total_amount"] for r in results)
        }
