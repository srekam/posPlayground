"""
Sales Repository
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.repositories.base import BaseRepository
from app.models.sales import Sale, SaleItem, Refund, Reprint
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class SalesRepository(BaseRepository, LoggerMixin):
    """Sales repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "sales")
        self.sale_items_collection = db["sale_items"]
        self.refunds_collection = db["refunds"]
        self.reprints_collection = db["reprints"]
    
    # Sale methods
    async def get_sale_by_id(self, sale_id: str) -> Optional[Sale]:
        """Get sale by ID"""
        return await self.get_by_id(sale_id)
    
    async def get_sales_by_store(self, store_id: str, skip: int = 0, limit: int = 100) -> List[Sale]:
        """Get sales by store"""
        cursor = self.collection.find({"store_id": store_id}).skip(skip).limit(limit)
        return [Sale(**doc) async for doc in cursor]
    
    async def get_sales_by_shift(self, shift_id: str, skip: int = 0, limit: int = 100) -> List[Sale]:
        """Get sales by shift"""
        cursor = self.collection.find({"shift_id": shift_id}).skip(skip).limit(limit)
        return [Sale(**doc) async for doc in cursor]
    
    async def get_sales_by_employee(self, employee_id: str, skip: int = 0, limit: int = 100) -> List[Sale]:
        """Get sales by employee"""
        cursor = self.collection.find({"employee_id": employee_id}).skip(skip).limit(limit)
        return [Sale(**doc) async for doc in cursor]
    
    async def create_sale(self, sale: Sale) -> Sale:
        """Create a new sale"""
        return await self.create(sale)
    
    async def update_sale(self, sale_id: str, updates: Dict[str, Any]) -> Optional[Sale]:
        """Update sale"""
        return await self.update_by_id(sale_id, updates)
    
    async def delete_sale(self, sale_id: str) -> bool:
        """Delete sale"""
        return await self.delete_by_id(sale_id)
    
    # Sale Item methods
    async def get_sale_items_by_sale(self, sale_id: str) -> List[SaleItem]:
        """Get sale items by sale ID"""
        cursor = self.sale_items_collection.find({"sale_id": sale_id})
        return [SaleItem(**doc) async for doc in cursor]
    
    async def create_sale_item(self, sale_item: SaleItem) -> SaleItem:
        """Create a new sale item"""
        doc = await self.sale_items_collection.insert_one(sale_item.dict())
        sale_item.id = doc.inserted_id
        return sale_item
    
    # Refund methods
    async def get_refunds_by_sale(self, sale_id: str) -> List[Refund]:
        """Get refunds by sale ID"""
        cursor = self.refunds_collection.find({"sale_id": sale_id})
        return [Refund(**doc) async for doc in cursor]
    
    async def create_refund(self, refund: Refund) -> Refund:
        """Create a new refund"""
        doc = await self.refunds_collection.insert_one(refund.dict())
        refund.id = doc.inserted_id
        return refund
    
    # Reprint methods
    async def get_reprints_by_ticket(self, ticket_id: str) -> List[Reprint]:
        """Get reprints by ticket ID"""
        cursor = self.reprints_collection.find({"ticket_id": ticket_id})
        return [Reprint(**doc) async for doc in cursor]
    
    async def create_reprint(self, reprint: Reprint) -> Reprint:
        """Create a new reprint"""
        doc = await self.reprints_collection.insert_one(reprint.dict())
        reprint.id = doc.inserted_id
        return reprint
    
    # Analytics methods
    async def get_sales_summary(self, store_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get sales summary for a date range"""
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
                    "total_sales": {"$sum": "$total_amount"},
                    "total_items": {"$sum": "$total_items"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {"total_sales": 0, "total_items": 0, "count": 0}
    
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
        
        return await self.collection.aggregate(pipeline).to_list(limit)
