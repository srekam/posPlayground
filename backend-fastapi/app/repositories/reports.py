"""
Reports Repository
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.repositories.base import BaseRepository
from app.models.audit import AuditLog, EventType
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class ReportRepository(BaseRepository, LoggerMixin):
    """Reports repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "audit_logs")
        self.sales_collection = db["sales"]
        self.tickets_collection = db["tickets"]
        self.shifts_collection = db["shifts"]
        self.products_collection = db["products"]
    
    # Audit Log methods
    async def get_audit_log_by_id(self, audit_id: str) -> Optional[AuditLog]:
        """Get audit log by ID"""
        return await self.get_by_id(audit_id)
    
    async def get_audit_logs_by_store(self, store_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by store"""
        cursor = self.collection.find({"store_id": store_id}).skip(skip).limit(limit)
        return [AuditLog(**doc) async for doc in cursor]
    
    async def get_audit_logs_by_employee(self, employee_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by employee"""
        cursor = self.collection.find({"employee_id": employee_id}).skip(skip).limit(limit)
        return [AuditLog(**doc) async for doc in cursor]
    
    async def get_audit_logs_by_event_type(self, event_type: EventType, store_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by event type"""
        cursor = self.collection.find({"event_type": event_type.value, "store_id": store_id}).skip(skip).limit(limit)
        return [AuditLog(**doc) async for doc in cursor]
    
    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        """Create a new audit log"""
        return await self.create(audit_log)
    
    # Sales Reports
    async def get_sales_report(self, store_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get sales report"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_sales": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "total_items": {"$sum": "$total_items"},
                    "avg_sale_amount": {"$avg": "$total_amount"},
                    "max_sale_amount": {"$max": "$total_amount"},
                    "min_sale_amount": {"$min": "$total_amount"}
                }
            }
        ]
        
        result = await self.sales_collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_sales": 0,
            "total_revenue": 0,
            "total_items": 0,
            "avg_sale_amount": 0,
            "max_sale_amount": 0,
            "min_sale_amount": 0
        }
    
    async def get_sales_by_hour(self, store_id: str, date: str) -> List[Dict[str, Any]]:
        """Get sales by hour"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "created_at": {"$gte": f"{date}T00:00:00", "$lte": f"{date}T23:59:59"}
                }
            },
            {
                "$group": {
                    "_id": {"$hour": "$created_at"},
                    "sales_count": {"$sum": 1},
                    "revenue": {"$sum": "$total_amount"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        return await self.sales_collection.aggregate(pipeline).to_list(24)
    
    async def get_top_products(self, store_id: str, start_date: str, end_date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$lookup": {
                    "from": "sale_items",
                    "localField": "_id",
                    "foreignField": "sale_id",
                    "as": "items"
                }
            },
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product_id",
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.unit_price"]}}
                }
            },
            {"$sort": {"total_quantity": -1}},
            {"$limit": limit}
        ]
        
        return await self.sales_collection.aggregate(pipeline).to_list(limit)
    
    # Employee Performance Reports
    async def get_employee_performance(self, store_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get employee performance report"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$employee_id",
                    "total_sales": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_sale_amount": {"$avg": "$total_amount"}
                }
            },
            {"$sort": {"total_revenue": -1}}
        ]
        
        return await self.sales_collection.aggregate(pipeline).to_list(100)
    
    # Inventory Reports
    async def get_low_stock_products(self, store_id: str, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get products with low stock"""
        cursor = self.products_collection.find({
            "store_id": store_id,
            "stock_quantity": {"$lte": threshold}
        })
        return [doc async for doc in cursor]
    
    async def get_inventory_value(self, store_id: str) -> Dict[str, Any]:
        """Get total inventory value"""
        pipeline = [
            {"$match": {"store_id": store_id}},
            {
                "$group": {
                    "_id": None,
                    "total_products": {"$sum": 1},
                    "total_value": {"$sum": {"$multiply": ["$stock_quantity", "$price"]}},
                    "low_stock_count": {
                        "$sum": {"$cond": [{"$lte": ["$stock_quantity", 10]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await self.products_collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_products": 0,
            "total_value": 0,
            "low_stock_count": 0
        }
    
    # Shift Reports
    async def get_shift_summary(self, store_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get shift summary report"""
        pipeline = [
            {
                "$match": {
                    "store_id": store_id,
                    "start_time": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_shifts": {"$sum": 1},
                    "total_hours": {"$sum": "$duration_hours"},
                    "avg_duration": {"$avg": "$duration_hours"}
                }
            }
        ]
        
        result = await self.shifts_collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_shifts": 0,
            "total_hours": 0,
            "avg_duration": 0
        }
