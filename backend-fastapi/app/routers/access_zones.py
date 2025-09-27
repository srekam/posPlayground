"""
Access Zones API Router
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
import structlog

from app.schemas.common import SuccessResponse, ErrorResponse
from app.models.access_zones import (
    AccessZone, AccessZoneCreateRequest, AccessZoneUpdateRequest, AccessZoneResponse
)
from app.repositories.access_zones import AccessZoneRepository
from app.deps import get_current_tenant

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/access/zones", tags=["Access Zones"])


@router.get("/test")
async def test_access_zones():
    """Test endpoint for access zones"""
    return {"message": "Access Zones API is working!", "status": "ok"}


@router.get("/test-list")
async def test_list_access_zones():
    """Test endpoint for listing access zones without authentication"""
    try:
        tenant_id = "test-tenant"
        repo = AccessZoneRepository()
        
        # Build query
        query = {"tenant_id": tenant_id}
        zones = await repo.get_many(query)
        
        # Convert to response format
        response_data = [
            AccessZoneResponse.from_model(zone) for zone in zones
        ]
        
        return SuccessResponse(
            data=response_data,
            message="Access zones retrieved successfully"
        ).dict()
        
    except Exception as e:
        logger.error("Failed to list test access zones", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message="Failed to list access zones"
            ).dict()
        )


@router.get("/test-get/{zone_id}")
async def test_get_access_zone(zone_id: str):
    """Test endpoint for getting a single access zone without authentication"""
    try:
        repo = AccessZoneRepository()
        
        # Get access zone
        access_zone = await repo.get_by_id(zone_id, "zone_id")
        if not access_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="E_NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        return SuccessResponse(
            data=AccessZoneResponse.from_model(access_zone),
            message="Access zone retrieved successfully"
        ).dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get test access zone", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message="Failed to get access zone"
            ).dict()
        )


@router.post("/test-create")
async def test_create_access_zone(request: AccessZoneCreateRequest):
    """Test endpoint for creating access zones without authentication"""
    try:
        # Use a default tenant_id for testing
        tenant_id = "test-tenant"
        store_id = "test-store"
        
        repo = AccessZoneRepository()
        
        # Create AccessZone document object
        from app.models.access_zones import AccessZone
        from datetime import datetime
        import uuid
        
        access_zone_doc = AccessZone(
            zone_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            store_id=store_id,
            name=request.name,
            description=request.description,
            capacity=request.capacity,
            active=request.active,
            current_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Create access zone
        access_zone = await repo.create(access_zone_doc)
        
        return SuccessResponse(
            data=AccessZoneResponse.from_model(access_zone),
            message="Access zone created successfully"
        ).dict()
        
    except Exception as e:
        logger.error("Failed to create test access zone", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message="Failed to create access zone"
            ).dict()
        )


@router.put("/test-update/{zone_id}")
async def test_update_access_zone(zone_id: str, request: AccessZoneUpdateRequest):
    """Test endpoint for updating access zones without authentication"""
    try:
        repo = AccessZoneRepository()
        
        # Get existing access zone
        existing_zone = await repo.get_by_id(zone_id, "zone_id")
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="E_NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        # Update access zone
        updated_zone = await repo.update_by_id(
            zone_id, 
            request.dict(exclude_unset=True), 
            "zone_id"
        )
        
        return SuccessResponse(
            data=AccessZoneResponse.from_model(updated_zone),
            message="Access zone updated successfully"
        ).dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update test access zone", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message="Failed to update access zone"
            ).dict()
        )


@router.delete("/test-delete/{zone_id}")
async def test_delete_access_zone(zone_id: str):
    """Test endpoint for deleting access zones without authentication"""
    try:
        repo = AccessZoneRepository()
        
        # Check if access zone exists
        existing_zone = await repo.get_by_id(zone_id, "zone_id")
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="E_NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        # Delete access zone
        await repo.delete_by_id(zone_id, "zone_id")
        
        return SuccessResponse(
            data={"zone_id": zone_id},
            message="Access zone deleted successfully"
        ).dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete test access zone", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message="Failed to delete access zone"
            ).dict()
        )


@router.post("/", response_model=SuccessResponse[AccessZoneResponse], status_code=status.HTTP_201_CREATED)
async def create_access_zone(
    request: AccessZoneCreateRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Create a new access zone"""
    try:
        repo = AccessZoneRepository()
        
        # Generate zone_id
        import uuid
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        
        # Create zone data
        zone_data = {
            "zone_id": zone_id,
            "tenant_id": tenant_id,
            "store_id": "default",  # TODO: Get from context
            "name": request.name,
            "description": request.description,
            "active": request.active,
            "capacity": request.capacity,
            "current_count": 0,
        }
        
        zone = await repo.create(zone_data)
        
        # Convert to response format
        response_data = AccessZoneResponse(
            zone_id=zone["zone_id"],
            name=zone["name"],
            description=zone.get("description"),
            active=zone["active"],
            capacity=zone.get("capacity"),
            current_count=zone.get("current_count", 0),
            created_at=zone["created_at"],
            updated_at=zone["updated_at"]
        )
        
        return SuccessResponse(
            data=response_data,
            message="Access zone created successfully"
        )
    
    except Exception as e:
        logger.error("Error creating access zone", error=str(e), tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to create access zone"
            ).dict()
        )


@router.get("/", response_model=SuccessResponse[List[AccessZoneResponse]])
async def list_access_zones(
    active: Optional[bool] = Query(None, description="Filter by active status"),
    tenant_id: str = Depends(get_current_tenant)
):
    """List access zones with filtering"""
    try:
        repo = AccessZoneRepository()
        
        # Build query
        query = {"tenant_id": tenant_id}
        if active is not None:
            query["active"] = active
        
        zones = await repo.get_many(query)
        
        # Convert to response format
        response_data = [
            AccessZoneResponse(
                zone_id=zone["zone_id"],
                name=zone["name"],
                description=zone.get("description"),
                active=zone["active"],
                capacity=zone.get("capacity"),
                current_count=zone.get("current_count", 0),
                created_at=zone["created_at"],
                updated_at=zone["updated_at"]
            )
            for zone in zones
        ]
        
        return SuccessResponse(
            data=response_data,
            message="Access zones retrieved successfully"
        )
    
    except Exception as e:
        logger.error("Error listing access zones", error=str(e), tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to list access zones"
            ).dict()
        )


@router.get("/{zone_id}", response_model=SuccessResponse[AccessZoneResponse])
async def get_access_zone(
    zone_id: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Get access zone by ID"""
    try:
        repo = AccessZoneRepository()
        
        query = {"zone_id": zone_id, "tenant_id": tenant_id}
        zone = await repo.get_one(query)
        
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        # Convert to response format
        response_data = AccessZoneResponse(
            zone_id=zone["zone_id"],
            name=zone["name"],
            description=zone.get("description"),
            active=zone["active"],
            capacity=zone.get("capacity"),
            current_count=zone.get("current_count", 0),
            created_at=zone["created_at"],
            updated_at=zone["updated_at"]
        )
        
        return SuccessResponse(
            data=response_data,
            message="Access zone retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting access zone", error=str(e), zone_id=zone_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to get access zone"
            ).dict()
        )


@router.put("/{zone_id}", response_model=SuccessResponse[AccessZoneResponse])
async def update_access_zone(
    zone_id: str,
    request: AccessZoneUpdateRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Update an access zone"""
    try:
        repo = AccessZoneRepository()
        
        # Check if zone exists
        query = {"zone_id": zone_id, "tenant_id": tenant_id}
        existing_zone = await repo.get_one(query)
        
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        # Prepare update data
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description
        if request.active is not None:
            update_data["active"] = request.active
        if request.capacity is not None:
            update_data["capacity"] = request.capacity
        
        # Update zone
        zone = await repo.update_by_id(zone_id, update_data, "zone_id")
        
        # Convert to response format
        response_data = AccessZoneResponse(
            zone_id=zone["zone_id"],
            name=zone["name"],
            description=zone.get("description"),
            active=zone["active"],
            capacity=zone.get("capacity"),
            current_count=zone.get("current_count", 0),
            created_at=zone["created_at"],
            updated_at=zone["updated_at"]
        )
        
        return SuccessResponse(
            data=response_data,
            message="Access zone updated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating access zone", error=str(e), zone_id=zone_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to update access zone"
            ).dict()
        )


@router.delete("/{zone_id}", response_model=SuccessResponse[dict])
async def delete_access_zone(
    zone_id: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Delete an access zone (soft delete)"""
    try:
        repo = AccessZoneRepository()
        
        # Check if zone exists
        query = {"zone_id": zone_id, "tenant_id": tenant_id}
        existing_zone = await repo.get_one(query)
        
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        # Soft delete by setting active to False
        await repo.update_by_id(zone_id, {"active": False}, "zone_id")
        
        return SuccessResponse(
            data={"deleted": True},
            message="Access zone deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting access zone", error=str(e), zone_id=zone_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to delete access zone"
            ).dict()
        )


@router.patch("/{zone_id}/status", response_model=SuccessResponse[dict])
async def update_access_zone_status(
    zone_id: str,
    active: bool,
    tenant_id: str = Depends(get_current_tenant)
):
    """Update access zone status (activate/deactivate)"""
    try:
        repo = AccessZoneRepository()
        
        # Check if zone exists
        query = {"zone_id": zone_id, "tenant_id": tenant_id}
        existing_zone = await repo.get_one(query)
        
        if not existing_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error="NOT_FOUND",
                    message="Access zone not found"
                ).dict()
            )
        
        # Update status
        await repo.update_by_id(zone_id, {"active": active}, "zone_id")
        
        return SuccessResponse(
            data={"active": active},
            message=f"Access zone {'activated' if active else 'deactivated'} successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating access zone status", error=str(e), zone_id=zone_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to update access zone status"
            ).dict()
        )
