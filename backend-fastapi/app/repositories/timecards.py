"""
Timecard Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.timecards import Timecard


class TimecardRepository(BaseRepository[Timecard]):
    """Timecard repository"""
    
    def __init__(self):
        super().__init__("timecards", Timecard)
    
    async def get_active_by_employee(self, employee_id: str) -> Optional[Timecard]:
        """Get active timecard by employee"""
        query = {
            "employee_id": employee_id,
            "status": {"$in": ["clocked_in", "break"]}
        }
        sort = [("clock_in", -1)]
        results = await self.get_many(query, limit=1, sort=sort)
        return results[0] if results else None
    
    async def get_by_employee_and_date_range(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Timecard]:
        """Get timecards by employee and date range"""
        query = {
            "employee_id": employee_id,
            "clock_in": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("clock_in", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_by_store_and_date_range(
        self,
        store_id: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Timecard]:
        """Get timecards by store and date range"""
        query = {
            "store_id": store_id,
            "clock_in": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("clock_in", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def clock_in(
        self,
        timecard_id: str,
        employee_id: str,
        tenant_id: str,
        store_id: str,
        notes: Optional[str] = None
    ) -> Timecard:
        """Clock in employee"""
        now = datetime.utcnow()
        
        # Check for overlapping timecards
        overlap_query = {
            "employee_id": employee_id,
            "clock_in": {"$lte": now},
            "$or": [
                {"clock_out": None},
                {"clock_out": {"$gte": now}}
            ]
        }
        
        existing = await self.get_many(overlap_query, limit=1)
        if existing:
            raise ValueError("Employee already has an active timecard")
        
        timecard_data = {
            "timecard_id": timecard_id,
            "employee_id": employee_id,
            "tenant_id": tenant_id,
            "store_id": store_id,
            "clock_in": now,
            "status": "clocked_in",
            "notes": notes,
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(timecard_data)
        timecard_data["_id"] = result.inserted_id
        return Timecard(**timecard_data)
    
    async def clock_out(
        self,
        timecard_id: str,
        notes: Optional[str] = None
    ) -> Optional[Timecard]:
        """Clock out employee"""
        now = datetime.utcnow()
        
        timecard = await self.get_by_field("timecard_id", timecard_id)
        if not timecard:
            return None
        
        # Calculate total work time
        total_break_time = timecard.total_break_time
        work_duration = now - timecard.clock_in
        total_work_time = int(work_duration.total_seconds() / 60) - total_break_time
        
        update_data = {
            "clock_out": now,
            "status": "clocked_out",
            "total_work_time": total_work_time,
            "notes": notes
        }
        
        return await self.update_by_id(timecard_id, update_data, "timecard_id")
    
    async def start_break(
        self,
        timecard_id: str,
        break_type: str = "break",
        notes: Optional[str] = None
    ) -> Optional[Timecard]:
        """Start break"""
        now = datetime.utcnow()
        update_data = {
            "break_start": now,
            "status": "break",
            "notes": notes
        }
        
        return await self.update_by_id(timecard_id, update_data, "timecard_id")
    
    async def end_break(
        self,
        timecard_id: str,
        notes: Optional[str] = None
    ) -> Optional[Timecard]:
        """End break"""
        now = datetime.utcnow()
        
        timecard = await self.get_by_field("timecard_id", timecard_id)
        if not timecard or not timecard.break_start:
            return None
        
        # Calculate break duration and add to total
        break_duration = now - timecard.break_start
        break_minutes = int(break_duration.total_seconds() / 60)
        total_break_time = timecard.total_break_time + break_minutes
        
        update_data = {
            "break_end": now,
            "status": "clocked_in",
            "total_break_time": total_break_time,
            "notes": notes
        }
        
        return await self.update_by_id(timecard_id, update_data, "timecard_id")
    
    async def get_employee_summary(
        self,
        employee_id: str,
        date: datetime
    ) -> Dict[str, Any]:
        """Get employee timecard summary for a date"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        timecards = await self.get_by_employee_and_date_range(
            employee_id, start_of_day, end_of_day
        )
        
        if not timecards:
            return {
                "employee_id": employee_id,
                "date": date.strftime("%Y-%m-%d"),
                "total_work_time": 0,
                "total_break_time": 0,
                "status": "not_clocked_in"
            }
        
        # Get the most recent timecard for the day
        latest_timecard = timecards[0]
        
        total_work_time = latest_timecard.total_work_time or 0
        total_break_time = latest_timecard.total_break_time
        
        return {
            "employee_id": employee_id,
            "date": date.strftime("%Y-%m-%d"),
            "clock_in": latest_timecard.clock_in,
            "clock_out": latest_timecard.clock_out,
            "total_work_time": total_work_time,
            "total_break_time": total_break_time,
            "status": latest_timecard.status
        }
