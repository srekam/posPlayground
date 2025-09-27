"""
Catalog Router - Packages CRUD API
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from pydantic import BaseModel, Field

from app.models.catalog import Package, PackageType
from app.deps import CurrentUser, get_catalog_service, get_user_repository
from app.services.catalog import CatalogService
from app.repositories.catalog import CatalogRepository

router = APIRouter()


class PackageCreateRequest(BaseModel):
    """Package creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: PackageType = PackageType.SINGLE
    price: float = Field(..., ge=0)
    quota_or_minutes: int = Field(..., ge=1)
    active: bool = True
    visible_on: List[str] = Field(default_factory=list)
    access_zones: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)


class PackageUpdateRequest(BaseModel):
    """Package update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: Optional[PackageType] = None
    price: Optional[float] = Field(None, ge=0)
    quota_or_minutes: Optional[int] = Field(None, ge=1)
    active: Optional[bool] = None
    visible_on: Optional[List[str]] = None
    access_zones: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class PackageResponse(BaseModel):
    """Package response"""
    package_id: str
    tenant_id: str
    store_id: str
    name: str
    description: Optional[str]
    type: PackageType
    price: float
    quota_or_minutes: int
    active: bool
    visible_on: List[str]
    access_zones: List[str]
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


@router.get("/packages", response_model=Dict[str, Any])
async def get_packages(
    store_id: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get packages list with filtering"""
    
    try:
        # Use user's store_id if not provided
        if not store_id:
            store_id = current_user.store_id
        
        # Create catalog repository
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Get packages
        packages = await catalog_repo.get_packages(
            store_id=store_id,
            active=active,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format
        package_list = []
        for package in packages:
            package_list.append(PackageResponse(
                package_id=package.package_id,
                tenant_id=package.tenant_id,
                store_id=package.store_id,
                name=package.name,
                description=package.description,
                type=package.type,
                price=package.price,
                quota_or_minutes=package.quota_or_minutes,
                active=package.active,
                visible_on=package.visible_on,
                access_zones=package.access_zones,
                settings=package.settings,
                created_at=package.created_at.isoformat(),
                updated_at=package.updated_at.isoformat()
            ))
        
        return {
            "data": package_list,
            "total": len(package_list),
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve packages"
            }
        )


@router.get("/packages/{package_id}", response_model=PackageResponse)
async def get_package(
    package_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> PackageResponse:
    """Get package by ID"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        package = await catalog_repo.get_package_by_id(package_id)
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_PACKAGE_NOT_FOUND",
                    "message": "Package not found"
                }
            )
        
        return PackageResponse(
            package_id=package.package_id,
            tenant_id=package.tenant_id,
            store_id=package.store_id,
            name=package.name,
            description=package.description,
            type=package.type,
            price=package.price,
            quota_or_minutes=package.quota_or_minutes,
            active=package.active,
            visible_on=package.visible_on,
            access_zones=package.access_zones,
            settings=package.settings,
            created_at=package.created_at.isoformat(),
            updated_at=package.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve package"
            }
        )


@router.post("/packages", response_model=PackageResponse)
async def create_package(
    request: PackageCreateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> PackageResponse:
    """Create a new package"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Generate package ID
        from datetime import datetime
        package_id = f"pkg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{current_user.employee_id}"
        
        # Create package
        package = Package(
            package_id=package_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            name=request.name,
            description=request.description,
            type=request.type,
            price=request.price,
            quota_or_minutes=request.quota_or_minutes,
            active=request.active,
            visible_on=request.visible_on,
            access_zones=request.access_zones,
            settings=request.settings
        )
        
        created_package = await catalog_repo.create_package(package)
        
        return PackageResponse(
            package_id=created_package.package_id,
            tenant_id=created_package.tenant_id,
            store_id=created_package.store_id,
            name=created_package.name,
            description=created_package.description,
            type=created_package.type,
            price=created_package.price,
            quota_or_minutes=created_package.quota_or_minutes,
            active=created_package.active,
            visible_on=created_package.visible_on,
            access_zones=created_package.access_zones,
            settings=created_package.settings,
            created_at=created_package.created_at.isoformat(),
            updated_at=created_package.updated_at.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to create package"
            }
        )


@router.put("/packages/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: str,
    request: PackageUpdateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> PackageResponse:
    """Update a package"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Get existing package
        existing_package = await catalog_repo.get_package_by_id(package_id)
        if not existing_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_PACKAGE_NOT_FOUND",
                    "message": "Package not found"
                }
            )
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        updated_package = await catalog_repo.update_package(package_id, update_data)
        
        return PackageResponse(
            package_id=updated_package.package_id,
            tenant_id=updated_package.tenant_id,
            store_id=updated_package.store_id,
            name=updated_package.name,
            description=updated_package.description,
            type=updated_package.type,
            price=updated_package.price,
            quota_or_minutes=updated_package.quota_or_minutes,
            active=updated_package.active,
            visible_on=updated_package.visible_on,
            access_zones=updated_package.access_zones,
            settings=updated_package.settings,
            created_at=updated_package.created_at.isoformat(),
            updated_at=updated_package.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to update package"
            }
        )


@router.delete("/packages/{package_id}")
async def delete_package(
    package_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Delete a package"""
    
    try:
        catalog_repo = CatalogRepository(user_repository.db)
        
        # Check if package exists
        existing_package = await catalog_repo.get_package_by_id(package_id)
        if not existing_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_PACKAGE_NOT_FOUND",
                    "message": "Package not found"
                }
            )
        
        # Delete package
        await catalog_repo.delete_package(package_id)
        
        return {
            "success": True,
            "message": "Package deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to delete package"
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
