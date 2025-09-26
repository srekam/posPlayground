"""
Reports Router
"""
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.deps import CurrentUser, get_report_service
from app.services.reports import ReportService

router = APIRouter()


@router.get("/sales")
async def get_sales_report(
    current_user,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    report_service: ReportService = Depends(get_report_service)
) -> Dict[str, Any]:
    """Get sales report"""
    
    try:
        result = await report_service.get_sales_report(
            user=current_user,
            from_date=from_date,
            to_date=to_date
        )
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to generate sales report"
            }
        )


@router.get("/shifts")
async def get_shifts_report(
    current_user,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    report_service: ReportService = Depends(get_report_service)
) -> Dict[str, Any]:
    """Get shifts report"""
    
    try:
        result = await report_service.get_shifts_report(
            user=current_user,
            from_date=from_date,
            to_date=to_date
        )
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to generate shifts report"
            }
        )


@router.get("/tickets")
async def get_tickets_report(
    current_user,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    report_service: ReportService = Depends(get_report_service)
) -> Dict[str, Any]:
    """Get tickets report"""
    
    try:
        result = await report_service.get_tickets_report(
            user=current_user,
            from_date=from_date,
            to_date=to_date
        )
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to generate tickets report"
            }
        )


@router.get("/fraud")
async def get_fraud_report(
    current_user,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    report_service: ReportService = Depends(get_report_service)
) -> Dict[str, Any]:
    """Get fraud detection report"""
    
    try:
        result = await report_service.get_fraud_report(
            user=current_user,
            from_date=from_date,
            to_date=to_date
        )
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to generate fraud report"
            }
        )
