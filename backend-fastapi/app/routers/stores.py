"""
Stores Router - Store and Device Management
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import structlog

from app.deps import get_user_repository, CurrentUser
from app.models.core import Store, Device
from app.utils.errors import PlayParkException, ErrorCode

logger = structlog.get_logger(__name__)
router = APIRouter()


# Request/Response Models
class StoreCreateRequest(BaseModel):
    """Store creation request"""
    name: str = Field(..., min_length=1, max_length=100, description="Store name")
    address: Optional[str] = Field(default=None, max_length=200, description="Store address")
    timezone: str = Field(default="UTC", description="Store timezone")
    currency: str = Field(default="THB", description="Store currency")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Store settings")


class StoreUpdateRequest(BaseModel):
    """Store update request"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    address: Optional[str] = Field(default=None, max_length=200)
    timezone: Optional[str] = Field(default=None)
    currency: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    settings: Optional[Dict[str, Any]] = Field(default=None)


class StoreResponse(BaseModel):
    """Store response"""
    store_id: str
    tenant_id: str
    name: str
    address: Optional[str]
    timezone: str
    currency: str
    status: str
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


class DeviceResponse(BaseModel):
    """Device response"""
    device_id: str
    tenant_id: str
    store_id: str
    type: str
    name: str
    status: str
    last_seen: Optional[str]
    created_at: str
    updated_at: str


# Store Endpoints
@router.get("/stores", response_model=Dict[str, Any])
async def get_stores(
    skip: int = 0,
    limit: int = 100,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get all stores for the current tenant"""
    try:
        logger.info("Fetching stores", tenant_id=current_user.tenant_id, skip=skip, limit=limit)
        
        stores = await user_repository.get_stores_by_tenant(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit
        )
        
        store_responses = [
            StoreResponse(
                store_id=store.store_id,
                tenant_id=store.tenant_id,
                name=store.name,
                address=store.address,
                timezone=store.timezone,
                currency=store.currency,
                status=store.status,
                settings=store.settings,
                created_at=store.created_at.isoformat(),
                updated_at=store.updated_at.isoformat()
            )
            for store in stores
        ]
        
        return {
            "success": True,
            "data": store_responses,
            "total": len(store_responses)
        }
        
    except Exception as e:
        logger.error("Failed to fetch stores", error=str(e), tenant_id=current_user.tenant_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Failed to fetch stores"
        )


@router.post("/stores", response_model=Dict[str, Any])
async def create_store(
    request: StoreCreateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Create a new store"""
    try:
        logger.info("Creating store", tenant_id=current_user.tenant_id, name=request.name)
        
        # Generate unique store ID
        import uuid
        store_id = f"store_{uuid.uuid4().hex[:8]}"
        
        store = Store(
            store_id=store_id,
            tenant_id=current_user.tenant_id,
            name=request.name,
            address=request.address,
            timezone=request.timezone,
            currency=request.currency,
            settings=request.settings
        )
        
        created_store = await user_repository.create_store(store)
        
        store_response = StoreResponse(
            store_id=created_store.store_id,
            tenant_id=created_store.tenant_id,
            name=created_store.name,
            address=created_store.address,
            timezone=created_store.timezone,
            currency=created_store.currency,
            status=created_store.status,
            settings=created_store.settings,
            created_at=created_store.created_at.isoformat(),
            updated_at=created_store.updated_at.isoformat()
        )
        
        logger.info("Store created successfully", store_id=store_id, tenant_id=current_user.tenant_id)
        
        return {
            "success": True,
            "data": store_response,
            "message": "Store created successfully"
        }
        
    except Exception as e:
        logger.error("Failed to create store", error=str(e), tenant_id=current_user.tenant_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Failed to create store"
        )


@router.get("/stores/{store_id}", response_model=Dict[str, Any])
async def get_store(
    store_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get store by ID"""
    try:
        logger.info("Fetching store", store_id=store_id, tenant_id=current_user.tenant_id)
        
        store = await user_repository.get_store_by_id(store_id)
        if not store:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Store not found"
            )
        
        if store.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.FORBIDDEN,
                message="Access denied"
            )
        
        store_response = StoreResponse(
            store_id=store.store_id,
            tenant_id=store.tenant_id,
            name=store.name,
            address=store.address,
            timezone=store.timezone,
            currency=store.currency,
            status=store.status,
            settings=store.settings,
            created_at=store.created_at.isoformat(),
            updated_at=store.updated_at.isoformat()
        )
        
        return {
            "success": True,
            "data": store_response
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Failed to fetch store", error=str(e), store_id=store_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Failed to fetch store"
        )


@router.put("/stores/{store_id}", response_model=Dict[str, Any])
async def update_store(
    store_id: str,
    request: StoreUpdateRequest,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Update store"""
    try:
        logger.info("Updating store", store_id=store_id, tenant_id=current_user.tenant_id)
        
        store = await user_repository.get_store_by_id(store_id)
        if not store:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Store not found"
            )
        
        if store.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.FORBIDDEN,
                message="Access denied"
            )
        
        # Prepare update data
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.address is not None:
            update_data["address"] = request.address
        if request.timezone is not None:
            update_data["timezone"] = request.timezone
        if request.currency is not None:
            update_data["currency"] = request.currency
        if request.status is not None:
            update_data["status"] = request.status
        if request.settings is not None:
            update_data["settings"] = request.settings
        
        # Update store
        updated_store = await user_repository.stores_repo.update_by_id(
            store_id,
            update_data,
            "store_id"
        )
        
        if not updated_store:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Failed to update store"
            )
        
        store_response = StoreResponse(
            store_id=updated_store.store_id,
            tenant_id=updated_store.tenant_id,
            name=updated_store.name,
            address=updated_store.address,
            timezone=updated_store.timezone,
            currency=updated_store.currency,
            status=updated_store.status,
            settings=updated_store.settings,
            created_at=updated_store.created_at.isoformat(),
            updated_at=updated_store.updated_at.isoformat()
        )
        
        logger.info("Store updated successfully", store_id=store_id)
        
        return {
            "success": True,
            "data": store_response,
            "message": "Store updated successfully"
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Failed to update store", error=str(e), store_id=store_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Failed to update store"
        )


@router.delete("/stores/{store_id}", response_model=Dict[str, Any])
async def delete_store(
    store_id: str,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Delete store"""
    try:
        logger.info("Deleting store", store_id=store_id, tenant_id=current_user.tenant_id)
        
        store = await user_repository.get_store_by_id(store_id)
        if not store:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Store not found"
            )
        
        if store.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.FORBIDDEN,
                message="Access denied"
            )
        
        # Check if store has devices
        devices = await user_repository.get_devices_by_store(
            tenant_id=current_user.tenant_id,
            store_id=store_id
        )
        
        if devices:
            raise PlayParkException(
                error_code=ErrorCode.BAD_REQUEST,
                message="Cannot delete store with active devices"
            )
        
        # Delete store
        deleted = await user_repository.stores_repo.delete_by_id(store_id, "store_id")
        
        if not deleted:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Failed to delete store"
            )
        
        logger.info("Store deleted successfully", store_id=store_id)
        
        return {
            "success": True,
            "message": "Store deleted successfully"
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Failed to delete store", error=str(e), store_id=store_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Failed to delete store"
        )


# Device Endpoints
@router.get("/devices", response_model=Dict[str, Any])
async def get_devices(
    store_id: Optional[str] = None,
    type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get devices for the current tenant"""
    try:
        logger.info("Fetching devices", tenant_id=current_user.tenant_id, store_id=store_id)
        
        if store_id:
            devices = await user_repository.get_devices_by_store(
                tenant_id=current_user.tenant_id,
                store_id=store_id,
                type=type,
                skip=skip,
                limit=limit
            )
        else:
            # Get all devices for tenant
            devices = await user_repository.devices_repo.get_many(
                {"tenant_id": current_user.tenant_id},
                skip=skip,
                limit=limit
            )
        
        device_responses = [
            DeviceResponse(
                device_id=device.device_id,
                tenant_id=device.tenant_id,
                store_id=device.store_id,
                type=device.type,
                name=device.name,
                status=device.status,
                last_seen=device.last_seen.isoformat() if device.last_seen else None,
                created_at=device.created_at.isoformat(),
                updated_at=device.updated_at.isoformat()
            )
            for device in devices
        ]
        
        return {
            "success": True,
            "data": device_responses,
            "total": len(device_responses)
        }
        
    except Exception as e:
        logger.error("Failed to fetch devices", error=str(e), tenant_id=current_user.tenant_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to fetch devices"
        )


@router.get("/stores/{store_id}/devices", response_model=Dict[str, Any])
async def get_store_devices(
    store_id: str,
    type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = CurrentUser,
    user_repository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get devices for a specific store"""
    try:
        logger.info("Fetching store devices", store_id=store_id, tenant_id=current_user.tenant_id)
        
        # Verify store exists and belongs to tenant
        store = await user_repository.get_store_by_id(store_id)
        if not store or store.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Store not found"
            )
        
        devices = await user_repository.get_devices_by_store(
            tenant_id=current_user.tenant_id,
            store_id=store_id,
            device_type=device_type,
            skip=skip,
            limit=limit
        )
        
        device_responses = [
            DeviceResponse(
                device_id=device.device_id,
                tenant_id=device.tenant_id,
                store_id=device.store_id,
                type=device.type,
                name=device.name,
                status=device.status,
                last_seen=device.last_seen.isoformat() if device.last_seen else None,
                created_at=device.created_at.isoformat(),
                updated_at=device.updated_at.isoformat()
            )
            for device in devices
        ]
        
        return {
            "success": True,
            "data": device_responses,
            "total": len(device_responses)
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Failed to fetch store devices", error=str(e), store_id=store_id)
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Failed to fetch store devices"
        )
