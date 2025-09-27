"""
Timecard Router
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.timecards import (
    Timecard, TimecardClockInRequest, TimecardClockOutRequest,
    TimecardBreakRequest, TimecardResponse, TimecardSummary
)
from app.repositories.timecards import TimecardRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/clock-in", response_model=TimecardResponse)
async def clock_in(
    clock_in_data: TimecardClockInRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Clock in employee"""
    try:
        timecard_repo = TimecardRepository()
        
        # Check if employee already has an active timecard
        active_timecard = await timecard_repo.get_active_by_employee(current_user.employee_id)
        if active_timecard:
            raise PlayParkException(
                error_code=ErrorCode.E_RULE_CONFLICT,
                message="Employee is already clocked in",
                status_code=400
            )
        
        # Generate timecard ID
        timecard_id = str(ULID())
        
        # Clock in
        timecard = await timecard_repo.clock_in(
            timecard_id=timecard_id,
            employee_id=current_user.employee_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            notes=clock_in_data.notes
        )
        
        return TimecardResponse(
            timecard_id=timecard.timecard_id,
            employee_id=timecard.employee_id,
            clock_in=timecard.clock_in,
            clock_out=timecard.clock_out,
            break_start=timecard.break_start,
            break_end=timecard.break_end,
            total_break_time=timecard.total_break_time,
            total_work_time=timecard.total_work_time,
            status=timecard.status,
            notes=timecard.notes,
            created_at=timecard.created_at,
            updated_at=timecard.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to clock in",
            details={"error": str(e)}
        )


@router.post("/clock-out", response_model=TimecardResponse)
async def clock_out(
    clock_out_data: TimecardClockOutRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Clock out employee"""
    try:
        timecard_repo = TimecardRepository()
        
        # Get active timecard
        active_timecard = await timecard_repo.get_active_by_employee(current_user.employee_id)
        if not active_timecard:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No active timecard found",
                status_code=404
            )
        
        # Clock out
        updated_timecard = await timecard_repo.clock_out(
            active_timecard.timecard_id, clock_out_data.notes
        )
        
        if not updated_timecard:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to clock out"
            )
        
        return TimecardResponse(
            timecard_id=updated_timecard.timecard_id,
            employee_id=updated_timecard.employee_id,
            clock_in=updated_timecard.clock_in,
            clock_out=updated_timecard.clock_out,
            break_start=updated_timecard.break_start,
            break_end=updated_timecard.break_end,
            total_break_time=updated_timecard.total_break_time,
            total_work_time=updated_timecard.total_work_time,
            status=updated_timecard.status,
            notes=updated_timecard.notes,
            created_at=updated_timecard.created_at,
            updated_at=updated_timecard.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to clock out",
            details={"error": str(e)}
        )


@router.post("/break/start", response_model=TimecardResponse)
async def start_break(
    break_data: TimecardBreakRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Start break"""
    try:
        timecard_repo = TimecardRepository()
        
        # Get active timecard
        active_timecard = await timecard_repo.get_active_by_employee(current_user.employee_id)
        if not active_timecard:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No active timecard found",
                status_code=404
            )
        
        # Start break
        updated_timecard = await timecard_repo.start_break(
            active_timecard.timecard_id, break_data.break_type, break_data.notes
        )
        
        if not updated_timecard:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to start break"
            )
        
        return TimecardResponse(
            timecard_id=updated_timecard.timecard_id,
            employee_id=updated_timecard.employee_id,
            clock_in=updated_timecard.clock_in,
            clock_out=updated_timecard.clock_out,
            break_start=updated_timecard.break_start,
            break_end=updated_timecard.break_end,
            total_break_time=updated_timecard.total_break_time,
            total_work_time=updated_timecard.total_work_time,
            status=updated_timecard.status,
            notes=updated_timecard.notes,
            created_at=updated_timecard.created_at,
            updated_at=updated_timecard.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to start break",
            details={"error": str(e)}
        )


@router.post("/break/end", response_model=TimecardResponse)
async def end_break(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """End break"""
    try:
        timecard_repo = TimecardRepository()
        
        # Get active timecard
        active_timecard = await timecard_repo.get_active_by_employee(current_user.employee_id)
        if not active_timecard:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No active timecard found",
                status_code=404
            )
        
        # End break
        updated_timecard = await timecard_repo.end_break(active_timecard.timecard_id)
        
        if not updated_timecard:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to end break"
            )
        
        return TimecardResponse(
            timecard_id=updated_timecard.timecard_id,
            employee_id=updated_timecard.employee_id,
            clock_in=updated_timecard.clock_in,
            clock_out=updated_timecard.clock_out,
            break_start=updated_timecard.break_start,
            break_end=updated_timecard.break_end,
            total_break_time=updated_timecard.total_break_time,
            total_work_time=updated_timecard.total_work_time,
            status=updated_timecard.status,
            notes=updated_timecard.notes,
            created_at=updated_timecard.created_at,
            updated_at=updated_timecard.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to end break",
            details={"error": str(e)}
        )


@router.get("/", response_model=List[TimecardResponse])
async def get_timecards(
    employee_id: Optional[str] = Query(None),
    start_date: str = Query(...),
    end_date: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get timecards"""
    try:
        timecard_repo = TimecardRepository()
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Use provided employee_id or current user's employee_id
        target_employee_id = employee_id or current_user.employee_id
        
        # Get timecards
        timecards = await timecard_repo.get_by_employee_and_date_range(
            target_employee_id, start_dt, end_dt, skip, limit
        )
        
        return [
            TimecardResponse(
                timecard_id=tc.timecard_id,
                employee_id=tc.employee_id,
                clock_in=tc.clock_in,
                clock_out=tc.clock_out,
                break_start=tc.break_start,
                break_end=tc.break_end,
                total_break_time=tc.total_break_time,
                total_work_time=tc.total_work_time,
                status=tc.status,
                notes=tc.notes,
                created_at=tc.created_at,
                updated_at=tc.updated_at
            )
            for tc in timecards
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve timecards",
            details={"error": str(e)}
        )


@router.get("/summary/{employee_id}")
async def get_employee_summary(
    employee_id: str,
    date: str = Query(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get employee timecard summary for a date"""
    try:
        timecard_repo = TimecardRepository()
        
        # Parse date
        target_date = datetime.fromisoformat(date)
        
        # Get summary
        summary = await timecard_repo.get_employee_summary(employee_id, target_date)
        
        return summary
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get employee summary",
            details={"error": str(e)}
        )


@router.get("/current", response_model=TimecardResponse)
async def get_current_timecard(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current active timecard"""
    try:
        timecard_repo = TimecardRepository()
        
        active_timecard = await timecard_repo.get_active_by_employee(current_user.employee_id)
        if not active_timecard:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No active timecard found",
                status_code=404
            )
        
        return TimecardResponse(
            timecard_id=active_timecard.timecard_id,
            employee_id=active_timecard.employee_id,
            clock_in=active_timecard.clock_in,
            clock_out=active_timecard.clock_out,
            break_start=active_timecard.break_start,
            break_end=active_timecard.break_end,
            total_break_time=active_timecard.total_break_time,
            total_work_time=active_timecard.total_work_time,
            status=active_timecard.status,
            notes=active_timecard.notes,
            created_at=active_timecard.created_at,
            updated_at=active_timecard.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get current timecard",
            details={"error": str(e)}
        )
