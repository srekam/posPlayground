"""
Shifts Router
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import CurrentUser, get_shift_service
from app.services.shifts import ShiftService

router = APIRouter()


@router.post("/open")
async def open_shift(
    request: Dict[str, Any],
    current_user,
    shift_service: ShiftService = Depends(get_shift_service)
) -> Dict[str, Any]:
    """Open a new shift"""
    
    try:
        result = await shift_service.open_shift(request, current_user)
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to open shift"
            }
        )


@router.post("/close")
async def close_shift(
    request: Dict[str, Any],
    current_user,
    shift_service: ShiftService = Depends(get_shift_service)
) -> Dict[str, Any]:
    """Close current shift"""
    
    try:
        result = await shift_service.close_shift(request, current_user)
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to close shift"
            }
        )


@router.get("/current")
async def get_current_shift(
    current_user,
    shift_service: ShiftService = Depends(get_shift_service)
) -> Dict[str, Any]:
    """Get current active shift"""
    
    try:
        result = await shift_service.get_current_shift(current_user)
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve current shift"
            }
        )
