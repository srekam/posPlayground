"""
Catalog Router
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import CurrentUser
from app.services.catalog import CatalogService

router = APIRouter()


@router.get("/packages")
async def get_packages(
    store_id: str,
    current_user = CurrentUser,
    catalog_service: CatalogService = Depends()
) -> Dict[str, Any]:
    """Get available packages"""
    
    try:
        result = await catalog_service.get_packages(store_id, current_user)
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve packages"
            }
        )


@router.get("/pricing/rules")
async def get_pricing_rules(
    store_id: str,
    current_user = CurrentUser,
    catalog_service: CatalogService = Depends()
) -> Dict[str, Any]:
    """Get pricing rules"""
    
    try:
        result = await catalog_service.get_pricing_rules(store_id, current_user)
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve pricing rules"
            }
        )
