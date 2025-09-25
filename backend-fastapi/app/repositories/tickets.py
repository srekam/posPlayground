"""
Tickets Repository
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.repositories.base import BaseRepository
from app.models.tickets import Ticket, Redemption, TicketStatus
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class TicketRepository(BaseRepository, LoggerMixin):
    """Tickets repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "tickets")
        self.redemptions_collection = db["redemptions"]
    
    # Ticket methods
    async def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID"""
        return await self.get_by_id(ticket_id)
    
    async def get_tickets_by_store(self, store_id: str, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Get tickets by store"""
        cursor = self.collection.find({"store_id": store_id}).skip(skip).limit(limit)
        return [Ticket(**doc) async for doc in cursor]
    
    async def get_tickets_by_shift(self, shift_id: str, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Get tickets by shift"""
        cursor = self.collection.find({"shift_id": shift_id}).skip(skip).limit(limit)
        return [Ticket(**doc) async for doc in cursor]
    
    async def get_tickets_by_employee(self, employee_id: str, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Get tickets by employee"""
        cursor = self.collection.find({"employee_id": employee_id}).skip(skip).limit(limit)
        return [Ticket(**doc) async for doc in cursor]
    
    async def get_tickets_by_status(self, status: TicketStatus, store_id: str, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Get tickets by status"""
        cursor = self.collection.find({"status": status.value, "store_id": store_id}).skip(skip).limit(limit)
        return [Ticket(**doc) async for doc in cursor]
    
    async def create_ticket(self, ticket: Ticket) -> Ticket:
        """Create a new ticket"""
        return await self.create(ticket)
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Optional[Ticket]:
        """Update ticket"""
        return await self.update_by_id(ticket_id, updates)
    
    async def delete_ticket(self, ticket_id: str) -> bool:
        """Delete ticket"""
        return await self.delete_by_id(ticket_id)
    
    # Redemption methods
    async def get_redemptions_by_ticket(self, ticket_id: str) -> List[Redemption]:
        """Get redemptions by ticket ID"""
        cursor = self.redemptions_collection.find({"ticket_id": ticket_id})
        return [Redemption(**doc) async for doc in cursor]
    
    async def create_redemption(self, redemption: Redemption) -> Redemption:
        """Create a new redemption"""
        doc = await self.redemptions_collection.insert_one(redemption.dict())
        redemption.id = doc.inserted_id
        return redemption
    
    async def update_redemption(self, redemption_id: str, updates: Dict[str, Any]) -> Optional[Redemption]:
        """Update redemption"""
        result = await self.redemptions_collection.update_one(
            {"_id": redemption_id},
            {"$set": updates}
        )
        if result.modified_count:
            doc = await self.redemptions_collection.find_one({"_id": redemption_id})
            return Redemption(**doc) if doc else None
        return None
    
    async def delete_redemption(self, redemption_id: str) -> bool:
        """Delete redemption"""
        result = await self.redemptions_collection.delete_one({"_id": redemption_id})
        return result.deleted_count > 0
    
    # Analytics methods
    async def get_tickets_summary(self, store_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get tickets summary for a date range"""
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
                    "total_tickets": {"$sum": 1},
                    "total_amount": {"$sum": "$total_amount"},
                    "open_tickets": {
                        "$sum": {"$cond": [{"$eq": ["$status", "open"]}, 1, 0]}
                    },
                    "closed_tickets": {
                        "$sum": {"$cond": [{"$eq": ["$status", "closed"]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_tickets": 0,
            "total_amount": 0,
            "open_tickets": 0,
            "closed_tickets": 0
        }
    
    async def get_tickets_by_hour(self, store_id: str, date: str) -> List[Dict[str, Any]]:
        """Get ticket count by hour for a specific date"""
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
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$total_amount"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        return await self.collection.aggregate(pipeline).to_list(24)
