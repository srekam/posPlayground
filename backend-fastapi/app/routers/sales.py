"""
Sales Router
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer

from app.models.sales import (
    SaleCreateRequest,
    SaleResponse,
    RefundRequest,
    RefundResponse,
    ReprintRequest,
    ReprintResponse
)
from app.deps import (
    CurrentUser,
    CurrentDevice,
    
    Idempotency,
    RequireCashier,
    RequireSalesScope
)
from app.services.sales import SalesService
from app.utils.errors import PlayParkException

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/", response_model=SaleResponse)
async def create_sale(
    request: SaleCreateRequest,
    current_user = Depends(CurrentUser),
    current_device = Depends(CurrentDevice),
    idempotency_key: Optional[str] = Depends(Idempotency),
    sales_service: SalesService = Depends(),
    _: None = Depends(RateLimit)
) -> SaleResponse:
    """Create a new sale"""
    
    try:
        # Use idempotency key from request if provided
        if hasattr(request, 'idempotency_key') and request.idempotency_key:
            idempotency_key = request.idempotency_key
        
        result = await sales_service.create_sale(
            request=request,
            user=current_user,
            device=current_device,
            idempotency_key=idempotency_key
        )
        
        return SaleResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Sale creation failed"
            }
        )


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: str,
    current_user = Depends(CurrentUser),
    sales_service: SalesService = Depends(),
    _: None = Depends(RateLimit)
) -> SaleResponse:
    """Get sale by ID"""
    
    try:
        result = await sales_service.get_sale_by_id(sale_id, current_user)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_SALE_NOT_FOUND",
                    "message": "Sale not found"
                }
            )
        
        return SaleResponse(**result)
    
    except HTTPException:
        raise
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve sale"
            }
        )


@router.get("/", response_model=Dict[str, Any])
async def get_sales(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    status: Optional[str] = Query(default=None),
    current_user = Depends(CurrentUser),
    sales_service: SalesService = Depends(),
    _: None = Depends(RateLimit)
) -> Dict[str, Any]:
    """Get sales list"""
    
    try:
        result = await sales_service.get_sales(
            user=current_user,
            limit=limit,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            status=status
        )
        
        return result
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve sales"
            }
        )


@router.post("/refunds", response_model=RefundResponse)
async def request_refund(
    request: RefundRequest,
    current_user = Depends(CurrentUser),
    sales_service: SalesService = Depends(),
    _: None = Depends(RateLimit)
) -> RefundResponse:
    """Request a refund"""
    
    try:
        result = await sales_service.request_refund(request, current_user)
        return RefundResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Refund request failed"
            }
        )


@router.post("/reprints", response_model=ReprintResponse)
async def request_reprint(
    request: ReprintRequest,
    current_user = Depends(CurrentUser),
    sales_service: SalesService = Depends(),
    _: None = Depends(RateLimit)
) -> ReprintResponse:
    """Request a reprint"""
    
    try:
        result = await sales_service.request_reprint(request, current_user)
        return ReprintResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Reprint request failed"
            }
        )
