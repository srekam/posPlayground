"""
Open Ticket Repository
"""
from typing import List, Optional
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.open_tickets import OpenTicket


class OpenTicketRepository(BaseRepository[OpenTicket]):
    """Open ticket repository"""
    
    def __init__(self):
        super().__init__("open_tickets", OpenTicket)
    
    async def get_active_by_store(
        self,
        store_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OpenTicket]:
        """Get active open tickets by store"""
        query = {"store_id": store_id, "status": "active"}
        sort = [("created_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_active_by_device(
        self,
        device_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OpenTicket]:
        """Get active open tickets by device"""
        query = {"device_id": device_id, "status": "active"}
        sort = [("created_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_active_by_cashier(
        self,
        cashier_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OpenTicket]:
        """Get active open tickets by cashier"""
        query = {"cashier_id": cashier_id, "status": "active"}
        sort = [("created_at", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_expired_tickets(self, limit: int = 100) -> List[OpenTicket]:
        """Get expired open tickets"""
        now = datetime.utcnow()
        query = {
            "status": "active",
            "expires_at": {"$lt": now}
        }
        sort = [("expires_at", 1)]
        return await self.get_many(query, limit=limit, sort=sort)
    
    async def mark_as_checked_out(self, open_ticket_id: str) -> Optional[OpenTicket]:
        """Mark open ticket as checked out"""
        return await self.update_by_id(open_ticket_id, {"status": "checked_out"}, "open_ticket_id")
    
    async def mark_as_expired(self, open_ticket_id: str) -> Optional[OpenTicket]:
        """Mark open ticket as expired"""
        return await self.update_by_id(open_ticket_id, {"status": "expired"}, "open_ticket_id")
    
    async def cancel(self, open_ticket_id: str) -> Optional[OpenTicket]:
        """Cancel open ticket"""
        return await self.update_by_id(open_ticket_id, {"status": "cancelled"}, "open_ticket_id")
    
    async def cleanup_expired_tickets(self) -> int:
        """Clean up expired tickets"""
        now = datetime.utcnow()
        query = {
            "status": "active",
            "expires_at": {"$lt": now}
        }
        
        result = await self.collection.update_many(
            query,
            {"$set": {"status": "expired", "updated_at": now}}
        )
        
        return result.modified_count
