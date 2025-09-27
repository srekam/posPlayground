"""
Cash Drawer Router
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.cash_drawers import (
    CashDrawer, CashMovement, CashDrawerOpenRequest, CashDrawerCloseRequest,
    CashMovementCreateRequest, CashDrawerResponse, CashDrawerSummary
)
from app.repositories.cash_drawers import CashDrawerRepository, CashMovementRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/open", response_model=CashDrawerResponse)
async def open_cash_drawer(
    open_data: CashDrawerOpenRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Open cash drawer"""
    try:
        cash_drawer_repo = CashDrawerRepository()
        
        # Check if there's already an open drawer
        existing_drawer = await cash_drawer_repo.get_current_by_device(current_user.device_id)
        if existing_drawer:
            raise PlayParkException(
                error_code=ErrorCode.E_RULE_CONFLICT,
                message="Cash drawer is already open",
                status_code=400
            )
        
        # Generate drawer ID
        drawer_id = str(ULID())
        
        # Open cash drawer
        drawer = await cash_drawer_repo.open_drawer(
            drawer_id=drawer_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            device_id=current_user.device_id,
            employee_id=current_user.employee_id,
            opening_amount=open_data.opening_amount,
            notes=open_data.notes
        )
        
        return CashDrawerResponse(
            drawer_id=drawer.drawer_id,
            status=drawer.status,
            opened_at=drawer.opened_at,
            closed_at=drawer.closed_at,
            opening_amount=drawer.opening_amount,
            closing_amount=drawer.closing_amount,
            expected_amount=drawer.expected_amount,
            variance=drawer.variance,
            notes=drawer.notes,
            created_at=drawer.created_at,
            updated_at=drawer.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to open cash drawer",
            details={"error": str(e)}
        )


@router.post("/close", response_model=CashDrawerResponse)
async def close_cash_drawer(
    close_data: CashDrawerCloseRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Close cash drawer"""
    try:
        cash_drawer_repo = CashDrawerRepository()
        
        # Get current open drawer
        drawer = await cash_drawer_repo.get_current_by_device(current_user.device_id)
        if not drawer:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No open cash drawer found",
                status_code=404
            )
        
        # Close cash drawer
        closed_drawer = await cash_drawer_repo.close_drawer(
            drawer.drawer_id, close_data.closing_amount, close_data.notes
        )
        
        if not closed_drawer:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to close cash drawer"
            )
        
        return CashDrawerResponse(
            drawer_id=closed_drawer.drawer_id,
            status=closed_drawer.status,
            opened_at=closed_drawer.opened_at,
            closed_at=closed_drawer.closed_at,
            opening_amount=closed_drawer.opening_amount,
            closing_amount=closed_drawer.closing_amount,
            expected_amount=closed_drawer.expected_amount,
            variance=closed_drawer.variance,
            notes=closed_drawer.notes,
            created_at=closed_drawer.created_at,
            updated_at=closed_drawer.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to close cash drawer",
            details={"error": str(e)}
        )


@router.get("/current", response_model=CashDrawerResponse)
async def get_current_cash_drawer(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current open cash drawer"""
    try:
        cash_drawer_repo = CashDrawerRepository()
        
        drawer = await cash_drawer_repo.get_current_by_device(current_user.device_id)
        if not drawer:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No open cash drawer found",
                status_code=404
            )
        
        return CashDrawerResponse(
            drawer_id=drawer.drawer_id,
            status=drawer.status,
            opened_at=drawer.opened_at,
            closed_at=drawer.closed_at,
            opening_amount=drawer.opening_amount,
            closing_amount=drawer.closing_amount,
            expected_amount=drawer.expected_amount,
            variance=drawer.variance,
            notes=drawer.notes,
            created_at=drawer.created_at,
            updated_at=drawer.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get current cash drawer",
            details={"error": str(e)}
        )


@router.get("/summary", response_model=CashDrawerSummary)
async def get_cash_drawer_summary(
    drawer_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get cash drawer summary"""
    try:
        cash_drawer_repo = CashDrawerRepository()
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        if drawer_id:
            # Get summary for specific drawer
            summary = await cash_drawer_repo.get_drawer_summary(drawer_id, start_dt, end_dt)
        else:
            # Get current drawer summary
            drawer = await cash_drawer_repo.get_current_by_device(current_user.device_id)
            if not drawer:
                raise PlayParkException(
                    error_code=ErrorCode.NOT_FOUND,
                    message="No open cash drawer found",
                    status_code=404
                )
            
            summary = await cash_drawer_repo.get_drawer_summary(drawer.drawer_id, start_dt, end_dt)
        
        return CashDrawerSummary(**summary)
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get cash drawer summary",
            details={"error": str(e)}
        )


@router.post("/movements", status_code=201)
async def create_cash_movement(
    movement_data: CashMovementCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create cash movement"""
    try:
        cash_drawer_repo = CashDrawerRepository()
        cash_movement_repo = CashMovementRepository()
        
        # Get current open drawer
        drawer = await cash_drawer_repo.get_current_by_device(current_user.device_id)
        if not drawer:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="No open cash drawer found",
                status_code=404
            )
        
        # Generate movement ID
        movement_id = str(ULID())
        
        # Create cash movement
        movement = await cash_movement_repo.add_movement(
            movement_id=movement_id,
            drawer_id=drawer.drawer_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            movement_type=movement_data.type,
            amount=movement_data.amount,
            employee_id=current_user.employee_id,
            sale_id=movement_data.sale_id,
            notes=movement_data.notes
        )
        
        return {
            "movement_id": movement.movement_id,
            "message": "Cash movement created successfully"
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create cash movement",
            details={"error": str(e)}
        )


@router.get("/movements", response_model=List[dict])
async def get_cash_movements(
    drawer_id: Optional[str] = Query(None),
    movement_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get cash movements"""
    try:
        cash_drawer_repo = CashDrawerRepository()
        cash_movement_repo = CashMovementRepository()
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        movements = []
        
        if drawer_id:
            # Get movements for specific drawer
            movements = await cash_movement_repo.get_by_drawer_and_date_range(
                drawer_id, start_dt, end_dt, skip, limit
            )
        elif movement_type and start_dt and end_dt:
            # Get movements by type and date range
            movements = await cash_movement_repo.get_by_type_and_date_range(
                movement_type, start_dt, end_dt, skip, limit
            )
        else:
            # Get current drawer movements
            drawer = await cash_drawer_repo.get_current_by_device(current_user.device_id)
            if drawer:
                movements = await cash_movement_repo.get_by_drawer_and_date_range(
                    drawer.drawer_id, start_dt, end_dt, skip, limit
                )
        
        return [
            {
                "movement_id": m.movement_id,
                "drawer_id": m.drawer_id,
                "type": m.type,
                "amount": m.amount,
                "employee_id": m.employee_id,
                "sale_id": m.sale_id,
                "timestamp": m.timestamp,
                "notes": m.notes,
                "created_at": m.created_at
            }
            for m in movements
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve cash movements",
            details={"error": str(e)}
        )
