"""
Items API Router
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
import structlog

from app.schemas.items import (
    ItemCreateRequest, ItemUpdateRequest, ItemStatusUpdateRequest, ItemsListRequest,
    ItemResponse, ItemsListResponse, ItemErrorCode
)
from app.schemas.common import SuccessResponse, ErrorResponse
from app.services.items import ItemsService
from app.deps import get_current_tenant

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/items", tags=["Items"])

# In-memory storage for test items (in production, this would be a database)
_test_items_storage = []


@router.get("/test")
async def test_items_api():
    """Test endpoint for items API"""
    return {"message": "Items API is working!", "status": "ok"}


@router.post("/test-create")
async def test_create_item(request: dict):
    """Test endpoint for creating items without authentication"""
    try:
        # Use a default tenant_id for testing
        tenant_id = "test-tenant"
        
        # Create a simple item response without using the complex service
        from datetime import datetime
        import uuid
        
        # Generate a simple item_id
        item_id = str(uuid.uuid4())
        
        # Create a simple item response
        item_data = {
            "item_id": item_id,
            "tenant_id": tenant_id,
            "name": request.get("name", "Untitled Item"),
            "description": request.get("description", ""),
            "type": request.get("type", "NON_STOCKED_SERVICE"),
            "price_satang": request.get("price_satang", 0),
            "active": request.get("active", True),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store the item in our in-memory storage
        _test_items_storage.append(item_data)
        
        return SuccessResponse(
            data=item_data,
            message="Item created successfully"
        ).dict()
        
    except Exception as e:
        logger.error("Failed to create test item", error=str(e), request_data=request)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message=f"Failed to create item: {str(e)}"
            ).dict()
        )


@router.get("/test-list")
async def test_list_items():
    """Test endpoint for listing items without authentication"""
    try:
        # Return items from our in-memory storage
        if not _test_items_storage:
            # If no items exist, return some sample items
            from datetime import datetime
            import uuid
            
            sample_items = [
                {
                    "item_id": str(uuid.uuid4()),
                    "tenant_id": "test-tenant",
                    "name": "Sample Stocked Good",
                    "description": "A sample stocked good item",
                    "type": "STOCKED_GOOD",
                    "price_satang": 10000,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "item_id": str(uuid.uuid4()),
                    "tenant_id": "test-tenant", 
                    "name": "Sample Pass Time",
                    "description": "A sample pass time item",
                    "type": "PASS_TIME",
                    "price_satang": 50000,
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            _test_items_storage.extend(sample_items)
        
        return SuccessResponse(
            data=_test_items_storage,
            message="Items retrieved successfully"
        ).dict()
        
    except Exception as e:
        logger.error("Failed to list test items", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="E_INTERNAL_ERROR",
                message="Failed to list items"
            ).dict()
        )


@router.post("/", response_model=SuccessResponse[ItemResponse], status_code=status.HTTP_201_CREATED)
async def create_item(
    request: ItemCreateRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Create a new item"""
    try:
        service = ItemsService()
        item = await service.create_item(tenant_id, request)
        
        return SuccessResponse(
            data=item,
            message="Item created successfully"
        )
    
    except ValueError as e:
        logger.error("Validation error creating item", error=str(e), tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=ItemErrorCode.INVALID_TYPE,
                message=str(e)
            ).dict()
        )
    
    except Exception as e:
        logger.error("Error creating item", error=str(e), tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to create item"
            ).dict()
        )


@router.get("/", response_model=SuccessResponse[ItemsListResponse])
async def list_items(
    type: Optional[str] = Query(None, description="Filter by item type"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    q: Optional[str] = Query(None, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    tenant_id: str = Depends(get_current_tenant)
):
    """List items with filtering and pagination"""
    try:
        from app.models.items import ItemType
        
        request = ItemsListRequest(
            type=ItemType(type) if type else None,
            category_id=category_id,
            active=active,
            q=q,
            page=page,
            limit=limit
        )
        
        service = ItemsService()
        items = await service.list_items(tenant_id, request)
        
        return SuccessResponse(
            data=items,
            message="Items retrieved successfully"
        )
    
    except ValueError as e:
        logger.error("Validation error listing items", error=str(e), tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=ItemErrorCode.INVALID_TYPE,
                message=str(e)
            ).dict()
        )
    
    except Exception as e:
        logger.error("Error listing items", error=str(e), tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to list items"
            ).dict()
        )


@router.get("/{item_id}", response_model=SuccessResponse[ItemResponse])
async def get_item(
    item_id: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Get item by ID"""
    try:
        service = ItemsService()
        item = await service.get_item(item_id, tenant_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=ItemErrorCode.NOT_FOUND,
                    message="Item not found"
                ).dict()
            )
        
        return SuccessResponse(
            data=item,
            message="Item retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting item", error=str(e), item_id=item_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to get item"
            ).dict()
        )


@router.put("/{item_id}", response_model=SuccessResponse[ItemResponse])
async def update_item(
    item_id: str,
    request: ItemUpdateRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Update an item"""
    try:
        service = ItemsService()
        item = await service.update_item(item_id, tenant_id, request)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=ItemErrorCode.NOT_FOUND,
                    message="Item not found"
                ).dict()
            )
        
        return SuccessResponse(
            data=item,
            message="Item updated successfully"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Validation error updating item", error=str(e), item_id=item_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=ItemErrorCode.INVALID_TYPE,
                message=str(e)
            ).dict()
        )
    
    except Exception as e:
        logger.error("Error updating item", error=str(e), item_id=item_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to update item"
            ).dict()
        )


@router.patch("/{item_id}/status", response_model=SuccessResponse[dict])
async def update_item_status(
    item_id: str,
    request: ItemStatusUpdateRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Update item status (activate/deactivate)"""
    try:
        service = ItemsService()
        success = await service.update_item_status(item_id, tenant_id, request.active)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=ItemErrorCode.NOT_FOUND,
                    message="Item not found"
                ).dict()
            )
        
        return SuccessResponse(
            data={"active": request.active},
            message="Item status updated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating item status", error=str(e), item_id=item_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to update item status"
            ).dict()
        )


@router.delete("/{item_id}", response_model=SuccessResponse[dict])
async def delete_item(
    item_id: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Delete an item (soft delete)"""
    try:
        service = ItemsService()
        success = await service.delete_item(item_id, tenant_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    error=ItemErrorCode.NOT_FOUND,
                    message="Item not found"
                ).dict()
            )
        
        return SuccessResponse(
            data={"deleted": True},
            message="Item deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting item", error=str(e), item_id=item_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Failed to delete item"
            ).dict()
        )
