"""
Settings Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BaseRepository
from app.models.settings import Setting, FeatureFlag


class SettingRepository(BaseRepository[Setting]):
    """Setting repository"""
    
    def __init__(self):
        super().__init__("settings", Setting)
    
    async def get_by_tenant(self, tenant_id: str) -> List[Setting]:
        """Get settings by tenant"""
        return await self.get_many({"tenant_id": tenant_id})
    
    async def get_by_store(self, store_id: str) -> List[Setting]:
        """Get settings by store"""
        return await self.get_many({"store_id": store_id})
    
    async def get_by_key(
        self,
        tenant_id: str,
        key: str,
        store_id: Optional[str] = None
    ) -> Optional[Setting]:
        """Get setting by key with store override"""
        # First try to get store-specific setting
        if store_id:
            query = {"tenant_id": tenant_id, "store_id": store_id, "key": key}
            store_setting = await self.get_many(query, limit=1)
            if store_setting:
                return store_setting[0]
        
        # Fall back to tenant-level setting
        query = {"tenant_id": tenant_id, "store_id": None, "key": key}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def get_merged_settings(
        self,
        tenant_id: str,
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get merged settings (tenant + store overrides)"""
        # Get tenant-level settings
        tenant_settings = await self.get_by_tenant(tenant_id)
        tenant_dict = {s.key: s.value for s in tenant_settings if s.store_id is None}
        
        # Get store-level overrides
        if store_id:
            store_settings = await self.get_by_store(store_id)
            store_dict = {s.key: s.value for s in store_settings if s.tenant_id == tenant_id}
            tenant_dict.update(store_dict)
        
        return tenant_dict
    
    async def set_setting(
        self,
        tenant_id: str,
        key: str,
        value: Any,
        store_id: Optional[str] = None,
        setting_type: str = "string",
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> Setting:
        """Set a setting value"""
        # Check if setting exists
        existing = await self.get_by_key(tenant_id, key, store_id)
        
        if existing:
            # Update existing setting
            update_data = {"value": value}
            if description is not None:
                update_data["description"] = description
            if category is not None:
                update_data["category"] = category
            
            return await self.update_by_id(existing.id, update_data)
        else:
            # Create new setting
            setting_data = {
                "tenant_id": tenant_id,
                "store_id": store_id,
                "key": key,
                "value": value,
                "type": setting_type,
                "description": description,
                "category": category,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(setting_data)
            setting_data["_id"] = result.inserted_id
            return Setting(**setting_data)


class FeatureFlagRepository(BaseRepository[FeatureFlag]):
    """Feature flag repository"""
    
    def __init__(self):
        super().__init__("feature_flags", FeatureFlag)
    
    async def get_by_key(
        self,
        key: str,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None
    ) -> Optional[FeatureFlag]:
        """Get feature flag by key with tenant/store overrides"""
        # Try store-specific override first
        if store_id:
            query = {"key": key, "store_id": store_id}
            store_flag = await self.get_many(query, limit=1)
            if store_flag:
                return store_flag[0]
        
        # Try tenant-specific override
        if tenant_id:
            query = {"key": key, "tenant_id": tenant_id, "store_id": None}
            tenant_flag = await self.get_many(query, limit=1)
            if tenant_flag:
                return tenant_flag[0]
        
        # Fall back to global setting
        query = {"key": key, "tenant_id": None, "store_id": None}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def is_enabled(
        self,
        key: str,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None
    ) -> bool:
        """Check if feature flag is enabled"""
        flag = await self.get_by_key(key, tenant_id, store_id)
        return flag.enabled if flag else False
    
    async def set_flag(
        self,
        key: str,
        enabled: bool,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> FeatureFlag:
        """Set feature flag value"""
        # Check if flag exists
        existing = await self.get_by_key(key, tenant_id, store_id)
        
        if existing:
            # Update existing flag
            update_data = {"enabled": enabled}
            if conditions is not None:
                update_data["conditions"] = conditions
            if description is not None:
                update_data["description"] = description
            
            return await self.update_by_id(existing.id, update_data)
        else:
            # Create new flag
            flag_data = {
                "key": key,
                "enabled": enabled,
                "tenant_id": tenant_id,
                "store_id": store_id,
                "conditions": conditions or {},
                "description": description,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(flag_data)
            flag_data["_id"] = result.inserted_id
            return FeatureFlag(**flag_data)
