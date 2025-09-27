"""
Settings Router
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query

from app.models.settings import (
    SettingCreateRequest, SettingUpdateRequest, SettingResponse,
    FeatureFlagUpdateRequest, FeatureFlagResponse
)
from app.repositories.settings import SettingRepository, FeatureFlagRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_settings(
    store_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get merged settings (tenant + store overrides)"""
    try:
        setting_repo = SettingRepository()
        
        # Get merged settings
        settings = await setting_repo.get_merged_settings(
            current_user.tenant_id, store_id or current_user.store_id
        )
        
        return settings
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve settings",
            details={"error": str(e)}
        )


@router.get("/keys/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    store_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific setting by key"""
    try:
        setting_repo = SettingRepository()
        
        setting = await setting_repo.get_by_key(
            current_user.tenant_id, key, store_id or current_user.store_id
        )
        
        if not setting:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Setting not found",
                status_code=404
            )
        
        return SettingResponse(
            key=setting.key,
            value=setting.value,
            type=setting.type,
            description=setting.description,
            category=setting.category,
            created_at=setting.created_at,
            updated_at=setting.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve setting",
            details={"error": str(e)}
        )


@router.put("/keys/{key}", response_model=SettingResponse)
async def set_setting(
    key: str,
    setting_data: SettingUpdateRequest,
    store_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Set a setting value"""
    try:
        setting_repo = SettingRepository()
        
        setting = await setting_repo.set_setting(
            tenant_id=current_user.tenant_id,
            key=key,
            value=setting_data.value,
            store_id=store_id or current_user.store_id,
            description=setting_data.description,
            category=setting_data.category
        )
        
        return SettingResponse(
            key=setting.key,
            value=setting.value,
            type=setting.type,
            description=setting.description,
            category=setting.category,
            created_at=setting.created_at,
            updated_at=setting.updated_at
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to set setting",
            details={"error": str(e)}
        )


@router.post("/keys", response_model=SettingResponse)
async def create_setting(
    setting_data: SettingCreateRequest,
    store_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new setting"""
    try:
        setting_repo = SettingRepository()
        
        # Check if setting already exists
        existing_setting = await setting_repo.get_by_key(
            current_user.tenant_id, setting_data.key, store_id or current_user.store_id
        )
        if existing_setting:
            raise PlayParkException(
                error_code=ErrorCode.E_DUPLICATE,
                message="Setting already exists",
                status_code=400
            )
        
        setting = await setting_repo.set_setting(
            tenant_id=current_user.tenant_id,
            key=setting_data.key,
            value=setting_data.value,
            store_id=store_id or current_user.store_id,
            setting_type=setting_data.type,
            description=setting_data.description,
            category=setting_data.category
        )
        
        return SettingResponse(
            key=setting.key,
            value=setting.value,
            type=setting.type,
            description=setting.description,
            category=setting.category,
            created_at=setting.created_at,
            updated_at=setting.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create setting",
            details={"error": str(e)}
        )


@router.get("/feature-flags", response_model=Dict[str, bool])
async def get_feature_flags(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get feature flags"""
    try:
        feature_flag_repo = FeatureFlagRepository()
        
        # This would typically get all feature flags for the tenant
        # For now, return a simple example
        flags = {}
        
        # Example flags
        flags["new_checkout_flow"] = await feature_flag_repo.is_enabled(
            "new_checkout_flow", current_user.tenant_id, current_user.store_id
        )
        flags["loyalty_program"] = await feature_flag_repo.is_enabled(
            "loyalty_program", current_user.tenant_id, current_user.store_id
        )
        flags["advanced_reporting"] = await feature_flag_repo.is_enabled(
            "advanced_reporting", current_user.tenant_id, current_user.store_id
        )
        
        return flags
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve feature flags",
            details={"error": str(e)}
        )


@router.put("/feature-flags/{key}", response_model=FeatureFlagResponse)
async def set_feature_flag(
    key: str,
    flag_data: FeatureFlagUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Set feature flag value"""
    try:
        feature_flag_repo = FeatureFlagRepository()
        
        flag = await feature_flag_repo.set_flag(
            key=key,
            enabled=flag_data.enabled,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            conditions=flag_data.conditions,
            description=flag_data.description
        )
        
        return FeatureFlagResponse(
            key=flag.key,
            enabled=flag.enabled,
            conditions=flag.conditions,
            description=flag.description,
            created_at=flag.created_at,
            updated_at=flag.updated_at
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to set feature flag",
            details={"error": str(e)}
        )


@router.get("/feature-flags/{key}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    key: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific feature flag"""
    try:
        feature_flag_repo = FeatureFlagRepository()
        
        flag = await feature_flag_repo.get_by_key(
            key, current_user.tenant_id, current_user.store_id
        )
        
        if not flag:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Feature flag not found",
                status_code=404
            )
        
        return FeatureFlagResponse(
            key=flag.key,
            enabled=flag.enabled,
            conditions=flag.conditions,
            description=flag.description,
            created_at=flag.created_at,
            updated_at=flag.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve feature flag",
            details={"error": str(e)}
        )