"""
Cash Drawer Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.cash_drawers import CashDrawer, CashMovement


class CashDrawerRepository(BaseRepository[CashDrawer]):
    """Cash drawer repository"""
    
    def __init__(self):
        super().__init__("cash_drawers", CashDrawer)
    
    async def get_current_by_store(self, store_id: str) -> Optional[CashDrawer]:
        """Get current open cash drawer by store"""
        query = {
            "store_id": store_id,
            "status": "open"
        }
        sort = [("opened_at", -1)]
        results = await self.get_many(query, limit=1, sort=sort)
        return results[0] if results else None
    
    async def get_current_by_device(self, device_id: str) -> Optional[CashDrawer]:
        """Get current open cash drawer by device"""
        query = {
            "device_id": device_id,
            "status": "open"
        }
        sort = [("opened_at", -1)]
        results = await self.get_many(query, limit=1, sort=sort)
        return results[0] if results else None
    
    async def open_drawer(
        self,
        drawer_id: str,
        tenant_id: str,
        store_id: str,
        device_id: str,
        employee_id: str,
        opening_amount: int,
        notes: Optional[str] = None
    ) -> CashDrawer:
        """Open cash drawer"""
        now = datetime.utcnow()
        drawer_data = {
            "drawer_id": drawer_id,
            "tenant_id": tenant_id,
            "store_id": store_id,
            "device_id": device_id,
            "employee_id": employee_id,
            "status": "open",
            "opened_at": now,
            "opening_amount": opening_amount,
            "notes": notes,
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(drawer_data)
        drawer_data["_id"] = result.inserted_id
        return CashDrawer(**drawer_data)
    
    async def close_drawer(
        self,
        drawer_id: str,
        closing_amount: int,
        notes: Optional[str] = None
    ) -> Optional[CashDrawer]:
        """Close cash drawer"""
        now = datetime.utcnow()
        update_data = {
            "status": "closed",
            "closed_at": now,
            "closing_amount": closing_amount,
            "notes": notes
        }
        
        return await self.update_by_id(drawer_id, update_data, "drawer_id")
    
    async def get_drawer_summary(
        self,
        drawer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cash drawer summary"""
        drawer = await self.get_by_field("drawer_id", drawer_id)
        if not drawer:
            return {}
        
        # Get movements for this drawer
        movement_repo = CashMovementRepository()
        movements = await movement_repo.get_by_drawer_and_date_range(
            drawer_id, start_date, end_date
        )
        
        # Calculate totals
        totals = {
            "sales": 0,
            "refunds": 0,
            "drops": 0,
            "pickups": 0,
            "adjustments": 0
        }
        
        for movement in movements:
            if movement.type == "sale":
                totals["sales"] += movement.amount
            elif movement.type == "refund":
                totals["refunds"] += movement.amount
            elif movement.type == "drop":
                totals["drops"] += movement.amount
            elif movement.type == "pickup":
                totals["pickups"] += movement.amount
            elif movement.type == "adjustment":
                totals["adjustments"] += movement.amount
        
        # Calculate expected amount
        expected_amount = drawer.opening_amount + totals["sales"] - totals["refunds"] + totals["drops"] - totals["pickups"] + totals["adjustments"]
        
        return {
            "drawer_id": drawer.drawer_id,
            "status": drawer.status,
            "opened_at": drawer.opened_at,
            "closed_at": drawer.closed_at,
            "opening_amount": drawer.opening_amount,
            "closing_amount": drawer.closing_amount,
            "expected_amount": expected_amount,
            "variance": (drawer.closing_amount or 0) - expected_amount,
            "totals": totals,
            "movement_count": len(movements),
            "reconciliation_rule": "standard"
        }


class CashMovementRepository(BaseRepository[CashMovement]):
    """Cash movement repository"""
    
    def __init__(self):
        super().__init__("cash_movements", CashMovement)
    
    async def get_by_drawer_and_date_range(
        self,
        drawer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CashMovement]:
        """Get movements by drawer and date range"""
        query = {"drawer_id": drawer_id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        sort = [("timestamp", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def get_by_type_and_date_range(
        self,
        movement_type: str,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[CashMovement]:
        """Get movements by type and date range"""
        query = {
            "type": movement_type,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("timestamp", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def add_movement(
        self,
        movement_id: str,
        drawer_id: str,
        tenant_id: str,
        store_id: str,
        movement_type: str,
        amount: int,
        employee_id: str,
        sale_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> CashMovement:
        """Add cash movement"""
        now = datetime.utcnow()
        movement_data = {
            "movement_id": movement_id,
            "drawer_id": drawer_id,
            "tenant_id": tenant_id,
            "store_id": store_id,
            "type": movement_type,
            "amount": amount,
            "employee_id": employee_id,
            "sale_id": sale_id,
            "timestamp": now,
            "notes": notes,
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(movement_data)
        movement_data["_id"] = result.inserted_id
        return CashMovement(**movement_data)
