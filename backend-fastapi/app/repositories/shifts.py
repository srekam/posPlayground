"""
Shifts Repository
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.repositories.base import BaseRepository
from app.models.shifts import Shift, ShiftStatus
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class ShiftRepository(BaseRepository, LoggerMixin):
    """Shifts repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "shifts")
    
    # Shift methods
    async def get_shift_by_id(self, shift_id: str) -> Optional[Shift]:
        """Get shift by ID"""
        return await self.get_by_id(shift_id)
    
    async def get_shifts_by_store(self, store_id: str, skip: int = 0, limit: int = 100) -> List[Shift]:
        """Get shifts by store"""
        cursor = self.collection.find({"store_id": store_id}).skip(skip).limit(limit)
        return [Shift(**doc) async for doc in cursor]
    
    async def get_shifts_by_employee(self, employee_id: str, skip: int = 0, limit: int = 100) -> List[Shift]:
        """Get shifts by employee"""
        cursor = self.collection.find({"employee_id": employee_id}).skip(skip).limit(limit)
        return [Shift(**doc) async for doc in cursor]
    
    async def get_active_shift_by_employee(self, employee_id: str) -> Optional[Shift]:
        """Get active shift for employee"""
        doc = await self.collection.find_one({
            "employee_id": employee_id,
            "status": ShiftStatus.ACTIVE.value
        })
        return Shift(**doc) if doc else None
    
    async def get_shifts_by_status(self, status: ShiftStatus, store_id: str, skip: int = 0, limit: int = 100) -> List[Shift]:
        """Get shifts by status"""
        cursor = self.collection.find({"status": status.value, "store_id": store_id}).skip(skip).limit(limit)
        return [Shift(**doc) async for doc in cursor]
    
    async def get_shifts_by_date_range(self, store_id: str, start_date: str, end_date: str) -> List[Shift]:
        """Get shifts by date range"""
        cursor = self.collection.find({
            "store_id": store_id,
            "start_time": {"$gte": start_date, "$lte": end_date}
        })
        return [Shift(**doc) async for doc in cursor]
    
    async def create_shift(self, shift: Shift) -> Shift:
        """Create a new shift"""
        return await self.create(shift)
    
    async def update_shift(self, shift_id: str, updates: Dict[str, Any]) -> Optional[Shift]:
        """Update shift"""
        return await self.update_by_id(shift_id, updates)
    
    async def delete_shift(self, shift_id: str) -> bool:
        """Delete shift"""
        return await self.delete_by_id(shift_id)
    
    # Shift management methods
    async def start_shift(self, shift_id: str, employee_id: str, store_id: str) -> Optional[Shift]:
        """Start a shift"""
        updates = {
            "status": ShiftStatus.ACTIVE.value,
            "start_time": "now()",
            "employee_id": employee_id,
            "store_id": store_id
        }
        return await self.update_by_id(shift_id, updates)
    
    async def end_shift(self, shift_id: str, end_time: str, closing_amount: float) -> Optional[Shift]:
        """End a shift"""
        updates = {
            "status": ShiftStatus.CLOSED.value,
            "end_time": end_time,
            "closing_amount": closing_amount
        }
        return await self.update_by_id(shift_id, updates)
    
    async def pause_shift(self, shift_id: str) -> Optional[Shift]:
        """Pause a shift"""
        updates = {"status": ShiftStatus.PAUSED.value}
        return await self.update_by_id(shift_id, updates)
    
    async def resume_shift(self, shift_id: str) -> Optional[Shift]:
        """Resume a shift"""
        updates = {"status": ShiftStatus.ACTIVE.value}
        return await self.update_by_id(shift_id, updates)
    
    # Analytics methods
    async def get_shift_summary(self, store_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get shift summary for a date range"""
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
                    "active_shifts": {
                        "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                    },
                    "closed_shifts": {
                        "$sum": {"$cond": [{"$eq": ["$status", "closed"]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_shifts": 0,
            "total_hours": 0,
            "active_shifts": 0,
            "closed_shifts": 0
        }
    
    async def get_employee_shift_stats(self, employee_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get employee shift statistics"""
        pipeline = [
            {
                "$match": {
                    "employee_id": employee_id,
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
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0] if result else {
            "total_shifts": 0,
            "total_hours": 0,
            "avg_duration": 0
        }
