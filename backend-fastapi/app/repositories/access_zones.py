"""
Access Zone Repository
"""
from typing import List, Optional

from .base import BaseRepository
from app.models.access_zones import AccessZone, PackageZoneMap


class AccessZoneRepository(BaseRepository[AccessZone]):
    """Access zone repository"""
    
    def __init__(self):
        super().__init__("access_zones", AccessZone)
    
    async def get_by_store(self, store_id: str) -> List[AccessZone]:
        """Get access zones by store"""
        return await self.get_many({"store_id": store_id, "active": True})
    
    async def update_occupancy(self, zone_id: str, count: int) -> Optional[AccessZone]:
        """Update zone occupancy"""
        return await self.update_by_id(zone_id, {"current_count": count}, "zone_id")
    
    async def deactivate(self, zone_id: str) -> Optional[AccessZone]:
        """Deactivate access zone"""
        return await self.update_by_id(zone_id, {"active": False}, "zone_id")
    
    async def activate(self, zone_id: str) -> Optional[AccessZone]:
        """Activate access zone"""
        return await self.update_by_id(zone_id, {"active": True}, "zone_id")


class PackageZoneMapRepository(BaseRepository[PackageZoneMap]):
    """Package zone map repository"""
    
    def __init__(self):
        super().__init__("package_zone_map", PackageZoneMap)
    
    async def get_by_package(self, package_id: str) -> List[PackageZoneMap]:
        """Get zone mappings by package"""
        return await self.get_many({"package_id": package_id})
    
    async def get_by_zone(self, zone_id: str) -> List[PackageZoneMap]:
        """Get zone mappings by zone"""
        return await self.get_many({"zone_id": zone_id})
    
    async def get_package_zones(self, package_id: str) -> List[PackageZoneMap]:
        """Get all zones for a package"""
        return await self.get_many({"package_id": package_id})
    
    async def check_package_zone_access(
        self,
        package_id: str,
        zone_id: str
    ) -> Optional[PackageZoneMap]:
        """Check if package has access to zone"""
        query = {"package_id": package_id, "zone_id": zone_id}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
