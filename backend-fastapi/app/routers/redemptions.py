"""
Redemption Router
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.redemptions import Redemption, RedemptionCreateRequest, RedemptionResponse
from app.repositories.redemptions import RedemptionRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=RedemptionResponse, status_code=201)
async def create_redemption(
    redemption_data: RedemptionCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new redemption record"""
    try:
        redemption_repo = RedemptionRepository()
        
        # Generate redemption ID
        redemption_id = str(ULID())
        
        # Create redemption document
        redemption = Redemption(
            redemption_id=redemption_id,
            ticket_id=redemption_data.ticket_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            device_id=redemption_data.device_id,
            result="pass",  # Default to pass, will be updated by business logic
            meta=redemption_data.meta
        )
        
        created_redemption = await redemption_repo.create(redemption)
        
        return RedemptionResponse(
            redemption_id=created_redemption.redemption_id,
            ticket_id=created_redemption.ticket_id,
            result=created_redemption.result,
            reason=created_redemption.reason,
            redeemed_at=created_redemption.redeemed_at,
            meta=created_redemption.meta
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create redemption",
            details={"error": str(e)}
        )


@router.get("/", response_model=List[RedemptionResponse])
async def get_redemptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ticket_id: Optional[str] = Query(None),
    device_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get redemptions with optional filters"""
    try:
        redemption_repo = RedemptionRepository()
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        redemptions = []
        
        if ticket_id:
            # Get redemptions by ticket ID
            redemptions = await redemption_repo.get_by_ticket_id(ticket_id)
        elif device_id and start_dt and end_dt:
            # Get redemptions by device and date range
            redemptions = await redemption_repo.get_by_device_and_date_range(
                device_id, start_dt, end_dt, skip, limit
            )
        elif start_dt and end_dt:
            # Get redemptions by store and date range
            redemptions = await redemption_repo.get_by_store_and_date_range(
                current_user.store_id, start_dt, end_dt, skip, limit
            )
        else:
            # Get all redemptions for store
            query = {"store_id": current_user.store_id}
            if result:
                query["result"] = result
            redemptions = await redemption_repo.get_many(query, skip, limit)
        
        return [
            RedemptionResponse(
                redemption_id=r.redemption_id,
                ticket_id=r.ticket_id,
                result=r.result,
                reason=r.reason,
                redeemed_at=r.redeemed_at,
                meta=r.meta
            )
            for r in redemptions
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve redemptions",
            details={"error": str(e)}
        )


@router.get("/stats/summary")
async def get_redemption_stats(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get redemption statistics"""
    try:
        redemption_repo = RedemptionRepository()
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        stats = await redemption_repo.get_redemption_stats(
            current_user.store_id, start_dt, end_dt
        )
        
        return stats
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get redemption statistics",
            details={"error": str(e)}
        )


@router.get("/duplicate-check/{ticket_id}")
async def check_duplicate_redemption(
    ticket_id: str,
    device_id: str = Query(...),
    time_window_minutes: int = Query(5, ge=1, le=60),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Check for duplicate redemption within time window"""
    try:
        redemption_repo = RedemptionRepository()
        
        is_duplicate = await redemption_repo.check_duplicate_redemption(
            ticket_id, device_id, time_window_minutes
        )
        
        return {
            "ticket_id": ticket_id,
            "device_id": device_id,
            "time_window_minutes": time_window_minutes,
            "is_duplicate": is_duplicate
        }
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to check duplicate redemption",
            details={"error": str(e)}
        )
