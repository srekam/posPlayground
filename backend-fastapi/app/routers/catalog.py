"""
Catalog Router
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body

from app.deps import CurrentUser, get_catalog_service
from app.services.catalog import CatalogService

router = APIRouter()


@router.get("/packages")
async def get_packages(
    store_id: str,
    current_user = CurrentUser,
    catalog_service: CatalogService = Depends(get_catalog_service)
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
    catalog_service: CatalogService = Depends(get_catalog_service)
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


@router.post("/pricing/calculate")
async def calculate_pricing(
    current_user = CurrentUser,
    catalog_service: CatalogService = Depends(get_catalog_service),
    request: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """Calculate pricing for a package with rules applied"""
    
    try:
        package_id = request.get("package_id")
        quantity = request.get("quantity", 1)
        apply_rules = request.get("apply_rules", True)
        
        if not package_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "E_BAD_REQUEST",
                    "message": "package_id is required"
                }
            )
        
        result = await catalog_service.calculate_pricing(
            package_id=package_id,
            quantity=quantity,
            user=current_user,
            apply_rules=apply_rules
        )
        
        return {"data": result}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to calculate pricing"
            }
        )
